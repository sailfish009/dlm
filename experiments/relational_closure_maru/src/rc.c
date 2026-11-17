/* Relational closure lab — native C, no Python.
 *
 * Faithful test of the "closure primitive" hypothesis (docs/diagnosis-0253.md):
 * a closure-COMPUTATION task on a RELATIONAL fixture, where the unary lab's
 * per-entity Boolean closure cannot discriminate.
 *
 * Domain: NENT entities, NPRED binary predicates. Ground atom = (p, a, b), a!=b.
 * Rules: 2-variable composition  h(X,Z) :- b1(X,Y), b2(Y,Z)  (shared join var Y).
 * Closure: forward join to least fixed point (monotone, confluent).
 * Depth:   min number of rule applications to derive an atom (BFS layering).
 *
 * Stage 1 (this file): kernel + world generation + genuine-depth census + dump.
 * Stage 2 (next): closure-computation model (facts+rules -> fixpoint), depth
 * ladder, beta->inf kernel-match soundness gate, matched baselines.
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#ifndef NENT
#define NENT 6
#endif
#ifndef NPRED
#define NPRED 3
#endif
#define NATOMS (NPRED*NENT*NENT)        /* slots incl. unused a==b diagonal */
#define NRULES (NPRED*NPRED*NPRED)      /* composition rules h:-b1,b2 */
#define MAXWORDS ((NATOMS+63)/64)

typedef struct { int head, b1, b2; } Rule;   /* h(X,Z):-b1(X,Y),b2(Y,Z) */

static Rule all_rules[NRULES];
static int g_goaldepth = 2;
static int g_goal_scan = 0;

static void build_rules(void){
  int k = 0;
  for (int h = 0; h < NPRED; h++)
    for (int a = 0; a < NPRED; a++)
      for (int b = 0; b < NPRED; b++){
        all_rules[k].head = h; all_rules[k].b1 = a; all_rules[k].b2 = b; k++;
      }
  if (k != NRULES){ fprintf(stderr, "rule table %d\n", k); exit(2); }
}

static int atom_idx(int p, int a, int b){ return (p*NENT + a)*NENT + b; }
static int valid_atom(int p, int a, int b){ (void)p; return a != b; }

/* ---- bitset helpers over NATOMS bits ---- */
static void bs_zero(uint64_t *x){ memset(x, 0, MAXWORDS*sizeof(uint64_t)); }
static void bs_copy(uint64_t *d, const uint64_t *s){ memcpy(d, s, MAXWORDS*sizeof(uint64_t)); }
static int bs_test(const uint64_t *x, int i){ return (x[i>>6] >> (i&63)) & 1ULL; }
static void bs_set(uint64_t *x, int i){ x[i>>6] |= 1ULL << (i&63); }
static int bs_eq(const uint64_t *a, const uint64_t *b){
  for (int w = 0; w < MAXWORDS; w++) if (a[w] != b[w]) return 0; return 1;
}
static int bs_count(const uint64_t *x){
  int c = 0; for (int w = 0; w < MAXWORDS; w++) c += __builtin_popcountll(x[w]); return c;
}

/* one parallel T_P step: apply every rule once (join on shared Y). returns #new atoms */
static int closure_step(const uint64_t *in, uint64_t *out, const int *rules, int nrules){
  bs_copy(out, in);
  int added = 0;
  for (int k = 0; k < nrules; k++){
    const Rule *r = &all_rules[rules[k]];
    for (int X = 0; X < NENT; X++)
      for (int Y = 0; Y < NENT; Y++){
        if (!bs_test(in, atom_idx(r->b1, X, Y))) continue;
        for (int Z = 0; Z < NENT; Z++){
          if (X == Z) continue;
          if (bs_test(in, atom_idx(r->b2, Y, Z))){
            int hi = atom_idx(r->head, X, Z);
            if (!bs_test(out, hi)){ bs_set(out, hi); added++; }
          }
        }
      }
  }
  return added;
}

/* closure to fixpoint; if depth!=NULL, depth[i]=min derivation layer (0=fact) */
static void closure(const uint64_t *facts, const int *rules, int nrules,
                    uint64_t *out, int *depth){
  uint64_t cur[MAXWORDS], nxt[MAXWORDS];
  bs_copy(cur, facts);
  if (depth) for (int i = 0; i < NATOMS; i++) depth[i] = bs_test(facts, i) ? 0 : -1;
  int layer = 0;
  for (;;){
    int added = closure_step(cur, nxt, rules, nrules);
    if (depth)
      for (int i = 0; i < NATOMS; i++)
        if (depth[i] < 0 && bs_test(nxt, i)) depth[i] = layer + 1;
    bs_copy(cur, nxt);
    layer++;
    if (!added) break;
    if (layer > NATOMS){ fprintf(stderr, "closure non-termination\n"); exit(2); }
  }
  bs_copy(out, cur);
}

/* ---------------- deterministic PRNG ---------------- */
static uint64_t rng_state;
static uint64_t mix64(uint64_t x){ x ^= x>>12; x ^= x<<25; x ^= x>>27; return x*2685821657736338717ULL; }
static uint64_t nextrand(void){ rng_state = mix64(rng_state); return rng_state; }
static int randbelow(int n){ return (int)(nextrand() % (uint64_t)n); }
static int chance_pct(int p){ return randbelow(100) < p; }
static void shuffle_ints(int *v, int n){
  for (int i = n-1; i > 0; i--){ int j = randbelow(i+1); int t=v[i]; v[i]=v[j]; v[j]=t; }
}

/* ---------------- world ---------------- */
#define SEED_RULES 3
#define POOL 12
#define GOAL_COUNT 3
typedef struct {
  int split, idx;
  uint64_t facts[MAXWORDS];
  int theory[SEED_RULES];
  int cands[POOL];
  int ngoals;
  int goal_atom[GOAL_COUNT];      /* atom index */
  int goal_depth[GOAL_COUNT];     /* genuine closure depth */
} World;

static int g_fallback = 0, g_depth_used = 0;

/* generate a world; goals drawn from atoms at the requested closure depth.
 * returns 0 if no genuine depth-k goal exists (scan mode tries next structure). */
static int make_world(World *w, int split, int idx){
  w->split = split; w->idx = idx; g_fallback = 0;
  rng_state = mix64((uint64_t)(split*7919u + (uint64_t)idx*104729u) ^ 0x5DEECE66DULL) | 1ULL;
  bs_zero(w->facts);
  /* random facts: ~18% of valid off-diagonal slots */
  for (int p = 0; p < NPRED; p++)
    for (int a = 0; a < NENT; a++)
      for (int b = 0; b < NENT; b++)
        if (a != b && chance_pct(18)) bs_set(w->facts, atom_idx(p, a, b));
  int order[NRULES];
  for (int i = 0; i < NRULES; i++) order[i] = i;
  shuffle_ints(order, NRULES);
  for (int i = 0; i < SEED_RULES; i++) w->theory[i] = order[i];
  for (int i = 0; i < POOL; i++) w->cands[i] = order[SEED_RULES + i];

  /* closure with ALL rules to find the deepest reachable atoms */
  int all[SEED_RULES + POOL];
  for (int i = 0; i < SEED_RULES; i++) all[i] = w->theory[i];
  for (int i = 0; i < POOL; i++) all[SEED_RULES+i] = w->cands[i];
  uint64_t full[MAXWORDS]; int depth[NATOMS];
  closure(w->facts, all, SEED_RULES+POOL, full, depth);

  int want = g_goaldepth > 0 ? g_goaldepth : 2;
  int gp[NATOMS], ng = 0;
  for (int i = 0; i < NATOMS; i++)
    if (depth[i] == want) gp[ng++] = i;
  if (ng == 0 && g_goal_scan) return 0;
  if (ng == 0){
    /* fallback: shallowest non-empty depth <= want (recorded) */
    for (int d2 = want-1; d2 >= 1 && ng == 0; d2--){
      for (int i = 0; i < NATOMS; i++) if (depth[i] == d2) gp[ng++] = i;
      if (ng > 0){ g_fallback = 1; g_depth_used = d2; }
    }
  }
  if (ng == 0) return 0;
  /* shuffle goal list with a local stream keyed by (split,idx,depth) */
  uint64_t gs = mix64((uint64_t)(split*131 + idx*2654435761u + (uint64_t)want*2654435761u) ^ 0xA5A5A5A55A5A5A5AULL);
  for (int i = ng-1; i > 0; i--){ gs = mix64(gs); int j = (int)(gs % (uint64_t)(i+1));
    int t=gp[i]; gp[i]=gp[j]; gp[j]=t; }
  w->ngoals = ng < GOAL_COUNT ? ng : GOAL_COUNT;
  for (int g = 0; g < w->ngoals; g++){ w->goal_atom[g] = gp[g]; w->goal_depth[g] = want; }
  return 1;
}

/* ---------------- census / dump ---------------- */
static void dump_world(const World *w, FILE *f){
  fprintf(f, "W %d %d %d %d\n", w->split, w->idx, w->ngoals, g_fallback);
  fprintf(f, "FACTS");
  for (int i = 0; i < NATOMS; i++) if (bs_test(w->facts, i)) fprintf(f, " %d", i);
  fprintf(f, "\nTHEORY");
  for (int i = 0; i < SEED_RULES; i++) fprintf(f, " %d", w->theory[i]);
  fprintf(f, "\nCANDS");
  for (int i = 0; i < POOL; i++) fprintf(f, " %d", w->cands[i]);
  fprintf(f, "\nGOALS");
  for (int g = 0; g < w->ngoals; g++) fprintf(f, " %d:%d", w->goal_atom[g], w->goal_depth[g]);
  fprintf(f, "\n");
}

static void build_split(int split, int nworlds, FILE *dump){
  long genuine = 0, fallback = 0, scans = 0;
  int src = 0;
  World w;
  for (int i = 0; i < nworlds; i++){
    int ok = 0;
    if (g_goal_scan){
      int guard = 0;
      while (!ok && guard++ < 50000){ ok = make_world(&w, split, src++); scans++; }
      if (!ok){ fprintf(stderr, "SCAN-FAIL split=%d world=%d depth=%d\n", split, i, g_goaldepth); exit(3); }
    } else {
      while (!ok) ok = make_world(&w, split, i);
    }
    if (g_fallback) fallback++; else genuine++;
    if (dump) dump_world(&w, dump);
  }
  fprintf(stderr, "CENSUS split=%d depth=%d worlds=%d genuine=%ld fallback=%ld scans=%ld mode=%s\n",
          split, g_goaldepth, nworlds, genuine, fallback, scans, g_goal_scan ? "scan" : "fallback");
}

/* depth distribution of all reachable atoms over a batch of worlds (fixture design aid) */
static void depth_histogram(int nworlds){
  long hist[NATOMS+1]; memset(hist, 0, sizeof hist);
  World w;
  for (int i = 0; i < nworlds; i++){
    if (!make_world(&w, 0, i)) continue;
    int all[SEED_RULES+POOL];
    for (int k=0;k<SEED_RULES;k++) all[k]=w.theory[k];
    for (int k=0;k<POOL;k++) all[SEED_RULES+k]=w.cands[k];
    uint64_t full[MAXWORDS]; int depth[NATOMS];
    closure(w.facts, all, SEED_RULES+POOL, full, depth);
    for (int a=0;a<NATOMS;a++) if (depth[a]>=0 && depth[a]<=NATOMS) hist[depth[a]]++;
  }
  printf("DEPTH-HIST worlds=%d (atoms per derivation depth, all rules)\n", nworlds);
  for (int d=0; d<=12; d++) printf("  depth %2d : %ld\n", d, hist[d]);
}

#ifndef RC_NO_MAIN
int main(int argc, char **argv){
  build_rules();
  const char *dump = NULL;
  int nworlds = 100, hist = 0, selfcheck = 0;
  for (int i = 1; i < argc; i++){
    if (!strcmp(argv[i], "--dump") && i+1 < argc) dump = argv[++i];
    else if (!strcmp(argv[i], "--worlds") && i+1 < argc) nworlds = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--goaldepth") && i+1 < argc) g_goaldepth = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--goal-scan")) g_goal_scan = 1;
    else if (!strcmp(argv[i], "--depth-hist")) hist = 1;
    else if (!strcmp(argv[i], "--self-check")) selfcheck = 1;
  }
  if (selfcheck){
    /* (1) confluence: fixpoint is independent of rule order (monotone T_P). */
    int bad = 0;
    World w;
    for (int i = 0; i < 50; i++){
      if (!make_world(&w, 0, i)) continue;
      int all[SEED_RULES+POOL], rev[SEED_RULES+POOL];
      for (int k=0;k<SEED_RULES;k++){ all[k]=w.theory[k]; rev[k]=w.theory[k]; }
      for (int k=0;k<POOL;k++){ all[SEED_RULES+k]=w.cands[k]; rev[SEED_RULES+k]=w.cands[POOL-1-k]; }
      uint64_t c1[MAXWORDS], c2[MAXWORDS];
      closure(w.facts, all, SEED_RULES+POOL, c1, NULL);
      closure(w.facts, rev, SEED_RULES+POOL, c2, NULL);
      if (!bs_eq(c1, c2)) bad++;
    }
    /* (2) hand example: transitive closure of a 4-chain under p(X,Z):-p(X,Y),p(Y,Z).
     * facts p(0,1),p(1,2),p(2,3); rule index h=0,b1=0,b2=0 is 0. Parallel join
     * doubling: p(0,2),p(1,3) at depth 1; p(0,3) at depth 2; no reverse edge. */
    uint64_t f[MAXWORDS]; bs_zero(f);
    bs_set(f, atom_idx(0,0,1)); bs_set(f, atom_idx(0,1,2)); bs_set(f, atom_idx(0,2,3));
    int r0[1] = {0};   /* all_rules[0] = h0:-b0,b0 (p transitivity) */
    uint64_t c[MAXWORDS]; int dep[NATOMS];
    closure(f, r0, 1, c, dep);
    int hand_ok = bs_test(c, atom_idx(0,0,3)) && dep[atom_idx(0,0,3)]==2
               && dep[atom_idx(0,0,2)]==1 && dep[atom_idx(0,1,3)]==1
               && !bs_test(c, atom_idx(0,3,0));   /* no reverse edge */
    printf("SELF-CHECK confluence_violations=%d hand_transitive=%s %s\n",
           bad, hand_ok?"ok":"BAD", (bad==0 && hand_ok)?"PASS":"FAIL");
    return (bad==0 && hand_ok)?0:1;
  }
  if (hist){ depth_histogram(nworlds); return 0; }
  if (dump){
    FILE *f = fopen(dump, "w");
    if (!f){ fprintf(stderr, "cannot open %s\n", dump); return 2; }
    build_split(0, nworlds, f);
    fclose(f);
    printf("RC-DUMP worlds=%d depth=%d path=%s\n", nworlds, g_goaldepth, dump);
    return 0;
  }
  build_split(0, nworlds, NULL);
  return 0;
}
#endif /* RC_NO_MAIN */