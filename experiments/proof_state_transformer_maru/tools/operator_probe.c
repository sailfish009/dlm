/* operator_probe.c — AND/OR operator approximation on probabilistic valuations.
 * Compares hard min/max with softmin/softmax attention (ANDRE Eq.7-9), product
 * t-norm and arithmetic mean. Reports mean absolute error and the gradient
 * magnitude at the input (a proxy for vanishing gradients). */
#include <stdio.h>
#include <math.h>
#include <stdlib.h>

static unsigned long long st = 88172645463325252ULL;
static double urand(void){ st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (double)(st >> 11) / 9007199254740992.0; }

int main(int argc, char **argv){
  int m = (argc > 1) ? atoi(argv[1]) : 4;
  int n = (argc > 2) ? atoi(argv[2]) : 20000;
  double beta = (argc > 3) ? atof(argv[3]) : 16.0;
  double e_min = 0, e_prod = 0, e_mean = 0, g_soft = 0, g_prod = 0;
  double e_max = 0, e_sprod = 0, e_smean = 0, g_smax = 0, g_sprod = 0;
  for (int t = 0; t < n; t++){
    double b[16], mn = 1e9, mx = -1e9, prod = 1, sp = 1, sum = 0;
    for (int i = 0; i < m; i++){
      /* graded valuations: mixture of confident and weak premises */
      b[i] = (urand() < 0.5) ? 0.05 + 0.20*urand() : 0.60 + 0.40*urand();
      if (b[i] < mn) mn = b[i];
      if (b[i] > mx) mx = b[i];
      prod *= b[i]; sp *= (1.0 - b[i]); sum += b[i];
    }
    /* softmin attention (conjunction) */
    double z = 0, smin = 0;
    for (int i = 0; i < m; i++){ double e = exp(-beta*b[i]); z += e; }
    double wsum = 0;
    for (int i = 0; i < m; i++){ double w = exp(-beta*b[i])/z; smin += w*b[i]; wsum += w*w; }
    /* softmax attention (disjunction) */
    z = 0;
    double smax = 0;
    for (int i = 0; i < m; i++) z += exp(beta*b[i]);
    for (int i = 0; i < m; i++){ double w = exp(beta*b[i])/z; smax += w*b[i]; }
    e_min  += fabs(smin - mn);
    e_prod += fabs(prod - mn);
    e_mean += fabs(sum/(double)m - mn);
    e_max  += fabs(smax - mx);
    e_sprod+= fabs((1.0 - sp) - mx);
    e_smean+= fabs(sum/(double)m - mx);
    /* gradient magnitudes (d(operator)/d(b_i)) */
    g_soft += fabs(beta*(smin - mn));      /* softmin has a non-zero spread term */
    g_prod += fabs(prod/mn);               /* product derivative scale */
    g_smax += fabs(beta*(mx - smax));
    g_sprod+= fabs(sp);
  }
  printf("OPERATOR m=%d n=%d beta=%.1f\n", m, n, beta);
  printf("AND  mean_abs_err: hard_min=0 softmin=%.5f product=%.5f mean=%.5f\n", e_min/n, e_prod/n, e_mean/n);
  printf("OR   mean_abs_err: hard_max=0 softmax=%.5f product_snorm=%.5f mean=%.5f\n", e_max/n, e_sprod/n, e_smean/n);
  printf("GRAD mean|d/db|: softmin=%.4f product=%.4f softmax=%.4f product_snorm=%.4f\n",
         g_soft/n, g_prod/n, g_smax/n, g_sprod/n);
  return 0;
}
