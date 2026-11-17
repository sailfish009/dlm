/* Closure-layer primitive + soundness/expressibility gates (0253 item 4).
 *
 * The candidate primitive: one layer = one parallel relational closure step.
 *   state v[a] in [0,1] per ground atom, init from facts.
 *   binding (X,Y,Z) for rule h(X,Z):-b1(X,Y),b2(Y,Z):
 *     AND  c = softmin(v[b1(X,Y)], v[b2(Y,Z)]; beta)      (ANDRE eq 7/8)
 *     OR   a_hat = softmax_over_bindings(c; beta)          (ANDRE eq 9)
 *     monotone update  v_new[a] = max(v[a], a_hat)
 *   L layers = L parallel closure steps.
 *
 * Soundness gate (beta->inf): hard layer (min/max) iterated to fixpoint MUST equal
 * the kernel closure() exactly (0 violations). Expressibility: hard L layers derive
 * every goal of depth <= L (constructive, L=depth solves).
 */
#define RC_NO_MAIN
#include "rc.c"
#include <math.h>

typedef struct { int head, a1, a2, rule; } Triple;
static Triple g_tr[NRULES*NENT*NENT*NENT];
static int g_ntr;
static int g_hstart[NATOMS], g_hcount[NATOMS];

/* build binding triples for a rule set, grouped by head atom */
static void build_triples(const int *rules, int nrules){
  g_ntr = 0;
  for (int k = 0; k < nrules; k++){
    const Rule *r = &all_rules[rules[k]];
    for (int X = 0; X < NENT; X++)
      for (int Y = 0; Y < NENT; Y++)
        for (int Z = 0; Z < NENT; Z++){
          if (X == Z) continue;
          g_tr[g_ntr].head = atom_idx(r->head, X, Z);
          g_tr[g_ntr].a1   = atom_idx(r->b1, X, Y);
          g_tr[g_ntr].a2   = atom_idx(r->b2, Y, Z);
          g_tr[g_ntr].rule = rules[k];
          g_ntr++;
        }
  }
  /* counting sort by head */
  static Triple tmp[NRULES*NENT*NENT*NENT];
  int cnt[NATOMS]; memset(cnt, 0, sizeof cnt);
  for (int i = 0; i < g_ntr; i++) cnt[g_tr[i].head]++;
  g_hstart[0] = 0;
  for (int a = 1; a < NATOMS; a++) g_hstart[a] = g_hstart[a-1] + cnt[a-1];
  for (int a = 0; a < NATOMS; a++) g_hcount[a] = cnt[a];
  int pos[NATOMS]; for (int a = 0; a < NATOMS; a++) pos[a] = g_hstart[a];
  for (int i = 0; i < g_ntr; i++) tmp[pos[g_tr[i].head]++] = g_tr[i];
  memcpy(g_tr, tmp, g_ntr*sizeof(Triple));
}

static double softmin2(double v1, double v2, double beta){
  double m = v1 < v2 ? v1 : v2;
  double e1 = exp(-beta*(v1-m)), e2 = exp(-beta*(v2-m));
  double z = e1 + e2;
  return (e1*v1 + e2*v2)/z;
}

/* one hard layer (beta=inf): min/max, monotone. v in {0,1} => exact kernel step */
static void hard_layer(const double *v, double *vn){
  memcpy(vn, v, NATOMS*sizeof(double));
  for (int a = 0; a < NATOMS; a++){
    if (!g_hcount[a]) continue;
    double best = 0.0;
    for (int j = 0; j < g_hcount[a]; j++){
      const Triple *t = &g_tr[g_hstart[a]+j];
      double c = v[t->a1] < v[t->a2] ? v[t->a1] : v[t->a2];   /* min = AND */
      if (c > best) best = c;                                 /* max = OR */
    }
    if (best > vn[a]) vn[a] = best;                           /* monotone */
  }
}

/* one soft layer (finite beta): softmin AND, softmax OR, monotone max */
static void soft_layer(const double *v, double *vn, double beta){
  memcpy(vn, v, NATOMS*sizeof(double));
  for (int a = 0; a < NATOMS; a++){
    int n = g_hcount[a];
    if (!n) continue;
    double c[NRULES*NENT]; double mx = -1e30;
    for (int j = 0; j < n; j++){
      const Triple *t = &g_tr[g_hstart[a]+j];
      c[j] = softmin2(v[t->a1], v[t->a2], beta);
      if (c[j] > mx) mx = c[j];
    }
    double z = 0, ah = 0;
    for (int j = 0; j < n; j++){ double e = exp(beta*(c[j]-mx)); z += e; ah += e*c[j]; }
    ah /= z;
    if (ah > vn[a]) vn[a] = ah;
  }
}

static void init_v(const uint64_t *facts, double *v){
  for (int a = 0; a < NATOMS; a++) v[a] = bs_test(facts, a) ? 1.0 : 0.0;
}

/* ---- gates ---- */
static int gate_kernel_match(int nworlds){
  int viol = 0, checked = 0;
  World w;
  for (int i = 0; i < nworlds; i++){
    if (!make_world(&w, 0, i)) continue;
    int all[SEED_RULES+POOL];
    for (int k=0;k<SEED_RULES;k++) all[k]=w.theory[k];
    for (int k=0;k<POOL;k++) all[SEED_RULES+k]=w.cands[k];
    build_triples(all, SEED_RULES+POOL);
    uint64_t kc[MAXWORDS]; closure(w.facts, all, SEED_RULES+POOL, kc, NULL);
    double v[NATOMS], vn[NATOMS]; init_v(w.facts, v);
    for (int L = 0; L < NATOMS; L++){ hard_layer(v, vn); memcpy(v, vn, NATOMS*sizeof(double)); }
    for (int a = 0; a < NATOMS; a++){
      int kv = bs_test(kc, a); int mv = v[a] > 0.5;
      if (kv != mv) viol++;
    }
    checked++;
  }
  printf("KERNEL-MATCH worlds=%d atoms_checked=%d violations=%d %s\n",
         checked, checked*NATOMS, viol, viol==0?"PASS":"FAIL");
  return viol==0?0:1;
}

/* constructive depth-scaling: hard L layers derive exactly the atoms of depth<=L */
static int gate_depth_scaling(int nworlds){
  int bad = 0, checked = 0;
  World w;
  for (int i = 0; i < nworlds; i++){
    if (!make_world(&w, 0, i)) continue;
    int all[SEED_RULES+POOL];
    for (int k=0;k<SEED_RULES;k++) all[k]=w.theory[k];
    for (int k=0;k<POOL;k++) all[SEED_RULES+k]=w.cands[k];
    build_triples(all, SEED_RULES+POOL);
    uint64_t kc[MAXWORDS]; int dep[NATOMS];
    closure(w.facts, all, SEED_RULES+POOL, kc, dep);
    double v[NATOMS], vn[NATOMS]; init_v(w.facts, v);
    for (int L = 1; L <= 6; L++){
      hard_layer(v, vn); memcpy(v, vn, NATOMS*sizeof(double));
      for (int a = 0; a < NATOMS; a++){
        if (dep[a] < 0) continue;
        int derived = v[a] > 0.5;
        int should = (dep[a] <= L);
        if (derived != should) bad++;
      }
    }
    checked++;
  }
  printf("DEPTH-SCALING worlds=%d mismatches=%d %s (hard L layers == depth<=L)\n",
         checked, bad, bad==0?"PASS":"FAIL");
  return bad==0?0:1;
}

/* soft layer finite-beta sanity: beta large => approaches hard; monotone non-decreasing */
static int gate_soft_sanity(int nworlds){
  int bad = 0; World w;
  for (int i = 0; i < nworlds; i++){
    if (!make_world(&w, 0, i)) continue;
    int all[SEED_RULES+POOL];
    for (int k=0;k<SEED_RULES;k++) all[k]=w.theory[k];
    for (int k=0;k<POOL;k++) all[SEED_RULES+k]=w.cands[k];
    build_triples(all, SEED_RULES+POOL);
    double v[NATOMS], vn[NATOMS], vh[NATOMS]; init_v(w.facts, v);
    for (int L = 0; L < 4; L++){
      soft_layer(v, vn, 64.0);
      hard_layer(v, vh);
      for (int a = 0; a < NATOMS; a++){
        if (vn[a] < v[a] - 1e-9) bad++;          /* monotone */
        if (fabs(vn[a]-vh[a]) > 0.02) bad++;      /* beta=64 ~ hard */
      }
      memcpy(v, vn, NATOMS*sizeof(double));
    }
  }
  printf("SOFT-SANITY worlds=%d violations=%d %s (monotone + beta64~hard)\n",
         nworlds, bad, bad==0?"PASS":"FAIL");
  return bad==0?0:1;
}

/* ---- trainable weighted soft layer + analytic backward (item 4b) ----------
 * per-rule inclusion alpha[r]=sigmoid(theta[r]); binding value c_j=alpha[r_j]*softmin2.
 * Gradcheck verifies dLoss/dtheta through L soft layers (loss=MSE vs kernel closure). */
static double sigm(double x){ return x>=0 ? 1.0/(1.0+exp(-x)) : exp(x)/(1.0+exp(x)); }

static void weighted_soft_layer(const double *v, double *vn, double beta, const double *alpha){
  memcpy(vn, v, NATOMS*sizeof(double));
  for (int a = 0; a < NATOMS; a++){
    int n = g_hcount[a]; if (!n) continue;
    double c[NRULES*NENT]; double mx=-1e30;
    for (int j=0;j<n;j++){
      const Triple *t=&g_tr[g_hstart[a]+j];
      c[j]=alpha[t->rule]*softmin2(v[t->a1],v[t->a2],beta);
      if(c[j]>mx)mx=c[j];
    }
    double z=0,ah=0;
    for(int j=0;j<n;j++){double e=exp(beta*(c[j]-mx));z+=e;ah+=e*c[j];}
    ah/=z;
    if(ah>vn[a])vn[a]=ah;
  }
}

/* backward of one weighted soft layer: recompute forward quantities from v_in */
static void backward_layer(const double *v_in, const double *g_vout, double beta,
                           const double *alpha, double *g_vin, double *g_alpha){
  for(int a=0;a<NATOMS;a++) g_vin[a]=0;
  for(int a=0;a<NATOMS;a++){
    int n=g_hcount[a]; if(!n){ g_vin[a]+=g_vout[a]; continue; }
    double c[NRULES*NENT], s[NRULES*NENT], w1[NRULES*NENT];
    double mx=-1e30;
    for(int j=0;j<n;j++){
      const Triple *t=&g_tr[g_hstart[a]+j];
      double v1=v_in[t->a1],v2=v_in[t->a2];
      double m=v1<v2?v1:v2;
      double e1=exp(-beta*(v1-m)),e2=exp(-beta*(v2-m)),z=e1+e2;
      w1[j]=e1/z; s[j]=(e1*v1+e2*v2)/z;
      c[j]=alpha[t->rule]*s[j];
      if(c[j]>mx)mx=c[j];
    }
    double z=0,ah=0,w[NRULES*NENT];
    for(int j=0;j<n;j++){w[j]=exp(beta*(c[j]-mx));z+=w[j];ah+=w[j]*c[j];}
    ah/=z; for(int j=0;j<n;j++)w[j]/=z;
    double g_ah = (ah>=v_in[a]) ? g_vout[a] : 0.0;
    double g_direct = (ah>=v_in[a]) ? 0.0 : g_vout[a];
    for(int j=0;j<n;j++){
      const Triple *t=&g_tr[g_hstart[a]+j];
      double g_c = g_ah * w[j]*(1.0+beta*(c[j]-ah));
      g_alpha[t->rule] += g_c * s[j];
      double g_s = g_c * alpha[t->rule];
      double v1=v_in[t->a1],v2=v_in[t->a2],ww=w1[j];
      double ds_dv1 = ww + beta*ww*(1.0-ww)*(v2-v1);
      double ds_dv2 = (1.0-ww) + beta*ww*(1.0-ww)*(v1-v2);
      g_vin[t->a1] += g_s*ds_dv1;
      g_vin[t->a2] += g_s*ds_dv2;
    }
    g_vin[a]+=g_direct;
  }
}

#define GLMAX 8
static double g_vl[GLMAX+1][NATOMS];
static double forward_loss(const double *theta, const uint64_t *facts, const double *target,
                           int L, double beta, double *alpha){
  for(int r=0;r<NRULES;r++) alpha[r]=sigm(theta[r]);
  init_v(facts, g_vl[0]);
  for(int l=0;l<L;l++) weighted_soft_layer(g_vl[l], g_vl[l+1], beta, alpha);
  double loss=0;
  for(int a=0;a<NATOMS;a++){double d=g_vl[L][a]-target[a];loss+=0.5*d*d;}
  return loss;
}

/* gradient of forward_loss wrt theta for one world (reuses verified backward) */
static void compute_grad(const double *theta, const uint64_t *facts, const double *target,
                         int L, double beta, double *g_theta){
  double alpha[NRULES],g_alpha[NRULES],g_vin[NATOMS],g_vout[NATOMS];
  forward_loss(theta,facts,target,L,beta,alpha);
  for(int a=0;a<NATOMS;a++)g_vout[a]=g_vl[L][a]-target[a];
  for(int r=0;r<NRULES;r++)g_theta[r]=0;
  for(int l=L-1;l>=0;l--){
    for(int r=0;r<NRULES;r++)g_alpha[r]=0;
    backward_layer(g_vl[l],g_vout,beta,alpha,g_vin,g_alpha);
    for(int r=0;r<NRULES;r++)g_theta[r]+=g_alpha[r]*alpha[r]*(1.0-alpha[r]);
    memcpy(g_vout,g_vin,NATOMS*sizeof(double));
  }
}

/* training demo: learn per-rule weights from kernel-closure supervision (MSE).
 * The sound primitive's optimum is alpha=1 for active rules; this verifies the
 * learning loop converges (loss down, active alpha up). */
static int gate_train(int nworlds, int epochs){
  World ws[64]; double targets[64][NATOMS]; int nw=0;
  for(int i=0;i<nworlds && nw<64;i++){
    if(!make_world(&ws[nw],0,i))continue;
    int all[SEED_RULES+POOL];
    for(int k=0;k<SEED_RULES;k++)all[k]=ws[nw].theory[k];
    for(int k=0;k<POOL;k++)all[SEED_RULES+k]=ws[nw].cands[k];
    build_triples(all,SEED_RULES+POOL);
    uint64_t kc[MAXWORDS];closure(ws[nw].facts,all,SEED_RULES+POOL,kc,NULL);
    for(int a=0;a<NATOMS;a++)targets[nw][a]=bs_test(kc,a)?1.0:0.0;
    nw++;
  }
  int L=4; double beta=8.0;
  double theta[NRULES],m[NRULES],v[NRULES],g[NRULES],gt[NRULES],alpha[NRULES];
  rng_state=777;
  for(int r=0;r<NRULES;r++){theta[r]=0.2*((double)randbelow(1000)/1000.0-0.5);m[r]=v[r]=0;}
  double lr=0.05;
  printf("TRAIN worlds=%d L=%d beta=%.1f epochs=%d\n",nw,L,beta,epochs);
  for(int ep=0;ep<epochs;ep++){
    for(int r=0;r<NRULES;r++)g[r]=0;
    double loss=0;
    for(int i=0;i<nw;i++){
      int all[SEED_RULES+POOL];
      for(int k=0;k<SEED_RULES;k++)all[k]=ws[i].theory[k];
      for(int k=0;k<POOL;k++)all[SEED_RULES+k]=ws[i].cands[k];
      build_triples(all,SEED_RULES+POOL);
      loss+=forward_loss(theta,ws[i].facts,targets[i],L,beta,alpha);
      compute_grad(theta,ws[i].facts,targets[i],L,beta,gt);
      for(int r=0;r<NRULES;r++)g[r]+=gt[r]/nw;
    }
    int t=ep+1;
    for(int r=0;r<NRULES;r++){
      m[r]=0.9*m[r]+0.1*g[r]; v[r]=0.999*v[r]+0.001*g[r]*g[r];
      double mh=m[r]/(1-pow(0.9,t)), vh=v[r]/(1-pow(0.999,t));
      theta[r]-=lr*mh/(sqrt(vh)+1e-8);
    }
    if(ep==0||ep==epochs/2||ep==epochs-1)
      printf("  epoch %3d loss=%.5f\n",ep,loss/nw);
  }
  for(int r=0;r<NRULES;r++)alpha[r]=sigm(theta[r]);
  double amin=1,amax=0; for(int r=0;r<NRULES;r++){if(alpha[r]<amin)amin=alpha[r];if(alpha[r]>amax)amax=alpha[r];}
  printf("TRAIN-DONE final_alpha_range=[%.3f,%.3f] %s\n",amin,amax,(amax>0.9)?"PASS":"CHECK");
  return 0;
}

static int gate_gradcheck(void){
  World w; if(!make_world(&w,0,7)) return 1;
  int all[SEED_RULES+POOL];
  for(int k=0;k<SEED_RULES;k++)all[k]=w.theory[k];
  for(int k=0;k<POOL;k++)all[SEED_RULES+k]=w.cands[k];
  build_triples(all,SEED_RULES+POOL);
  uint64_t kc[MAXWORDS]; closure(w.facts,all,SEED_RULES+POOL,kc,NULL);
  double target[NATOMS]; for(int a=0;a<NATOMS;a++)target[a]=bs_test(kc,a)?1.0:0.0;
  int L=3; double beta=4.0;
  double theta[NRULES],alpha[NRULES],g_alpha[NRULES],g_theta[NRULES],g_vin[NATOMS],g_vout[NATOMS];
  rng_state=12345;
  for(int r=0;r<NRULES;r++)theta[r]=0.3*((double)randbelow(1000)/1000.0-0.5);
  forward_loss(theta,w.facts,target,L,beta,alpha);
  for(int a=0;a<NATOMS;a++)g_vout[a]=g_vl[L][a]-target[a];
  for(int r=0;r<NRULES;r++)g_theta[r]=0;
  for(int l=L-1;l>=0;l--){
    for(int r=0;r<NRULES;r++)g_alpha[r]=0;
    backward_layer(g_vl[l],g_vout,beta,alpha,g_vin,g_alpha);
    for(int r=0;r<NRULES;r++)g_theta[r]+=g_alpha[r]*alpha[r]*(1.0-alpha[r]);
    memcpy(g_vout,g_vin,NATOMS*sizeof(double));
  }
  double eps=1e-6,max_rel=0,max_abs=0; int checked=0;
  for(int r=0;r<NRULES;r++){
    double o=theta[r];
    theta[r]=o+eps; double lp=forward_loss(theta,w.facts,target,L,beta,alpha);
    theta[r]=o-eps; double lm=forward_loss(theta,w.facts,target,L,beta,alpha);
    theta[r]=o;
    double num=(lp-lm)/(2*eps), ana=g_theta[r];
    double den=fabs(num)+fabs(ana)+1e-8, rel=fabs(num-ana)/den;
    if(fabs(num-ana)>max_abs)max_abs=fabs(num-ana);
    if(rel>max_rel && fabs(num)+fabs(ana)>1e-7)max_rel=rel;
    checked++;
  }
  int ok = max_abs < 1e-4;
  printf("GRADCHECK rules=%d L=%d max_abs=%.3e max_rel_small=%.3e %s\n",
         checked,L,max_abs,max_rel,ok?"PASS":"FAIL");
  return ok?0:1;
}

int main(int argc, char **argv){
  build_rules();
  int nworlds = 100, gradcheck = 0, train = 0, epochs = 60;
  for (int i = 1; i < argc; i++){
    if (!strcmp(argv[i], "--worlds") && i+1 < argc) nworlds = atoi(argv[++i]);
    else if (!strcmp(argv[i], "--gradcheck")) gradcheck = 1;
    else if (!strcmp(argv[i], "--train")) train = 1;
    else if (!strcmp(argv[i], "--epochs") && i+1 < argc) epochs = atoi(argv[++i]);
  }
  if (gradcheck) return gate_gradcheck();
  if (train) return gate_train(nworlds, epochs);
  int r1 = gate_kernel_match(nworlds);
  int r2 = gate_depth_scaling(nworlds);
  int r3 = gate_soft_sanity(nworlds);
  printf("CLOSURE-PRIMITIVE-GATES %s\n", (r1||r2||r3)?"FAIL":"PASS");
  return (r1||r2||r3)?1:0;
}