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
#include <math.h>

#define P 6                      /* unary predicates */
#define NSLOT 2
#define MAXENT 12                /* largest split (train) */
#define WENT 6                   /* entities per world */
#define SEED_RULES 2
#define POOL 24                  /* candidate rules per world */
#define NSTEPS 4
#define GOAL_COUNT 3
#define NRULES_ALL 90            /* 30 unary + 60 binary */
#define CAND_DIM (8 + P + NSLOT*P)      /* 26 */
#define STATE_DIM 8
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
static int popcount6(uint8_t x){ return __builtin_popcount((unsigned)x); }

static double rule_cost(const Rule *r){ return 0.5 + 0.75 * (double)r->blen; }

/* utility = 5*new_goals + 0.15*new_atoms - cost */
static double utility(const World *w, const int *rules, int nrules, int cand){
  uint8_t before[WENT], after[WENT];
  closure(w->facts, rules, nrules, before);
  int extra[1] = {cand};
  int tmp[SEED_RULES + NSTEPS + 1];
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

/* ---------------- features (M1 formulas) ---------------- */
static int support(const Rule *r, const uint8_t known[WENT]){
  uint8_t bm = 0;
  for (int s = 0; s < r->blen; s++) bm |= (uint8_t)(1u << r->body[s]);
  int c = 0;
  for (int e = 0; e < WENT; e++) if ((known[e] & bm) == bm) c++;
  return c;
}

static void state_features(const World *w, const int *rules, int nrules,
                           const int *live, int nlive, double out[STATE_DIM]){
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
}

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
}

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
static int make_world(World *w, int split, int idx){
  w->split = split; w->idx = idx;
  sample_ents(split, w->ents);
  for (int e = 0; e < WENT; e++){
    uint8_t m = 0;
    for (int p = 0; p < P; p++) if (chance_pct(26)) m |= (uint8_t)(1u << p);
    w->facts[e] = m;
  }
  for (int p = 0; p < P; p++)
    w->facts[randbelow(WENT)] |= (uint8_t)(1u << p);

  int order[NRULES_ALL];
  for (int i = 0; i < NRULES_ALL; i++) order[i] = i;
  shuffle_ints(order, NRULES_ALL);
  for (int i = 0; i < SEED_RULES; i++) w->theory[i] = order[i];
  for (int i = 0; i < POOL; i++) w->cands[i] = order[SEED_RULES + i];

  uint8_t base[WENT];
  closure(w->facts, w->theory, SEED_RULES, base);

  int gp[POOL*WENT], ge[POOL*WENT], ng = 0;
  for (int i = 0; i < POOL; i++){
    const Rule *r = &all_rules[w->cands[i]];
    uint8_t hm = (uint8_t)(1u << r->head);
    int ok = (support(r, base) > 0);
    if (!ok) continue;
    for (int e = 0; e < WENT; e++)
      if (!(base[e] & hm)){ gp[ng] = r->head; ge[ng] = e; ng++; }
  }
  if (ng == 0) return 0;
  /* shuffle goal list */
  for (int i = ng-1; i > 0; i--){
    int j = randbelow(i+1);
    int t = gp[i]; gp[i] = gp[j]; gp[j] = t;
    t = ge[i]; ge[i] = ge[j]; ge[j] = t;
  }
  w->ngoals = (ng < GOAL_COUNT) ? ng : GOAL_COUNT;
  for (int g = 0; g < w->ngoals; g++){ w->goal_pred[g] = gp[g]; w->goal_ent[g] = ge[g]; }
  return 1;
}

/* Roll out up to NSTEPS proof steps, oracles choosing the best candidate.
 * Fills steps[] and returns the number of steps. `used` marks applied rules. */
static int rollout(const World *w, Step *steps){
  int rules[SEED_RULES + NSTEPS];
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
    state_features(w, rules, nrules, live, nlive, st->state);
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
  fprintf(f, "W %d %d %d\n", w->split, w->idx, w->ngoals);
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
  int rules[SEED_RULES + NSTEPS];
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
  long nsteps_total = 0;
  for (int i = 0; i < nworlds; i++){
    int ok = 0;
    while (!ok) ok = make_world(&g_world, split, i);
    int ns = rollout(&g_world, g_steps);
    nsteps_total += ns;
    if (dump) dump_world(&g_world, g_steps, ns, dump);
  }
  *out_steps = nsteps_total;
  return 0;
}

