/* Native integral-credit composition kernel — v0.0243.
 *
 * Improvement over 0.0242 after review: the 0.0242 "integral vs single" gap was
 * confounded (400 train episodes vs 1) and the candidate order used a fixed
 * shuffled index as an implicit prior. This kernel fixes the protocol:
 *
 *   1. data/compute-matched memoryless arm (`last`): same episodes visited,
 *      weights = credit of the most recent episode only.
 *   2. randomized tie-break among equal-weight candidates during BOTH training
 *      credit and test search, so no fixed index order can act as a hidden
 *      prior; rule-table shuffle also varies per seed.
 *   3. exact-credit control (`exact`): full-budget participation credit, to
 *      separate "accumulation" from "credit fidelity" (0242 attributed the gain
 *      to noise, which this arm tests).
 *   4. recency control (`ema`) and online feedback arms (`online`, `online_exact`)
 *      where accumulated weights guide the training closure itself.
 *   5. structural oracles (`hot_oracle`, `pos_oracle`) as positive controls and
 *      ceilings, plus an independent-sample estimation-error curve (L1) so
 *      "accumulation denoises" is measured, not asserted.
 *   6. paired per-episode statistics (wins/losses, integer z, native bootstrap
 *      CI), 12 seeds, order-permutation controls.
 *
 * The axiom base is read through the Maru array-view ABI (include/array_view.h).
 * Integer-only kernel (no float/libm), deterministic xorshift PRNG, deterministic
 * across -O0/-O2/-O3. Ground closure of the generated worlds is cross-checked
 * against Maru p-close (src/parity-world.l), not just the 6-atom toy.
 */
#include "array_view.h"
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define NTOPIC 8
#define CHAIN 4                              /* atoms 4*t .. 4*t+3 per topic */
#define NDEC 8
#define NRULES (NTOPIC*(CHAIN-1) + NDEC)     /* 32 */
#define NATOMS (NTOPIC*CHAIN + NDEC)         /* 40 */
#define BUDGET 6                             /* test firing budget */
#define FULLB 64                             /* full closure (no budget pressure) */
#define CREDITB 6                            /* tight training credit budget */
#define NTRAIN 400
#define NTEST 400
#define NTARGET 400                          /* independent sample for the L1 target */
#define NSEED 12
#define FIRSTSEED 777
#define NSNAP 6
#define NARM 11

/* ---------------- axiom base through the Maru array-view ABI ---------------- */

static int32_t axiom_tab[NRULES*3];          /* [head, body_lo, body_hi] */
static MaruArrayView axiom_view;

static int rule_head(int r){ return (int)mav_get(&axiom_view, 3*r); }
static uint64_t rule_body(int r){
  return (mav_get(&axiom_view, 3*r+1) & 0xffffffffULL) |
         (mav_get(&axiom_view, 3*r+2) << 32);
}

static void build_rules(uint64_t shuffle_seed){
  int k = 0;
  for (int t = 0; t < NTOPIC; t++)
    for (int s = 0; s < CHAIN-1; s++){
      axiom_tab[3*k+0] = t*CHAIN + s + 1;
      axiom_tab[3*k+1] = (int32_t)(1ULL << (t*CHAIN + s));
      axiom_tab[3*k+2] = 0;
      k++;
    }
  for (int d = 0; d < NDEC; d++){
    axiom_tab[3*k+0] = NTOPIC*CHAIN + d;      /* dead-end head, never a goal */
    axiom_tab[3*k+1] = (int32_t)(1ULL << (d*CHAIN));
    axiom_tab[3*k+2] = 0;
    k++;
  }
  /* deterministic shuffle so the table index is uninformative */
  uint64_t s = shuffle_seed;
  for (int i = NRULES-1; i > 0; i--){
    s ^= s >> 12; s ^= s << 25; s ^= s >> 27;
    int j = (int)((s * 2685821657736338717ULL) % (uint64_t)(i+1));
    for (int f = 0; f < 3; f++){
      int32_t tmp = axiom_tab[3*i+f];
      axiom_tab[3*i+f] = axiom_tab[3*j+f];
      axiom_tab[3*j+f] = tmp;
    }
  }
  axiom_view.data = (const uint8_t*)axiom_tab;
  axiom_view.length = NRULES*3;
  axiom_view.stride = 4;
  axiom_view.elem_size = 4;
  if (!mav_valid(&axiom_view)){ fprintf(stderr, "array-view invalid\n"); exit(2); }
}

/* ---------------- deterministic integer PRNG ---------------- */

static uint64_t rng_state;
static uint64_t nextrand(void){
  uint64_t x = rng_state;
  x ^= x >> 12; x ^= x << 25; x ^= x >> 27;
  rng_state = x;
  return x * 2685821657736338717ULL;
}
static int randbelow(int n){ return (int)(nextrand() % (uint64_t)n); }
static int chance(int pct){ return randbelow(100) < pct; }
static uint64_t mix64(uint64_t x){
  x ^= x >> 12; x ^= x << 25; x ^= x >> 27;
  return x * 2685821657736338717ULL;
}

typedef struct { uint64_t facts; uint64_t goals; } Episode;

static Episode make_episode(void){
  Episode e; e.facts = 0; e.goals = 0;
  for (int t = 0; t < NTOPIC; t++){
    if (chance(70)) e.facts |= 1ULL << (t*CHAIN);
    int p = (t < 4) ? 85 : 25;                        /* hot vs cold topics */
    if (chance(p)) e.goals |= 1ULL << (t*CHAIN + CHAIN-1);
  }
  if (!e.goals) e.goals |= 1ULL << (CHAIN-1);
  for (int i = 0; i < 3; i++) e.facts |= 1ULL << randbelow(NATOMS);
  return e;
}

/* ---------------- budget-limited composition ---------------- */

/* Greedy closure guided by w (higher first). rand_tb=1 breaks ties uniformly at
 * random from tseed, so no fixed table index can act as a prior; rand_tb=0 keeps
 * the 0.0242 lowest-index tie-break for the ablation. */
static uint64_t close_w(Episode e, long budget, const long *w,
                        int *parent, int *fired, uint64_t tseed, int rand_tb){
  uint64_t known = e.facts, st = tseed | 1ULL;
  for (int a = 0; a < NATOMS; a++) parent[a] = -1;
  for (int r = 0; r < NRULES; r++) fired[r] = 0;
  long used = 0;
  int cand[NRULES];
  while (used < budget){
    int nc = 0; long bestw = 0;
    for (int r = 0; r < NRULES; r++){
      uint64_t body = rule_body(r);
      if ((known & body) == body && !(known & (1ULL << rule_head(r)))){
        long ww = w ? w[r] : 0;
        if (nc == 0 || ww > bestw){ bestw = ww; nc = 0; cand[nc++] = r; }
        else if (ww == bestw) cand[nc++] = r;
      }
    }
    if (!nc) break;
    int pick = cand[0];
    if (rand_tb && nc > 1){
      st = mix64(st);
      pick = cand[(int)(st % (uint64_t)nc)];
    }
    known |= 1ULL << rule_head(pick);
    parent[rule_head(pick)] = pick;
    fired[pick] = 1;
    used++;
  }
  return known;
}

/* Partial participation credit: a fired rule is credited iff its head is an
 * ancestor of a goal that the closure reached. */
static void participation(uint64_t known, Episode e, const int *fired, long *credit){
  uint64_t anc = e.goals & known;
  int changed = 1;
  while (changed){
    changed = 0;
    for (int r = 0; r < NRULES; r++){
      if (fired[r] && (anc & (1ULL << rule_head(r)))){
        uint64_t add = rule_body(r) & ~anc;
        if (add){ anc |= add; changed = 1; }
      }
    }
  }
  for (int r = 0; r < NRULES; r++)
    credit[r] = (fired[r] && (anc & (1ULL << rule_head(r)))) ? 1 : 0;
}

static int goals_reached(uint64_t known, Episode e){
  int c = 0;
  for (int a = 0; a < NATOMS; a++)
    if ((e.goals & (1ULL << a)) && (known & (1ULL << a))) c++;
  return c;
}
static int goals_total(Episode e){
  int c = 0;
  for (int a = 0; a < NATOMS; a++) if (e.goals & (1ULL << a)) c++;
  return c;
}

/* ---------------- integer statistics helpers ---------------- */

static int64_t isqrt64(uint64_t n){
  uint64_t x = 0, b = 1ULL << 62;
  while (b > n) b >>= 2;
  while (b){
    if (n >= x + b){ n -= x + b; x = (x >> 1) + b; }
    else x >>= 1;
    b >>= 2;
  }
  return (int64_t)x;
}
static int cmp_long(const void *a, const void *b){
  long x = *(const long*)a, y = *(const long*)b;
  return (x > y) - (x < y);
}

/* ---------------- experiment state ---------------- */

static Episode train[NTRAIN], test[NTEST], target[NTARGET];
static int parent[NATOMS], fired[NRULES];
static long credit[NRULES], credit_full[NRULES], credit_online[NRULES],
            credit_online_exact[NRULES];

typedef struct {
  long prior[NRULES], exact[NRULES], online[NRULES], online_exact[NRULES],
       ema[NRULES], last[NRULES], exact_last[NRULES];
  long snap[NSNAP][NRULES], snap_last[NSNAP][NRULES];
} Model;

static const int snap_n[NSNAP] = {1,10,50,100,200,400};

static void zero_model(Model *m){
  memset(m, 0, sizeof *m);
}

/* Learn all arms on train[] visited in the order perm[]. Offline arms use a
 * weight-free (uniform) training closure; online arms feed their own running
 * weights back into the training closure. All use the randomized tie-break. */
static void learn(const int *perm, Model *m, uint64_t *noise_disagree,
                  uint64_t *episodes_any_credit){
  int si = 0;
  for (int k = 0; k < NTRAIN; k++){
    int i = perm[k];
    uint64_t es = mix64((uint64_t)(i+1) * 0x9E3779B97F4A7C15ULL);

    uint64_t kt = close_w(train[i], CREDITB, 0, parent, fired, es, 1);
    participation(kt, train[i], fired, credit);

    uint64_t kf = close_w(train[i], FULLB, 0, parent, fired, es, 1);
    participation(kf, train[i], fired, credit_full);

    uint64_t ko = close_w(train[i], CREDITB, m->online, parent, fired, es, 1);
    participation(ko, train[i], fired, credit_online);

    uint64_t koe = close_w(train[i], FULLB, m->online_exact, parent, fired, es, 1);
    participation(koe, train[i], fired, credit_online_exact);

    int any = 0, diff = 0;
    for (int r = 0; r < NRULES; r++){
      m->prior[r]      += credit[r];
      m->exact[r]      += credit_full[r];
      m->online[r]     += credit_online[r];
      m->online_exact[r] += credit_online_exact[r];
      m->ema[r] = m->ema[r] - (m->ema[r] >> 3) + credit[r];   /* alpha = 1/8 */
      m->last[r] = credit[r];
      m->exact_last[r] = credit_full[r];
      if (credit[r]) any = 1;
      if (credit[r] != credit_full[r]) diff = 1;
    }
    if (any) (*episodes_any_credit)++;
    if (diff) (*noise_disagree)++;
    if (si < NSNAP && k+1 == snap_n[si]){
      for (int r = 0; r < NRULES; r++){
        m->snap[si][r] = m->prior[r];
        m->snap_last[si][r] = m->last[r];
      }
      si++;
    }
  }
}

/* ---------------- evaluation ---------------- */

static const char *arm_name[NARM];
static const long *arm_w[NARM];
static int arm_n = 0;
static long ep_reached[NARM][NTEST];
static long seed_pct[NSEED][NARM];

static void eval_arm(int slot, const char *name, const long *w){
  arm_name[slot] = name; arm_w[slot] = w;
  for (int i = 0; i < NTEST; i++){
    uint64_t known = close_w(test[i], BUDGET, w, parent, fired,
                             mix64((uint64_t)(i+1) * 0x2545F4914F6CDD1DULL), 1);
    ep_reached[slot][i] = goals_reached(known, test[i]);
  }
  if (slot + 1 > arm_n) arm_n = slot + 1;
}

static long arm_reached[NARM], arm_total[NARM], arm_full[NARM];
static void summarize(int slot){
  arm_reached[slot] = 0; arm_total[slot] = 0; arm_full[slot] = 0;
  for (int i = 0; i < NTEST; i++){
    arm_reached[slot] += ep_reached[slot][i];
    arm_total[slot] += goals_total(test[i]);
    if (ep_reached[slot][i] == goals_total(test[i])) arm_full[slot]++;
  }
}
static long arm_pct(int slot){
  return arm_total[slot] ? (arm_reached[slot]*10000)/arm_total[slot] : 0;
}
static void print_pct(const char *tag, int slot){
  long p = arm_pct(slot);
  printf("%s %s=%ld.%02ld", tag, arm_name[slot], p/100, p%100);
}

/* paired comparison of two evaluated arms; prints wins/losses/ties, integer z,
 * and a native bootstrap CI of the percentage difference. */
static void paired(const char *seed_str, int a, int b){
  int W = 0, L = 0, T = 0;
  for (int i = 0; i < NTEST; i++){
    if (ep_reached[a][i] > ep_reached[b][i]) W++;
    else if (ep_reached[a][i] < ep_reached[b][i]) L++;
    else T++;
  }
  long disc = W + L;
  long z = disc ? ((long)(W - L) * 1000) / isqrt64((uint64_t)disc) : 0;
  long pa = arm_pct(a), pb = arm_pct(b), d = pa - pb;
  printf("SEED %s PAIRED %s_vs_%s wins=%d losses=%d ties=%d z_milli=%ld diff_pp=%s%ld.%02ld\n",
         seed_str, arm_name[a], arm_name[b], W, L, T, z,
         d < 0 ? "-" : "+", (d<0?-d:d)/100, (d<0?-d:d)%100);

  enum { NB = 4000 };
  static long boot[NB];
  uint64_t st = 0xC0FFEEULL ^ (uint64_t)(a*131 + b);
  for (int bi = 0; bi < NB; bi++){
    long ra = 0, rb = 0, tt = 0;
    for (int i = 0; i < NTEST; i++){
      st = mix64(st);
      int j = (int)(st % (uint64_t)NTEST);
      ra += ep_reached[a][j]; rb += ep_reached[b][j];
      tt += goals_total(test[j]);
    }
    boot[bi] = tt ? ((ra - rb) * 10000) / tt : 0;
  }
  qsort(boot, NB, sizeof(long), cmp_long);
  long lo = boot[(NB*25)/1000], hi = boot[(NB*975)/1000], med = boot[NB/2];
  printf("SEED %s BOOT %s_minus_%s lo=%s%ld.%02ld hi=%s%ld.%02ld med=%s%ld.%02ld\n",
         seed_str, arm_name[a], arm_name[b],
         lo<0?"-":"", (lo<0?-lo:lo)/100, (lo<0?-lo:lo)%100,
         hi<0?"-":"", (hi<0?-hi:hi)/100, (hi<0?-hi:hi)%100,
         med<0?"-":"", (med<0?-med:med)/100, (med<0?-med:med)%100);
}

/* ---------------- per-seed run ---------------- */

static int run_seed(int seed, int detail){
  char sbuf[16]; snprintf(sbuf, sizeof sbuf, "%d", seed);
  build_rules(424242ULL + (uint64_t)(seed - FIRSTSEED));

  /* world episodes */
  rng_state = (uint64_t)seed;
  for (int i = 0; i < NTRAIN; i++) train[i] = make_episode();
  for (int i = 0; i < NTEST; i++) test[i] = make_episode();
  for (int i = 0; i < NTARGET; i++) target[i] = make_episode();

  /* independent-sample targets: the tight-credit expectation (what the prior
   * is estimating) and the exact-credit expectation (credit fidelity gap). */
  long target_tight[NRULES], target_exact[NRULES];
  for (int r = 0; r < NRULES; r++){ target_tight[r] = 0; target_exact[r] = 0; }
  for (int i = 0; i < NTARGET; i++){
    uint64_t es = mix64((uint64_t)(i+1) * 0xA24BAED4963EE407ULL);
    uint64_t kn = close_w(target[i], CREDITB, 0, parent, fired, es, 1);
    participation(kn, target[i], fired, credit);
    for (int r = 0; r < NRULES; r++) target_tight[r] += credit[r];
    uint64_t kf = close_w(target[i], FULLB, 0, parent, fired, es, 1);
    participation(kf, target[i], fired, credit_full);
    for (int r = 0; r < NRULES; r++) target_exact[r] += credit_full[r];
  }
  {
    long long num = 0;
    for (int r = 0; r < NRULES; r++){
      long long a = (long long)target_tight[r];
      long long b = (long long)target_exact[r];
      num += (a > b) ? (a - b) : (b - a);
    }
    printf("SEED %s CREDIT-GAP tight_vs_exact_l1_milli=%ld\n", sbuf,
           (long)((num * 1000) / (long long)NTARGET));
  }

  /* permutations: identity, reversed, xorshift-shuffled */
  static int perm[3][NTRAIN];
  for (int k = 0; k < NTRAIN; k++){ perm[0][k] = k; perm[1][k] = NTRAIN-1-k; perm[2][k] = k; }
  {
    uint64_t s = 0x5DEECE66DULL + (uint64_t)seed;
    for (int i = NTRAIN-1; i > 0; i--){
      s = mix64(s);
      int j = (int)(s % (uint64_t)(i+1));
      int t = perm[2][i]; perm[2][i] = perm[2][j]; perm[2][j] = t;
    }
  }

  static Model m_id, m_rev, m_shuf;
  zero_model(&m_id); zero_model(&m_rev); zero_model(&m_shuf);
  uint64_t noise_id = 0, epcredit = 0, noise_rev = 0, epcredit_rev = 0,
           noise_shuf = 0, epcredit_shuf = 0;
  learn(perm[0], &m_id, &noise_id, &epcredit);
  learn(perm[1], &m_rev, &noise_rev, &epcredit_rev);
  learn(perm[2], &m_shuf, &noise_shuf, &epcredit_shuf);
  const Model *m = &m_id;

  /* structural oracles / positive controls */
  long hot_oracle[NRULES], pos_oracle[NRULES];
  for (int r = 0; r < NRULES; r++){
    int h = rule_head(r);
    int hot = (h < NTOPIC*CHAIN) && (h/CHAIN < 4);
    hot_oracle[r] = (h < NTOPIC*CHAIN) ? (hot ? 2 : 1) : 0;
    /* depth-first: deeper chain rules win, so a started chain completes;
     * topic hotness breaks ties between equally deep candidates. */
    pos_oracle[r] = (h < NTOPIC*CHAIN) ? (100L*(h % CHAIN) + (hot ? 2 : 1)) : 0;
  }
  long rand_w[NRULES], zero_w[NRULES];
  rng_state = 999;
  for (int r = 0; r < NRULES; r++){ rand_w[r] = randbelow(1000); zero_w[r] = 0; }

  arm_n = 0;
  eval_arm(0, "prior", m->prior);
  eval_arm(1, "last", m->last);
  eval_arm(2, "uniform", zero_w);
  eval_arm(3, "random", rand_w);
  eval_arm(4, "ema", m->ema);
  eval_arm(5, "exact", m->exact);
  eval_arm(6, "exact_last", m->exact_last);
  eval_arm(7, "online", m->online);
  eval_arm(8, "online_exact", m->online_exact);
  eval_arm(9, "hot_oracle", hot_oracle);
  eval_arm(10, "pos_oracle", pos_oracle);
  for (int a = 0; a < arm_n; a++) summarize(a);
  for (int a = 0; a < arm_n; a++) seed_pct[seed - FIRSTSEED][a] = arm_pct(a);

  printf("SEED %s ARMS", sbuf);
  for (int a = 0; a < arm_n; a++) print_pct("", a);
  printf("\n");
  printf("SEED %s FULLSUCCESS", sbuf);
  for (int a = 0; a < arm_n; a++) printf(" %s=%ld/%d", arm_name[a], arm_full[a], NTEST);
  printf("\n");
  /* ablation: the 0.0242 protocol (fixed lowest-index tie-break) on the same
   * learned weights. Quantifies how much of a "no-learning" baseline was the
   * fixed table index acting as a hidden prior. */
  {
    long ra = 0, rb = 0, tt = 0;
    for (int i = 0; i < NTEST; i++){
      uint64_t k1 = close_w(test[i], BUDGET, m->prior, parent, fired, 1, 0);
      uint64_t k2 = close_w(test[i], BUDGET, zero_w, parent, fired, 1, 0);
      ra += goals_reached(k1, test[i]); rb += goals_reached(k2, test[i]);
      tt += goals_total(test[i]);
    }
    printf("SEED %s ABLATION fixed_tiebreak prior_pct=%ld.%02ld uniform_pct=%ld.%02ld "
           "(randomized prior_pct=%ld.%02ld uniform_pct=%ld.%02ld)\n",
           sbuf, tt?(ra*10000)/tt/100:0, tt?((ra*10000)/tt)%100:0,
           tt?(rb*10000)/tt/100:0, tt?((rb*10000)/tt)%100:0,
           arm_pct(0)/100, arm_pct(0)%100, arm_pct(2)/100, arm_pct(2)%100);
  }

  paired(sbuf, 0, 1);    /* prior vs last       (data/compute matched) */
  paired(sbuf, 0, 2);    /* prior vs uniform    (no learning) */
  paired(sbuf, 0, 4);    /* prior vs ema        (recency) */
  paired(sbuf, 0, 5);    /* prior vs exact      (credit fidelity) */

  /* order sensitivity: offline prior must be invariant (appendix control);
   * online feedback is path dependent by construction. */
  {
    int same_rev = 1, same_shuf = 1;
    for (int r = 0; r < NRULES; r++){
      if (m_id.prior[r] != m_rev.prior[r]) same_rev = 0;
      if (m_id.prior[r] != m_shuf.prior[r]) same_shuf = 0;
    }
    long o_id = 0, o_rev = 0, o_shuf = 0;
    for (int r = 0; r < NRULES; r++){
      o_id += m_id.online[r]; o_rev += m_rev.online[r]; o_shuf += m_shuf.online[r];
    }
    printf("SEED %s ORDER prior_invariant reversed=%d shuffled=%d online_weight_sum id=%ld rev=%ld shuf=%ld\n",
           sbuf, same_rev, same_shuf, o_id, o_rev, o_shuf);
  }

  if (detail){
    /* ground-closure parity worlds (same episodes that --emit-maru writes) */
    {
      uint64_t save = rng_state;
      rng_state = 12345;
      Episode ref = make_episode();
      rng_state = save;
      uint64_t kr = close_w(ref, FULLB, 0, parent, fired, 1, 0);
      printf("WORLD ref derived=%d reached=%d total=%d\n",
             __builtin_popcountll(kr), goals_reached(kr, ref), goals_total(ref));
      uint64_t kt = close_w(test[0], FULLB, 0, parent, fired, 1, 0);
      printf("WORLD test0 derived=%d reached=%d total=%d\n",
             __builtin_popcountll(kt), goals_reached(kt, test[0]), goals_total(test[0]));
    }
    printf("SEED %s NOISE episodes_with_credit=%llu tight_vs_full_disagree=%llu/%d\n",
           sbuf, (unsigned long long)epcredit, (unsigned long long)noise_id, NTRAIN);
    /* estimation-error curve: L1 distance to the independent-sample exact rate */
    for (int s = 0; s < NSNAP; s++){
      long long num = 0;
      for (int r = 0; r < NRULES; r++){
        long long a = (long long)m->snap[s][r] * (long long)NTARGET;
        long long b = (long long)target_tight[r] * (long long)snap_n[s];
        num += (a > b) ? (a - b) : (b - a);
      }
      long long den = (long long)snap_n[s] * (long long)NTARGET;
      long l1 = (long)((num * 1000) / den);
      long pi = 0, pl = 0, tt = 0;
      for (int i = 0; i < NTEST; i++){
        uint64_t k1 = close_w(test[i], BUDGET, m->snap[s], parent, fired,
                              mix64((uint64_t)(i+1) * 0x2545F4914F6CDD1DULL), 1);
        int g1 = goals_reached(k1, test[i]);
        uint64_t k2 = close_w(test[i], BUDGET, m->snap_last[s], parent, fired,
                              mix64((uint64_t)(i+1) * 0x2545F4914F6CDD1DULL), 1);
        int g2 = goals_reached(k2, test[i]);
        int gt = goals_total(test[i]);
        pi += g1; pl += g2; tt += gt;
      }
      printf("SEED %s CURVE n=%d prior_pct=%ld.%02ld last_pct=%ld.%02ld l1_milli=%ld\n",
             sbuf, snap_n[s],
             tt ? (pi*10000)/tt/100 : 0, tt ? ((pi*10000)/tt)%100 : 0,
             tt ? (pl*10000)/tt/100 : 0, tt ? ((pl*10000)/tt)%100 : 0, l1);
    }
    /* distribution of single-episode policies (no accumulation): what one
     * episode's credit vector achieves on the held-out set. */
    {
      enum { NSP = 100 };
      long sum = 0, mn = 0, mx = 0;
      for (int e = 0; e < NSP; e++){
        uint64_t es = mix64((uint64_t)(e+1) * 0x9E3779B97F4A7C15ULL);
        uint64_t kn = close_w(train[e], CREDITB, 0, parent, fired, es, 1);
        participation(kn, train[e], fired, credit);
        long rr = 0, tt = 0;
        for (int i = 0; i < NTEST; i++){
          uint64_t known = close_w(test[i], BUDGET, credit, parent, fired,
                                   mix64((uint64_t)(i+1) * 0x2545F4914F6CDD1DULL), 1);
          rr += goals_reached(known, test[i]); tt += goals_total(test[i]);
        }
        long p = tt ? (rr*10000)/tt : 0;
        sum += p;
        if (e == 0 || p < mn) mn = p;
        if (e == 0 || p > mx) mx = p;
      }
      printf("SEED %s SINGLEPOLICY n=%d mean_pct=%ld.%02ld min_pct=%ld.%02ld max_pct=%ld.%02ld\n",
             sbuf, NSP, (sum/NSP)/100, (sum/NSP)%100, mn/100, mn%100, mx/100, mx%100);
    }
    /* rank agreement between learned prior and exact-credit prior (tau-a) */
    {
      long C = 0, Dp = 0;
      for (int i = 0; i < NRULES; i++)
        for (int j = i+1; j < NRULES; j++){
          long da = m->prior[i] - m->prior[j], db = m->exact[i] - m->exact[j];
          long s = da * db;
          if (s > 0) C++; else if (s < 0) Dp++;
        }
      long dd = C + Dp;
      long tau = dd ? ((C - Dp) * 1000) / dd : 0;
      printf("SEED %s KENDALL prior_vs_exact concordant=%ld discordant=%ld tau_milli=%ld\n",
             sbuf, C, Dp, tau);
    }
    /* topic and chain-position diagnostics on the true mapping (head atom) */
    {
      long topic[NTOPIC], pos[CHAIN-1];
      for (int t = 0; t < NTOPIC; t++) topic[t] = 0;
      for (int s = 0; s < CHAIN-1; s++) pos[s] = 0;
      for (int r = 0; r < NRULES; r++){
        int h = rule_head(r);
        if (h < NTOPIC*CHAIN){          /* chain heads are 4t+1,4t+2,4t+3 */
          topic[h/CHAIN] += m->prior[r];
          pos[(h % CHAIN) - 1] += m->prior[r];
        }
      }
      long hot = 0, cold = 0;
      for (int t = 0; t < 4; t++) hot += topic[t];
      for (int t = 4; t < NTOPIC; t++) cold += topic[t];
      printf("SEED %s TOPIC", sbuf);
      for (int t = 0; t < NTOPIC; t++) printf(" t%d=%ld", t, topic[t]);
      printf(" hot_sum=%ld cold_sum=%ld hot_gt_cold=%d\n", hot, cold, hot > cold);
      printf("SEED %s POSITION s0=%ld s1=%ld s2=%ld depth_ordered=%d\n",
             sbuf, pos[0], pos[1], pos[2], (pos[2] >= pos[1] && pos[1] >= pos[0]));
    }
    /* learned prior per rule (head, topic, position) */
    for (int r = 0; r < NRULES; r++){
      int h = rule_head(r);
      printf("RULE %d head=%d topic=%d pos=%d prior=%ld exact=%ld\n",
             r, h, (h < NTOPIC*CHAIN) ? h/CHAIN : -1,
             (h < NTOPIC*CHAIN) ? (h % CHAIN) - 1 : -1, m->prior[r], m->exact[r]);
    }
  }
  return 0;
}

/* ---------------- Maru world emit ---------------- */

static void emit_case(const char *tag, Episode e){
  {
    uint64_t known = close_w(e, FULLB, 0, parent, fired, 1, 0);
    printf("(define %s-derived %d)\n", tag, __builtin_popcountll(known));
    printf("(define %s-reached %d)\n", tag, goals_reached(known, e));
    printf("(define %s-facts (list\n", tag);
    for (int a = 0; a < NATOMS; a++)
      if (e.facts & (1ULL << a))
        printf("  (l-fact \"f%d\" (l-atom 'at (list \"a%d\")))\n", a, a);
    printf("  ))\n(define %s-rules (list\n", tag);
    for (int r = 0; r < NRULES; r++){
      uint64_t body = rule_body(r);
      printf("  (l-rule (l-atom 'at (list \"a%d\")) (list", rule_head(r));
      for (int b = 0; b < NATOMS; b++)
        if (body & (1ULL << b)) printf(" (l-atom 'at (list \"a%d\"))", b);
      printf("))\n");
    }
    printf("  ))\n(define %s-goals (list\n", tag);
    for (int a = 0; a < NATOMS; a++)
      if (e.goals & (1ULL << a))
        printf("  (l-atom 'at (list \"a%d\"))\n", a);
    printf("  ))\n");
  }
}

static void emit_maru(void){
  build_rules(424242ULL);
  rng_state = 12345;
  Episode ref = make_episode();
  emit_case("wref", ref);
  /* same stream as run_seed(777): 400 train episodes, then test[0] */
  rng_state = FIRSTSEED;
  for (int i = 0; i < NTRAIN; i++) train[i] = make_episode();
  test[0] = make_episode();
  emit_case("wtest0", test[0]);
}

int main(int argc, char **argv){
  if (argc > 1 && strcmp(argv[1], "--emit-maru") == 0){ emit_maru(); return 0; }

  /* toy parity theory (also in src/parity.l) */
  {
    int ph[4] = {1,2,4,5};
    uint64_t pb[4] = {1ULL<<0, 1ULL<<1, 1ULL<<3, 1ULL<<4};
    uint64_t facts = (1ULL<<0)|(1ULL<<3), goals = (1ULL<<2)|(1ULL<<5);
    uint64_t known = facts;
    int changed = 1;
    while (changed){
      changed = 0;
      for (int r = 0; r < 4; r++)
        if ((known & pb[r]) == pb[r] && !(known & (1ULL << ph[r]))){
          known |= 1ULL << ph[r]; changed = 1;
        }
    }
    printf("PARITY2 derived=%d reached=%d known=%llu\n",
           __builtin_popcountll(known), __builtin_popcountll(known & goals),
           (unsigned long long)known);
  }

  for (int s = 0; s < NSEED; s++) run_seed(FIRSTSEED + s, s == 0);

  /* aggregate over seeds (computed, not asserted) */
  {
    long pmin = 0, pmax = 0, lmax = 0, umax = 0, pmed = 0, minmargin = 0;
    long pm[64], lm[64];
    for (int s = 0; s < NSEED; s++){
      int seed = FIRSTSEED + s;
      long p = seed_pct[seed - FIRSTSEED][0];
      long l = seed_pct[seed - FIRSTSEED][1];
      long u = seed_pct[seed - FIRSTSEED][2];
      pm[s] = p; lm[s] = l;
      if (s == 0 || p < pmin) pmin = p;
      if (s == 0 || p > pmax) pmax = p;
      if (s == 0 || l > lmax) lmax = l;
      if (s == 0 || u > umax) umax = u;
      if (s == 0 || (p - l) < minmargin) minmargin = p - l;
    }
    for (int i = 0; i < NSEED; i++)
      for (int j = i+1; j < NSEED; j++)
        if (pm[j] < pm[i]){ long t = pm[i]; pm[i] = pm[j]; pm[j] = t; }
    pmed = pm[NSEED/2];
    (void)lm;
    printf("AGG prior_min=%ld.%02ld prior_median=%ld.%02ld prior_max=%ld.%02ld "
           "last_max=%ld.%02ld uniform_max=%ld.%02ld min_margin_pp=%ld.%02ld seeds=%d\n",
           pmin/100, pmin%100, pmed/100, pmed%100, pmax/100, pmax%100,
           lmax/100, lmax%100, umax/100, umax%100,
           minmargin/100, (minmargin<0?-minmargin:minmargin)%100, NSEED);
  }
  printf("DONE\n");
  return 0;
}