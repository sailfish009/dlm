/* 0.0270 alias census: feature-only decision limit on the relational fixture.
 * Groups live candidates by IDENTICAL S0 feature rows within a state; counts
 * groups whose kernel DP labels differ (or whose optimal sets are disjoint).
 * If such aliases exist, no function of the S0 features alone can rank
 * optimally — the binding information must come from elsewhere (S0e/S1). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#define main pst_main
#include "../src/pst.c"
#undef main

int main(int argc, char **argv){
  build_all_rules();
  g_goal_scan = 1; g_goaldepth = argc > 1 ? atoi(argv[1]) : 2; g_collect = 1;
  int split = argc > 2 ? atoi(argv[2]) : 0;
  g_nw[0] = 60; g_nw[1] = 10; g_nw[2] = 60;
  g_valmode = 1;
  alloc_globals();
  build_dataset();
  long states = 0, alias_groups = 0, label_diff = 0, opt_disjoint = 0, cands_in_alias = 0;
  long top_aliases = 0;   /* alias group contains a top-label candidate */
  for (int i = 0; i < g_nw[split]; i++){
    const WSteps *ws = &g_data[split][i];
    for (int st = 0; st < ws->nsteps; st++){
      const RStep *rs = &ws->st[st];
      states++;
      double mx = -1e30;
      for (int k = 0; k < rs->nlive; k++) if (rs->util[k] > mx) mx = rs->util[k];
      int done[POOL] = {0};
      for (int a = 0; a < rs->nlive; a++){
        if (done[a]) continue;
        int grp[POOL], ng = 0;
        for (int b = a; b < rs->nlive; b++){
          if (done[b]) continue;
          int same = 1;
          for (int d = 0; d < CAND_DIM; d++)
            if (fabs(rs->cf[a][d] - rs->cf[b][d]) > 1e-9){ same = 0; break; }
          if (same){ grp[ng++] = b; done[b] = 1; }
        }
        if (ng < 2) continue;
        alias_groups++; cands_in_alias += ng;
        int ldiff = 0, has_top = 0, has_nontop = 0;
        for (int q = 0; q < ng; q++){
          if (fabs(rs->util[grp[q]] - rs->util[a]) > 1e-9) ldiff = 1;
          if (rs->util[grp[q]] >= mx - 1e-9) has_top = 1; else has_nontop = 1;
        }
        if (ldiff) label_diff++;
        if (has_top && has_nontop){ opt_disjoint++; top_aliases++; }
      }
    }
  }
  printf("ALIAS-CENSUS states=%ld alias_groups=%ld cands_in_alias=%ld label_diff=%ld top_mixed=%ld\n",
         states, alias_groups, cands_in_alias, label_diff, top_aliases);
  printf("ALIAS-RATES group_rate=%.4f label_diff_rate=%.4f top_mixed_rate=%.4f\n",
         states ? (double)alias_groups/(double)states : 0,
         alias_groups ? (double)label_diff/(double)alias_groups : 0,
         alias_groups ? (double)top_aliases/(double)alias_groups : 0);
  return 0;
}
