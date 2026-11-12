/* dt_selector_c.c — feasibility probe: DT-1 selector hot path in Q16 C.
 * Data/weights are generated from the v0.0204 Maru/PyTorch DT fixture.
 * This is an untrusted scoring kernel; the proof gate stays in Maru. */
#include "fixture.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define D 32
#define MAXTOK 32

static inline long fx_mul(long a, long b) { return (a * b) >> 16; }
static inline long fx_div(long a, long b) { return b ? (a * Q16) / b : 0; }

static long fx_isqrt_search(long lo, long hi, long n) {
  while (hi - lo > 1) { long mid = (lo + hi) / 2; if (mid * mid <= n) lo = mid; else hi = mid; }
  return lo;
}
static long fx_isqrt(long n) {
  if (n <= 0) return 0;
  long hi = 1;
  while (hi * hi <= n) hi *= 2;
  return fx_isqrt_search(0, hi, n);
}
static long fx_sqrt(long x) { return x <= 0 ? 0 : fx_isqrt(x * Q16); }
static long fx_exp(long x) {
  if (x >= 0) return Q16;
  long t = (-x) * 32;
  long i = t >> 16;
  long frac = t - (i << 16);
  if (i >= 512) return 0;
  long y0 = exp_table[i], y1 = exp_table[i+1];
  return y0 + fx_mul(y1 - y0, frac);
}

static long v_dot(const long *a, const long *b, int n) {
  long s = 0; for (int i=0;i<n;i++) s += fx_mul(a[i],b[i]); return s;
}
static void v_addto(const long *a, const long *b, long *out, int n) {
  for (int i=0;i<n;i++) out[i] = a[i] + b[i];
}
static void matvec(const long *w, int rows, int cols, const long *x, const long *b, long *out) {
  for (int r=0;r<rows;r++) {
    long s = 0;
    for (int c=0;c<cols;c++) s += fx_mul(w[r*cols+c], x[c]);
    out[r] = s + b[r];
  }
}
static void project(const long toks[MAXTOK][D], int nt, const long *w, int rows,
                    const long *b, long out[MAXTOK][D]) {
  for (int t=0;t<nt;t++) matvec(w, rows, D, toks[t], b, out[t]);
}
static void layernorm(const long *x, const long *g, const long *b, long *out) {
  long sum=0; for (int i=0;i<D;i++) sum += x[i];
  long mu = sum / D;
  long var=0; for (int i=0;i<D;i++) { long d=x[i]-mu; var += fx_mul(d,d); }
  var /= D;
  long inv = fx_div(Q16, fx_sqrt(var + 1));
  for (int i=0;i<D;i++) out[i] = fx_mul(fx_mul(x[i]-mu, inv), g[i]) + b[i];
}
static void softmax(const long *s, int n, long *out) {
  long m=s[0]; for (int i=1;i<n;i++) if (s[i]>m) m=s[i];
  long e[MAXTOK]; long z=0;
  for (int i=0;i<n;i++) { e[i]=fx_exp(s[i]-m); z+=e[i]; }
  for (int i=0;i<n;i++) out[i] = z ? (e[i]*Q16)/z : 0;
}
static void mha(long toks[MAXTOK][D], int nt, const long *inw, const long *inb,
                const long *ow, const long *ob, long out[MAXTOK][D]) {
  long q[MAXTOK][D], k[MAXTOK][D], v[MAXTOK][D], a[MAXTOK][D], z[MAXTOK][D];
  for (int t=0;t<nt;t++) {
    matvec(inw + 0*D, D, D, toks[t], inb + 0*D, q[t]);
    matvec(inw + 32*D, D, D, toks[t], inb + 32*D, k[t]);
    matvec(inw + 64*D, D, D, toks[t], inb + 64*D, v[t]);
  }
  for (int i=0;i<nt;i++) {
    long sc[MAXTOK], w[MAXTOK];
    for (int j=0;j<nt;j++) sc[j] = fx_div(v_dot(q[i],k[j],D), 370728);
    softmax(sc, nt, w);
    for (int d=0;d<D;d++) { long s=0; for (int j=0;j<nt;j++) s += fx_mul(v[j][d], w[j]); a[i][d]=s; }
  }
  project(a, nt, ow, D, ob, z);
  memcpy(out, z, sizeof(long)*D*nt);
}
static void block(long toks[MAXTOK][D], int nt, const long *inw, const long *inb,
                  const long *ow, const long *ob, const long *l1w, const long *l1b,
                  const long *l2w, const long *l2b, const long *n1g, const long *n1b,
                  const long *n2g, const long *n2b) {
  long a[MAXTOK][D], x1[MAXTOK][D], f1[MAXTOK][64], f2[MAXTOK][D], x2[MAXTOK][D];
  mha(toks, nt, inw, inb, ow, ob, a);
  for (int t=0;t<nt;t++) {
    long s[D]; v_addto(toks[t], a[t], s, D);
    layernorm(s, n1g, n1b, x1[t]);
    matvec(l1w, 64, D, x1[t], l1b, f1[t]);
    for (int i=0;i<64;i++) if (f1[t][i] < 0) f1[t][i] = 0;
    long f2v[D]; matvec(l2w, D, 64, f1[t], l2b, f2v);
    long s2[D]; v_addto(x1[t], f2v, s2, D);
    layernorm(s2, n2g, n2b, x2[t]);
  }
  memcpy(toks, x2, sizeof(long)*D*nt);
}

static int body_ok(const long *bits, const long *codes, int len) {
  for (int i=0;i<len;i++) {
    long c=codes[i];
    int idx = c>0 ? (int)(c-1) : (int)(-c-1);
    int want = c>0 ? 1 : 0;
    if (bits[idx] != want) return 0;
  }
  return 1;
}
static void rule_features(const long *bits, int k, long *f) {
  const long *codes=rule_bodies[k]; int n=rule_lengths[k];
  int on=0, off=0; long si=0; long sat=0;
  for (int i=0;i<n;i++) {
    long c=codes[i];
    if (c>0) on++; else off++;
    si += c>0 ? c-1 : -c-1;
    if (body_ok(bits, &codes[i], 1)) sat += Q16;
  }
  for (int i=0;i<10;i++) f[i] = (i==rule_heads[k]) ? Q16 : 0;
  f[10] = fx_div(n>30?30:n, 30);
  f[11] = fx_div(on, n);
  f[12] = fx_div(off, n);
  f[13] = fx_div(si, 196*n);
  f[14] = sat / n;
  f[15] = Q16 - f[14];
}

static void knn(const long *bits, long *topd, long *toplab, int *topn) {
  for (int p=0;p<POOL_COUNT;p++) {
    long d=0;
    for (int i=0;i<196;i++) { long x=bits[i]-pool_bits[p][i]; d += x*x; }
    /* insert into ascending top 5 */
    int pos=*topn;
    for (int j=0;j<*topn;j++) if (d <= topd[j]) { pos=j; break; }
    if (pos < 5) {
      int lim = *topn < 5 ? *topn : 4;
      for (int j=lim;j>pos;j--) { topd[j]=topd[j-1]; toplab[j]=toplab[j-1]; }
      topd[pos]=d; toplab[pos]=pool_labels[p];
      if (*topn<5) (*topn)++;
    }
  }
}

int main(void) {
  long bits[196]; for (int i=0;i<196;i++) bits[i]=case_bits[i];
  int valid[RULE_COUNT], nv=0;
  for (int k=0;k<RULE_COUNT;k++) if (body_ok(bits, rule_bodies[k], rule_lengths[k])) valid[nv++]=k;
  printf("CASE 0 VALID");
  for (int i=0;i<nv;i++) printf(" %d", valid[i]);
  printf("\n");

  long toks[MAXTOK][D]; int nt=1;
  for (int i=0;i<196;i++) toks[0][i] = 0; /* not used as image token */
  long img[196]; for (int i=0;i<196;i++) img[i]=case_bits[i]*Q16;
  matvec((const long*)img_w, D, 196, img, (const long*)img_b, toks[0]);
  for (int vi=0;vi<nv;vi++) {
    int k=valid[vi]; long feat[16]; rule_features(bits,k,feat);
    for (int i=0;i<D;i++) toks[1+vi][i]=0;
    matvec((const long*)rule_w, D, 16, feat, (const long*)rule_b, toks[1+vi]);
    nt++;
  }
  for (int b=0;b<6;b++)
    block(toks, nt, (const long*)in_w, (const long*)in_b, (const long*)out_w, (const long*)out_b,
          (const long*)l1_w, (const long*)l1_b, (const long*)l2_w, (const long*)l2_b,
          (const long*)n1g, (const long*)n1b, (const long*)n2g, (const long*)n2b);
  long sel[RULE_COUNT];
  for (int vi=0;vi<nv;vi++) sel[vi] = v_dot((const long*)final_w, toks[1+vi], D) + final_b[0];

  long topd[5], toplab[5]; int topn=0; knn(bits,topd,toplab,&topn);
  long counts[10]={0};
  for (int i=0;i<topn;i++) counts[toplab[i]]++;
  long best=-999999999; int bestk=-1;
  printf("C-SELECTOR");
  for (int vi=0;vi<nv;vi++) {
    int k=valid[vi]; long prior=prior_log[counts[rule_heads[k]]];
    long sc=sel[vi] + 4*prior;
    printf(" %.9f", (double)sel[vi]/(double)Q16);
    if (sc>best) { best=sc; bestk=k; }
  }
  printf("\nC-SCORE");
  for (int vi=0;vi<nv;vi++) {
    int k=valid[vi]; long prior=prior_log[counts[rule_heads[k]]];
    printf(" %.9f", (double)(sel[vi]+4*prior)/(double)Q16);
  }
  printf("\nC-PICK %d\n", bestk);
  return 0;
}
