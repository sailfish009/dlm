/* Stacked-attention baseline for chain reachability (0253 item 5).
 * Permutation-equivariant entity tokens, L attention layers, readout on (src,tgt).
 * Forward + analytic backward + gradcheck. Trained short, tested long (item 6).
 */
#define RC_CHAIN_NO_MAIN
#include "rc_chain.c"

#ifndef D
#define D 32
#endif
#ifndef ALAYERS
#define ALAYERS 3
#endif
#define FIN (2*NENT+2)
#define LNL 1e-5

typedef struct {
  double We[D*FIN], be[D];
  double Wq[ALAYERS][D*D], Wk[ALAYERS][D*D], Wv[ALAYERS][D*D], Wo[ALAYERS][D*D];
  double g1[ALAYERS][D], be1[ALAYERS][D];
  double W1[ALAYERS][D*D], fb1[ALAYERS][D], W2[ALAYERS][D*D], fb2[ALAYERS][D];
  double g2[ALAYERS][D], be2[ALAYERS][D];
  double gf[D], bef[D];
  double Wr[3*D], br;
} Attn;

typedef struct {
  double h[NENT][D], ln1[NENT][D], q[NENT][D], k[NENT][D], v[NENT][D];
  double att[NENT][NENT], ao[NENT][D], h1[NENT][D], ln2[NENT][D], pre[NENT][D], act[NENT][D];
} ALayer;

static double gelu(double x){ double u=0.7978845608028654*(x+0.044715*x*x*x); double t=tanh(u); return 0.5*x*(1+t); }
static double gelu_d(double x){ double u=0.7978845608028654*(x+0.044715*x*x*x); double t=tanh(u); double du=0.7978845608028654*(1+3*0.044715*x*x); return 0.5*(1+t)+0.5*x*(1-t*t)*du; }
static void ln_fwd(const double*x,const double*g,const double*b,double*y,double*xh,double*inv){
  double mu=0; for(int i=0;i<D;i++)mu+=x[i]; mu/=D;
  double var=0; for(int i=0;i<D;i++){double d=x[i]-mu;var+=d*d;} var/=D;
  double iv=1.0/sqrt(var+LNL); *inv=iv;
  for(int i=0;i<D;i++){xh[i]=(x[i]-mu)*iv;y[i]=xh[i]*g[i]+b[i];}
}
static void ln_bwd(const double*dy,const double*xh,double inv,const double*g,double*dx,double*dg,double*db){
  double s1=0,s2=0;
  for(int i=0;i<D;i++){double dxh=dy[i]*g[i];dg[i]+=dy[i]*xh[i];db[i]+=dy[i];s1+=dxh;s2+=dxh*xh[i];}
  for(int i=0;i<D;i++){double dxh=dy[i]*g[i];dx[i]+=inv*(dxh-s1/D-xh[i]*s2/D);}
}

static void attn_input(const ChainWorld*w,double x[NENT][FIN]){
  for(int i=0;i<NENT;i++){
    for(int j=0;j<NENT;j++){ x[i][j]=adj_test(&w->facts,i,j)?1.0:0.0; x[i][NENT+j]=adj_test(&w->facts,j,i)?1.0:0.0; }
    x[i][2*NENT]=(i==w->qs)?1.0:0.0; x[i][2*NENT+1]=(i==w->qt)?1.0:0.0;
  }
}

static Attn *g_ap; static ALayer g_al[ALAYERS];
static double g_h0[NENT][D], g_hf[NENT][D], g_xh0[NENT][D], g_xhf[NENT][D];
static double g_hfin[NENT][D], g_x0[NENT][FIN];
static double g_readin[3*D]; static int g_qs,g_qt;

static void attn_forward(const Attn*p,const double x[NENT][FIN],double*logit){
  for(int i=0;i<NENT;i++)for(int d=0;d<D;d++){
    double s=p->be[d]; for(int k=0;k<FIN;k++)s+=p->We[d*FIN+k]*x[i][k]; g_h0[i][d]=s;
  }
  double h[NENT][D]; memcpy(h,g_h0,sizeof h);
  for(int l=0;l<ALAYERS;l++){
    ALayer*lc=&g_al[l]; memcpy(lc->h,h,sizeof h);
    double xh[D],inv;
    for(int i=0;i<NENT;i++)ln_fwd(h[i],p->g1[l],p->be1[l],lc->ln1[i],xh,&inv);
    for(int i=0;i<NENT;i++)for(int r=0;r<D;r++){
      double sq=0,sk=0,sv=0;
      for(int d=0;d<D;d++){sq+=p->Wq[l][r*D+d]*lc->ln1[i][d];sk+=p->Wk[l][r*D+d]*lc->ln1[i][d];sv+=p->Wv[l][r*D+d]*lc->ln1[i][d];}
      lc->q[i][r]=sq;lc->k[i][r]=sk;lc->v[i][r]=sv;
    }
    double scale=1.0/sqrt((double)D);
    for(int i=0;i<NENT;i++){
      double mx=-1e30,sc[NENT];
      for(int j=0;j<NENT;j++){double s=0;for(int d=0;d<D;d++)s+=lc->q[i][d]*lc->k[j][d];s*=scale;sc[j]=s;if(s>mx)mx=s;}
      double z=0; for(int j=0;j<NENT;j++){double e=exp(sc[j]-mx);lc->att[i][j]=e;z+=e;}
      for(int j=0;j<NENT;j++)lc->att[i][j]/=z;
      for(int d=0;d<D;d++){double s=0;for(int j=0;j<NENT;j++)s+=lc->att[i][j]*lc->v[j][d];lc->ao[i][d]=s;}
    }
    for(int i=0;i<NENT;i++)for(int d=0;d<D;d++){
      double s=0;for(int k=0;k<D;k++)s+=p->Wo[l][d*D+k]*lc->ao[i][k];
      lc->h1[i][d]=h[i][d]+s;
    }
    for(int i=0;i<NENT;i++)ln_fwd(lc->h1[i],p->g2[l],p->be2[l],lc->ln2[i],xh,&inv);
    for(int i=0;i<NENT;i++){
      for(int f=0;f<D;f++){double s=p->fb1[l][f];for(int d=0;d<D;d++)s+=p->W1[l][f*D+d]*lc->ln2[i][d];lc->pre[i][f]=s;lc->act[i][f]=gelu(s);}
      for(int d=0;d<D;d++){double s=p->fb2[l][d];for(int f=0;f<D;f++)s+=p->W2[l][d*D+f]*lc->act[i][f];h[i][d]=lc->h1[i][d]+s;}
    }
  }
  double inv;
  memcpy(g_hfin,h,sizeof h);
  for(int i=0;i<NENT;i++)ln_fwd(h[i],p->gf,p->bef,g_hf[i],g_xhf[i],&inv);
  for(int d=0;d<D;d++){g_readin[d]=g_hf[g_qs][d];g_readin[D+d]=g_hf[g_qt][d];g_readin[2*D+d]=g_hf[g_qs][d]*g_hf[g_qt][d];}
  double s=p->br; for(int k=0;k<3*D;k++)s+=p->Wr[k]*g_readin[k];
  *logit=s;
}

/* backward: given dlogit, accumulate grads into g (Attn). returns dx (input grad, optional). */
static void attn_backward(const Attn*p,double dlogit,Attn*g){
  double dhf[NENT][D]; memset(dhf,0,sizeof dhf);
  /* readout */
  g->br+=dlogit;
  double drin[3*D];
  for(int k=0;k<3*D;k++){g->Wr[k]+=dlogit*g_readin[k];drin[k]=dlogit*p->Wr[k];}
  for(int d=0;d<D;d++){
    dhf[g_qs][d]+=drin[d]+drin[2*D+d]*g_hf[g_qt][d];
    dhf[g_qt][d]+=drin[D+d]+drin[2*D+d]*g_hf[g_qs][d];
  }
  /* final LN backward */
  double dh[NENT][D]; memset(dh,0,sizeof dh);
  for(int i=0;i<NENT;i++){
    double inv; double xh[D],tmp[D]; ln_fwd(g_hfin[i],p->gf,p->bef,tmp,xh,&inv);
    double dx[D]; memset(dx,0,sizeof dx);
    ln_bwd(dhf[i],xh,inv,p->gf,dx,g->gf,g->bef);
    for(int d=0;d<D;d++)dh[i][d]+=dx[d];
  }
  /* layers backward */
  for(int l=ALAYERS-1;l>=0;l--){
    ALayer*lc=&g_al[l];
    double dh1[NENT][D],dln2[NENT][D],dpre[NENT][D],dao[NENT][D],dq[NENT][D],dk[NENT][D],dv[NENT][D];
    memset(dh1,0,sizeof dh1);memset(dao,0,sizeof dao);memset(dq,0,sizeof dq);memset(dk,0,sizeof dk);memset(dv,0,sizeof dv);
    /* FFN backward */
    for(int i=0;i<NENT;i++){
      for(int d=0;d<D;d++)dh1[i][d]+=dh[i][d];
      for(int f=0;f<D;f++){double s=0;for(int d=0;d<D;d++)s+=p->W2[l][d*D+f]*dh[i][d];dpre[i][f]=s*gelu_d(lc->pre[i][f]);}
      for(int d=0;d<D;d++)g->fb2[l][d]+=dh[i][d];
      for(int d=0;d<D;d++)for(int f=0;f<D;f++)g->W2[l][d*D+f]+=dh[i][d]*lc->act[i][f];
      for(int f=0;f<D;f++){g->fb1[l][f]+=dpre[i][f];for(int d=0;d<D;d++)g->W1[l][f*D+d]+=dpre[i][f]*lc->ln2[i][d];}
      memset(dln2[i],0,sizeof(double)*D);
      for(int d=0;d<D;d++){double s=0;for(int f=0;f<D;f++)s+=p->W1[l][f*D+d]*dpre[i][f];dln2[i][d]=s;}
    }
    /* LN2 backward */
    for(int i=0;i<NENT;i++){
      double inv,xh[D],tmp[D]; ln_fwd(lc->h1[i],p->g2[l],p->be2[l],tmp,xh,&inv);
      double dx[D];memset(dx,0,sizeof dx);
      ln_bwd(dln2[i],xh,inv,p->g2[l],dx,g->g2[l],g->be2[l]);
      for(int d=0;d<D;d++)dh1[i][d]+=dx[d];
    }
    /* attention out proj backward */
    for(int i=0;i<NENT;i++){
      for(int d=0;d<D;d++)for(int k=0;k<D;k++)g->Wo[l][d*D+k]+=dh1[i][d]*lc->ao[i][k];
      for(int k=0;k<D;k++){double s=0;for(int d=0;d<D;d++)s+=p->Wo[l][d*D+k]*dh1[i][d];dao[i][k]=s;}
    }
    /* attention backward */
    double scale=1.0/sqrt((double)D);
    for(int i=0;i<NENT;i++){
      double datt[NENT]; memset(datt,0,sizeof datt);
      for(int j=0;j<NENT;j++)for(int d=0;d<D;d++){
        datt[j]+=dao[i][d]*lc->v[j][d];
        dv[j][d]+=lc->att[i][j]*dao[i][d];
      }
      double sdot=0; for(int j=0;j<NENT;j++)sdot+=lc->att[i][j]*datt[j];
      for(int j=0;j<NENT;j++){
        double ds=lc->att[i][j]*(datt[j]-sdot)*scale;
        for(int d=0;d<D;d++){dq[i][d]+=ds*lc->k[j][d];dk[j][d]+=ds*lc->q[i][d];}
      }
    }
    /* qkv proj + LN1 backward */
    double din[NENT][D]; memset(din,0,sizeof din);
    for(int i=0;i<NENT;i++){
      for(int r=0;r<D;r++)for(int d=0;d<D;d++){
        g->Wq[l][r*D+d]+=dq[i][r]*lc->ln1[i][d];
        g->Wk[l][r*D+d]+=dk[i][r]*lc->ln1[i][d];
        g->Wv[l][r*D+d]+=dv[i][r]*lc->ln1[i][d];
      }
      double dln1[D];memset(dln1,0,sizeof dln1);
      for(int d=0;d<D;d++){double s=0;for(int r=0;r<D;r++)s+=p->Wq[l][r*D+d]*dq[i][r]+p->Wk[l][r*D+d]*dk[i][r]+p->Wv[l][r*D+d]*dv[i][r];dln1[d]=s;}
      double inv,xh[D],tmp[D]; ln_fwd(lc->h[i],p->g1[l],p->be1[l],tmp,xh,&inv);
      double dx[D];memset(dx,0,sizeof dx);
      ln_bwd(dln1,xh,inv,p->g1[l],dx,g->g1[l],g->be1[l]);
      for(int d=0;d<D;d++)din[i][d]=dh1[i][d]+dx[d];
    }
    memcpy(dh,din,sizeof dh);
  }
  /* embedding backward */
  for(int i=0;i<NENT;i++)for(int d=0;d<D;d++){
    g->be[d]+=dh[i][d];
    /* input grad would go here; not needed for param gradcheck */
    for(int k=0;k<FIN;k++)g->We[d*FIN+k]+=dh[i][d]*g_x0[i][k];
  }
}

static void attn_init(Attn*p,uint64_t seed){
  rng_state=mix64(seed)|1ULL;
  double (*r)(void)=NULL;(void)r;
  #define RR (((double)(nextrand()>>11)/9007199254740992.0)*2-1)
  double se=1.0/sqrt((double)FIN),sd=1.0/sqrt((double)D);
  for(int i=0;i<D*FIN;i++)p->We[i]=RR*se;
  for(int d=0;d<D;d++)p->be[d]=0;
  for(int l=0;l<ALAYERS;l++){
    for(int i=0;i<D*D;i++){p->Wq[l][i]=RR*sd;p->Wk[l][i]=RR*sd;p->Wv[l][i]=RR*sd;p->Wo[l][i]=RR*sd;p->W1[l][i]=RR*sd;p->W2[l][i]=RR*sd;}
    for(int d=0;d<D;d++){p->g1[l][d]=1;p->be1[l][d]=0;p->g2[l][d]=1;p->be2[l][d]=0;p->fb1[l][d]=0;p->fb2[l][d]=0;}
  }
  for(int d=0;d<D;d++){p->gf[d]=1;p->bef[d]=0;}
  for(int k=0;k<3*D;k++)p->Wr[k]=RR*sd;
  p->br=0;
  #undef RR
}
static long attn_nparam(void){ return sizeof(Attn)/sizeof(double); }

static int gate_gradcheck(void){
  ChainWorld w; rng_state=mix64(42)|1ULL; make_chain(&w,4,0,0);
  g_qs=w.qs;g_qt=w.qt; attn_input(&w,g_x0);
  Attn p,g; attn_init(&p,777); memset(&g,0,sizeof g);
  double logit; attn_forward(&p,g_x0,&logit);
  double label=w.label; double pr=sigm(logit);
  double dlogit=pr-label;
  attn_backward(&p,dlogit,&g);
  double eps=1e-6,max_abs=0,max_rel=0; double*pp=(double*)&p;double*gg=(double*)&g;
  long n=attn_nparam();
  for(long i=0;i<n;i++){
    double o=pp[i];
    pp[i]=o+eps; double lp; attn_forward(&p,g_x0,&lp); double Lp=-(label*log(sigm(lp)+1e-12)+(1-label)*log(1-sigm(lp)+1e-12));
    pp[i]=o-eps; double lm; attn_forward(&p,g_x0,&lm); double Lm=-(label*log(sigm(lm)+1e-12)+(1-label)*log(1-sigm(lm)+1e-12));
    pp[i]=o;
    double num=(Lp-Lm)/(2*eps),ana=gg[i];
    double ad=fabs(num-ana); if(ad>max_abs)max_abs=ad;
    double den=fabs(num)+fabs(ana)+1e-8; double rel=ad/den;
    if(rel>max_rel&&fabs(num)+fabs(ana)>1e-7)max_rel=rel;
  }
  int ok=max_abs<1e-4;
  printf("ATTN-GRADCHECK params=%ld L=%d D=%d max_abs=%.3e max_rel_small=%.3e %s\n",n,ALAYERS,D,max_abs,max_rel,ok?"PASS":"FAIL");
  return ok?0:1;
}

static Attn g_grad, g_am, g_av;
static void attn_train(Attn*p,const Dataset*d,int epochs,double lr,int verbose){
  memset(&g_am,0,sizeof g_am);memset(&g_av,0,sizeof g_av);
  double*pp=(double*)p;double*gg=(double*)&g_grad;double*mm=(double*)&g_am;double*vv=(double*)&g_av;
  long n=attn_nparam(); double x[NENT][FIN];
  for(int ep=0;ep<epochs;ep++){
    memset(&g_grad,0,sizeof g_grad); double loss=0;
    for(int i=0;i<d->n;i++){
      const ChainWorld*w=&d->w[i]; g_qs=w->qs;g_qt=w->qt; attn_input(w,g_x0);
      double logit; attn_forward(p,g_x0,&logit); double pr=sigm(logit);
      loss+=-(w->label*log(pr+1e-12)+(1-w->label)*log(1-pr+1e-12));
      attn_backward(p,pr-w->label,&g_grad);
    }
    int t=ep+1; double inv=1.0/d->n;
    for(long k=0;k<n;k++){
      double gk=gg[k]*inv;
      mm[k]=0.9*mm[k]+0.1*gk; vv[k]=0.999*vv[k]+0.001*gk*gk;
      double mh=mm[k]/(1-pow(0.9,t)),vh=vv[k]/(1-pow(0.999,t));
      pp[k]-=lr*mh/(sqrt(vh)+1e-8);
    }
    if(verbose&&(ep%50==0||ep==epochs-1))printf("  epoch %3d loss=%.4f\n",ep,loss/d->n);
  }
}
static double attn_eval(const Attn*p,const Dataset*d){
  int correct=0; double x[NENT][FIN];
  for(int i=0;i<d->n;i++){
    const ChainWorld*w=&d->w[i]; g_qs=w->qs;g_qt=w->qt; attn_input(w,g_x0);
    double logit; attn_forward(p,g_x0,&logit);
    if((logit>0?1:0)==w->label)correct++;
  }
  return (double)correct/d->n;
}
static int gate_attn_extrapolation(int epochs,int decoy){
  Dataset tr=gen_dataset(400,2,4,decoy,101);
  Dataset ts=gen_dataset(200,2,4,decoy,202);
  Dataset tl=gen_dataset(200,6,10,decoy,303);
  Attn p; attn_init(&p,777);
  printf("ATTN-EXTRAP train L2-4 (n=%d) test short/long (n=%d) L=%d D=%d params=%ld decoy=%d\n",tr.n,ts.n,ALAYERS,D,attn_nparam(),decoy);
  for(int ep=0;ep<=epochs;ep++){
    if(ep>0)attn_train(&p,&tr,1,0.001,0);
    if(ep%50==0||ep==epochs){
      double a=attn_eval(&p,&tr),b=attn_eval(&p,&ts),c=attn_eval(&p,&tl);
      printf("  epoch %3d train=%.3f test_short=%.3f test_long=%.3f\n",ep,a,b,c);
    }
  }
  double fs=attn_eval(&p,&ts),fl=attn_eval(&p,&tl);
  printf("ATTN-EXTRAP-DONE short=%.3f long=%.3f gap=%.3f\n",fs,fl,fs-fl);
  free(tr.w);free(ts.w);free(tl.w); return 0;
}

int main(int argc,char**argv){
  int gc=0,extrap=0,epochs=300,decoy=0; for(int i=1;i<argc;i++){
    if(!strcmp(argv[i],"--gradcheck"))gc=1;
    else if(!strcmp(argv[i],"--extrap"))extrap=1;
    else if(!strcmp(argv[i],"--epochs")&&i+1<argc)epochs=atoi(argv[++i]);
    else if(!strcmp(argv[i],"--decoy")&&i+1<argc)decoy=atoi(argv[++i]);
  }
  if(gc)return gate_gradcheck();
  if(extrap)return gate_attn_extrapolation(epochs,decoy);
  printf("use --gradcheck or --extrap\n"); return 0;
}