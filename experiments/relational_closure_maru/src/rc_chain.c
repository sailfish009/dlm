/* Chain reachability / length-extrapolation discrimination (0253 items 5/6).
 *
 * The faithful "long-range dependency" test for the closure primitive:
 *   - single binary predicate p, transitivity rule p(X,Z):-p(X,Y),p(Y,Z).
 *   - world = a path of L edges over distinct entities + decoy edges.
 *   - query (s,t): is p(s,t) in the closure? (reachability)
 *   - TRAIN on short paths (L<=4), TEST on long paths (L=6..10).
 *
 * Closure primitive: L layers of monotone join compute reachability at ANY path
 * length constructively (depth-scaling). A learned model (MLP / attention) must
 * acquire the algorithm from short examples and may fail to extrapolate length.
 *
 * Stage 1 (this file): fixture + oracle + closure-primitive length-scaling + MLP.
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#ifndef NENT
#define NENT 12
#endif
#define NPAIR (NENT*NENT)
#define MAXPATH (NENT-1)

/* adjacency bitset: adj[i] bit j = p(i,j). diagonal unused. */
typedef struct { uint64_t adj[NENT]; } Adj;
static int adj_test(const Adj *a, int i, int j){ return (a->adj[i] >> j) & 1ULL; }
static void adj_set(Adj *a, int i, int j){ a->adj[i] |= 1ULL << j; }

/* transitive closure (Warshall), confluent */
static void tclosure(const Adj *in, Adj *out){
  *out = *in;
  for (int k = 0; k < NENT; k++)
    for (int i = 0; i < NENT; i++){
      if (!adj_test(out, i, k)) continue;
      out->adj[i] |= out->adj[k];
    }
}

/* one parallel join step (closure primitive hard layer): out[i][j] |= OR_k in[i][k]&in[k][j] */
static int join_step(const Adj *in, Adj *out){
  *out = *in; int added = 0;
  for (int i = 0; i < NENT; i++)
    for (int k = 0; k < NENT; k++){
      if (!adj_test(in, i, k)) continue;
      uint64_t row = in->adj[k];
      uint64_t nw = row & ~out->adj[i];
      if (nw){ out->adj[i] |= nw; added += __builtin_popcountll(nw); }
    }
  return added;
}

/* ---------------- PRNG ---------------- */
static uint64_t rng_state;
static uint64_t mix64(uint64_t x){ x ^= x>>12; x ^= x<<25; x ^= x>>27; return x*2685821657736338717ULL; }
static uint64_t nextrand(void){ rng_state = mix64(rng_state); return rng_state; }
static int randbelow(int n){ return (int)(nextrand() % (uint64_t)n); }
static void shuffle_ints(int *v, int n){ for(int i=n-1;i>0;i--){int j=randbelow(i+1);int t=v[i];v[i]=v[j];v[j]=t;} }

/* ---------------- chain world ---------------- */
typedef struct {
  Adj facts;
  int path[MAXPATH+1];   /* entity sequence */
  int plen;              /* #edges = path length */
  int qs, qt;            /* query */
  int label;             /* reachability of (qs,qt) */
  int dist;              /* path distance qs->qt (<=plen), the difficulty */
} ChainWorld;

/* generate a path of length L over distinct entities + decoy edges; query along path.
 * decoy_rate: extra random edges (may create shortcuts; label computed by oracle). */
static void make_chain(ChainWorld *w, int L, int decoy_pct, int negative){
  memset(w, 0, sizeof *w);
  int ents[NENT]; for(int i=0;i<NENT;i++)ents[i]=i;
  shuffle_ints(ents, NENT);
  if (L > MAXPATH) L = MAXPATH;
  w->plen = L;
  for(int i=0;i<=L;i++) w->path[i]=ents[i];
  for(int i=0;i<L;i++) adj_set(&w->facts, w->path[i], w->path[i+1]);
  /* decoy edges among non-path-adjacent pairs */
  for(int i=0;i<NENT;i++)for(int j=0;j<NENT;j++){
    if(i==j)continue;
    int ispath=0; for(int k=0;k<L;k++)if(w->path[k]==i&&w->path[k+1]==j)ispath=1;
    if(!ispath && (randbelow(100)<decoy_pct)) adj_set(&w->facts,i,j);
  }
  if(!negative){
    /* positive query: start=path[0], end=path[L] (distance L) */
    w->qs=w->path[0]; w->qt=w->path[L]; w->dist=L;
  } else {
    /* negative query: pick a pair likely unreachable (reverse path end->start) */
    w->qs=w->path[L]; w->qt=w->path[0]; w->dist=L;
  }
  Adj cl; tclosure(&w->facts,&cl);
  w->label = adj_test(&cl,w->qs,w->qt);
}

/* ---------------- closure-primitive length scaling ---------------- */
/* hard join layers needed to derive the query vs path length; constructive check */
static int gate_primitive_scaling(int nworlds){
  int bad=0;
  printf("PRIMITIVE-SCALING (hard join layers to derive query, by path length)\n");
  for(int L=2;L<=10;L++){
    int layers_needed_max=0, solved=0;
    for(int i=0;i<nworlds;i++){
      rng_state = mix64((uint64_t)(L*1000+i)*0x9E3779B97F4A7C15ULL)|1ULL;
      ChainWorld w; make_chain(&w,L,10,0);
      Adj cur=w.facts, nxt; int layers=0;
      while(!adj_test(&cur,w.qs,w.qt) && layers<NENT){ join_step(&cur,&nxt); cur=nxt; layers++; }
      if(adj_test(&cur,w.qs,w.qt)){ solved++; if(layers>layers_needed_max)layers_needed_max=layers; }
    }
    printf("  L=%2d solved=%d/%d max_layers=%d\n",L,solved,nworlds,layers_needed_max);
    if(solved!=nworlds)bad++;
  }
  printf("PRIMITIVE-SCALING %s (primitive derives every length with <=NENT layers)\n",bad?"FAIL":"PASS");
  return bad?1:0;
}

/* ---------------- MLP baseline (trainable) ---------------- */
/* input: adjacency flattened (NPAIR) + query one-hots (2*NENT). output: reachability logit.
 * single hidden layer, sigmoid BCE. Trained on short paths, tested on long. */
#define MLP_IN (NPAIR + 2*NENT)
#ifndef MLP_H
#define MLP_H 64
#endif
typedef struct {
  double W1[MLP_H*MLP_IN], b1[MLP_H];
  double W2[MLP_H], b2;
} MLP;
static double sigm(double x){ return x>=0?1.0/(1.0+exp(-x)):exp(x)/(1.0+exp(x)); }

static void mlp_input(const ChainWorld *w, double *x){
  for(int i=0;i<NENT;i++)for(int j=0;j<NENT;j++) x[i*NENT+j]=adj_test(&w->facts,i,j)?1.0:0.0;
  for(int i=0;i<NENT;i++){ x[NPAIR+i]=(i==w->qs)?1.0:0.0; x[NPAIR+NENT+i]=(i==w->qt)?1.0:0.0; }
}
static double mlp_forward(const MLP *m, const double *x, double *h){
  double logit=m->b2;
  for(int j=0;j<MLP_H;j++){
    double s=m->b1[j];
    for(int k=0;k<MLP_IN;k++)s+=m->W1[j*MLP_IN+k]*x[k];
    h[j]=tanh(s);
    logit+=m->W2[j]*h[j];
  }
  return logit;
}
static void mlp_init(MLP *m, uint64_t seed){
  rng_state=mix64(seed)|1ULL;
  double s1=1.0/sqrt((double)MLP_IN), s2=1.0/sqrt((double)MLP_H);
  for(int i=0;i<MLP_H*MLP_IN;i++)m->W1[i]=((double)(nextrand()>>11)/9007199254740992.0*2-1)*s1;
  for(int j=0;j<MLP_H;j++){m->b1[j]=0;m->W2[j]=((double)(nextrand()>>11)/9007199254740992.0*2-1)*s2;}
  m->b2=0;
}
/* BCE loss + gradient */
static double mlp_loss_grad(const MLP *m, const double *x, double label, double *gW1, double *gb1, double *gW2, double *gb2){
  double h[MLP_H]; double logit=mlp_forward(m,x,h);
  double p=sigm(logit);
  double loss=-(label*log(p+1e-12)+(1-label)*log(1-p+1e-12));
  double dl=p-label;   /* dLoss/dlogit */
  if(gW1){
    *gb2+=dl;
    for(int j=0;j<MLP_H;j++){
      double dh=dl*m->W2[j]*(1-h[j]*h[j]);
      gW2[j]+=dl*h[j];
      gb1[j]+=dh;
      for(int k=0;k<MLP_IN;k++)gW1[j*MLP_IN+k]+=dh*x[k];
    }
  }
  return loss;
}

typedef struct { ChainWorld *w; int n; } Dataset;
static Dataset gen_dataset(int n, int Lmin, int Lmax, int decoy, uint64_t seed){
  Dataset d; d.w=calloc(n,sizeof(ChainWorld)); d.n=n;
  rng_state=mix64(seed)|1ULL;
  for(int i=0;i<n;i++){
    int L=Lmin+randbelow(Lmax-Lmin+1);
    make_chain(&d.w[i],L,decoy, randbelow(2));   /* mix positive/negative */
  }
  return d;
}
static double mlp_eval(const MLP *m, const Dataset *d){
  int correct=0; double x[MLP_IN],h[MLP_H];
  for(int i=0;i<d->n;i++){
    mlp_input(&d->w[i],x);
    double logit=mlp_forward(m,x,h);
    int pred=(logit>0)?1:0;
    if(pred==d->w[i].label)correct++;
  }
  return (double)correct/d->n;
}
static void mlp_train(MLP *m, const Dataset *tr, int epochs, double lr){
  double gW1[MLP_H*MLP_IN],gb1[MLP_H],gW2[MLP_H],gb2;
  double x[MLP_IN];
  for(int ep=0;ep<epochs;ep++){
    memset(gW1,0,sizeof gW1);memset(gb1,0,sizeof gb1);memset(gW2,0,sizeof gW2);gb2=0;
    for(int i=0;i<tr->n;i++){
      mlp_input(&tr->w[i],x);
      mlp_loss_grad(m,x,tr->w[i].label,gW1,gb1,gW2,&gb2);
    }
    double inv=1.0/tr->n;
    for(int k=0;k<MLP_H*MLP_IN;k++)m->W1[k]-=lr*gW1[k]*inv;
    for(int j=0;j<MLP_H;j++){m->b1[j]-=lr*gb1[j]*inv;m->W2[j]-=lr*gW2[j]*inv;}
    m->b2-=lr*gb2*inv;
  }
}

static int gate_mlp_extrapolation(void){
  Dataset tr=gen_dataset(400,2,4,0,101);    /* train L=2..4, no decoys (clean length signal) */
  Dataset te_short=gen_dataset(200,2,4,0,202);
  Dataset te_long=gen_dataset(200,6,10,0,303);  /* test L=6..10 */
  MLP m; mlp_init(&m,777);
  printf("MLP-EXTRAP train L2-4 (n=%d), test short L2-4 / long L6-10 (n=%d each), H=%d, decoy=0\n",tr.n,te_short.n,MLP_H);
  for(int ep=0;ep<=400;ep++){
    if(ep>0)mlp_train(&m,&tr,1,0.05);
    if(ep%100==0){
      double a=mlp_eval(&m,&tr),b=mlp_eval(&m,&te_short),c=mlp_eval(&m,&te_long);
      printf("  epoch %3d train=%.3f test_short=%.3f test_long=%.3f\n",ep,a,b,c);
    }
  }
  double fin_short=mlp_eval(&m,&te_short), fin_long=mlp_eval(&m,&te_long);
  printf("MLP-EXTRAP-DONE short=%.3f long=%.3f gap=%.3f\n",fin_short,fin_long,fin_short-fin_long);
  free(tr.w);free(te_short.w);free(te_long.w);
  return 0;
}

#ifndef RC_CHAIN_NO_MAIN
int main(int argc, char **argv){
  int nworlds=30, mlp=0;
  for(int i=1;i<argc;i++){
    if(!strcmp(argv[i],"--worlds")&&i+1<argc)nworlds=atoi(argv[++i]);
    else if(!strcmp(argv[i],"--mlp"))mlp=1;
  }
  if(mlp)return gate_mlp_extrapolation();
  return gate_primitive_scaling(nworlds);
}
#endif