/* alias_audit.c — feature-alias audit (0.0245 review R245-3).
 *
 * Constructs legal goal-set variants of the same world (same facts, seed rules,
 * candidates and committed prefix; one goal's entity substituted), computes the
 * aggregate (M1) features and the goal-binding-preserving features, and checks
 * whether two variants with IDENTICAL features have disjoint optimal first-action
 * sets under the remaining budget. Independent of the lab sources.
 *
 * Usage: alias_audit <worlds.txt> [max_worlds]
 * Output:
 *   ALIAS worlds=.. variants=.. pairs=..
 *   ALIAS base feature_equal=<n> alias_pairs=<n> min_pair_regret=<f>
 *   ALIAS relob feature_equal=<n> alias_pairs=<n> min_pair_regret=<f>
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define NP 6
#define WENT 6
#define NRULES_ALL 90
#define MAXC 24
#define MAXG 3
#define BUDGET 4
#define PREFIX 2
#define REMAIN (BUDGET - PREFIX)
#define NBASE_STATE 8
#define NBASE_CAND 26

typedef struct { int head; int nb; int body[2]; } Rule;
static Rule rules[NRULES_ALL];

static void build_rules(void){
  int k = 0;
  for (int h = 0; h < NP; h++){
    for (int b = 0; b < NP; b++)
      if (b != h){ rules[k].head = h; rules[k].nb = 1; rules[k].body[0] = b; k++; }
    for (int b1 = 0; b1 < NP; b1++)
      for (int b2 = b1+1; b2 < NP; b2++)
        if (h != b1 && h != b2){ rules[k].head = h; rules[k].nb = 2; rules[k].body[0] = b1; rules[k].body[1] = b2; k++; }
  }
}

static int body_ok(uint64_t atoms, const Rule *r, int e){
  for (int k = 0; k < r->nb; k++) if (!(atoms & (1ULL << (e*NP + r->body[k])))) return 0;
  return 1;
}
static uint64_t apply_rule(uint64_t atoms, const Rule *r){
  uint64_t add = 0;
  for (int e = 0; e < WENT; e++) if (body_ok(atoms, r, e)) add |= 1ULL << (e*NP + r->head);
  return atoms | add;
}
static uint64_t close_rules(uint64_t atoms, const int *ids, int n){
  int changed = 1;
  while (changed){
    changed = 0;
    for (int i = 0; i < n; i++){
      uint64_t nx = apply_rule(atoms, &rules[ids[i]]);
      if (nx != atoms){ atoms = nx; changed = 1; }
    }
  }
  return atoms;
}

typedef struct {
  int ngoal, gp[MAXG], ge[MAXG];
  int ncand, cand[MAXC];
} World;

static int goals_in(uint64_t atoms, const World *w, const int *gp, const int *ge, int n){
  int c = 0;
  for (int g = 0; g < n; g++) if (atoms & (1ULL << (ge[g]*NP + gp[g]))) c++;
  return c;
}
static int support_at(uint64_t atoms, const Rule *r){
  int c = 0;
  for (int e = 0; e < WENT; e++) if (body_ok(atoms, r, e)) c++;
  return c;
}
static void base_state(uint64_t known, const World *w, const int *gp, const int *ge, int ng,
                       int nrules, int nlive, double out[NBASE_STATE]){
  int kn = __builtin_popcountll(known);
  double total = (double)(NP*WENT);
  int gk = 0;
  for (int g = 0; g < ng; g++) if (known & (1ULL << (ge[g]*NP + gp[g]))) gk++;
  double smin = 1e9, smax = -1e9, ssum = 0;
  for (int i = 0; i < w->ncand; i++){
    const Rule *r = &rules[w->cand[i]];
    double s = (double)support_at(known, r)/(double)WENT;
    if (s < smin) smin = s;
    if (s > smax) smax = s;
    ssum += s;
  }
  out[0] = (double)kn/total;
  out[1] = ng ? (double)gk/(double)ng : 0.0;
  out[2] = 1.0 - (double)kn/total;
  out[3] = (double)nlive/(double)MAXC;
  out[4] = nlive ? ssum/(double)MAXC : 0.0;
  out[5] = nlive ? smax : 0.0;
  out[6] = nlive ? smin : 0.0;
  out[7] = (double)nrules/8.0;
}
static void base_cand(uint64_t known, const World *w, const int *gp, const int *ge, int ng,
                      int cid, double out[NBASE_CAND]){
  const Rule *r = &rules[cid];
  uint64_t bm = 0;
  for (int k = 0; k < r->nb; k++) bm |= 1ULL << r->body[k];
  int sup = 0, bk = 0, hk = 0;
  for (int e = 0; e < WENT; e++){
    if ((known & (bm << (e*NP))) == (bm << (e*NP))) { sup++; bk++; }
    if (known & (1ULL << (e*NP + r->head))) hk++;
  }
  int gc = 0;
  for (int g = 0; g < ng; g++) if (gp[g] == r->head) gc++;
  out[0] = (double)r->nb/2.0;
  out[1] = (0.5 + 0.75*(double)r->nb)/2.0;
  out[2] = (double)sup/(double)WENT;
  out[3] = (double)bk/(double)WENT;
  out[4] = (double)hk/(double)WENT;
  out[5] = ng ? (double)gc/(double)ng : 0.0;
  out[6] = sup > 0 ? 1.0 : 0.0;
  out[7] = gc > 0 ? 1.0 : 0.0;
  for (int p = 0; p < NP; p++) out[8+p] = (r->head == p) ? 1.0 : 0.0;
  for (int s = 0; s < 2; s++)
    for (int p = 0; p < NP; p++) out[8+NP+s*NP+p] = (s < r->nb && r->body[s] == p) ? 1.0 : 0.0;
}
/* goal-binding features: per goal (pred one-hot, entity one-hot) and per candidate
 * (head match, head known at goal entity, body supported at goal entity, would derive) */
static void relob_state(uint64_t known, const World *w, const int *gp, const int *ge, int ng,
                        double out[NBASE_STATE + MAXG*(NP+WENT)]){
  base_state(known, w, gp, ge, ng, 0, MAXC, out);
  int k = NBASE_STATE;
  for (int i = k; i < NBASE_STATE + MAXG*(NP+WENT); i++) out[i] = 0.0;
  for (int g = 0; g < ng; g++){
    for (int p = 0; p < NP; p++) out[k++] = (gp[g] == p) ? 1.0 : 0.0;
    for (int e = 0; e < WENT; e++) out[k++] = (ge[g] == e) ? 1.0 : 0.0;
  }
}
static void relob_cand(uint64_t known, const World *w, const int *gp, const int *ge, int ng,
                       int cid, double out[NBASE_CAND + MAXG*4]){
  base_cand(known, w, gp, ge, ng, cid, out);
  int k = NBASE_CAND;
  for (int i = k; i < NBASE_CAND + MAXG*4; i++) out[i] = 0.0;
  const Rule *r = &rules[cid];
  uint64_t bm = 0;
  for (int q = 0; q < r->nb; q++) bm |= 1ULL << r->body[q];
  for (int g = 0; g < ng; g++){
    int e = ge[g];
    int body_at = ((known >> (e*NP)) & bm) == bm;
    int head_at = (known >> (e*NP + r->head)) & 1ULL;
    out[k++] = (r->head == gp[g]) ? 1.0 : 0.0;
    out[k++] = (double)head_at;
    out[k++] = (double)body_at;
    out[k++] = (r->head == gp[g] && body_at) ? 1.0 : 0.0;
  }
}

typedef struct {
  int alive;                /* eligible goal set under seed-persistent semantics */
  double s[NBASE_STATE + MAXG*(NP+WENT)];
  double c[MAXC][NBASE_CAND + MAXG*4];
  int nrem;
  int rem[MAXC];
  int optmask;              /* bitmask over remaining candidates */
  int best;
} Variant;

int main(int argc, char **argv){
  build_rules();
  int maxw = (argc > 2) ? atoi(argv[2]) : 8;
  FILE *f = fopen(argv[1], "r");
  if (!f){ fprintf(stderr, "cannot open %s\n", argv[1]); return 2; }
  char line[16384];
  World w; uint64_t facts = 0; int theory[2] = {0,0}, ntheory = 0, have = 0;
  long worlds = 0, variants = 0, pairs = 0;
  long base_eq = 0, base_alias = 0, relob_eq = 0, relob_alias = 0;
  long base_optdiff = 0, relob_optdiff = 0;
  double base_regret = 0, relob_regret = 0;
  int counted_worlds = 0;

  while (fgets(line, sizeof line, f)){
    char tag = line[0];
    if (tag == 'W'){ w.ncand = 0; w.ngoal = 0; facts = 0; ntheory = 0; have = 1; }
    else if (tag == 'F'){
      char *p = line + 1;
      for (int e = 0; e < WENT; e++){
        long m = strtol(p, &p, 10);
        for (int q = 0; q < NP; q++) if ((m >> q) & 1) facts |= 1ULL << (e*NP + q);
      }
    } else if (tag == 'T'){
      char *p = line + 1; ntheory = 0;
      for (int i = 0; i < 2; i++){ long id = strtol(p, &p, 10); theory[ntheory++] = (int)id; }
    } else if (tag == 'C'){
      char *p = line + 1; w.ncand = 0;
      for (int i = 0; i < MAXC; i++){ long id = strtol(p, &p, 10); w.cand[w.ncand++] = (int)id; }
    } else if (tag == 'G'){
      char *p = line + 1; w.ngoal = 0;
      while (w.ngoal < MAXG){
        long pr = strtol(p, &p, 10);
        if (*p != ':') { if (*p == 0 || *p == '\n') break; p++; continue; }
        p++;
        long ei = strtol(p, &p, 10);
        w.gp[w.ngoal] = (int)pr; w.ge[w.ngoal] = (int)ei; w.ngoal++;
        if (*p == 0 || *p == '\n') break;
      }
    } else if (tag == 'S' && line[1] == 'T'){
      if (!have) continue;
      have = 0;
      worlds++;
      if (counted_worlds >= maxw) continue;
      counted_worlds++;
      if (w.ngoal < 1) continue;

      uint64_t base = close_rules(facts, theory, ntheory);
      /* seed-persistent goal pool: K1 \ union_r closure(seed + {r}) */
      int allc[MAXC+2], ma = 0;
      for (int t = 0; t < ntheory; t++) allc[ma++] = theory[t];
      for (int i = 0; i < w.ncand; i++) allc[ma++] = w.cand[i];
      uint64_t k1 = close_rules(facts, allc, ma);
      uint64_t k0 = base;
      for (int i = 0; i < w.ncand; i++){
        int one[3]; int mo = 0;
        for (int t = 0; t < ntheory; t++) one[mo++] = theory[t];
        one[mo++] = w.cand[i];
        k0 |= close_rules(facts, one, mo);
      }
      uint64_t pool = k1 & ~k0;

      /* applicable candidates at the base state */
      int app[MAXC], napp = 0;
      for (int i = 0; i < w.ncand; i++){
        const Rule *r = &rules[w.cand[i]];
        for (int e = 0; e < WENT; e++) if (body_ok(base, r, e)){ app[napp++] = w.cand[i]; break; }
      }
      if (napp < PREFIX) continue;

      /* several committed prefixes: every pair of applicable candidates (up to 8) */
      int lim = napp;
      for (int pa = 0; pa < lim; pa++)
      for (int pb = pa+1; pb < lim; pb++){
        int prefix[PREFIX]; prefix[0] = app[pa]; prefix[1] = app[pb];
        int prules[2+PREFIX]; int mr = 0;
        for (int t = 0; t < ntheory; t++) prules[mr++] = theory[t];
        for (int q = 0; q < PREFIX; q++) prules[mr++] = prefix[q];
        uint64_t known = close_rules(facts, prules, mr);
        int rem[MAXC], nrem = 0;
        for (int i = 0; i < w.ncand; i++){
          int used = 0;
          for (int q = 0; q < PREFIX; q++) if (prefix[q] == w.cand[i]) used = 1;
          if (!used) rem[nrem++] = w.cand[i];
        }
        for (int slot = 0; slot < w.ngoal; slot++)
        for (int pr = 0; pr < NP; pr++){
          int es[WENT], ne = 0;
          for (int e = 0; e < WENT; e++) if (pool & (1ULL << (e*NP + pr))) es[ne++] = e;
          for (int i = 0; i < ne; i++)
            for (int j = i+1; j < ne; j++){
              int gpA[MAXG], geA[MAXG], gpB[MAXG], geB[MAXG];
              int ng = w.ngoal;
              for (int g = 0; g < ng; g++){ gpA[g] = w.gp[g]; geA[g] = w.ge[g]; gpB[g] = w.gp[g]; geB[g] = w.ge[g]; }
              gpA[slot] = pr; geA[slot] = es[i]; gpB[slot] = pr; geB[slot] = es[j];
              Variant A, B;
              memset(&A, 0, sizeof A); memset(&B, 0, sizeof B);
              relob_state(known, &w, gpA, geA, ng, A.s);
              relob_state(known, &w, gpB, geB, ng, B.s);
              A.nrem = B.nrem = nrem;
              for (int q = 0; q < nrem; q++){
                A.rem[q] = B.rem[q] = rem[q];
                relob_cand(known, &w, gpA, geA, ng, rem[q], A.c[q]);
                relob_cand(known, &w, gpB, geB, ng, rem[q], B.c[q]);
              }
              int bestA = -1, maskA = 0, bestB = -1, maskB = 0;
              for (int q = 0; q < nrem; q++){
                int sa[BUDGET+2]; int m = 0;
                for (int t = 0; t < ntheory; t++) sa[m++] = theory[t];
                for (int t = 0; t < PREFIX; t++) sa[m++] = prefix[t];
                sa[m++] = rem[q];
                int va = goals_in(close_rules(facts, sa, m), &w, gpA, geA, ng);
                int vb = goals_in(close_rules(facts, sa, m), &w, gpB, geB, ng);
                for (int k2 = 0; k2 < nrem; k2++){
                  if (k2 == q) continue;
                  int s2[BUDGET+3]; int m2 = 0;
                  for (int t = 0; t < m; t++) s2[m2++] = sa[t];
                  s2[m2++] = rem[k2];
                  int ua = goals_in(close_rules(facts, s2, m2), &w, gpA, geA, ng);
                  int ub = goals_in(close_rules(facts, s2, m2), &w, gpB, geB, ng);
                  if (ua > va) va = ua;
                  if (ub > vb) vb = ub;
                }
                if (va > bestA){ bestA = va; maskA = 1 << q; } else if (va == bestA) maskA |= 1 << q;
                if (vb > bestB){ bestB = vb; maskB = 1 << q; } else if (vb == bestB) maskB |= 1 << q;
              }
              pairs++;
              int base_same = !memcmp(A.s, B.s, sizeof(double)*NBASE_STATE) &&
                              !memcmp(A.c, B.c, sizeof(double)*NBASE_CAND*nrem);
              int relob_same = !memcmp(A.s, B.s, sizeof(double)*(NBASE_STATE+MAXG*(NP+WENT))) &&
                               !memcmp(A.c, B.c, sizeof(double)*(NBASE_CAND+MAXG*4)*nrem);
              int disjoint = (maskA & maskB) == 0;
              int optdiff = (maskA != maskB) || (bestA != bestB);
              if (base_same){
                base_eq++;
                if (disjoint) base_alias++;
                if (optdiff) base_optdiff++;
              }
              if (relob_same){
                relob_eq++;
                if (disjoint) relob_alias++;
                if (optdiff) relob_optdiff++;
              }
            }
        }
      }
      variants += 2;
    }
  }
  fclose(f);
  printf("ALIAS worlds=%ld counted=%d variants=%ld pairs=%ld\n", worlds, counted_worlds, variants, pairs);
  printf("ALIAS base feature_equal=%ld alias_pairs=%ld optimal_differs=%ld\n", base_eq, base_alias, base_optdiff);
  printf("ALIAS relob feature_equal=%ld alias_pairs=%ld optimal_differs=%ld\n", relob_eq, relob_alias, relob_optdiff);
  if (base_optdiff > 0 && relob_eq == 0)
    printf("FEATURE-ALIAS-CONFIRMED aggregate_aliases=%ld relob_aliases=0\n", base_optdiff);
  else if (base_optdiff == 0)
    printf("FEATURE-ALIAS-NOT-FOUND\n");
  else
    printf("FEATURE-ALIAS-RELOB-STILL-ALIASED %ld\n", relob_optdiff);
  return 0;
}