/* Proof-state transformer lab — native C/LLVM, no Python, no torch.
 *
 * Fixture port of experiments/m1_proof_state/world.py (0.0238, PyTorch):
 *   finite propositional Horn theory over 6 unary predicates and disjoint
 *   entity splits; candidate actions are Horn rules; utility is measured by
 *   closure growth on a sandbox copy of the current theory:
 *       utility = 5 * newly-derived goal atoms + 0.15 * all newly-derived
 *                 atoms - rule cost
 *   Features never see entity ids, so the task is entity-held-out.
 *
 * Stages in this file:
 *   1. world generation + closure oracle + M1 features + proof-policy rollout
 *   2. (next) set-transformer forward/backward, training, variants
 *
 * Parity: `./pst --dump out/worlds.txt` writes the generated worlds and the
 * computed features/utilities; tools/check_parity.py recomputes them with the
 * reference Python implementation (m1_proof_state/world.py) and compares.
 */
#include "array_view.h"
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <math.h>

#ifndef MAXBUDGET
#define MAXBUDGET 6              /* R250-1: rule-sequence arrays must cover eval budget 6 */
#endif
#ifndef HARD_GOALS
#define HARD_GOALS 0             /* 0 = reference goal distribution, 1 = declared harder fixture */
#endif
#ifndef RELOB
#define RELOB 0                  /* 1 = goal-binding/dependency preserving features */
#endif
#ifndef BINDTOK
#define BINDTOK 0                /* 0 off, 1 aligned binding tokens, 2 entity-shifted (control) */
#endif
#ifndef INTEGRAL
#define INTEGRAL 0               /* 1 = path-integral support (avg/growth) + per-rule prior features */
#endif
#ifndef LIFTED
#define LIFTED 0                 /* 1 = scale the predicate-id one-hot block by LIFT_RHO (lifted token) */
#endif
#ifndef LIFT_RHO
#define LIFT_RHO 1.0             /* residual scale on predicate identity; 1.0 == base, 0 = type-only */
#endif
#ifndef PRIOR_SHUF
#define PRIOR_SHUF 0             /* 1 = derange the per-rule prior (identity-destroying control) */
#endif
#ifndef PATH_GAMMA
#define PATH_GAMMA 1.0           /* retention decay on the path integral; 1.0 = monotone accumulation */
#endif
#ifndef REMFEAT
#define REMFEAT 0                /* 0.0269: remaining-budget slot in the state features */
#endif
#ifndef ENTFEAT
#define ENTFEAT 0                /* 0.0270 S0e control: absolute entity/role one-hots in
                                  * candidate features (binding info WITHOUT typed tokens) */
#endif
#ifndef TYPEDSHUF
#define TYPEDSHUF 0              /* 0.0270 S1shuf control: fact-token atom identities passed
                                  * through a fixed derangement (content destroyed, counts and
                                  * type structure preserved; candidates/goals stay true) */
#endif
#if ENTFEAT && !RELATOM
#error "ENTFEAT requires RELATOM"
#endif
#if TYPEDSHUF && !TYPED
#error "TYPEDSHUF requires TYPED"
#endif
#define BIND_FEAT (NSLOT*WENT + WENT)   /* body slot x entity support + head-atom known */
#define ID_BLOCK_LO 8                 /* candidate predicate-id one-hot block: head + body slots */
#define ID_BLOCK_HI (8 + P + NSLOT*P) /* = 26 */
static int g_goaldepth = 0;      /* 0 = default (HARD_GOALS compile flag), k>=1 = goals need k candidate steps */
static int g_eval_budget = 4;
static int g_label_rem_max = 4;  /* 0.0267: labels are defined at budget 4 regardless of
                                  * the search budget (0.0268: rem = label_rem - step) */
static int g_seed_base = 11;
static const char *g_save_weights = (const char*)0;
static const char *g_load_weights = (const char*)0;
static int g_no_bound = 0;    /* policy/bound step budget; equals NSTEPS by default */
static int g_holdout_mask = 0; /* predicate-held-out bitmask: train/val exclude, test all-in */

#define P 6                      /* unary predicates */
#define NSLOT 2
#define MAXENT 12                /* largest split (train) */
#define WENT 6                   /* entities per world */
#define SEED_RULES 2
/* a lemma action commits TWO rules for one budget slot, so the rule-sequence
 * arrays must cover 2*MAXBUDGET (0260 gate found a stack overflow at 0257/0259
 * sizing: depth 4 with with lemma actions wrote past SEED_RULES+MAXBUDGET). */
#define MAXRULE (SEED_RULES + 2*MAXBUDGET)
#define POOL 24                  /* candidate rules per world */
#define NSTEPS 4
#define GOAL_COUNT 3
/* 0.0270 relational fixture: ground binary atoms, binding-sensitive goals.
 * The kernel stays propositional (small trusted checker); bindings live in the
 * ground rule instances. Facts are stored in the same WENT=6 bytes (48 bits >=
 * NA=36 atoms) so every FactSet signature in the lab is unchanged. */
#ifndef RELATOM
#define RELATOM 0
#endif
#if RELATOM && (CERT || BINDTOK || LIFTED || INTEGRAL || SYMGATE)
#error "RELATOM 0.0270 supports the S0/S1 core only: CERT/BINDTOK/LIFTED/INTEGRAL/SYMGATE ports are follow-ups"
#endif
#if RELATOM
#define EREL 3
#define PU 3
#define PB 3
#define NA (PU*EREL + PB*EREL*EREL)      /* 36 atoms: unary p*E+e, binary 9+r*9+e1*E+e2 */
#define BINMASK 0xFFFFFFFFE00ULL       /* bits 9..35 */
#if !HARD_GOALS
#error "RELATOM requires HARD_GOALS=1"
#endif
static uint64_t fs_load(const uint8_t f[WENT]){
  uint64_t m = 0; for (int i = 0; i < WENT; i++) m |= (uint64_t)f[i] << (8*i); return m;
}
static void fs_store(uint64_t m, uint8_t f[WENT]){
  for (int i = 0; i < WENT; i++) f[i] = (uint8_t)(m >> (8*i));
}
static int atom_pred(int id){ return id < PU*EREL ? id/EREL : (id-PU*EREL)/(EREL*EREL); }
static int atom_e1(int id){ return id < PU*EREL ? id%EREL : ((id-PU*EREL)%(EREL*EREL))/EREL; }
static int atom_e2(int id){ return id < PU*EREL ? id%EREL : (id-PU*EREL)%EREL; }
#define GOAL_ATOM(w,g) (PU*EREL + (w)->goal_pred[g]*(EREL*EREL) + (w)->goal_ent[g])
#define GOAL_KNOWN(w,g,fs) ((fs_load(fs) >> GOAL_ATOM(w,g)) & 1ULL)
#define ATOM_KNOWN(fs,id) ((fs_load(fs) >> (id)) & 1ULL)
#define GPRED PB
#define GENT (EREL*EREL)
#define HP PB
#else
#define GOAL_KNOWN(w,g,fs) ((fs)[(w)->goal_ent[g]] & (uint8_t)(1u << (w)->goal_pred[g]))
#define GPRED P
#define GENT WENT
#define HP P
#endif
#if RELATOM
#define NRULES_ALL 63            /* 18 unary chains + 27 compositions + 18 bridges */
#else
#define NRULES_ALL 90            /* 30 unary + 60 two-body */
#endif
#if RELATOM
#define CAND_BASE (8 + PB + NSLOT*PB)   /* 17: head + 2 body predicate one-hots (PB=3) */
#else
#define CAND_BASE (8 + P + NSLOT*P)     /* 26 */
#endif
#define STATE_BASE 8
#define GOAL_FEAT (GPRED + GENT)        /* per goal: predicate one-hot + binding one-hot */
#define CAND_GOAL_FEAT 4                /* head match, head known, body supported, would derive */
#define PATH_OFF (CAND_BASE + (RELOB ? GOAL_COUNT*CAND_GOAL_FEAT : 0) + (BINDTOK ? BIND_FEAT : 0))
#define ENT_OFF (PATH_OFF + (INTEGRAL ? 3 : 0))
#if RELATOM
#define CAND_DIM (ENT_OFF + (ENTFEAT ? 6*EREL : 0))   /* head e1/e2 + 2 body slots e1/e2 */
#else
#define CAND_DIM (PATH_OFF + (INTEGRAL ? 3 : 0))
#endif
#define STATE_DIM (STATE_BASE + (RELOB ? GOAL_COUNT*GOAL_FEAT : 0) + (REMFEAT ? 1 : 0))
#define MAXLIVE POOL

typedef struct { int head; int body[NSLOT]; int blen; } Rule;

typedef struct {
  int split;                     /* 0 train, 1 val, 2 test */
  int idx;
  int ents[WENT];
  uint8_t facts[WENT];           /* 6-bit predicate mask per entity slot */
  int theory[SEED_RULES];
  int cands[POOL];
  int ngoals;
  int goal_pred[GOAL_COUNT];
  int goal_ent[GOAL_COUNT];      /* entity slot, not entity id */
} World;

typedef struct {
  int world;
  int step;
  int nlive;
  int live[POOL];                /* rule ids */
  int best;
  double state[STATE_DIM];
  double cf[POOL][CAND_DIM];
  double util[POOL];
} Step;

static Rule all_rules[NRULES_ALL];
static double g_rule_prior[NRULES_ALL]; /* per-rule mean train utility (INTEGRAL prior feature) */

#if !RELATOM
static void build_all_rules(void){
  /* Order must match the reference ALL_RULES (m1_proof_state/world.py):
   * per head predicate, the unary rules first, then the binary rules. */
  int k = 0;
  for (int h = 0; h < P; h++){
    for (int b = 0; b < P; b++)
      if (b != h){ all_rules[k].head = h; all_rules[k].body[0] = b; all_rules[k].blen = 1; k++; }
    for (int b1 = 0; b1 < P; b1++)
      for (int b2 = b1+1; b2 < P; b2++)
        if (h != b1 && h != b2){
          all_rules[k].head = h; all_rules[k].body[0] = b1; all_rules[k].body[1] = b2;
          all_rules[k].blen = 2; k++;
        }
  }
  if (k != NRULES_ALL){ fprintf(stderr, "rule table %d\n", k); exit(2); }
}
#endif

/* ---------------- deterministic integer PRNG (xorshift64*) ---------------- */
static uint64_t rng_state;
static uint64_t nextrand(void){
  uint64_t x = rng_state;
  x ^= x >> 12; x ^= x << 25; x ^= x >> 27;
  rng_state = x;
  return x * 2685821657736338717ULL;
}
static int randbelow(int n){ return (int)(nextrand() % (uint64_t)n); }
static int chance_pct(int pct){ return randbelow(100) < pct; }
static uint64_t mix64(uint64_t x){ x ^= x>>12; x ^= x<<25; x ^= x>>27; return x*2685821657736338717ULL; }

/* ---------------- closure over 6-bit masks ---------------- */
#if !RELATOM
static void closure(const uint8_t facts[WENT], const int *rules, int nrules, uint8_t out[WENT]){
  for (int e = 0; e < WENT; e++) out[e] = facts[e];
  int changed = 1;
  while (changed){
    changed = 0;
    for (int k = 0; k < nrules; k++){
      const Rule *r = &all_rules[rules[k]];
      uint8_t bm = 0;
      for (int s = 0; s < r->blen; s++) bm |= (uint8_t)(1u << r->body[s]);
      uint8_t hm = (uint8_t)(1u << r->head);
      for (int e = 0; e < WENT; e++)
        if ((out[e] & bm) == bm && !(out[e] & hm)){ out[e] |= hm; changed = 1; }
    }
  }
}
#endif
static int popcount6(uint8_t x){ return __builtin_popcount((unsigned)x); }

static double rule_cost(const Rule *r){ return 0.5 + 0.75 * (double)r->blen; }

/* utility = 5*new_goals + 0.15*new_atoms - cost */
#if !RELATOM
static double utility(const World *w, const int *rules, int nrules, int cand){
  uint8_t before[WENT], after[WENT];
  closure(w->facts, rules, nrules, before);
  int extra[1] = {cand};
  int tmp[SEED_RULES + MAXBUDGET + 1];
  for (int i = 0; i < nrules; i++) tmp[i] = rules[i];
  tmp[nrules] = extra[0];
  closure(w->facts, tmp, nrules + 1, after);
  int goal_new = 0;
  for (int g = 0; g < w->ngoals; g++){
    int e = w->goal_ent[g], p = w->goal_pred[g];
    uint8_t bit = (uint8_t)(1u << p);
    if ((after[e] & bit) && !(before[e] & bit)) goal_new++;
  }
  int new_atoms = 0;
  for (int e = 0; e < WENT; e++) new_atoms += popcount6((uint8_t)(after[e] & ~before[e]));
  return 5.0*goal_new + 0.15*(double)new_atoms - rule_cost(&all_rules[cand]);
}
#endif

/* ---------------- features (M1 formulas) ---------------- */
#if !RELATOM
static int support(const Rule *r, const uint8_t known[WENT]){
  uint8_t bm = 0;
  for (int s = 0; s < r->blen; s++) bm |= (uint8_t)(1u << r->body[s]);
  int c = 0;
  for (int e = 0; e < WENT; e++) if ((known[e] & bm) == bm) c++;
  return c;
}
#endif

/* ---- path-integral retention state (INTEGRAL) -----------------------------
 * A_t(r) = sum_{tau<=t} gamma^{t-tau} support_tau(r), accumulated over the
 * committed-rule prefix. This is a kernel-consistent state function: train
 * (oracle prefix) and eval (policy prefix) recompute it identically from the
 * committed set, so there is no teacher/policy exposure confound. gamma=1 is
 * monotone accumulation (retention); gamma<1 is the decay ablation. */
typedef struct { double acc[NRULES_ALL]; double root[NRULES_ALL]; double wsum; int t; } PathState;
#if INTEGRAL
static void path_init(PathState *ps){ memset(ps, 0, sizeof *ps); }
static void path_update(PathState *ps, const World *w, const uint8_t known[WENT]){
  double g = PATH_GAMMA;
  ps->wsum = g*ps->wsum + 1.0;
  for (int i = 0; i < POOL; i++){
    int c = w->cands[i];
    double s = (double)support(&all_rules[c], known)/(double)WENT;
    if (ps->t == 0) ps->root[c] = s;
    ps->acc[c] = g*ps->acc[c] + s;
  }
  ps->t++;
}
static void path_features(const PathState *ps, int cand, const uint8_t known[WENT], double *out){
  double s_now = (double)support(&all_rules[cand], known)/(double)WENT;
  out[PATH_OFF+0] = ps->acc[cand]/ps->wsum;      /* time-averaged past support */
  out[PATH_OFF+1] = s_now - ps->root[cand];      /* support growth over the path */
}
/* Recompute the path integral by replaying the committed prefix (theory + the
 * rules committed so far). A pure function of (facts, committed set), so train
 * and eval agree by construction and beam branches need no inherited state. */
static void fill_path_features(const World *w, const int *rules, int nrules,
                               const int *live, int nlive, double (*cf)[CAND_DIM]){
  PathState ps; path_init(&ps);
  uint8_t kn[WENT];
  for (int m = SEED_RULES; m <= nrules; m++){
    closure(w->facts, rules, m, kn);
    path_update(&ps, w, kn);
  }
  for (int k = 0; k < nlive; k++) path_features(&ps, live[k], kn, cf[k]);
}
static void fill_prior_features(const int *live, int nlive, double (*cf)[CAND_DIM]){
  for (int k = 0; k < nlive; k++) cf[k][PATH_OFF+2] = g_rule_prior[live[k]];
}
#else
static void path_init(PathState *ps){ (void)ps; }
static void path_update(PathState *ps, const World *w, const uint8_t known[WENT]){ (void)ps;(void)w;(void)known; }
static void path_features(const PathState *ps, int cand, const uint8_t known[WENT], double *out){ (void)ps;(void)cand;(void)known;(void)out; }
static void fill_path_features(const World *w, const int *rules, int nrules,
                               const int *live, int nlive, double (*cf)[CAND_DIM]){ (void)w;(void)rules;(void)nrules;(void)live;(void)nlive;(void)cf; }
static void fill_prior_features(const int *live, int nlive, double (*cf)[CAND_DIM]){ (void)live;(void)nlive;(void)cf; }
#endif

/* predicate-held-out acceptance: train/val worlds must have NO held-out goal,
 * test worlds must have ALL goals held-out (pure transfer rung). */
static int holdout_ok(const World *w, int split){
  if (!g_holdout_mask) return 1;
  int any = 0, all = 1;
  for (int g = 0; g < w->ngoals; g++){
    if ((1u << w->goal_pred[g]) & (unsigned)g_holdout_mask) any = 1; else all = 0;
  }
  return (split == 2) ? all : !any;
}

#if !RELATOM
static void state_features(const World *w, const int *rules, int nrules,
                           const int *live, int nlive, double out[STATE_DIM], int rem){
  uint8_t known[WENT];
  closure(w->facts, rules, nrules, known);
  int known_n = 0;
  for (int e = 0; e < WENT; e++) known_n += popcount6(known[e]);
  double total = (double)(P * WENT);
  int goal_known = 0;
  for (int g = 0; g < w->ngoals; g++)
    if (known[w->goal_ent[g]] & (uint8_t)(1u << w->goal_pred[g])) goal_known++;
  double smin = 1e9, smax = -1e9, ssum = 0;
  for (int i = 0; i < nlive; i++){
    double s = (double)support(&all_rules[live[i]], known) / (double)WENT;
    if (s < smin) smin = s;
    if (s > smax) smax = s;
    ssum += s;
  }
  out[0] = (double)known_n / total;
  out[1] = (double)goal_known / (double)(w->ngoals > 0 ? w->ngoals : 1);
  out[2] = 1.0 - (double)known_n / total;
  out[3] = (double)nlive / (double)POOL;
  out[4] = nlive ? ssum / (double)nlive : 0.0;
  out[5] = nlive ? smax : 0.0;
  out[6] = nlive ? smin : 0.0;
  out[7] = (double)nrules / 8.0;
#if RELOB
  {
    int k = STATE_BASE;
    for (int i = 0; i < GOAL_COUNT*GOAL_FEAT; i++) out[i + STATE_BASE] = 0.0;
    for (int g = 0; g < w->ngoals; g++){
      for (int p = 0; p < P; p++) out[k++] = (w->goal_pred[g] == p) ? 1.0 : 0.0;
      for (int e = 0; e < WENT; e++) out[k++] = (w->goal_ent[g] == e) ? 1.0 : 0.0;
    }
  }
#endif
#if REMFEAT
  /* 0.0269: the DP value label depends on the remaining budget, which the
   * closure features do not encode (nrules miscounts it under contracts).
   * This slot makes the identifiability gap explicit without recurrence. */
  out[STATE_DIM-1] = (double)rem / (double)MAXBUDGET;
#endif
}
#endif

#if !RELATOM
static void cand_features(const World *w, const int *rules, int nrules,
                          int cand, double out[CAND_DIM]){
  uint8_t known[WENT];
  closure(w->facts, rules, nrules, known);
  const Rule *r = &all_rules[cand];
  int sup = support(r, known);
  int goal_count = 0;
  for (int g = 0; g < w->ngoals; g++) if (w->goal_pred[g] == r->head) goal_count++;
  int head_known = 0, body_known = 0;
  uint8_t bm = 0;
  for (int s = 0; s < r->blen; s++) bm |= (uint8_t)(1u << r->body[s]);
  for (int e = 0; e < WENT; e++){
    if (known[e] & (uint8_t)(1u << r->head)) head_known++;
    if ((known[e] & bm) == bm) body_known++;
  }
  double body_known_r = (double)body_known / (double)WENT;
  out[0] = (double)r->blen / 2.0;
  out[1] = rule_cost(r) / 2.0;
  out[2] = (double)sup / (double)WENT;
  out[3] = body_known_r;
  out[4] = (double)head_known / (double)WENT;
  out[5] = (double)goal_count / (double)(w->ngoals > 0 ? w->ngoals : 1);
  out[6] = (sup > 0) ? 1.0 : 0.0;
  out[7] = (goal_count > 0) ? 1.0 : 0.0;
  for (int p = 0; p < P; p++) out[8+p] = (r->head == p) ? 1.0 : 0.0;
  for (int s = 0; s < NSLOT; s++)
    for (int p = 0; p < P; p++)
      out[8+P + s*P + p] = (s < r->blen && r->body[s] == p) ? 1.0 : 0.0;
#if BINDTOK
  {
    /* the exact input of a binding+AND cell: which premise is satisfied at
     * which entity, and where the head atom already holds. */
    int k = CAND_BASE
#if RELOB
            + GOAL_COUNT*CAND_GOAL_FEAT
#endif
            ;
    /* BINDTOK=2 is the matched-width control: the same block with a per-rule
     * entity shift, so row sums and marginal statistics are preserved while the
     * correspondence to the actual premise/goal entities is destroyed. */
    int src_cand = cand;
    if (BINDTOK == 2){
      int ci = 0;
      for (int i2 = 0; i2 < POOL; i2++) if (w->cands[i2] == cand){ ci = i2; break; }
      src_cand = w->cands[(ci + 7) % POOL];   /* another candidate's binding rows */
    }
    const Rule *rsrc = (BINDTOK == 2) ? &all_rules[src_cand] : r;
    int shift = 0;
    for (int sl = 0; sl < NSLOT; sl++)
      for (int e0 = 0; e0 < WENT; e0++){
        int e = (e0 + shift) % WENT;
        if (sl >= rsrc->blen){ out[k++] = 0.0; continue; }
        out[k++] = (known[e] & (uint8_t)(1u << rsrc->body[sl])) ? 1.0 : 0.0;
      }
    for (int e0 = 0; e0 < WENT; e0++){
      int e = (e0 + shift) % WENT;
      out[k++] = (known[e] & (uint8_t)(1u << rsrc->head)) ? 1.0 : 0.0;
    }
  }
#endif
#if RELOB
  {
    int k = CAND_BASE;
    for (int g = 0; g < GOAL_COUNT; g++){
      if (g >= w->ngoals){ for (int z = 0; z < CAND_GOAL_FEAT; z++) out[k++] = 0.0; continue; }
      int e = w->goal_ent[g], gp = w->goal_pred[g];
      uint8_t hm = (uint8_t)(1u << r->head);
      int body_at = (int)((known[e] & bm) == bm);
      int head_at = (known[e] & hm) ? 1 : 0;
      out[k++] = (r->head == gp) ? 1.0 : 0.0;
      out[k++] = (double)head_at;
      out[k++] = (double)body_at;
      out[k++] = (r->head == gp && body_at) ? 1.0 : 0.0;
    }
  }
#endif
#if INTEGRAL
  /* prior column PATH_OFF+2 is filled by rule_prior_from_train (stored data)
   * or fill_prior_features (eval), AFTER the prior is computed from train. */
#endif
}
#endif
#if RELATOM
#include "rel_stage.inc"
#endif

/* ---------------- world + rollout generation ---------------- */
static void sample_ents(int split, int ents[WENT]){
  int lo = (split == 0) ? 0 : (split == 1) ? 12 : 18;
  int hi = (split == 0) ? 12 : (split == 1) ? 18 : 26;
  int pool[MAXENT], n = hi - lo;
  for (int i = 0; i < n; i++) pool[i] = lo + i;
  for (int i = 0; i < WENT; i++){
    int j = i + randbelow(n - i);
    int t = pool[i]; pool[i] = pool[j]; pool[j] = t;
    ents[i] = pool[i];
  }
}
static void shuffle_ints(int *v, int n){
  for (int i = n-1; i > 0; i--){
    int j = randbelow(i+1);
    int t = v[i]; v[i] = v[j]; v[j] = t;
  }
}

/* returns 0 if the world had to be retried */
static int g_goal_fallback = 0;   /* 1 = exact-depth pool was empty, shallower used */
static int g_dp_check = 0;     /* 1 = DP vs brute-force label audit */
static int g_goal_scan = 0;       /* 1 = scan structures until the exact depth is genuine */
static int g_goal_depth_used = 0;

static int make_world(World *w, int split, int idx){
  w->split = split; w->idx = idx;
  g_goal_fallback = 0;
  /* R250-2: world structure comes from a stream seeded ONLY by (split, idx), so
   * facts/seed-rules/candidates are identical at every goal depth. */
  rng_state = mix64((uint64_t)(split*7919u + (uint64_t)idx*104729u) ^ 0x5DEECE66DULL) | 1ULL;
#if RELATOM
  for (int e = 0; e < WENT; e++) w->ents[e] = e;
  {
    uint64_t fm = 0;
    for (int p = 0; p < PU; p++)
      for (int e = 0; e < EREL; e++) if (chance_pct(30)) fm |= 1ULL << (p*EREL+e);
    for (int p = 0; p < PU; p++) fm |= 1ULL << (p*EREL + randbelow(EREL));
    for (int r = 0; r < PB; r++)
      for (int e1 = 0; e1 < EREL; e1++)
        for (int e2 = 0; e2 < EREL; e2++)
          if (chance_pct(16)) fm |= 1ULL << (PU*EREL + r*EREL*EREL + e1*EREL+e2);
    /* guarantee at least one r0 and one r1 atom so joins are possible */
    fm |= 1ULL << (PU*EREL + 0*EREL*EREL + randbelow(EREL)*EREL + randbelow(EREL));
    fm |= 1ULL << (PU*EREL + 1*EREL*EREL + randbelow(EREL)*EREL + randbelow(EREL));
    fs_store(fm, w->facts);
  }
#else
  sample_ents(split, w->ents);
  for (int e = 0; e < WENT; e++){
    uint8_t m = 0;
    for (int p = 0; p < P; p++) if (chance_pct(26)) m |= (uint8_t)(1u << p);
    w->facts[e] = m;
  }
  for (int p = 0; p < P; p++)
    w->facts[randbelow(WENT)] |= (uint8_t)(1u << p);
#endif

  int order[NRULES_ALL];
  for (int i = 0; i < NRULES_ALL; i++) order[i] = i;
  shuffle_ints(order, NRULES_ALL);
  for (int i = 0; i < SEED_RULES; i++) w->theory[i] = order[i];
  for (int i = 0; i < POOL; i++) w->cands[i] = order[SEED_RULES + i];

  uint8_t base[WENT];
  closure(w->facts, w->theory, SEED_RULES, base);

#if RELATOM
  /* relational depth pool: binary atoms derivable with ALL candidates but not
   * with any subset of size <= depth-1 (same construction as HARD_GOALS, over
   * the atom mask). Per-goal witness = membership in k1; reachability audited
   * independently by tools/check_parity_rel.py. */
  int gp[POOL*WENT], ge[POOL*WENT], ng = 0;
  {
    int depth = (g_goaldepth > 0) ? g_goaldepth : 2;
    int all[SEED_RULES+POOL];
    for (int t = 0; t < SEED_RULES; t++) all[t] = w->theory[t];
    for (int i = 0; i < POOL; i++) all[SEED_RULES+i] = w->cands[i];
    uint8_t k1[WENT];
    closure(w->facts, all, SEED_RULES+POOL, k1);
    uint64_t pool = (fs_load(k1) & ~rel_union_upto(w, base, depth-1)) & BINMASK;
    for (int id = PU*EREL; id < NA; id++)
      if ((pool >> id) & 1ULL){
        gp[ng] = (id-PU*EREL)/(EREL*EREL);
        ge[ng] = (id-PU*EREL)%(EREL*EREL);
        ng++;
      }
  }
#elif HARD_GOALS
  /* depth-parameterised goal pool: goals = closure(seed + all) \ union over
   * candidate subsets of size <= k-1 of closure(seed + subset), i.e. goals that
   * need at least k candidate steps. k=2 is the 0.0245 hard fixture. */
  int gp[POOL*WENT], ge[POOL*WENT], ng = 0;
  uint8_t k1[WENT], k0[WENT];
  {
    int depth = (g_goaldepth > 0) ? g_goaldepth : 2;
    int all[SEED_RULES+POOL];
    for (int t = 0; t < SEED_RULES; t++) all[t] = w->theory[t];
    for (int i = 0; i < POOL; i++) all[SEED_RULES+i] = w->cands[i];
    closure(w->facts, all, SEED_RULES+POOL, k1);
    for (int e = 0; e < WENT; e++) k0[e] = base[e];
    /* union over subsets of size <= depth-1 */
    int maxk = depth - 1;
    int comb[4];
    for (int k = 1; k <= maxk && k <= 3; k++){
      for (int i = 0; i < k; i++) comb[i] = i;
      while (1){
        uint8_t tmp[WENT];
        int rules2[SEED_RULES+3];
        for (int t = 0; t < SEED_RULES; t++) rules2[t] = w->theory[t];
        for (int q = 0; q < k; q++) rules2[SEED_RULES+q] = w->cands[comb[q]];
        closure(w->facts, rules2, SEED_RULES+k, tmp);
        for (int e = 0; e < WENT; e++) k0[e] |= tmp[e];
        int pos = k-1;
        while (pos >= 0 && comb[pos] == POOL - k + pos) pos--;
        if (pos < 0) break;
        comb[pos]++;
        for (int q = pos+1; q < k; q++) comb[q] = comb[q-1]+1;
      }
    }
  }
  for (int p = 0; p < P; p++)
    for (int e = 0; e < WENT; e++){
      uint8_t bit = (uint8_t)(1u << p);
      if ((k1[e] & bit) && !(k0[e] & bit)){ gp[ng] = p; ge[ng] = e; ng++; }
    }
#else
  /* F1 (0.0245): the reference adds (head,e) only when the candidate body
   * holds AT THAT ENTITY e (m1_proof_state/world.py:97-101). The 0.0244 port
   * checked support anywhere in the world, which produced goals with no
   * per-entity witness (and goals unreachable even with every candidate). */
  int gp[POOL*WENT], ge[POOL*WENT], ng = 0;
  for (int i = 0; i < POOL; i++){
    const Rule *r = &all_rules[w->cands[i]];
    uint8_t hm = (uint8_t)(1u << r->head);
    uint8_t bm = 0;
    for (int k = 0; k < r->blen; k++) bm |= (uint8_t)(1u << r->body[k]);
    for (int e = 0; e < WENT; e++)
      if ((base[e] & bm) == bm && !(base[e] & hm)){ gp[ng] = r->head; ge[ng] = e; ng++; }
  }
#endif
  if (ng == 0 && g_goal_scan) return 0;   /* scan mode: try the next structure */
  if (ng == 0){
#if RELATOM
    int want = (g_goaldepth > 0) ? g_goaldepth : 2;
    int all2[SEED_RULES+POOL];
    for (int t = 0; t < SEED_RULES; t++) all2[t] = w->theory[t];
    for (int i2 = 0; i2 < POOL; i2++) all2[SEED_RULES+i2] = w->cands[i2];
    uint8_t kk[WENT];
    closure(w->facts, all2, SEED_RULES+POOL, kk);
    for (int d2 = want - 1; d2 >= 1 && ng == 0; d2--){
      uint64_t pool = (fs_load(kk) & ~rel_union_upto(w, base, d2-1)) & BINMASK;
      for (int id = PU*EREL; id < NA; id++)
        if ((pool >> id) & 1ULL){
          gp[ng] = (id-PU*EREL)/(EREL*EREL);
          ge[ng] = (id-PU*EREL)%(EREL*EREL);
          ng++;
        }
      if (ng > 0){ g_goal_fallback = 1; g_goal_depth_used = d2; }
    }
#else
    /* fallback: shallowest non-empty pool <= requested depth (recorded) */
    int want = (g_goaldepth > 0) ? g_goaldepth : 2;
    for (int d2 = want - 1; d2 >= 1 && ng == 0; d2--){
      uint8_t kk[WENT], k0b[WENT];
      int all2[SEED_RULES+POOL];
      for (int t = 0; t < SEED_RULES; t++) all2[t] = w->theory[t];
      for (int i2 = 0; i2 < POOL; i2++) all2[SEED_RULES+i2] = w->cands[i2];
      closure(w->facts, all2, SEED_RULES+POOL, kk);
      for (int e = 0; e < WENT; e++) k0b[e] = base[e];
      int comb2[4];
      for (int k2 = 1; k2 <= d2-1 && k2 <= 3; k2++){
        for (int i2 = 0; i2 < k2; i2++) comb2[i2] = i2;
        while (1){
          uint8_t tmp2[WENT]; int rr[SEED_RULES+3]; int mm = 0;
          for (int t = 0; t < SEED_RULES; t++) rr[mm++] = w->theory[t];
          for (int q = 0; q < k2; q++) rr[mm++] = w->cands[comb2[q]];
          closure(w->facts, rr, mm, tmp2);
          for (int e = 0; e < WENT; e++) k0b[e] |= tmp2[e];
          int pos2 = k2-1;
          while (pos2 >= 0 && comb2[pos2] == POOL - k2 + pos2) pos2--;
          if (pos2 < 0) break;
          comb2[pos2]++;
          for (int q = pos2+1; q < k2; q++) comb2[q] = comb2[q-1]+1;
        }
      }
      for (int p2 = 0; p2 < P; p2++)
        for (int e = 0; e < WENT; e++){
          uint8_t bit = (uint8_t)(1u << p2);
          if ((kk[e] & bit) && !(k0b[e] & bit)){ gp[ng] = p2; ge[ng] = e; ng++; }
        }
      if (ng > 0){ g_goal_fallback = 1; g_goal_depth_used = d2; }
    }
#endif
  }
  if (ng == 0) return 0;   /* no pool even at depth 1: reject the world (rare) */
  /* shuffle goal list with a LOCAL stream seeded by (split, idx, depth) */
  {
    int want = (g_goaldepth > 0) ? g_goaldepth : 2;
    uint64_t gs = mix64((uint64_t)(split*131 + idx*2654435761u
                        + (uint64_t)want*2654435761u) ^ 0xA5A5A5A55A5A5A5AULL);
    for (int i = ng-1; i > 0; i--){
      gs = mix64(gs);
      int j = (int)(gs % (uint64_t)(i+1));
      int t = gp[i]; gp[i] = gp[j]; gp[j] = t;
      t = ge[i]; ge[i] = ge[j]; ge[j] = t;
    }
  }
  w->ngoals = (ng < GOAL_COUNT) ? ng : GOAL_COUNT;
  for (int g = 0; g < w->ngoals; g++){ w->goal_pred[g] = gp[g]; w->goal_ent[g] = ge[g]; }
  return 1;
}

/* Roll out up to NSTEPS proof steps, oracles choosing the best candidate.
 * Fills steps[] and returns the number of steps. `used` marks applied rules. */
static int rollout(const World *w, Step *steps){
  int rules[SEED_RULES + MAXBUDGET];
  int nrules = SEED_RULES;
  for (int i = 0; i < SEED_RULES; i++) rules[i] = w->theory[i];
  int nsteps = 0;
  for (int s = 0; s < NSTEPS; s++){
    int live[POOL], nlive = 0;
    for (int i = 0; i < POOL; i++){
      int c = w->cands[i], used = 0;
      for (int k = 0; k < nrules; k++) if (rules[k] == c) used = 1;
      if (!used) live[nlive++] = c;
    }
    if (!nlive) break;
    Step *st = &steps[nsteps];
    st->world = w->idx; st->step = s; st->nlive = nlive;
    for (int i = 0; i < nlive; i++) st->live[i] = live[i];
    state_features(w, rules, nrules, live, nlive, st->state,
                   g_label_rem_max - s > 0 ? g_label_rem_max - s : 0);
    int best = 0;
    for (int i = 0; i < nlive; i++){
      cand_features(w, rules, nrules, live[i], st->cf[i]);
      st->util[i] = utility(w, rules, nrules, live[i]);
      if (st->util[i] > st->util[best]) best = i;
    }
    st->best = best;
    nsteps++;
    if (st->util[best] <= 0) break;
    rules[nrules++] = live[best];
  }
  return nsteps;
}

/* ---------------- dump mode (parity evidence) ---------------- */
static void dump_world(const World *w, const Step *steps, int nsteps, FILE *f){
  fprintf(f, "W %d %d %d %d %d\n", w->split, w->idx, w->ngoals,
          g_goal_fallback, g_goal_depth_used ? g_goal_depth_used : (g_goaldepth > 0 ? g_goaldepth : 2));
  fprintf(f, "E");
  for (int e = 0; e < WENT; e++) fprintf(f, " %d", w->ents[e]);
  fprintf(f, "\n");
  fprintf(f, "F");
  for (int e = 0; e < WENT; e++) fprintf(f, " %d", (int)w->facts[e]);
  fprintf(f, "\n");
  fprintf(f, "T");
  for (int i = 0; i < SEED_RULES; i++) fprintf(f, " %d", w->theory[i]);
  fprintf(f, "\n");
  fprintf(f, "C");
  for (int i = 0; i < POOL; i++) fprintf(f, " %d", w->cands[i]);
  fprintf(f, "\n");
  fprintf(f, "G");
  for (int g = 0; g < w->ngoals; g++) fprintf(f, " %d:%d", w->goal_pred[g], w->goal_ent[g]);
  fprintf(f, "\n");
  int nrules = SEED_RULES;
  int rules[SEED_RULES + MAXBUDGET];
  for (int i = 0; i < SEED_RULES; i++) rules[i] = w->theory[i];
  for (int s = 0; s < nsteps; s++){
    const Step *st = &steps[s];
    fprintf(f, "STEP %d %d %d", s, st->nlive, st->best);
    for (int i = 0; i < st->nlive; i++) fprintf(f, " %d", st->live[i]);
    fprintf(f, "\n");
    fprintf(f, "STATE");
    for (int i = 0; i < STATE_DIM; i++) fprintf(f, " %.6f", st->state[i]);
    fprintf(f, "\n");
    for (int i = 0; i < st->nlive; i++){
      fprintf(f, "CF %d", st->live[i]);
      for (int d = 0; d < CAND_DIM; d++) fprintf(f, " %.6f", st->cf[i][d]);
      fprintf(f, " U %.6f\n", st->util[i]);
    }
    if (st->util[st->best] <= 0) break;
    rules[nrules++] = st->live[st->best];
  }
}

/* ---------------- main (stage 1: dump/self-check) ---------------- */
static Step g_steps[NSTEPS];
static World g_world;

static int build_split(int split, int nworlds, uint64_t seed, FILE *dump, long *out_steps){
  rng_state = seed;
  long nsteps_total = 0, n_genuine = 0, n_fallback = 0, scans = 0;
  int src = 0;
  for (int i = 0; i < nworlds; i++){
    int ok = 0;
    if (g_goal_scan){
      /* genuine depth: advance the structure index until the exact-depth pool is
       * non-empty (each structure is keyed by its own (split, index) stream) */
      int guard = 0;
      while (!ok && guard++ < 20000){ ok = make_world(&g_world, split, src++) && holdout_ok(&g_world, split); scans++; }
      if (!ok){ fprintf(stderr, "SCAN-FAIL split=%d world=%d general=%d\n", split, i, g_goaldepth); exit(3); }
    } else {
      while (!ok) ok = make_world(&g_world, split, i);
    }
    if (g_goal_fallback) n_fallback++; else n_genuine++;
    int ns = rollout(&g_world, g_steps);
    nsteps_total += ns;
    if (dump) dump_world(&g_world, g_steps, ns, dump);
  }
  *out_steps = nsteps_total;
  fprintf(stderr, "CENSUS split=%d depth=%d worlds=%d genuine=%ld fallback=%ld scans=%ld mode=%s\n",
          split, g_goaldepth > 0 ? g_goaldepth : 2, nworlds, n_genuine, n_fallback, scans,
          g_goal_scan ? "scan" : "fallback");
  return 0;
}


#include "model.inc"
#include "train.inc"

/* ---------------- main ---------------- */
static void alloc_globals(void){
  g_p = (Params*)calloc(1, sizeof(Params));
  g_g = (Params*)calloc(1, sizeof(Params));
  g_m = (Params*)calloc(1, sizeof(Params));
  g_v = (Params*)calloc(1, sizeof(Params));
  g_c = (Cache*)calloc(1, sizeof(Cache));
  if (!g_p || !g_g || !g_m || !g_v || !g_c){ fprintf(stderr, "alloc\n"); exit(2); }
}

int main(int argc, char **argv){
  build_all_rules();
  for (int i = 1; i < argc; i++)
    if (!strcmp(argv[i], "--dump-rules") && i+1 < argc){
      FILE *f = fopen(argv[i+1], "w");
      if (!f){ fprintf(stderr, "cannot open %s\n", argv[i+1]); exit(2); }
#if RELATOM
      fprintf(f, "RELATOM 1 NA %d E %d PU %d PB %d NRULES %d POOL %d SEED_RULES %d GOAL_COUNT %d\n",
              NA, EREL, PU, PB, NRULES_ALL, POOL, SEED_RULES, GOAL_COUNT);
#else
      fprintf(f, "RELATOM 0 NRULES %d POOL %d SEED_RULES %d GOAL_COUNT %d WENT %d P %d\n",
              NRULES_ALL, POOL, SEED_RULES, GOAL_COUNT, WENT, P);
#endif
      for (int k = 0; k < NRULES_ALL; k++){
        const Rule *r = &all_rules[k];
        fprintf(f, "R %d %d %d %d %d\n", k, r->head,
                r->blen > 0 ? r->body[0] : -1, r->blen > 1 ? r->body[1] : -1, r->blen);
      }
      fclose(f);
      printf("DUMP-RULES %d rules -> %s\n", NRULES_ALL, argv[i+1]);
      return 0;
    }
  const char *mode = "train";
  const char *dump = NULL;
  uint64_t seed = 11;
  int nworlds = 4, seeds = 3, epochs = EPOCHS;
  for (int i = 1; i < argc; i++){
    if (!strcmp(argv[i], "--dump") && i+1 < argc) dump = argv[++i];
    else if (!strcmp(argv[i], "--dump-test") && i+1 < argc){ mode = "dumptest"; dump = argv[++i]; }
    else if (!strcmp(argv[i], "--seed") && i+1 < argc) seed = strtoull(argv[++i], 0, 10);
    else if (!strcmp(argv[i], "--worlds") && i+1 < argc) nworlds = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--seeds") && i+1 < argc) seeds = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--epochs") && i+1 < argc) epochs = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--train-n") && i+1 < argc) g_nw[0] = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--val-n") && i+1 < argc) g_nw[1] = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--test-n") && i+1 < argc) g_nw[2] = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--beam") && i+1 < argc) g_beam = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--collect") && i+1 < argc) g_collect = !strcmp(argv[++i], "full");
    else if (!strcmp(argv[i], "--sample") && i+1 < argc){
      const char *sm = argv[++i];
      g_sample = !strcmp(sm, "root") ? 1 : (!strcmp(sm, "sub") ? 2 : 0);
    }
    else if (!strcmp(argv[i], "--dataset-stats")) mode = "dsstats";
    else if (!strcmp(argv[i], "--goaldepth") && i+1 < argc) g_goaldepth = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--eval-budget") && i+1 < argc) g_eval_budget = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--seed-base") && i+1 < argc) g_seed_base = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--save-weights") && i+1 < argc) g_save_weights = argv[++i];
    else if (!strcmp(argv[i], "--load-weights") && i+1 < argc) g_load_weights = argv[++i];
    else if (!strcmp(argv[i], "--no-bound")) g_no_bound = 1;
    else if (!strcmp(argv[i], "--balance-reward")) g_balance = 1;
    else if (!strcmp(argv[i], "--regret")) g_regret = 1;
    else if (!strcmp(argv[i], "--dfs")) g_dfs = 1;
    else if (!strcmp(argv[i], "--onecommit-audit")) g_onecommit_audit = 1;
    else if (!strcmp(argv[i], "--branch") && i+1 < argc) g_branch = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--subsume") && i+1 < argc) g_subsume = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--prop") && i+1 < argc) g_prop = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--goal-directed") && i+1 < argc) g_focus = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--lemmas") && i+1 < argc) g_lemmas = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--lemma-cost") && i+1 < argc) g_lemma_cost = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--cert") && i+1 < argc) g_cert_on = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--cert-selftest")) g_cert_selftest = 1;
    else if (!strcmp(argv[i], "--pairmode") && i+1 < argc) g_pairmode = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--pair-keep") && i+1 < argc) g_pair_keep = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--valmode") && i+1 < argc) g_valmode = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--label-rem") && i+1 < argc) g_label_rem_max = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--dp-bruteforce-check")) g_dp_check = 1;
    else if (!strcmp(argv[i], "--goal-scan")) g_goal_scan = 1;
    else if (!strcmp(argv[i], "--serve") && i+1 < argc){ mode = "serve"; g_load_weights = argv[++i]; }
    else if (!strcmp(argv[i], "--holdout") && i+1 < argc){
      const char *h = argv[++i]; g_holdout_mask = 0;
      while (*h){ if (*h >= '0' && *h < '0'+P) g_holdout_mask |= 1 << (*h - '0'); h++; }
    }
    else if (!strcmp(argv[i], "--emit-worlds")) g_emit_worlds = 1;
    else if (!strcmp(argv[i], "--export-maru") && i+1 < argc){ mode = "export"; dump = argv[++i]; }
    else if (!strcmp(argv[i], "--cases") && i+1 < argc) nworlds = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--dump-forward") && i+1 < argc){ mode = "dumph"; dump = argv[++i]; }
    else if (!strcmp(argv[i], "--case") && i+1 < argc) nworlds = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--gradcheck")) mode = "gradcheck";
    else if (!strcmp(argv[i], "--dump-dp") && i+1 < argc){ mode = "dumpdp"; dump = argv[++i]; }
    else if (!strcmp(argv[i], "--path-check")) mode = "pathcheck";
    else if (!strcmp(argv[i], "--train")) mode = "train";
  }
  if (g_eval_budget > MAXBUDGET){
    fprintf(stderr, "EVAL-BUDGET-FAIL eval budget %d exceeds MAXBUDGET %d (rule-sequence capacity); rebuild with -DMAXBUDGET=%d\n",
            g_eval_budget, MAXBUDGET, g_eval_budget);
    return 2;
  }
  if (mode && !strcmp(mode, "dumph")){
  alloc_globals();
    dump_forward(dump, (int)seed, epochs, nworlds);
    return 0;
  }
  if (mode && !strcmp(mode, "dumptest")){
    FILE *f = fopen(dump, "w");
    if (!f){ fprintf(stderr, "cannot open %s\n", dump); return 2; }
    long st = 0;
    build_split(2, g_nw[2], seed + 2, f, &st);
    fclose(f);
    printf("DUMP-TEST worlds=%d steps=%ld seed=%llu path=%s\n", g_nw[2], st,
           (unsigned long long)(seed+2), dump);
    return 0;
  }
  if (mode && !strcmp(mode, "export")){
    alloc_globals();
    export_maru(dump, (int)seed, epochs, nworlds);
    return 0;
  }
  if (dump && (!mode || strcmp(mode, "export")) && strcmp(mode, "dumpdp")){
    FILE *f = fopen(dump, "w");
    if (!f){ fprintf(stderr, "cannot open %s\n", dump); return 2; }
    long total = 0, st = 0;
    build_split(0, nworlds, seed, f, &st); total += st;
    build_split(1, nworlds, seed + 1, f, &st); total += st;
    build_split(2, nworlds, seed + 2, f, &st); total += st;
    fclose(f);
    printf("WORLDS-%d STEPS-%ld SEED-%llu DUMP-%s\n", 3*nworlds, total,
           (unsigned long long)seed, dump);
    return 0;
  }
  if (g_holdout_mask && !g_goal_scan){
    fprintf(stderr, "HOLDOUT-REQUIRES-GOAL-SCAN\n"); return 2;
  }
  alloc_globals();
  if (!strcmp(mode, "serve")){
    build_dataset();
    /* serve always uses the test split; load the trained weights */
    FILE *lf = fopen(g_load_weights, "rb");
    if (!lf){ fprintf(stderr, "cannot open weights %s\n", g_load_weights); return 2; }
    WHeader h;
    if (fread(&h, sizeof h, 1, lf) != 1){ fprintf(stderr, "short header\n"); return 2; }
    if (fread(g_p, sizeof(Params), 1, lf) != 1){ fprintf(stderr, "short weights\n"); return 2; }
    fclose(lf);
    serve();
    return 0;
  }
  if (!strcmp(mode, "dsstats")){
    build_dataset();
    dataset_stats();
    return 0;
  }
  if (!strcmp(mode, "dumpdp")){
    build_dataset();
    rule_prior_from_train();
    FILE *f = fopen(dump, "w");
    if (!f){ fprintf(stderr, "cannot open %s\n", dump); exit(2); }
    for (int i = 0; i < g_nw[0]; i++){
      const WSteps *ws = &g_data[0][i];
      const World *w = &ws->w;
      fprintf(f, "W %d %d %d\n", w->split, w->idx, w->ngoals);
      fprintf(f, "F"); for (int e = 0; e < WENT; e++) fprintf(f, " %d", (int)w->facts[e]); fprintf(f, "\n");
      fprintf(f, "T"); for (int t = 0; t < SEED_RULES; t++) fprintf(f, " %d", w->theory[t]); fprintf(f, "\n");
      fprintf(f, "C"); for (int c = 0; c < POOL; c++) fprintf(f, " %d", w->cands[c]); fprintf(f, "\n");
      fprintf(f, "G"); for (int g = 0; g < w->ngoals; g++) fprintf(f, " %d:%d", w->goal_pred[g], w->goal_ent[g]); fprintf(f, "\n");
      for (int st = 0; st < ws->nsteps; st++){
        const RStep *rs = &ws->st[st];
        fprintf(f, "S %d %d %d", st, rs->nlive, rs->best);
        for (int k = 0; k < rs->nlive; k++) fprintf(f, " %d", rs->live[k]);
        fprintf(f, "\n");
        fprintf(f, "L"); for (int k = 0; k < rs->nlive; k++) fprintf(f, " %.6f", rs->util[k]); fprintf(f, "\n");
      }
    }
    fclose(f);
    printf("DUMP-DP worlds=%d -> %s\n", (int)g_nw[0], dump);
    return 0;
  }
  if (!strcmp(mode, "gradcheck")){
    double rel = gradcheck();
    printf(rel < 1e-5 ? "GRADCHECK-PASS\n" : "GRADCHECK-FAIL\n");
    return rel < 1e-5 ? 0 : 1;
  }
  if (!strcmp(mode, "pathcheck")) return path_check();
  run_variant(seeds, epochs, 1);
  return 0;
}
