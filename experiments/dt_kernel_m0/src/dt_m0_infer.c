/* M0: DT-1 inference at the real selector dimensions through the
 * array-view ABI. Integer Q16 path: no floating-point arithmetic.
 * Arithmetic order is deliberately identical to reference/dt_full_infer.c. */
#include "../include/array_view.h"
#include "fixture_all.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define D 32
#define MAXTOK 64
#ifndef M0_LAYERS
#define M0_LAYERS 6
#endif
_Static_assert(MODEL_SIZE == 15425, "M0 MODEL_SIZE");
_Static_assert(OFF_FINAL_W == 15392, "M0 OFF_FINAL_W");
_Static_assert(OFF_IMG_B == 6272, "M0 OFF_IMG_B");
_Static_assert(D == 32, "M0 D");

#ifdef M0_TRACE
static int trace_case, trace_layer;
static uint64_t trace_hash(const long *p, long n) {
  uint64_t h = 1469598103934665603ULL;
  const uint8_t *b = (const uint8_t *)p;
  for (long i = 0; i < n * (long)sizeof(long); i++) { h ^= b[i]; h *= 1099511628211ULL; }
  return h;
}
#define TRACE(tag, ptr, n) printf("TRACE %d %s %d %016llx\n", trace_case, tag, trace_layer, (unsigned long long)trace_hash((ptr), (n)))
#else
#define TRACE(tag, ptr, n) ((void)0)
#endif

static inline long fm(long a, long b) { return (a * b) >> 16; }
static inline long fd(long a, long b) { return b ? (a * Q16) / b : 0; }
static long isq(long lo, long hi, long n) { while (hi - lo > 1) { long m = (lo + hi) / 2; if (m * m <= n) lo = m; else hi = m; } return lo; }
static long isqrt(long n) { if (n <= 0) return 0; long h = 1; while (h * h <= n) h *= 2; return isq(0, h, n); }
static long fsqrt(long x) { return x <= 0 ? 0 : isqrt(x * Q16); }
static long fexp(long x) {
  if (x >= 0) return Q16;
  long t = (-x) * 32;
  long i = t >> 16;
  long fr = t - (i << 16);
  if (i >= 512) return 0;
  long y0 = exp_table[i], y1 = exp_table[i + 1];
  return y0 + fm(y1 - y0, fr);
}

/* Array-view scalar accessors. */
static inline long av(const MaruArrayView *v, long i) { return (long)mav_get(v, i); }
static inline void sv(const MaruArrayView *v, long i, long x) {
  uint8_t *p = (uint8_t *)v->data + i * v->stride;
  for (long b = 0; b < v->elem_size; b++) p[b] = (uint8_t)((x >> (8 * b)) & 255);
}
static inline MaruArrayView view(const long *p, long n) {
  MaruArrayView v = { (const uint8_t *)p, n, (long)sizeof(long), (long)sizeof(long) };
  return v;
}

static long dotv(const long *a, const long *b, int n) {
  MaruArrayView A = view(a, n), B = view(b, n);
  long s = 0;
  for (int i = 0; i < n; i++) s += fm(av(&A, i), av(&B, i));
  return s;
}

static void mvv(const long *w, int rows, int cols, const long *x, const long *b, long *out) {
  MaruArrayView W = view(w, (long)rows * cols), X = view(x, cols), B = view(b, rows);
  for (int r = 0; r < rows; r++) {
    long s = 0;
    for (int c = 0; c < cols; c++) s += fm(av(&W, (long)r * cols + c), av(&X, c));
    out[r] = s + av(&B, r);
  }
}

static void projv(long toks[MAXTOK][D], int nt, const long *w, int rows, const long *b, long out[MAXTOK][D]) {
  for (int t = 0; t < nt; t++) mvv(w, rows, D, toks[t], b, out[t]);
}

static void lnv(const long *x, const long *g, const long *b, long *out) {
  MaruArrayView X = view(x, D), G = view(g, D), B = view(b, D), O = view(out, D);
  long mu = 0;
  for (int i = 0; i < D; i++) mu += av(&X, i);
  mu /= D;
  long v = 0;
  for (int i = 0; i < D; i++) { long d = av(&X, i) - mu; v += fm(d, d); }
  v /= D;
  long inv = fd(Q16, fsqrt(v + 1));
  for (int i = 0; i < D; i++) sv(&O, i, fm(fm(av(&X, i) - mu, inv), av(&G, i)) + av(&B, i));
}

static void softmaxv(const long *s, int n, long *out) {
  MaruArrayView S = view(s, n), O = view(out, n);
  long m = av(&S, 0);
  for (int i = 1; i < n; i++) if (av(&S, i) > m) m = av(&S, i);
  long e[MAXTOK], z = 0;
  for (int i = 0; i < n; i++) { e[i] = fexp(av(&S, i) - m); z += e[i]; }
  for (int i = 0; i < n; i++) sv(&O, i, z ? (e[i] * Q16) / z : 0);
}

static void mhav(long t[MAXTOK][D], int nt, const long *inw, const long *inb, const long *ow, const long *ob) {
  long q[MAXTOK][D], k[MAXTOK][D], v[MAXTOK][D], a[MAXTOK][D], z[MAXTOK][D];
  for (int i = 0; i < nt; i++) {
    mvv(inw, D, D, t[i], inb, q[i]);
    mvv(inw + 32 * D, D, D, t[i], inb + 32, k[i]);
    mvv(inw + 64 * D, D, D, t[i], inb + 64, v[i]);
  }
  for (int i = 0; i < nt; i++) {
    long sc[MAXTOK], w[MAXTOK];
    for (int j = 0; j < nt; j++) sc[j] = fd(dotv(q[i], k[j], D), 370728);
    softmaxv(sc, nt, w);
    for (int d = 0; d < D; d++) {
      long s = 0;
      for (int j = 0; j < nt; j++) s += fm(v[j][d], w[j]);
      a[i][d] = s;
    }
  }
  projv(a, nt, ow, D, ob, z);
  memcpy(t, z, sizeof(long) * D * nt);
}

static void blkv(long t[MAXTOK][D], int nt, const long *m) {
  const long *inw = m + OFF_IN_W, *inb = m + OFF_IN_B, *ow = m + OFF_OUT_W, *ob = m + OFF_OUT_B;
  const long *l1w = m + OFF_L1_W, *l1b = m + OFF_L1_B, *l2w = m + OFF_L2_W, *l2b = m + OFF_L2_B;
  const long *n1g = m + OFF_N1G, *n1b = m + OFF_N1B, *n2g = m + OFF_N2G, *n2b = m + OFF_N2B;
  long orig[MAXTOK][D], x1[MAXTOK][D], f1[MAXTOK][64];
  memcpy(orig, t, sizeof(long) * D * nt);
  mhav(t, nt, inw, inb, ow, ob);
  TRACE("ATTN", t[0], D);
  for (int i = 0; i < nt; i++) {
    long s[D];
    for (int d = 0; d < D; d++) s[d] = orig[i][d] + t[i][d];
    lnv(s, n1g, n1b, x1[i]);
    mvv(l1w, 64, D, x1[i], l1b, f1[i]);
    for (int j = 0; j < 64; j++) if (f1[i][j] < 0) f1[i][j] = 0;
    long g[D];
    mvv(l2w, D, 64, f1[i], l2b, g);
    for (int d = 0; d < D; d++) s[d] = x1[i][d] + g[d];
    lnv(s, n2g, n2b, t[i]);
    TRACE("FFN", t[0], D);
  }
}

static int body_ok(const long *b, const long *code, int n) {
  for (int i = 0; i < n; i++) {
    long c = code[i];
    int idx = c > 0 ? (int)(c - 1) : (int)(-c - 1);
    int want = c > 0 ? 1 : 0;
    if (b[idx] != want) return 0;
  }
  return 1;
}

static void feats(const long *bits, int k, long *f) {
  const long *codes = rule_bodies[k];
  int n = rule_lengths[k], on = 0, off = 0;
  long si = 0, sat = 0;
  for (int i = 0; i < n; i++) {
    long c = codes[i];
    if (c > 0) on++; else off++;
    si += c > 0 ? c - 1 : -c - 1;
    if (body_ok(bits, &codes[i], 1)) sat += Q16;
  }
  for (int i = 0; i < 10; i++) f[i] = (i == rule_heads[k]) ? Q16 : 0;
  f[10] = fd(n > 30 ? 30 : n, 30);
  f[11] = fd(on, n);
  f[12] = fd(off, n);
  f[13] = fd(si, 196 * n);
  f[14] = sat / n;
  f[15] = Q16 - f[14];
}

static void knn(const long *bits, long *td, long *tl, int *tn) {
  for (int p = 0; p < POOL_COUNT; p++) {
    long d = 0;
    for (int i = 0; i < 196; i++) { long x = bits[i] - pool_bits[p][i]; d += x * x; }
    int pos = *tn;
    for (int j = 0; j < *tn; j++) if (d <= td[j]) { pos = j; break; }
    if (pos < 5) {
      int lim = *tn < 5 ? *tn : 4;
      for (int j = lim; j > pos; j--) { td[j] = td[j - 1]; tl[j] = tl[j - 1]; }
      td[pos] = d; tl[pos] = pool_labels[p];
      if (*tn < 5) (*tn)++;
    }
  }
}

int main(void) {
  for (int c = 0; c < 10; c++) {
#ifdef M0_TRACE
    trace_case = c;
#endif
    const long *m = models[c];
    const long *bits = case_bits[c];
    int valid[RULE_COUNT], nv = 0;
    for (int k = 0; k < RULE_COUNT; k++) if (body_ok(bits, rule_bodies[k], rule_lengths[k])) valid[nv++] = k;
    long t[MAXTOK][D];
    int nt = 1;
    long img[196];
    for (int i = 0; i < 196; i++) img[i] = bits[i] * Q16;
    mvv(m + OFF_IMG_W, D, 196, img, m + OFF_IMG_B, t[0]);
    for (int vi = 0; vi < nv; vi++) {
      long f[16];
      feats(bits, valid[vi], f);
      mvv(m + OFF_RULE_W, D, 16, f, m + OFF_RULE_B, t[1 + vi]);
      nt++;
    }
    TRACE("PROJ0", t[0], D);
    TRACE("PROJ1", t[1], D);
    for (int b = 0; b < M0_LAYERS; b++) {
#ifdef M0_TRACE
      trace_layer = b;
#endif
      blkv(t, nt, m);
    }
    long sel[RULE_COUNT];
    for (int vi = 0; vi < nv; vi++) sel[vi] = dotv(m + OFF_FINAL_W, t[1 + vi], D) + m[OFF_FINAL_W + 32];
    TRACE("SEL", sel, nv);
    long td[5], tl[5];
    int tn = 0;
    knn(bits, td, tl, &tn);
    long cnt[10] = {0};
    for (int i = 0; i < tn; i++) cnt[tl[i]]++;
    long best = -999999999;
    int bk = -1;
    printf("RESULT %d VALID", c);
    for (int vi = 0; vi < nv; vi++) printf(" %d", valid[vi]);
    printf(" SEL");
    for (int vi = 0; vi < nv; vi++) printf(" %.9f", (double)sel[vi] / Q16);
    printf(" PICK ");
    for (int vi = 0; vi < nv; vi++) {
      int k = valid[vi];
      long sc = sel[vi] + 4 * prior_log[cnt[rule_heads[k]]];
      if (sc > best) { best = sc; bk = k; }
    }
    printf("%d HEAD %d\n", bk, bk >= 0 ? rule_heads[bk] : -1);
  }
  printf("DONE 10\n");
  return 0;
}
