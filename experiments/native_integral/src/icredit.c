/* Native integral-credit composition kernel (Maru array-view ABI, integer Q16).
 *
 * The deductive-learning vision, native: an axiom base (Horn rule pool) +
 * budget-limited combinatorial composition guided by accumulated credit.
 *
 * Unlike 0241's EXACT single-rule utility (a potential difference, where
 * integral == greedy), here credit is PARTIAL proof-participation: a rule is
 * credited if it fired on the backward path to a reached goal. Participation
 * is noisy per episode but stable in expectation, so accumulating it over many
 * episodes (the integral) should denoise and guide budget-limited search better
 * than a single episode's credit (greedy/single) or random order.
 *
 * Modes: integral (running sum over train) / single (one episode) / random /
 * uniform. Test: goals reached within a firing budget on held-out episodes.
 *
 * Integer-only (no float/libm); deterministic xorshift PRNG; LLVM-friendly.
 * Unbounded closure is parity-checked against Maru p-close (parity.l).
 */
#include "array_view.h"
#include <stdio.h>
#include <stdint.h>

#define Q16 65536L
#define NTOPIC 8
#define CHAIN 4                 /* atoms 4*t .. 4*t+3 per topic */
#define NDEC 8                  /* decoy rules */
#define NRULES (NTOPIC*(CHAIN-1) + NDEC)   /* 24 + 8 = 32 */
#define NATOMS (NTOPIC*CHAIN + NDEC)       /* 32 + 8 = 40 */
#define BUDGET 6                /* test firing budget (order matters) */
#define FULLB 64                /* generous budget for parity reference */
#define CREDITB 6               /* tight budget for TRAIN credit -> noisy participation */
#define NTRAIN 400
#define NTEST 400
#ifndef SEED
#define SEED 777
#endif

typedef struct { int head; uint64_t body; } Rule;

static Rule rules[NRULES];
static long W[NRULES];          /* learned weights (Q16-ish integer credit) */

/* deterministic integer PRNG (xorshift64*) — no libm */
static uint64_t rng_state;
static uint64_t nextrand(void){
  uint64_t x = rng_state;
  x ^= x >> 12; x ^= x << 25; x ^= x >> 27;
  rng_state = x;
  return x * 2685821657736338717ULL;
}
static int randbelow(int n){ return (int)(nextrand() % (uint64_t)n); }
static int chance(int pct){ return randbelow(100) < pct; }

static void build_rules(void){
  int k = 0;
  for (int t = 0; t < NTOPIC; t++)
    for (int s = 0; s < CHAIN-1; s++){
      rules[k].head = t*CHAIN + s + 1;
      rules[k].body = 1ULL << (t*CHAIN + s);
      k++;
    }
  for (int d = 0; d < NDEC; d++){
    rules[k].head = NTOPIC*CHAIN + d;
    /* decoys fire off chain atoms but lead to dead-end atoms (no goals) */
    rules[k].body = 1ULL << (d*CHAIN);
    k++;
  }
  /* deterministic shuffle so index/uniform order is uninformative */
  uint64_t s = 424242;
  for (int i = NRULES-1; i > 0; i--){
    s ^= s >> 12; s ^= s << 25; s ^= s >> 27;
    int j = (int)((s * 2685821657736338717ULL) % (uint64_t)(i+1));
    Rule tmp = rules[i]; rules[i] = rules[j]; rules[j] = tmp;
  }
}

typedef struct { uint64_t facts; uint64_t goals; } Episode;

static Episode make_episode(void){
  Episode e; e.facts = 0; e.goals = 0;
  for (int t = 0; t < NTOPIC; t++){
    if (chance(70)) e.facts |= 1ULL << (t*CHAIN);          /* seed chain start */
    int p = (t < 4) ? 85 : 25;                             /* hot vs cold topics */
    if (chance(p)) e.goals |= 1ULL << (t*CHAIN + CHAIN-1); /* goal chain end */
  }
  if (!e.goals) e.goals |= 1ULL << (CHAIN-1);
  /* noise facts */
  for (int i = 0; i < 3; i++) e.facts |= 1ULL << randbelow(NATOMS);
  return e;
}

/* Budget-limited forward closure, rule order guided by W (higher first, tie by
 * index). Records which rule derived each atom (parent) and which fired. */
static uint64_t close_budget(Episode e, long budget, const long *w,
                             int *parent, int *fired){
  uint64_t known = e.facts;
  for (int a = 0; a < NATOMS; a++) parent[a] = -1;
  for (int r = 0; r < NRULES; r++) fired[r] = 0;
  long used = 0;
  while (used < budget){
    int best = -1; long bestw = -999999999;
    for (int r = 0; r < NRULES; r++){
      if ((known & rules[r].body) == rules[r].body &&
          !(known & (1ULL << rules[r].head))){
        long ww = w ? w[r] : 0;
        if (ww > bestw){ bestw = ww; best = r; }
      }
    }
    if (best < 0) break;
    known |= 1ULL << rules[best].head;
    parent[rules[best].head] = best;
    fired[best] = 1;
    used++;
  }
  return known;
}

/* Partial participation credit: backward from reached goals through fired
 * rules; credit a rule if its head is an ancestor of a reached goal. */
static void participation(uint64_t known, Episode e, const int *fired,
                          long *credit){
  uint64_t anc = e.goals & known;
  int changed = 1;
  while (changed){
    changed = 0;
    for (int r = 0; r < NRULES; r++){
      if (fired[r] && (anc & (1ULL << rules[r].head))){
        uint64_t add = rules[r].body & ~anc;
        if (add){ anc |= add; changed = 1; }
      }
    }
  }
  for (int r = 0; r < NRULES; r++)
    credit[r] = (fired[r] && (anc & (1ULL << rules[r].head))) ? 1 : 0;
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

int main(void){
  build_rules();

  /* ---- explicit parity theory (also encoded in parity.l, Maru p-close) ----
   * atoms 0..5; rules 0->1,1->2,3->4,4->5; facts {0,3}; goals {2,5}.
   * Unbounded closure: derived=6, reached=2, known=63. Order-independent. */
  {
    Rule pr[4] = {{1,1ULL<<0},{2,1ULL<<1},{4,1ULL<<3},{5,1ULL<<4}};
    uint64_t facts = (1ULL<<0)|(1ULL<<3);
    uint64_t goals = (1ULL<<2)|(1ULL<<5);
    uint64_t known = facts; int changed = 1;
    while (changed){ changed = 0;
      for (int r=0;r<4;r++)
        if ((known & pr[r].body)==pr[r].body && !(known & (1ULL<<pr[r].head))){
          known |= 1ULL<<pr[r].head; changed = 1; } }
    printf("PARITY2 derived=%d reached=%d known=%llu\n",
           __builtin_popcountll(known), __builtin_popcountll(known & goals),
           (unsigned long long)known);
  }

  /* ---- parity reference: unbounded closure on a fixed episode ---- */
  rng_state = 12345;
  Episode ref = make_episode();
  int parent[NATOMS], fired[NRULES];
  uint64_t full = close_budget(ref, FULLB, 0, parent, fired);
  printf("PARITY facts=%llu goals=%llu derived=%d reached=%d total=%d\n",
         (unsigned long long)ref.facts, (unsigned long long)ref.goals,
         __builtin_popcountll(full), goals_reached(full, ref), goals_total(ref));

  /* ---- generate train/test episodes deterministically ---- */
  static Episode train[NTRAIN], test[NTEST];
  rng_state = SEED;
  for (int i = 0; i < NTRAIN; i++) train[i] = make_episode();
  for (int i = 0; i < NTEST; i++) test[i] = make_episode();

  /* ---- learn weights ---- */
  long w_integral[NRULES], w_single[NRULES], w_random[NRULES], w_uniform[NRULES];
  long credit[NRULES];
  for (int r = 0; r < NRULES; r++){
    w_integral[r] = 0; w_single[r] = 0; w_uniform[r] = 0;
    w_random[r] = 0;
  }
  rng_state = 999;
  for (int r = 0; r < NRULES; r++) w_random[r] = randbelow(1000);

  for (int i = 0; i < NTRAIN; i++){
    /* tight-budget closure -> noisy participation (single sample unreliable) */
    uint64_t known = close_budget(train[i], CREDITB, w_uniform, parent, fired);
    participation(known, train[i], fired, credit);
    for (int r = 0; r < NRULES; r++){
      w_integral[r] += credit[r];          /* the integral: running sum denoises */
      if (i == 0) w_single[r] = credit[r]; /* single noisy episode */
    }
  }

  /* ---- evaluate on held-out test under budget ---- */
  const char *names[4] = {"integral","single","random","uniform"};
  const long *ws[4] = {w_integral, w_single, w_random, w_uniform};
  long sum_reached[4] = {0,0,0,0};
  long sum_total[4] = {0,0,0,0};
  long full_success[4] = {0,0,0,0};
  for (int m = 0; m < 4; m++){
    for (int i = 0; i < NTEST; i++){
      uint64_t known = close_budget(test[i], BUDGET, ws[m], parent, fired);
      int gr = goals_reached(known, test[i]);
      int gt = goals_total(test[i]);
      sum_reached[m] += gr;
      sum_total[m] += gt;
      if (gr == gt) full_success[m]++;
    }
  }
  for (int m = 0; m < 4; m++){
    long pct = sum_total[m] ? (sum_reached[m]*10000)/sum_total[m] : 0;
    printf("TEST %s reached=%ld total=%ld pct=%ld.%02ld full_success=%ld/%d\n",
           names[m], sum_reached[m], sum_total[m], pct/100, pct%100,
           full_success[m], NTEST);
  }
  /* learned-weight diagnostic: hot-topic chain rules should outweigh cold */
  long hot=0, cold=0;
  for (int t=0;t<4;t++) hot += w_integral[t*(CHAIN-1)];
  for (int t=4;t<NTOPIC;t++) cold += w_integral[t*(CHAIN-1)];
  printf("WEIGHT hot_first_rule_sum=%ld cold_first_rule_sum=%ld\n", hot, cold);
  printf("DONE\n");
  return 0;
}