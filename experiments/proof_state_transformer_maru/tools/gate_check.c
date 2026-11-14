/* gate_check.c — strict validator for the proof-state variant log (0.0245).
 *
 * Fixes the 0.0244 review's F2/F3: the old AWK gates accepted an empty file,
 * zero SEED rows, one row claiming N seeds, missing fields (read as 0) and a
 * model goal fraction below the support baseline.
 *
 * Checks
 *   1. exactly one MEAN line, exactly N distinct SEED lines with the expected ids
 *   2. every required field present and finite on SEED and MEAN lines
 *   3. MEAN recomputed from the SEED rows (tolerance 2e-3)
 *   4. permutation invariance, control margins, matched-search budget fields
 *   5. declared direction on the declared fixture (model beam vs prior/random/untrained)
 *   6. fixture qualification (ref saturated, hard has headroom) — reported
 * The support comparison is reported with its sign and never asserted: on the
 * repaired hard fixture support beats the learned ranker (negative result).
 *
 * Usage: gate_check <log> <ref|hard> <expected_seeds> [first_seed]
 * Exit 0 = PASS.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAXF 96
#define MAXROWS 64

typedef struct { char name[64]; double val; int present; } Field;
typedef struct { long seed; int nf; Field f[MAXF]; } Row;

static const char *REQ_FIELDS[] = {
  "top1","hit","regret","proof_model","full_model","proof_utility_greedy","proof_support",
  "proof_prior","proof_random","proof_untrained","proof_shuffled","proof_beam","full_beam",
  "beam_logp","beam_support","beam_prior","beam_random","beam_untrained","beam_full_support",
  "bound_goal","bound_full","perm_maxdiff","val_top1","pchk","base_support","base_prior",
  "base_random","search_states","search_cands","search_closes","forwards_model", NULL
};
static const char *REQ_MEAN[] = {
  "top1","hit","proof_model","full_model","proof_utility_greedy","proof_support",
  "proof_prior","proof_random","proof_untrained","proof_shuffled","proof_beam","full_beam",
  "beam_logp","beam_support","beam_prior","beam_random","beam_untrained","bound_goal",
  "bound_full","perm_maxdiff","beam_full_support","search_states","search_cands",
  "search_closes","forwards_model","val_top1","pchk","base_support","base_prior",
  "base_random","seeds", NULL
};

static int field_set(Row *r, const char *name, double v){
  for (int i = 0; i < r->nf; i++)
    if (!strcmp(r->f[i].name, name)){ r->f[i].val = v; r->f[i].present = 1; return 0; }
  if (r->nf >= MAXF) return -1;
  snprintf(r->f[r->nf].name, sizeof r->f[0].name, "%s", name);
  r->f[r->nf].val = v; r->f[r->nf].present = 1; r->nf++;
  return 0;
}
static double field_get(const Row *r, const char *name, int *present){
  for (int i = 0; i < r->nf; i++)
    if (!strcmp(r->f[i].name, name)){ if (present) *present = r->f[i].present; return r->f[i].val; }
  if (present) *present = 0;
  return NAN;
}

int main(int argc, char **argv){
  if (argc < 4){ fprintf(stderr, "usage: gate_check <log> <ref|hard> <seeds> [first]\n"); return 2; }
  const char *path = argv[1];
  const char *fixture = argv[2];
  int nseeds = atoi(argv[3]);
  int first = (argc > 4) ? atoi(argv[4]) : 11;
  FILE *f = fopen(path, "r");
  if (!f){ printf("GATE-FAIL cannot open %s\n", path); return 1; }

  Row rows[MAXROWS]; int nrows = 0;
  Row mean; memset(&mean, 0, sizeof mean); int nmean = 0;
  char line[16384];
  while (fgets(line, sizeof line, f)){
    if (!strncmp(line, "SEED ", 5)){
      char *p = line + 5;
      long seed = strtol(p, &p, 10);
      if (nrows >= MAXROWS){ printf("GATE-FAIL too many rows\n"); return 1; }
      Row *r = &rows[nrows]; memset(r, 0, sizeof *r); r->seed = seed;
      while (*p){
        while (*p == ' ') p++;
        if (!*p || *p == '\n') break;
        char key[64]; int k = 0;
        while (*p && *p != '=' && *p != ' ' && k < 63) key[k++] = *p++;
        key[k] = 0;
        if (*p != '='){ while (*p && *p != ' ') p++; continue; }
        p++;
        char *end = p;
        double v = strtod(p, &end);
        if (!strcmp(key, "variant") || !strcmp(key, "fixture")){
          while (*end && *end != ' ' && *end != '\n') end++;
          field_set(r, key, 0.0);
          p = end;
          continue;
        }
        if (end == p || (*end && *end != ' ' && *end != '\n')){
          printf("GATE-FAIL malformed value for %s: '%s'\n", key, p);
          return 1;
        }
        int dup = 0;
        for (int q = 0; q < r->nf; q++) if (!strcmp(r->f[q].name, key)) dup = 1;
        if (dup){ printf("GATE-FAIL duplicate field %s\n", key); return 1; }
        p = end;
        field_set(r, key, v);
      }
      nrows++;
    } else if (!strncmp(line, "MEAN ", 5)){
      nmean++;
      mean.seed = -1;
      char *p = line + 5;
      while (*p){
        while (*p == ' ') p++;
        if (!*p || *p == '\n') break;
        char key[64]; int k = 0;
        while (*p && *p != '=' && *p != ' ' && k < 63) key[k++] = *p++;
        key[k] = 0;
        if (*p != '='){ while (*p && *p != ' ') p++; continue; }
        p++;
        char *end = p;
        double v = strtod(p, &end);
        if (!strcmp(key, "variant") || !strcmp(key, "fixture")){
          while (*end && *end != ' ' && *end != '\n') end++;
          field_set(&mean, key, 0.0);
          p = end;
          continue;
        }
        if (end == p || (*end && *end != ' ' && *end != '\n')){
          printf("GATE-FAIL malformed MEAN value for %s\n", key);
          return 1;
        }
        int dup = 0;
        for (int q = 0; q < mean.nf; q++) if (!strcmp(mean.f[q].name, key)) dup = 1;
        if (dup){ printf("GATE-FAIL duplicate MEAN field %s\n", key); return 1; }
        p = end;
        field_set(&mean, key, v);
      }
    }
  }
  fclose(f);

  int bad = 0;
  if (nmean != 1){ printf("GATE-FAIL MEAN lines=%d (need exactly 1)\n", nmean); bad = 1; }
  if (nrows != nseeds){ printf("GATE-FAIL SEED rows=%d (need %d)\n", nrows, nseeds); bad = 1; }
  for (int i = 0; i < nrows && !bad; i++)
    for (int j = i+1; j < nrows; j++)
      if (rows[i].seed == rows[j].seed){ printf("GATE-FAIL duplicate seed %ld\n", rows[i].seed); bad = 1; }
  for (int i = 0; i < nrows && !bad; i++){
    int found = 0;
    for (int s = 0; s < nrows; s++) if (rows[s].seed == first + i) found = 1;
    if (!found){ printf("GATE-FAIL missing seed %d\n", first + i); bad = 1; }
  }
  if (bad) return 1;

  /* required fields + finiteness */
  for (int i = 0; i < nrows; i++)
    for (int k = 0; REQ_FIELDS[k]; k++){
      int pr = 0; double v = field_get(&rows[i], REQ_FIELDS[k], &pr);
      if (!pr || !isfinite(v)){
        printf("GATE-FAIL seed %ld missing/non-finite field %s\n", rows[i].seed, REQ_FIELDS[k]);
        return 1;
      }
    }
  for (int k = 0; REQ_MEAN[k]; k++){
    int pr = 0; double v = field_get(&mean, REQ_MEAN[k], &pr);
    if (!pr || !isfinite(v)){
      printf("GATE-FAIL MEAN missing/non-finite field %s\n", REQ_MEAN[k]);
      return 1;
    }
  }

  /* MEAN must equal the recomputation from SEED rows */
  for (int k = 0; REQ_MEAN[k]; k++){
    double sum = 0;
    for (int i = 0; i < nrows; i++) sum += field_get(&rows[i], REQ_MEAN[k], NULL);
    double rec = sum / (double)nrows;
    double got = field_get(&mean, REQ_MEAN[k], NULL);
    if (fabs(rec - got) > 2e-3){
      printf("GATE-FAIL MEAN %s=%.6f != recomputed %.6f\n", REQ_MEAN[k], got, rec);
      return 1;
    }
  }

  {
    int pr = 0; double declared = field_get(&mean, "seeds", &pr);
    if (!pr || !isfinite(declared) || declared != (double)nrows){
      printf("GATE-FAIL MEAN seeds=%.0f != SEED rows=%d\n", declared, nrows); return 1;
    }
  }
  /* ratios in [0,1]; budgets non-negative integers; model/beam <= exact bound */
  static const char *RATIO[] = {"hit","proof_model","full_model","proof_support","proof_prior",
    "proof_random","proof_untrained","proof_shuffled","proof_utility_greedy","proof_beam",
    "full_beam","beam_logp","beam_support","beam_prior","beam_random","beam_untrained",
    "beam_full_support","bound_goal","bound_full", NULL};
  for (int i = 0; i < nrows; i++)
    for (int k = 0; RATIO[k]; k++){
      double v = field_get(&rows[i], RATIO[k], NULL);
      if (!(v >= 0.0 && v <= 1.0)){
        printf("GATE-FAIL seed %ld %s=%.6f outside [0,1]\n", rows[i].seed, RATIO[k], v); return 1;
      }
    }
  for (int k = 0; RATIO[k]; k++){
    double v = field_get(&mean, RATIO[k], NULL);
    if (!(v >= 0.0 && v <= 1.0)){
      printf("GATE-FAIL MEAN %s=%.6f outside [0,1]\n", RATIO[k], v); return 1;
    }
  }
  double bgoal = field_get(&mean, "bound_goal", NULL);
  double bfull = field_get(&mean, "bound_full", NULL);
  static const char *VS_BOUND[] = {"proof_model","proof_utility_greedy","proof_support",
    "proof_prior","proof_random","proof_untrained","proof_shuffled","proof_beam",
    "beam_logp","beam_support","beam_prior","beam_random","beam_untrained", NULL};
  for (int k = 0; VS_BOUND[k]; k++){
    double v = field_get(&mean, VS_BOUND[k], NULL);
    if (!(v <= bgoal + 1e-9)){
      printf("GATE-FAIL MEAN %s=%.6f exceeds exact bound %.6f\n", VS_BOUND[k], v, bgoal); return 1;
    }
  }
  if (!(field_get(&mean, "full_model", NULL) <= bfull + 1e-9) ||
      !(field_get(&mean, "full_beam", NULL) <= bfull + 1e-9)){
    printf("GATE-FAIL MEAN full-success exceeds exact bound %.6f\n", bfull); return 1;
  }
  {
    static const char *BUDGET[] = {"search_states","search_cands","search_closes","forwards_model", NULL};
    for (int k = 0; BUDGET[k]; k++){
      double v = field_get(&mean, BUDGET[k], NULL);
      if (!isfinite(v) || v < 0 || v != floor(v)){
        printf("GATE-FAIL MEAN budget %s=%.6f not a non-negative integer\n", BUDGET[k], v); return 1;
      }
    }
    double fwd = field_get(&mean, "forwards_model", NULL);
    double sts = field_get(&mean, "search_states", NULL);
    if (fwd > sts + 1e-9){
      printf("GATE-FAIL forwards_model > search_states\n"); return 1;
    }
  }

  double perm = field_get(&mean, "perm_maxdiff", NULL);
  if (!(perm < 1e-9)){ printf("GATE-FAIL permutation invariance %.3e\n", perm); return 1; }

  double pm = field_get(&mean, "proof_model", NULL);
  double psh = field_get(&mean, "proof_shuffled", NULL);
  double pu = field_get(&mean, "proof_untrained", NULL);
  if (!(pm > psh + 0.10)){ printf("GATE-FAIL shuffled control too strong (model %.3f <= shuffled %.3f + 0.10)\n", pm, psh); return 1; }
  if (!(pm > pu + 0.10)){ printf("GATE-FAIL untrained control too strong (model %.3f <= untrained %.3f + 0.10)\n", pm, pu); return 1; }

  double st = field_get(&mean, "search_states", NULL);
  double cd = field_get(&mean, "search_cands", NULL);
  double cl = field_get(&mean, "search_closes", NULL);
  double fw = field_get(&mean, "forwards_model", NULL);
  if (!(st > 0 && cd > 0 && cl > 0 && fw > 0)){
    printf("GATE-FAIL matched-search budget fields\n"); return 1;
  }

  /* greedy-level direction: the learned ranker must beat the non-learned
   * baselines; the support comparison is reported (support wins on hard). */
  double gpr = field_get(&mean, "proof_prior", NULL);
  double grr = field_get(&mean, "proof_random", NULL);
  double guu = field_get(&mean, "proof_untrained", NULL);
  if (!(pm > gpr + 0.05)){ printf("GATE-FAIL greedy model %.3f <= prior %.3f + 0.05\n", pm, gpr); return 1; }
  if (!(pm > grr + 0.05)){ printf("GATE-FAIL greedy model %.3f <= random %.3f + 0.05\n", pm, grr); return 1; }
  if (!(pm > guu + 0.05)){ printf("GATE-FAIL greedy model %.3f <= untrained %.3f + 0.05\n", pm, guu); return 1; }

  double bm = field_get(&mean, "proof_beam", NULL);   /* MEAN name for the model raw-score beam */
  int prs = 0; double bs = field_get(&mean, "beam_support", &prs);
  double bp = field_get(&mean, "beam_prior", NULL);
  double br = field_get(&mean, "beam_random", NULL);
  double bu = field_get(&mean, "beam_untrained", NULL);
  if (!(bm > bp + 0.05)){ printf("GATE-FAIL beam model %.3f <= prior %.3f + 0.05\n", bm, bp); return 1; }
  if (!(bm > br + 0.05)){ printf("GATE-FAIL beam model %.3f <= random %.3f + 0.05\n", bm, br); return 1; }
  if (!(bm > bu + 0.05)){ printf("GATE-FAIL beam model %.3f <= untrained %.3f + 0.05\n", bm, bu); return 1; }

  double bg = field_get(&mean, "bound_goal", NULL);
  double bf = field_get(&mean, "bound_full", NULL);
  if (!strcmp(fixture, "ref")){
    if (!(bg >= 0.99)){
      printf("GATE-FAIL ref fixture is expected to be saturated (bound %.3f < 0.99)\n", bg);
      return 1;
    }
  } else {
    if (!(bg < 0.995 && bg > 0.5)){
      printf("GATE-FAIL hard fixture bound %.3f outside (0.5,0.995)\n", bg);
      return 1;
    }
  }
  if (!(bf >= 0.0 && bf <= 1.0)){ printf("GATE-FAIL bound_full range\n"); return 1; }

  printf("GATE-PASS fixture=%s seeds=%d model=%.4f beam_model=%.4f beam_support=%.4f "
         "(model-minus-support %+.4f, reported) bound_goal=%.4f bound_full=%.4f "
         "search states=%ld cands=%ld closes=%ld forwards=%ld\n",
         fixture, nrows, pm, bm, bs, bm - bs, bg, bf,
         (long)st, (long)cd, (long)cl, (long)fw);
  return 0;
}