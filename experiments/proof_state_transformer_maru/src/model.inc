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
#ifndef ATTMODE
#define ATTMODE 0        /* 0 = full softmax, k>=2 = top-k renormalised (branching layer) */
#endif
#ifndef SYMGATE
#define SYMGATE 0        /* 0 = off; 1 = soft: residual gate on inadmissible candidates;
                          * 2 = hard: inadmissible candidates removed from the choice set */
#endif
#ifndef CERT
#define CERT 0           /* 1 = independent proof-certificate check (Rocq kernel port) */
#endif
#ifndef FOCUS
#define FOCUS 0          /* 1 = obligation-directed candidate focus (Rocq tactic focus) */
#endif
#ifndef LEMMA
#define LEMMA 0          /* 1 = verified 2-rule lemma (contract) actions */
#endif
#ifndef PAIRMODE
#define PAIRMODE 0       /* 0 = off; 1 = mined contracts; 2 = learned proposer; 3 = random control */
#endif
#ifndef PHASEUNTIE
#define PHASEUNTIE 0     /* 1 = each VAR_LOOP pass has its own block parameters (Rocq tactic phases, untied) */
#endif
#ifndef BRANCHTOK
#define BRANCHTOK 0      /* B >= 2: B state registers (Screamer branching) instead of 1 */
#endif
#ifndef READMAX
#define READMAX 0        /* 1 = per-register output head, score = max over registers */
#endif
#ifndef REGSHUF
#define REGSHUF 0        /* 1 = control: registers share one bias and one readout head */
#endif
/* 0.0269 loop cell: the proof-state transition moves INSIDE the model. A latent
 * register z_t is carried across commits: tokens = [z_t, state_t, candidates_t],
 * and after the committed action a_t the cell updates z_{t+1} = GRU(z_t, emb(a_t)).
 * Training is episode-level BPTT over kernel-verified teacher rollouts; the kernel
 * still owns every label and every closure. PREDW adds a world-model auxiliary
 * loss: predict the next state's optimal DP value from (z_t, emb(a_t)) ALONE.
 * Controls: CELLDETACH cuts the recurrent gradient (untrained cell dynamics);
 * CELLSHUF feeds the cell a rotated action sequence (corrupted history content,
 * matched training); REMFEAT puts the remaining budget in the state features
 * (the identifiability gap the cell could otherwise be credited for closing). */
#ifndef LOOPCELL
#define LOOPCELL 0
#endif
#ifndef CELLDETACH
#define CELLDETACH 0     /* 1 = control: latent register is the STATIC z0 token at every
                          * step (no transition in forward or backward; cell params unused) */
#endif
#ifndef CELLSHUF
#define CELLSHUF 0
#endif
#ifndef PREDW
#define PREDW 0.0
#endif
#ifndef EPTRAIN
#define EPTRAIN 0        /* 1 = episode-batched training (protocol-matched baseline) */
#endif
#ifndef REMFEAT
#define REMFEAT 0        /* 1 = remaining-budget slot appended to the state features */
#endif
#if LOOPCELL && (BRANCHTOK >= 2 || READMAX)
#error "LOOPCELL requires a single state register (BRANCHTOK<2, READMAX=0)"
#endif
#if (CELLDETACH || CELLSHUF) && !LOOPCELL
#error "CELLDETACH/CELLSHUF require LOOPCELL"
#endif
#ifndef VALMODE
#define VALMODE 0        /* 0 = single-step utility; 1 = budget-exact DP value;
                          * 2 = same DP label multiset, shuffled across candidates;
                          * 3 = DP value + proof-cost tie-break (no cost term);
                          * 4 = VALMODE=3 with the correspondence shuffled (control) */
#endif
#ifndef LABEL_STEPS
#define LABEL_STEPS 0    /* 1 = add the min-derivation-length term (2x2 decomposition) */
#endif
#ifndef LABEL_NCOST
#define LABEL_NCOST 0    /* 1 = drop the rule-cost term (2x2 decomposition) */
#endif
/* census counters (kernel path condition / certificate / lemma), reset per run */
static long g_pc_tokens = 0, g_pc_dropped = 0, g_pc_fallback = 0, g_pc_picks = 0;
static long g_cert_ok = 0, g_cert_fail = 0, g_cert_checked = 0, g_cert_mutfail = 0;
static long g_lemma_uses = 0;
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
#define RB ((BRANCHTOK >= 2 || READMAX) ? 4 : 1)
#define NREG (BRANCHTOK >= 2 ? BRANCHTOK : 1)
#define ZTOK (LOOPCELL ? 1 : 0)
#define MAXL (RB+POOL+1)
#define NOUT (VAR_UTILHEAD ? 2 : 1)
#define NPASS (VAR_LOOP ? 2 : 1)
#define NBLK (NL*NPASS)                 /* cache blocks (pass-major) */
#define NBP (PHASEUNTIE ? NBLK : NL)    /* parameter blocks: untied phases add a full set */
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
  double Wqkv[NBP][3*D*D], bqkv[NBP][3*D];
  double Wo[NBP][D*D], bo[NBP][D];
  double g1[NBP][D], be1[NBP][D];
  double W1[NBP][FE*D], b1[NBP][FE];
  double W2[NBP][D*FE], b2[NBP][D];
  double g2[NBP][D], be2[NBP][D];
  double gam[NBP];
  double gf[D], bef[D];
  double Wout[NOUT*D], bout[NOUT];
  /* 0.0263 multi-register structure: per-register bias and (READMAX) per-register
   * readout head. RB is the compile-time register cap; only BRANCHTOK are used. */
  double Rbias[RB][D];
  double Wout_r[RB][NOUT*D], bout_r[RB][NOUT];
  /* 0.0269 loop cell (present in every build's struct; parameters only when
   * LOOPCELL, so non-cell weight files keep their exact 0268 layout/count) */
  double z0[D];
  double Wu[D*2*D], bu[D];
  double Wn[D*2*D], bn[D];
  double Wv[D*2*D], bv[D], wv[D];
} Params;

typedef struct { double x[2*D], u[D], n[D], z[D]; } CellCache;

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
  int L, nlive, nreg;
  int msk[POOL];
  int sym[MAXL];         /* symbolic path condition per token (1 = admissible) */
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
  for (int blk = 0; blk < NBP; blk++){
    s = 1.0/sqrt((double)D);
    for (int i = 0; i < 3*D*D; i++) p->Wqkv[blk][i] = xr()*s;
    for (int i = 0; i < 3*D; i++) p->bqkv[blk][i] = 0;
    for (int i = 0; i < D*D; i++) p->Wo[blk][i] = xr()*s;
    for (int i = 0; i < D; i++){ p->bo[blk][i] = 0; p->g1[blk][i] = 1.0; p->be1[blk][i] = 0; }
    for (int i = 0; i < FE*D; i++) p->W1[blk][i] = xr()*s;
    for (int i = 0; i < FE; i++) p->b1[blk][i] = 0;
    s = 1.0/sqrt((double)FE);
    for (int i = 0; i < D*FE; i++) p->W2[blk][i] = xr()*s;
    for (int i = 0; i < D; i++){ p->b2[blk][i] = 0; p->g2[blk][i] = 1.0; p->be2[blk][i] = 0; }
    p->gam[blk] = 0.1;
  }
  for (int i = 0; i < D; i++){ p->gf[i] = 1.0; p->bef[i] = 0; }
  s = 1.0/sqrt((double)D);
  for (int i = 0; i < NOUT*D; i++) p->Wout[i] = xr()*s;
  for (int i = 0; i < NOUT; i++) p->bout[i] = 0;
  for (int b = 0; b < RB; b++){
    for (int d = 0; d < D; d++) p->Rbias[b][d] = (b == 0 || REGSHUF) ? 0.0 : xr()*0.02;
    for (int r = 0; r < NOUT; r++){
      for (int d = 0; d < D; d++) p->Wout_r[b][r*D+d] = (b == 0 || REGSHUF) ? p->Wout[r*D+d] : xr()*s;
      p->bout_r[b][r] = 0.0;
    }
  }
#if LOOPCELL
  /* cell initialisation is gated so non-cell builds keep the exact RNG stream */
  for (int i = 0; i < D; i++) p->z0[i] = xr()*0.02;
  s = 1.0/sqrt((double)(2*D));
  for (int i = 0; i < D*2*D; i++){ p->Wu[i] = xr()*s; p->Wn[i] = xr()*s; }
  /* pred head starts deep in the tanh linear regime: with the utility-scale
   * targets (0..5) a 1/sqrt(2D) init saturates the tanh and the head collapses
   * to a constant (0269 dev probe: mse 6.8 vs constant-baseline 0.36) */
  for (int i = 0; i < D*2*D; i++) p->Wv[i] = xr()*s*0.125;
  for (int i = 0; i < D; i++){ p->bu[i] = 0; p->bn[i] = 0; p->bv[i] = 0; p->wv[i] = xr()*s; }
#endif
}

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

/* ---- 0.0269 loop cell: forward/backward of the latent transition ---------- */
static void cell_fwd(const Params *p, const double *z, const double *ea,
                     double *out, CellCache *cc){
  for (int d = 0; d < D; d++){ cc->x[d] = z[d]; cc->x[D+d] = ea[d]; cc->z[d] = z[d]; }
  for (int d = 0; d < D; d++){
    double su = p->bu[d], sn = p->bn[d];
    for (int k = 0; k < 2*D; k++){ su += p->Wu[d*2*D+k]*cc->x[k]; sn += p->Wn[d*2*D+k]*cc->x[k]; }
    cc->u[d] = sigmoid(su);
    cc->n[d] = tanh(sn);
    out[d] = (1.0-cc->u[d])*z[d] + cc->u[d]*cc->n[d];
  }
}
static void cell_bwd(const Params *p, Params *g, const CellCache *cc,
                     const double *dout, double *dz_in, double *dea){
  for (int d = 0; d < D; d++){
    double du = dout[d]*(cc->n[d]-cc->z[d]);
    double dn = dout[d]*cc->u[d];
    double dpu = du*cc->u[d]*(1.0-cc->u[d]);
    double dpn = dn*(1.0-cc->n[d]*cc->n[d]);
    g->bu[d] += dpu; g->bn[d] += dpn;
    for (int k = 0; k < 2*D; k++){
      g->Wu[d*2*D+k] += dpu*cc->x[k];
      g->Wn[d*2*D+k] += dpn*cc->x[k];
      double dx = p->Wu[d*2*D+k]*dpu + p->Wn[d*2*D+k]*dpn;
      if (k < D) dz_in[k] += dx; else dea[k-D] += dx;
    }
    dz_in[d] += dout[d]*(1.0-cc->u[d]);
  }
}
/* committed-action embedding: the SAME Wc/bc/tc that embed candidate tokens */
static void action_embed(const Params *p, const double *cfrow, double *ea){
  for (int d = 0; d < D; d++){
    double s = p->bc[d] + p->tc[d];
    for (int k = 0; k < CAND_DIM; k++){
      double w = p->Wc[d*CAND_DIM+k];
#if LIFTED
      if (k >= ID_BLOCK_LO && k < ID_BLOCK_HI) w *= LIFT_RHO;
#endif
      s += w*cfrow[k];
    }
    ea[d] = s;
  }
}
static void action_embed_bwd(Params *g, const double *cfrow, const double *dea){
  for (int d = 0; d < D; d++){
    g->bc[d] += dea[d]; g->tc[d] += dea[d];
    for (int k = 0; k < CAND_DIM; k++){
      double sc = 1.0;
#if LIFTED
      if (k >= ID_BLOCK_LO && k < ID_BLOCK_HI) sc = LIFT_RHO;
#endif
      g->Wc[d*CAND_DIM+k] += dea[d]*cfrow[k]*sc;
    }
  }
}
/* world-model head: next-state optimal value from (z_t, emb(a_t)) alone */
static double pred_fwd(const Params *p, const double *z, const double *ea,
                       double *th, double *x){
  for (int k = 0; k < D; k++){ x[k] = z[k]; x[D+k] = ea[k]; }
  double v = 0;
  for (int d = 0; d < D; d++){
    double s = p->bv[d];
    for (int k = 0; k < 2*D; k++) s += p->Wv[d*2*D+k]*x[k];
    th[d] = tanh(s);
    v += p->wv[d]*th[d];
  }
  return v;
}
static void pred_bwd(const Params *p, Params *g, const double *th, const double *x,
                     double dv, double *dz, double *dea){
  for (int d = 0; d < D; d++){
    g->wv[d] += dv*th[d];
    double dt = dv*p->wv[d]*(1.0-th[d]*th[d]);
    g->bv[d] += dt;
    for (int k = 0; k < 2*D; k++){
      g->Wv[d*2*D+k] += dt*x[k];
      double dx = p->Wv[d*2*D+k]*dt;
      if (k < D) dz[k] += dx; else dea[k-D] += dx;
    }
  }
}

static long param_count(void){
  /* the register block exists in the struct for every build, but it is only a
   * parameter of the model when the multi-register structure is enabled.
   * 0269: with LOOPCELL the cell block sits AFTER the register block, so the
   * trainable span is the whole struct (counting base+cell while skipping the
   * register gap silently froze wv and the tail of Wv/bv — dev probe caught it
   * via a flatlined prediction head; gradcheck must cover the same span). */
  if (LOOPCELL) return (long)(sizeof(Params)/sizeof(double));
  if (BRANCHTOK >= 2 || READMAX) return (long)(offsetof(Params, z0)/sizeof(double));
  return (long)(offsetof(Params, Rbias)/sizeof(double));
}
static double *pv(Params *p){ return (double*)p; }


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
static void model_forward_z(const Params *p, const double *state,
                            const double (*cf)[CAND_DIM], int nlive,
                            const double *z, Cache *c){
  c->nreg = NREG + ZTOK;
  c->L = c->nreg + nlive;
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
  for (int i = 0; i < c->L; i++) c->sym[i] = 1;
#if SYMGATE >= 1
  /* Silicon-style path condition: candidate j is admissible only when its body
   * is supported by the current kernel closure (feature 6). The state token is
   * always admissible. SYMGATE==1 gates the attention residual only (soft);
   * SYMGATE==2 additionally removes the token from the choice set (hard), so no
   * selection or backward pass can use it. */
  for (int j = 0; j < nlive; j++) c->sym[c->nreg+j] = (cf[j][6] > 0.5) ? 1 : 0;
#endif
#if SYMGATE >= 2
  {
    int adm = 0;
    for (int j = 0; j < nlive; j++){
      c->msk[j] = c->sym[c->nreg+j];
      adm += c->msk[j];
    }
    if (adm == 0){
      /* every candidate is inadmissible: no admissible action exists. Keep the
       * set (a score is still required) and count the fallback so the gate can
       * see it instead of silently reporting a proof. */
      for (int j = 0; j < nlive; j++) c->msk[j] = 1;
      g_pc_fallback++;
    }
  }
#endif
  { /* census: fraction of tokens the path condition removes */
    for (int i = 0; i < c->L; i++){ g_pc_tokens++; if (SYMGATE >= 1 && !c->sym[i]) g_pc_dropped++; }
  }
  for (int b = 0; b < c->nreg; b++){
#if LOOPCELL
    if (b == 0){   /* latent proof-state register: raw token, no input matrix */
      for (int i = 0; i < D; i++) c->h[0][i] = z ? z[i] : p->z0[i];
      continue;
    }
#endif
    for (int i = 0; i < D; i++){
      double s = p->bs[i] + p->ts[i];
      for (int k = 0; k < STATE_DIM; k++) s += p->Ws[i*STATE_DIM+k]*state[k];
      c->h[b][i] = s + p->Rbias[REGSHUF ? 0 : (b - ZTOK)][i];
    }
  }
  for (int j = 0; j < nlive; j++)
    for (int i = 0; i < D; i++){
      double s = p->bc[i] + p->tc[i];
      for (int k = 0; k < CAND_DIM; k++){
        double w = p->Wc[i*CAND_DIM+k];
#if LIFTED
        if (k >= ID_BLOCK_LO && k < ID_BLOCK_HI) w *= LIFT_RHO;  /* predicate-id residual */
#endif
        s += w*cf[j][k];
      }
      c->h[c->nreg+j][i] = s;
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
      int blk = PHASEUNTIE ? (pass*NL + l) : l;
      for (int i = 0; i < L; i++) for (int d = 0; d < D; d++) lc->in[i][d] = c->h[i][d];
      for (int i = 0; i < L; i++){
        double xh[D], inv;
        layer_norm_fwd(lc->in[i], p->g1[blk], p->be1[blk], lc->ln1[i], xh, &inv);
      }
      for (int i = 0; i < L; i++)
        for (int r = 0; r < 3*D; r++){
          double s = p->bqkv[blk][r];
          for (int d = 0; d < D; d++) s += p->Wqkv[blk][r*D+d]*lc->ln1[i][d];
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
            if (VAR_BIND) s += p->gam[blk]*c->bias[i][j];
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
#if ATTMODE >= 2
          {
            /* keep the ATTMODE largest weights and renormalise: a branching layer
             * that preserves several discrete alternatives instead of averaging
             * over all of them (Screamer-style choice inside the block). */
            int k = ATTMODE; if (k > L) k = L;
            double sorted[MAXL];
            for (int j = 0; j < L; j++) sorted[j] = lc->att[hh][i][j];
            for (int a = 0; a < L; a++)
              for (int b2 = a+1; b2 < L; b2++)
                if (sorted[b2] > sorted[a]){ double t = sorted[a]; sorted[a] = sorted[b2]; sorted[b2] = t; }
            double thr = sorted[k-1];
            double z = 0;
            for (int j = 0; j < L; j++){
              double w = lc->att[hh][i][j];
              lc->att[hh][i][j] = (w >= thr) ? w : 0.0;
              z += lc->att[hh][i][j];
            }
            if (z > 0) for (int j = 0; j < L; j++) lc->att[hh][i][j] /= z;
          }
#endif
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
          double s = p->bo[blk][d];
          for (int k = 0; k < D; k++) s += p->Wo[blk][d*D+k]*lc->ao[i][k];
          lc->h1[i][d] = lc->in[i][d] + (c->sym[i] ? s : 0.0);
        }
      for (int i = 0; i < L; i++){
        double xh[D], inv;
        layer_norm_fwd(lc->h1[i], p->g2[blk], p->be2[blk], lc->ln2[i], xh, &inv);
      }
      for (int i = 0; i < L; i++){
        for (int f = 0; f < FE; f++){
          double s = p->b1[blk][f];
          for (int d = 0; d < D; d++) s += p->W1[blk][f*D+d]*lc->ln2[i][d];
          lc->pre[i][f] = s;
          lc->act[i][f] = gelu(s);
        }
        for (int d = 0; d < D; d++){
          double s = p->b2[blk][d];
          for (int f = 0; f < FE; f++) s += p->W2[blk][d*FE+f]*lc->act[i][f];
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
#if READMAX
      /* per-register head; the candidate score is the max over registers
       * (Screamer "some value": one surviving branch decides). The single
       * global head is replaced, not mixed in, so its parameters are unused. */
      double best = -1e30;
      for (int b = 0; b < c->nreg; b++){
        int hb = REGSHUF ? 0 : b;      /* control: one shared head for all registers */
        double sb = p->bout_r[hb][r];
        for (int d = 0; d < D; d++) sb += p->Wout_r[hb][r*D+d]*c->lnf[c->nreg+j][d];
        if (sb > best) best = sb;
      }
      c->raw[j][r] = best;
#else
      double s = p->bout[r];
      for (int d = 0; d < D; d++) s += p->Wout[r*D+d]*c->lnf[c->nreg+j][d];
      c->raw[j][r] = s;
#endif
    }
#if VAR_UTILHEAD
    c->score[j] = 5.0*softplus(c->raw[j][0]) + 0.15*softplus(c->raw[j][1]) - c->cost[j];
#else
    c->score[j] = c->raw[j][0];
#endif
    if (!c->msk[j]) c->score[j] = -1e30;
  }
}
static void model_forward(const Params *p, const double *state,
                          const double (*cf)[CAND_DIM], int nlive, Cache *c){
  model_forward_z(p, state, cf, nlive, (const double*)0, c);
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

static void model_backward_ds(Cache *c, const double *statev,
                              const double (*cf)[CAND_DIM], int nlive,
                              const double *ds);
static double model_step(const double *statev, const double (*cf)[CAND_DIM],
                         const int *util_target_best, int best,
                         const double *util, int nlive){
  Cache *c = g_c;
  model_forward(g_p, statev, cf, nlive, c);
  double ds[POOL];
  double loss = loss_from_cache(c, util, best, nlive, ds);
  (void)util_target_best;
  model_backward_ds(c, statev, cf, nlive, ds);
  return loss;
}

/* score-gradient backward through the blocks; leaves the input-token gradient
 * in g_dh (token 0 is the latent register when LOOPCELL). Shared by the
 * per-state trainer and the episode-level BPTT so both use ONE objective. */
static void model_backward_ds(Cache *c, const double *statev,
                              const double (*cf)[CAND_DIM], int nlive,
                              const double *ds){
  Params *g = g_g;
  static double dlnf[MAXL][D];
  for (int i = 0; i < c->L; i++) for (int d = 0; d < D; d++) dlnf[i][d] = 0;
  for (int j = 0; j < nlive; j++){
    if (!c->msk[j] && ds[j] == 0.0) continue;
#if VAR_UTILHEAD
    {
      double dgr = ds[j]*5.0*sigmoid(c->raw[j][0]);
      double dnr = ds[j]*0.15*sigmoid(c->raw[j][1]);
      for (int d = 0; d < D; d++){
        g->Wout[0*D+d] += dgr*c->lnf[c->nreg+j][d];
        g->Wout[1*D+d] += dnr*c->lnf[c->nreg+j][d];
        dlnf[c->nreg+j][d] += dgr*g_p->Wout[0*D+d] + dnr*g_p->Wout[1*D+d];
      }
      g->bout[0] += dgr;
      g->bout[1] += dnr;
    }
#elif READMAX
    {
      /* route the gradient through the register head that produced the max */
      for (int r = 0; r < NOUT; r++){
        double dsr = ds[j];
        if (dsr == 0.0) continue;
        int bw = 0; double bv = -1e30;
        for (int b = 0; b < c->nreg; b++){
          int hb = REGSHUF ? 0 : b;
          double sb = g_p->bout_r[hb][r];
          for (int d = 0; d < D; d++) sb += g_p->Wout_r[hb][r*D+d]*c->lnf[c->nreg+j][d];
          if (sb > bv){ bv = sb; bw = hb; }
        }
        for (int d = 0; d < D; d++){
          g->Wout_r[bw][r*D+d] += dsr*c->lnf[c->nreg+j][d];
          dlnf[c->nreg+j][d] += dsr*g_p->Wout_r[bw][r*D+d];
        }
        g->bout_r[bw][r] += dsr;
      }
    }
#else
    {
      for (int d = 0; d < D; d++){
        g->Wout[d] += ds[j]*c->lnf[c->nreg+j][d];
        dlnf[c->nreg+j][d] += ds[j]*g_p->Wout[d];
      }
      g->bout[0] += ds[j];
    }
#endif
  }
  for (int i = 0; i < c->L; i++) for (int d = 0; d < D; d++) g_dh[i][d] = 0;
  for (int i = c->nreg; i < c->L; i++){
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
      int blk = PHASEUNTIE ? (pass*NL + l) : l;
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
          for (int d = 0; d < D; d++) s += g_p->W2[blk][d*FE+f]*dout[i][d];
          dact[i][f] = s;
          dpre[i][f] = s*gelu_d(lc->pre[i][f]);
        }
        for (int d = 0; d < D; d++) g->b2[blk][d] += dout[i][d];
        for (int d = 0; d < D; d++)
          for (int f = 0; f < FE; f++) g->W2[blk][d*FE+f] += dout[i][d]*lc->act[i][f];
        for (int f = 0; f < FE; f++){
          g->b1[blk][f] += dpre[i][f];
          for (int d = 0; d < D; d++) g->W1[blk][f*D+d] += dpre[i][f]*lc->ln2[i][d];
        }
        for (int d = 0; d < D; d++){
          double s = 0;
          for (int f = 0; f < FE; f++) s += g_p->W1[blk][f*D+d]*dpre[i][f];
          dln2[i][d] = s;
        }
      }
      /* LN2 backward */
      for (int i = 0; i < L; i++){
        double xh[D], inv, dx[D];
        layer_norm_fwd(lc->h1[i], g_p->g2[blk], g_p->be2[blk], lc->ln2[i], xh, &inv);
        for (int d = 0; d < D; d++) dx[d] = 0;
        layer_norm_bwd(dln2[i], xh, inv, g_p->g2[blk], dx, g->g2[blk], g->be2[blk]);
        for (int d = 0; d < D; d++) dh1[i][d] += dx[d];
      }
      /* attention out projection backward */
      for (int i = 0; i < L; i++){
        if (!c->sym[i]) continue;    /* symbolic path condition: this branch was gated off */
        for (int d = 0; d < D; d++) g->bo[blk][d] += dh1[i][d];
        for (int d = 0; d < D; d++)
          for (int k = 0; k < D; k++) g->Wo[blk][d*D+k] += dh1[i][d]*lc->ao[i][k];
        for (int k = 0; k < D; k++){
          double s = 0;
          for (int d = 0; d < D; d++) s += g_p->Wo[blk][d*D+k]*dh1[i][d];
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
      if (VAR_BIND) g->gam[blk] += dgam;
      /* qkv projection + LN1 backward */
      for (int i = 0; i < L; i++){
        for (int r = 0; r < 3*D; r++){
          g->bqkv[blk][r] += dqkv[i][r];
          for (int d = 0; d < D; d++) g->Wqkv[blk][r*D+d] += dqkv[i][r]*lc->ln1[i][d];
        }
        double dln1[D], dx[D], xh[D], inv;
        for (int d = 0; d < D; d++){
          double s = 0;
          for (int r = 0; r < 3*D; r++) s += g_p->Wqkv[blk][r*D+d]*dqkv[i][r];
          dln1[d] = s;
          dx[d] = 0;
        }
        layer_norm_fwd(lc->in[i], g_p->g1[blk], g_p->be1[blk], lc->ln1[i], xh, &inv);
        layer_norm_bwd(dln1, xh, inv, g_p->g1[blk], dx, g->g1[blk], g->be1[blk]);
        for (int d = 0; d < D; d++) din[i][d] = dh1[i][d] + dx[d];
      }
      for (int i = 0; i < L; i++) for (int d = 0; d < D; d++) g_dh[i][d] = din[i][d];
    }
  }
  /* embedding backward */
  for (int b = 0; b < c->nreg; b++){
#if LOOPCELL
    if (b == 0) continue;   /* latent register: gradient stays in g_dh[0] for BPTT */
#endif
    for (int d = 0; d < D; d++){
      g->bs[d] += g_dh[b][d];
      g->ts[d] += g_dh[b][d];
      for (int k = 0; k < STATE_DIM; k++) g->Ws[d*STATE_DIM+k] += g_dh[b][d]*statev[k];
      g->Rbias[REGSHUF ? 0 : (b - ZTOK)][d] += g_dh[b][d];
    }
  }
  for (int j = 0; j < nlive; j++)
    for (int d = 0; d < D; d++){
      g->bc[d] += g_dh[c->nreg+j][d];
      g->tc[d] += g_dh[c->nreg+j][d];
      for (int k = 0; k < CAND_DIM; k++){
        double sc = 1.0;
#if LIFTED
        if (k >= ID_BLOCK_LO && k < ID_BLOCK_HI) sc = LIFT_RHO;
#endif
        g->Wc[d*CAND_DIM+k] += g_dh[c->nreg+j][d]*cf[j][k]*sc;
      }
    }
}