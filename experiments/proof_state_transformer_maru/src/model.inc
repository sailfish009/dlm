/* ---------------- stage 2: native proof-state set transformer ----------------
 * Set transformer over [state token] + [candidate tokens]:
 *   h0 = Ws*state + bs + t_state ;  hj = Wc*cf_j + bc + t_cand
 *   NL pre-LN blocks: h += MHA(LN(h)); h += FFN(LN(h))
 *   score_j = Wout . LN_f(h_j)   (VAR_UTILHEAD: composed kernel-utility head)
 * Loss: listwise softmax CE on utility/temp + top-1 pairwise softplus.
 * Variants (compile-time):
 *   VAR_UTILHEAD  score = 5*softplus(goal) + 0.15*softplus(new) - cost
 *   VAR_MASK      kernel validity mask (support>0) at scoring time
 *   VAR_GOALX     candidate queries attend only to the state token
 *   VAR_LOOP      weight-tied second pass over the same blocks
 *   VAR_BIND      learned attention bias from shared predicate roles
 * Training: AdamW, grad-norm clip, val-based checkpoint selection.
 * No Python, no torch, deterministic (xorshift), LLVM O0/O2/O3 identical.
 */
#ifndef VAR_UTILHEAD
#define VAR_UTILHEAD 0
#endif
#ifndef VAR_MASK
#define VAR_MASK 0
#endif
#ifndef VAR_GOALX
#define VAR_GOALX 0
#endif
#ifndef VAR_LOOP
#define VAR_LOOP 0
#endif
#ifndef VAR_BIND
#define VAR_BIND 0
#endif
#ifndef VNAME
#define VNAME "base"
#endif
#ifndef MD
#define MD 32
#endif
#ifndef MFF
#define MFF 64
#endif
#ifndef MNH
#define MNH 4
#endif
#ifndef MNL
#define MNL 2
#endif

#define D MD
#define FE MFF
#define NH MNH
#define NL MNL
#define DH (D/NH)
#define MAXL (1+POOL)
#define NOUT (VAR_UTILHEAD ? 2 : 1)
#define NPASS (VAR_LOOP ? 2 : 1)
#define NBLK (NL*NPASS)
#define LN_EPS 1e-5
#define TEMP 0.8
#define PAIRW 0.5
#define LR 0.001
#define WD 1e-4
#define BETA1 0.9
#define BETA2 0.999
#define ADAM_EPS 1e-8

typedef struct {
  double Ws[D*STATE_DIM], bs[D];
  double Wc[D*CAND_DIM], bc[D];
  double ts[D], tc[D];
  double Wqkv[NL][3*D*D], bqkv[NL][3*D];
  double Wo[NL][D*D], bo[NL][D];
  double g1[NL][D], be1[NL][D];
  double W1[NL][FE*D], b1[NL][FE];
  double W2[NL][D*FE], b2[NL][D];
  double g2[NL][D], be2[NL][D];
  double gam[NL];
  double gf[D], bef[D];
  double Wout[NOUT*D], bout[NOUT];
} Params;

typedef struct {
  double in[MAXL][D];
  double ln1[MAXL][D];
  double qkv[MAXL][3*D];
  double att[NH][MAXL][MAXL];
  double ao[MAXL][D];
  double h1[MAXL][D];
  double ln2[MAXL][D];
  double pre[MAXL][FE];
  double act[MAXL][FE];
} LayerCache;

typedef struct {
  int L, nlive;
  int msk[POOL];
  double h[MAXL][D];
  double bias[MAXL][MAXL];
  LayerCache lc[NBLK];
  double lnf[MAXL][D];
  double raw[MAXL][NOUT];
  double score[POOL];
  double cost[POOL];
} Cache;

static Params *g_p, *g_g, *g_m, *g_v;
static Cache *g_c;
static double g_dh[MAXL][D];

static double xr(void){
  uint64_t x = mix64(rng_state);
  rng_state = x;
  return ((double)(x >> 11) / 9007199254740992.0) * 2.0 - 1.0;
}
static void init_params(Params *p, uint64_t seed){
  rng_state = mix64(seed*0x9E3779B97F4A7C15ULL + 0x1234567ULL);
  if (rng_state == 0) rng_state = 1;
  double s;
  s = 1.0/sqrt((double)STATE_DIM);
  for (int i = 0; i < D*STATE_DIM; i++) p->Ws[i] = xr()*s;
  for (int i = 0; i < D; i++){ p->bs[i] = 0; p->ts[i] = 0; p->tc[i] = 0; }
  s = 1.0/sqrt((double)CAND_DIM);
  for (int i = 0; i < D*CAND_DIM; i++) p->Wc[i] = xr()*s;
  for (int i = 0; i < D; i++) p->bc[i] = 0;
  for (int l = 0; l < NL; l++){
    s = 1.0/sqrt((double)D);
    for (int i = 0; i < 3*D*D; i++) p->Wqkv[l][i] = xr()*s;
    for (int i = 0; i < 3*D; i++) p->bqkv[l][i] = 0;
    for (int i = 0; i < D*D; i++) p->Wo[l][i] = xr()*s;
    for (int i = 0; i < D; i++){ p->bo[l][i] = 0; p->g1[l][i] = 1.0; p->be1[l][i] = 0; }
    for (int i = 0; i < FE*D; i++) p->W1[l][i] = xr()*s;
    for (int i = 0; i < FE; i++) p->b1[l][i] = 0;
    s = 1.0/sqrt((double)FE);
    for (int i = 0; i < D*FE; i++) p->W2[l][i] = xr()*s;
    for (int i = 0; i < D; i++){ p->b2[l][i] = 0; p->g2[l][i] = 1.0; p->be2[l][i] = 0; }
    p->gam[l] = 0.1;
  }
  for (int i = 0; i < D; i++){ p->gf[i] = 1.0; p->bef[i] = 0; }
  s = 1.0/sqrt((double)D);
  for (int i = 0; i < NOUT*D; i++) p->Wout[i] = xr()*s;
  for (int i = 0; i < NOUT; i++) p->bout[i] = 0;
}

static long param_count(void){ return (long)(sizeof(Params)/sizeof(double)); }
static double *pv(Params *p){ return (double*)p; }

/* ---- primitives ---- */
static void layer_norm_fwd(const double *x, const double *g, const double *b,
                           double *y, double *xhat, double *inv_out){
  double mu = 0;
  for (int i = 0; i < D; i++) mu += x[i];
  mu /= D;
  double var = 0;
  for (int i = 0; i < D; i++){ double d = x[i]-mu; var += d*d; }
  var /= D;
  double inv = 1.0/sqrt(var + LN_EPS);
  *inv_out = inv;
  for (int i = 0; i < D; i++){
    xhat[i] = (x[i]-mu)*inv;
    y[i] = xhat[i]*g[i] + b[i];
  }
}
static void layer_norm_bwd(const double *dy, const double *xhat, double inv,
                           const double *g, double *dx, double *dg, double *db){
  double sum1 = 0, sum2 = 0;
  for (int i = 0; i < D; i++){
    double dxh = dy[i]*g[i];
    dg[i] += dy[i]*xhat[i];
    db[i] += dy[i];
    sum1 += dxh;
    sum2 += dxh*xhat[i];
  }
  for (int i = 0; i < D; i++){
    double dxh = dy[i]*g[i];
    dx[i] += inv*(dxh - sum1/D - xhat[i]*sum2/D);
  }
}
static double gelu(double x){
  double u = 0.7978845608028654*(x + 0.044715*x*x*x);
  double t = tanh(u);
  return 0.5*x*(1.0+t);
}
static double gelu_d(double x){
  double u = 0.7978845608028654*(x + 0.044715*x*x*x);
  double t = tanh(u);
  double du = 0.7978845608028654*(1.0 + 3.0*0.044715*x*x);
  return 0.5*(1.0+t) + 0.5*x*(1.0 - t*t)*du;
}
static double softplus(double x){ return x > 30.0 ? x : log1p(exp(x)); }
static double sigmoid(double x){ return x >= 0 ? 1.0/(1.0+exp(-x)) : exp(x)/(1.0+exp(x)); }

/* shared-predicate role overlap, used by VAR_BIND as an attention bias value */
static double pred_shared(const double *fa, const double *fb){
  int ah = -1, bh = -1, ab[2] = {-1,-1}, bb[2] = {-1,-1};
  for (int p = 0; p < P; p++){
    if (fa[8+p] > 0.5) ah = p;
    if (fb[8+p] > 0.5) bh = p;
    if (fa[8+P+p] > 0.5) ab[0] = p;
    if (fa[8+P+P+p] > 0.5) ab[1] = p;
    if (fb[8+P+p] > 0.5) bb[0] = p;
    if (fb[8+P+P+p] > 0.5) bb[1] = p;
  }
  if (ah >= 0 && ah == bh) return 1.0;
  for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++)
    if (ab[i] >= 0 && ab[i] == bb[j]) return 3.0;
  if ((ah >= 0 && (ah == bb[0] || ah == bb[1])) ||
      (bh >= 0 && (bh == ab[0] || bh == ab[1]))) return 2.0;
  return 0.0;
}

/* ---- forward ---- */
static void model_forward(const Params *p, const double *state,
                          const double (*cf)[CAND_DIM], int nlive, Cache *c){
  c->L = 1 + nlive;
  c->nlive = nlive;
  for (int j = 0; j < nlive; j++){
    c->msk[j] = (VAR_MASK && cf[j][6] < 0.5) ? 0 : 1;
    c->cost[j] = 2.0*cf[j][1];
  }
  if (VAR_MASK){
    int m = 0;
    for (int j = 0; j < nlive; j++) m += c->msk[j];
    if (m == 0) for (int j = 0; j < nlive; j++) c->msk[j] = 1;
  }
  for (int i = 0; i < D; i++){
    double s = p->bs[i] + p->ts[i];
    for (int k = 0; k < STATE_DIM; k++) s += p->Ws[i*STATE_DIM+k]*state[k];
    c->h[0][i] = s;
  }
  for (int j = 0; j < nlive; j++)
    for (int i = 0; i < D; i++){
      double s = p->bc[i] + p->tc[i];
      for (int k = 0; k < CAND_DIM; k++) s += p->Wc[i*CAND_DIM+k]*cf[j][k];
      c->h[1+j][i] = s;
    }
  for (int i = 0; i < c->L; i++)
    for (int j = 0; j < c->L; j++) c->bias[i][j] = 0;
  if (VAR_BIND)
    for (int i = 0; i < nlive; i++)
      for (int j = 0; j < nlive; j++) c->bias[1+i][1+j] = pred_shared(cf[i], cf[j]);
  int L = c->L;
  for (int pass = 0; pass < NPASS; pass++){
    for (int l = 0; l < NL; l++){
      LayerCache *lc = &c->lc[pass*NL + l];
      for (int i = 0; i < L; i++) for (int d = 0; d < D; d++) lc->in[i][d] = c->h[i][d];
      for (int i = 0; i < L; i++){
        double xh[D], inv;
        layer_norm_fwd(lc->in[i], p->g1[l], p->be1[l], lc->ln1[i], xh, &inv);
      }
      for (int i = 0; i < L; i++)
        for (int r = 0; r < 3*D; r++){
          double s = p->bqkv[l][r];
          for (int d = 0; d < D; d++) s += p->Wqkv[l][r*D+d]*lc->ln1[i][d];
          lc->qkv[i][r] = s;
        }
      double scale = 1.0/sqrt((double)DH);
      for (int hh = 0; hh < NH; hh++){
        for (int i = 0; i < L; i++){
          double sc[MAXL], mx = -1e30;
          for (int j = 0; j < L; j++){
            if (VAR_GOALX && i > 0 && j > 0){ sc[j] = -1e30; continue; }
            double s = 0;
            for (int d = 0; d < DH; d++)
              s += lc->qkv[i][hh*DH+d]*lc->qkv[j][D+hh*DH+d];
            s *= scale;
            if (VAR_BIND) s += p->gam[l]*c->bias[i][j];
            sc[j] = s;
            if (s > mx) mx = s;
          }
          double sum = 0;
          for (int j = 0; j < L; j++){
            double e = (sc[j] <= -1e29) ? 0.0 : exp(sc[j]-mx);
            lc->att[hh][i][j] = e;
            sum += e;
          }
          for (int j = 0; j < L; j++) lc->att[hh][i][j] /= sum;
        }
        for (int i = 0; i < L; i++)
          for (int d = 0; d < DH; d++){
            double s = 0;
            for (int j = 0; j < L; j++) s += lc->att[hh][i][j]*lc->qkv[j][2*D+hh*DH+d];
            lc->ao[i][hh*DH+d] = s;
          }
      }
      for (int i = 0; i < L; i++)
        for (int d = 0; d < D; d++){
          double s = p->bo[l][d];
          for (int k = 0; k < D; k++) s += p->Wo[l][d*D+k]*lc->ao[i][k];
          lc->h1[i][d] = lc->in[i][d] + s;
        }
      for (int i = 0; i < L; i++){
        double xh[D], inv;
        layer_norm_fwd(lc->h1[i], p->g2[l], p->be2[l], lc->ln2[i], xh, &inv);
      }
      for (int i = 0; i < L; i++){
        for (int f = 0; f < FE; f++){
          double s = p->b1[l][f];
          for (int d = 0; d < D; d++) s += p->W1[l][f*D+d]*lc->ln2[i][d];
          lc->pre[i][f] = s;
          lc->act[i][f] = gelu(s);
        }
        for (int d = 0; d < D; d++){
          double s = p->b2[l][d];
          for (int f = 0; f < FE; f++) s += p->W2[l][d*FE+f]*lc->act[i][f];
          c->h[i][d] = lc->h1[i][d] + s;
        }
      }
    }
  }
  for (int i = 0; i < L; i++){
    double xh[D], inv;
    layer_norm_fwd(c->h[i], p->gf, p->bef, c->lnf[i], xh, &inv);
  }
  for (int j = 0; j < nlive; j++){
    for (int r = 0; r < NOUT; r++){
      double s = p->bout[r];
      for (int d = 0; d < D; d++) s += p->Wout[r*D+d]*c->lnf[1+j][d];
      c->raw[j][r] = s;
    }
#if VAR_UTILHEAD
    c->score[j] = 5.0*softplus(c->raw[j][0]) + 0.15*softplus(c->raw[j][1]) - c->cost[j];
#else
    c->score[j] = c->raw[j][0];
#endif
    if (!c->msk[j]) c->score[j] = -1e30;
  }
}

/* ---- loss + backward for one step ---- */
/* Shared scalar objective + score gradients. Both training and the
 * finite-difference checker call this one function, so the "mask" variant
 * cannot be checked against a different objective (0.0244 review F7). */
static double loss_from_cache(Cache *c, const double *util, int best, int nlive, double *ds){
  for (int j = 0; j < nlive; j++){
    if (VAR_MASK && !c->msk[j]) continue;
  }
  double mx = -1e30;
  for (int j = 0; j < nlive; j++) if (c->msk[j] && util[j]/TEMP > mx) mx = util[j]/TEMP;
  double zt = 0;
  for (int j = 0; j < nlive; j++) if (c->msk[j]) zt += exp(util[j]/TEMP - mx);
  double tgt[POOL], prob[POOL];
  double ms = -1e30;
  for (int j = 0; j < nlive; j++) if (c->msk[j] && c->score[j] > ms) ms = c->score[j];
  double zs = 0;
  for (int j = 0; j < nlive; j++) if (c->msk[j]) zs += exp(c->score[j] - ms);
  double loss = 0;
  for (int j = 0; j < nlive; j++){
    tgt[j] = c->msk[j] ? exp(util[j]/TEMP - mx)/zt : 0.0;
    prob[j] = c->msk[j] ? exp(c->score[j] - ms)/zs : 0.0;
    if (c->msk[j] && tgt[j] > 0) loss -= tgt[j]*log(prob[j] + 1e-30);
  }
  double pair = 0;
  int npair = 0;
  for (int j = 0; j < nlive; j++)
    if (c->msk[j] && j != best){ pair += softplus(c->score[j] - c->score[best]); npair++; }
  if (npair){ pair /= npair; loss += PAIRW*pair; }
  if (!ds) return loss;
  for (int j = 0; j < nlive; j++) ds[j] = c->msk[j] ? prob[j] - tgt[j] : 0.0;
  if (npair)
    for (int j = 0; j < nlive; j++){
      if (!(c->msk[j] && j != best)) continue;
      double gr = sigmoid(c->score[j] - c->score[best]) * PAIRW/npair;
      ds[j] += gr;
      ds[best] -= gr;
    }
  return loss;
}

static double model_step(const double *statev, const double (*cf)[CAND_DIM],
                         const int *util_target_best, int best,
                         const double *util, int nlive){
  Cache *c = g_c;
  model_forward(g_p, statev, cf, nlive, c);
  double ds[POOL];
  double loss = loss_from_cache(c, util, best, nlive, ds);
  (void)util_target_best;

  Params *g = g_g;
  static double dlnf[MAXL][D];
  for (int i = 0; i <= nlive; i++) for (int d = 0; d < D; d++) dlnf[i][d] = 0;
  for (int j = 0; j < nlive; j++){
    if (!c->msk[j] && ds[j] == 0.0) continue;
#if VAR_UTILHEAD
    {
      double dgr = ds[j]*5.0*sigmoid(c->raw[j][0]);
      double dnr = ds[j]*0.15*sigmoid(c->raw[j][1]);
      for (int d = 0; d < D; d++){
        g->Wout[0*D+d] += dgr*c->lnf[1+j][d];
        g->Wout[1*D+d] += dnr*c->lnf[1+j][d];
        dlnf[1+j][d] += dgr*g_p->Wout[0*D+d] + dnr*g_p->Wout[1*D+d];
      }
      g->bout[0] += dgr;
      g->bout[1] += dnr;
    }
#else
    {
      for (int d = 0; d < D; d++){
        g->Wout[d] += ds[j]*c->lnf[1+j][d];
        dlnf[1+j][d] += ds[j]*g_p->Wout[d];
      }
      g->bout[0] += ds[j];
    }
#endif
  }
  for (int i = 0; i <= nlive; i++) for (int d = 0; d < D; d++) g_dh[i][d] = 0;
  for (int i = 1; i <= nlive; i++){
    double xh[D], inv, dx[D];
    layer_norm_fwd(c->h[i], g_p->gf, g_p->bef, c->lnf[i], xh, &inv);
    for (int d = 0; d < D; d++) dx[d] = 0;
    layer_norm_bwd(dlnf[i], xh, inv, g_p->gf, dx, g->gf, g->bef);
    for (int d = 0; d < D; d++) g_dh[i][d] += dx[d];
  }
  static double dout[MAXL][D], dh1[MAXL][D], dln2[MAXL][D], din[MAXL][D];
  static double dpre[MAXL][FE], dact[MAXL][FE], dao[MAXL][D], dqkv[MAXL][3*D];
  static double datt[MAXL][MAXL];
  int L = c->L;
  for (int pass = NPASS-1; pass >= 0; pass--){
    for (int l = NL-1; l >= 0; l--){
      LayerCache *lc = &c->lc[pass*NL + l];
      for (int i = 0; i < L; i++){
        for (int d = 0; d < D; d++){ dout[i][d] = g_dh[i][d]; dao[i][d] = 0; }
        for (int f = 0; f < FE; f++) dact[i][f] = 0;
        for (int d = 0; d < D; d++){ dh1[i][d] = dout[i][d]; dln2[i][d] = 0; din[i][d] = 0; }
        for (int r = 0; r < 3*D; r++) dqkv[i][r] = 0;
      }
      /* FFN backward */
      for (int i = 0; i < L; i++){
        for (int f = 0; f < FE; f++){
          double s = 0;
          for (int d = 0; d < D; d++) s += g_p->W2[l][d*FE+f]*dout[i][d];
          dact[i][f] = s;
          dpre[i][f] = s*gelu_d(lc->pre[i][f]);
        }
        for (int d = 0; d < D; d++) g->b2[l][d] += dout[i][d];
        for (int d = 0; d < D; d++)
          for (int f = 0; f < FE; f++) g->W2[l][d*FE+f] += dout[i][d]*lc->act[i][f];
        for (int f = 0; f < FE; f++){
          g->b1[l][f] += dpre[i][f];
          for (int d = 0; d < D; d++) g->W1[l][f*D+d] += dpre[i][f]*lc->ln2[i][d];
        }
        for (int d = 0; d < D; d++){
          double s = 0;
          for (int f = 0; f < FE; f++) s += g_p->W1[l][f*D+d]*dpre[i][f];
          dln2[i][d] = s;
        }
      }
      /* LN2 backward */
      for (int i = 0; i < L; i++){
        double xh[D], inv, dx[D];
        layer_norm_fwd(lc->h1[i], g_p->g2[l], g_p->be2[l], lc->ln2[i], xh, &inv);
        for (int d = 0; d < D; d++) dx[d] = 0;
        layer_norm_bwd(dln2[i], xh, inv, g_p->g2[l], dx, g->g2[l], g->be2[l]);
        for (int d = 0; d < D; d++) dh1[i][d] += dx[d];
      }
      /* attention out projection backward */
      for (int i = 0; i < L; i++){
        for (int d = 0; d < D; d++) g->bo[l][d] += dh1[i][d];
        for (int d = 0; d < D; d++)
          for (int k = 0; k < D; k++) g->Wo[l][d*D+k] += dh1[i][d]*lc->ao[i][k];
        for (int k = 0; k < D; k++){
          double s = 0;
          for (int d = 0; d < D; d++) s += g_p->Wo[l][d*D+k]*dh1[i][d];
          dao[i][k] = s;
        }
      }
      double scale = 1.0/sqrt((double)DH);
      double dgam = 0;
      for (int hh = 0; hh < NH; hh++){
        for (int i = 0; i < L; i++)
          for (int j = 0; j < L; j++) datt[i][j] = 0;
        for (int i = 0; i < L; i++)
          for (int j = 0; j < L; j++){
            double a = lc->att[hh][i][j];
            if (a == 0.0) continue;
            for (int d = 0; d < DH; d++){
              datt[i][j] += dao[i][hh*DH+d]*lc->qkv[j][2*D+hh*DH+d];
              dqkv[j][2*D+hh*DH+d] += a*dao[i][hh*DH+d];
            }
          }
        for (int i = 0; i < L; i++){
          double sdot = 0;
          for (int j = 0; j < L; j++) sdot += lc->att[hh][i][j]*datt[i][j];
          for (int j = 0; j < L; j++){
            double dsij = lc->att[hh][i][j]*(datt[i][j] - sdot);
            if (dsij == 0.0) continue;
            if (VAR_BIND) dgam += c->bias[i][j]*dsij;
            for (int d = 0; d < DH; d++){
              dqkv[i][hh*DH+d] += dsij*scale*lc->qkv[j][D+hh*DH+d];
              dqkv[j][D+hh*DH+d] += dsij*scale*lc->qkv[i][hh*DH+d];
            }
          }
        }
      }
      if (VAR_BIND) g->gam[l] += dgam;
      /* qkv projection + LN1 backward */
      for (int i = 0; i < L; i++){
        for (int r = 0; r < 3*D; r++){
          g->bqkv[l][r] += dqkv[i][r];
          for (int d = 0; d < D; d++) g->Wqkv[l][r*D+d] += dqkv[i][r]*lc->ln1[i][d];
        }
        double dln1[D], dx[D], xh[D], inv;
        for (int d = 0; d < D; d++){
          double s = 0;
          for (int r = 0; r < 3*D; r++) s += g_p->Wqkv[l][r*D+d]*dqkv[i][r];
          dln1[d] = s;
          dx[d] = 0;
        }
        layer_norm_fwd(lc->in[i], g_p->g1[l], g_p->be1[l], lc->ln1[i], xh, &inv);
        layer_norm_bwd(dln1, xh, inv, g_p->g1[l], dx, g->g1[l], g->be1[l]);
        for (int d = 0; d < D; d++) din[i][d] = dh1[i][d] + dx[d];
      }
      for (int i = 0; i < L; i++) for (int d = 0; d < D; d++) g_dh[i][d] = din[i][d];
    }
  }
  /* embedding backward */
  for (int d = 0; d < D; d++){
    g->bs[d] += g_dh[0][d];
    g->ts[d] += g_dh[0][d];
    for (int k = 0; k < STATE_DIM; k++) g->Ws[d*STATE_DIM+k] += g_dh[0][d]*statev[k];
  }
  for (int j = 0; j < nlive; j++)
    for (int d = 0; d < D; d++){
      g->bc[d] += g_dh[1+j][d];
      g->tc[d] += g_dh[1+j][d];
      for (int k = 0; k < CAND_DIM; k++) g->Wc[d*CAND_DIM+k] += g_dh[1+j][d]*cf[j][k];
    }
  return loss;
}