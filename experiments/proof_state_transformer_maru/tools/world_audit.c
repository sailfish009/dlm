/* world_audit.c — independent audit of the proof-state worlds.
 *
 * Deliberately does NOT include or link the lab sources: it parses the dumped
 * worlds, re-derives the reference rule table, and represents known atoms as a
 * 36-bit set-of-atoms (bit = entity_slot*6 + predicate) instead of the lab's
 * per-entity 6-bit masks. It checks the 0.0244 review's F1 invariants and the
 * F4 budget-exact bound:
 *
 *   WITNESS      every goal (p,e) has a candidate rule whose head is p and
 *                whose body holds at e in the base closure
 *   REACHABLE    with every candidate rule available, the goal is derived
 *   BOUND(d<=4)  exhaustive search over closed states (action = one rule),
 *                deduplicated by atom set, gives the maximum goals any policy
 *                can reach within the 4-rule budget
 *
 * Usage: world_audit <worlds.txt>
 * Output: AUDIT worlds=.. goals=.. unique=.. witness_violations=..
 *         unreachable=.. bound_goal_pm=.. bound_full_pm=.. states=..
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
#define NSTEPS 4
#define HSSIZE (1u << 18)

typedef struct { int head; int nb; int body[2]; } Rule;

static Rule rules[NRULES_ALL];

static void build_rules(void){
  int k = 0;
  for (int h = 0; h < NP; h++){
    for (int b = 0; b < NP; b++)
      if (b != h){ rules[k].head = h; rules[k].nb = 1; rules[k].body[0] = b; k++; }
    for (int b1 = 0; b1 < NP; b1++)
      for (int b2 = b1+1; b2 < NP; b2++)
        if (h != b1 && h != b2){
          rules[k].head = h; rules[k].nb = 2; rules[k].body[0] = b1; rules[k].body[1] = b2; k++;
        }
  }
}

/* atom bit = e*NP + p ; 36 bits */
static int body_holds_at(uint64_t atoms, const Rule *r, int e){
  for (int k = 0; k < r->nb; k++)
    if (!(atoms & (1ULL << (e*NP + r->body[k])))) return 0;
  return 1;
}
static uint64_t apply_rule(uint64_t atoms, const Rule *r){
  uint64_t add = 0;
  for (int e = 0; e < WENT; e++)
    if (body_holds_at(atoms, r, e)) add |= 1ULL << (e*NP + r->head);
  return atoms | add;
}
static uint64_t close_all(uint64_t atoms, const int *ids, int n){
  int changed = 1;
  while (changed){
    changed = 0;
    for (int i = 0; i < n; i++){
      uint64_t next = apply_rule(atoms, &rules[ids[i]]);
      if (next != atoms){ atoms = next; changed = 1; }
    }
  }
  return atoms;
}

/* hash set for state dedup */
static uint64_t hs[HSSIZE];
static int hstamp[HSSIZE];
static int hgen = 0;
static void hs_clear(void){ hgen++; }
static int hs_add(uint64_t v){
  uint32_t h = (uint32_t)((v * 0x9E3779B97F4A7C15ULL) >> 40) & (HSSIZE-1);
  while (hstamp[h] == hgen){
    if (hs[h] == v) return 0;
    h = (h + 1) & (HSSIZE-1);
  }
  hstamp[h] = hgen; hs[h] = v;
  return 1;
}

typedef struct {
  int ngoal;
  int goal_pred[MAXG], goal_ent[MAXG];
  int ncand;
  int cand[MAXC];
} World;

static int goals_in(uint64_t atoms, const World *w){
  int c = 0;
  for (int g = 0; g < w->ngoal; g++)
    if (atoms & (1ULL << (w->goal_ent[g]*NP + w->goal_pred[g]))) c++;
  return c;
}

typedef struct {
  uint64_t *v;
  long n, cap;
} Layer;

static void layer_push(Layer *l, uint64_t x){
  if (l->n == l->cap){
    l->cap = l->cap ? l->cap*2 : 1024;
    l->v = (uint64_t*)realloc(l->v, (size_t)l->cap * sizeof(uint64_t));
    if (!l->v){ fprintf(stderr, "oom\n"); exit(2); }
  }
  l->v[l->n++] = x;
}

int main(int argc, char **argv){
  build_rules();
  if (argc < 2){ fprintf(stderr, "usage: world_audit worlds.txt\n"); return 2; }
  FILE *f = fopen(argv[1], "r");
  if (!f){ fprintf(stderr, "cannot open %s\n", argv[1]); return 2; }

  long worlds = 0, goals = 0, unique = 0, witness_bad = 0, unreach = 0;
  long pool_atoms = 0, goals_not_eligible = 0;
  long bound_goals = 0, bound_full_worlds = 0, states_total = 0;
  char line[16384];
  World w;
  uint64_t base = 0, facts = 0;
  int theory[2] = {0,0}, ntheory = 0;
  int have = 0;

  while (fgets(line, sizeof line, f)){
    char tag = line[0];
    if (tag == 'W'){
      int split, idx;
      sscanf(line, "W %d %d %d", &split, &idx, &w.ngoal);
      w.ncand = 0; base = 0; facts = 0; ntheory = 0; have = 1;
    } else if (tag == 'F'){
      /* F m0 m1 ... m5 : per-entity 6-bit predicate masks */
      char *p = line + 1;
      for (int e = 0; e < WENT; e++){
        long m = strtol(p, &p, 10);
        for (int q = 0; q < NP; q++) if ((m >> q) & 1) facts |= 1ULL << (e*NP + q);
      }
    } else if (tag == 'T'){
      char *p = line + 1;
      ntheory = 0;
      for (int i = 0; i < 2; i++){ long id = strtol(p, &p, 10); theory[ntheory++] = (int)id; }
    } else if (tag == 'C'){
      char *p = line + 1;
      w.ncand = 0;
      for (int i = 0; i < MAXC; i++){
        long id = strtol(p, &p, 10);
        w.cand[w.ncand++] = (int)id;
      }
    } else if (tag == 'G'){
      char *p = line + 1;
      int k = 0;
      while (k < w.ngoal && k < MAXG){
        long pr = strtol(p, &p, 10);
        if (*p == ':') p++;
        long ei = strtol(p, &p, 10);
        w.goal_pred[k] = (int)pr; w.goal_ent[k] = (int)ei; k++;
      }
      if (k != w.ngoal){ fprintf(stderr, "goal parse mismatch\n"); return 2; }
    } else if (tag == 'S' && line[1] == 'T'){
      /* STEP marks the end of the world record */
      if (!have) continue;
      have = 0;
      worlds++;
      base = close_all(facts, theory, ntheory);      /* base closure under the seed rules */
      /* R245-4: the kernel keeps the seed rules active together with the chosen
       * candidates, so reachability and the one-candidate control must too. */
      int allr[2+MAXC];
      for (int i = 0; i < ntheory; i++) allr[i] = theory[i];
      for (int i = 0; i < w.ncand; i++) allr[ntheory+i] = w.cand[i];
      uint64_t closed_all = close_all(facts, allr, ntheory + w.ncand);
      /* eligible hard-goal pool: K1 \ union_r closure(facts, seed + {r}) */
      uint64_t k0 = base;
      for (int i = 0; i < w.ncand; i++){
        int one[3];
        for (int t = 0; t < ntheory; t++) one[t] = theory[t];
        one[ntheory] = w.cand[i];
        k0 |= close_all(facts, one, ntheory+1);
      }
      uint64_t eligible = closed_all & ~k0;
      pool_atoms += __builtin_popcountll(eligible);

      /* WITNESS: some candidate with head p has its body true at the goal entity */
      for (int g = 0; g < w.ngoal; g++){
        goals++;
        int ok = 0;
        for (int i = 0; i < w.ncand; i++)
          if (rules[w.cand[i]].head == w.goal_pred[g] && body_holds_at(base, &rules[w.cand[i]], w.goal_ent[g])) ok = 1;
        if (!ok) witness_bad++;
        if (!(closed_all & (1ULL << (w.goal_ent[g]*NP + w.goal_pred[g])))) unreach++;
        if (!(eligible & (1ULL << (w.goal_ent[g]*NP + w.goal_pred[g])))) goals_not_eligible++;
      }
      /* UNIQUE goals (dedup by predicate+entity) */
      for (int g = 0; g < w.ngoal; g++){
        int dup = 0;
        for (int h = 0; h < g; h++) if (w.goal_pred[h] == w.goal_pred[g] && w.goal_ent[h] == w.goal_ent[g]) dup = 1;
        if (!dup) unique++;
      }
      /* BOUND: exhaustive over rule subsets of size <= NSTEPS (a committed
       * rule stays active while other rules add atoms). */
      int best = goals_in(base, &w);
      for (int k = 1; k <= NSTEPS; k++){
        int pick[NSTEPS]; for (int i = 0; i < NSTEPS; i++) pick[i] = 0;
        /* combination enumeration */
        int c[NSTEPS+1];
        for (int i = 0; i <= k; i++) c[i] = i;
        while (1){
          int rules[2+NSTEPS];
          for (int i = 0; i < ntheory; i++) rules[i] = theory[i];
          for (int i = 0; i < k; i++) rules[ntheory+i] = w.cand[c[i]];
          uint64_t closed = close_all(base, rules, ntheory+k);
          int g = goals_in(closed, &w);
          if (g > best) best = g;
          int pos = k-1;
          while (pos >= 0 && c[pos] == w.ncand - k + pos) pos--;
          if (pos < 0) break;
          c[pos]++;
          for (int i = pos+1; i < k; i++) c[i] = c[i-1]+1;
          states_total++;
        }
      }
      bound_goals += best;
      if (best == w.ngoal) bound_full_worlds++;
    }
  }
  fclose(f);
  long total_goals = goals;
  printf("AUDIT worlds=%ld goal_occurrences=%ld unique_goals=%ld witness_violations=%ld unreachable_all_candidates=%ld\n",
         worlds, total_goals, unique, witness_bad, unreach);
  printf("AUDIT pool_atoms=%ld goals_not_in_pool=%ld\n", pool_atoms, goals_not_eligible);
  printf("AUDIT bound_goal_pm=%ld bound_full_pm=%ld states=%ld\n",
         total_goals ? (bound_goals*1000000)/total_goals : 0,
         worlds ? (bound_full_worlds*1000000)/worlds : 0, states_total);
  return 0;
}