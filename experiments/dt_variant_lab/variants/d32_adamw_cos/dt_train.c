/* Full DT-1 selector training/inference in C/LLVM (no MLIR).
 * Float64 training on the compact valid-rule sequence; Adam + BCE.
 * This is a research port, not the Maru trusted kernel. */
#include "train_fixture.h"
#include "fixture_all.h"
#include "variant_layout.h"
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#define D 32
#define F 64
#define H 1
#define MAXH 8
#define T 9
_Static_assert(T >= MAXV + 1, "T must hold image + all valid rules");
#define PSIZE V_PSIZE
#define NEPOCH 60
#define NLAYER 6
#define LR 0.001
#define POSW 30.0
#define WD 0.01
#define DROP 0.0
#define SCHED 1
#define SCHED_STEPS 600

static double P[PSIZE], G[PSIZE], M[PSIZE], V[PSIZE];
static int fold_seed = 61;
static int sched_step = 0;


typedef struct {
 int nt;
 double xin[T][D], q[T][D], k[T][D], v[T][D], attn[MAXH][T][T], araw[T][D], mha[T][D];
 double pre1[T][D], x1[T][D], mu1[T], var1[T];
 double f1pre[T][F], f1[T][F], f2[T][D];
 double pre2[T][D], x2[T][D], mu2[T], var2[T];
} Cache;

static unsigned long rng_state=123456789;
static double urand(void){ rng_state = rng_state*6364136223846793005UL + 1; return ((rng_state>>11)&0xffffffffUL)/(double)0x100000000UL; }
static void init_params(int seed){ rng_state=seed; for(int i=0;i<PSIZE;i++){P[i]=0;G[i]=0;M[i]=0;V[i]=0;}
  for(int i=0;i<D*196;i++)P[IMG_W+i]=(urand()*2-1)/sqrt(196.0);
  for(int r=0;r<D;r++)P[IMG_B+r]=0;
  for(int i=0;i<D*16;i++)P[RULE_W+i]=(urand()*2-1)/4.0;
  for(int r=0;r<D;r++)P[RULE_B+r]=0;
  for(int i=0;i<3*D*D;i++)P[IN_W+i]=(urand()*2-1)/sqrt((double)D);
  for(int i=0;i<3*D;i++)P[IN_B+i]=0;
  for(int i=0;i<D*D;i++)P[OUT_W+i]=(urand()*2-1)/sqrt((double)D);
  for(int i=0;i<D;i++)P[OUT_B+i]=0;
  for(int i=0;i<F*D;i++)P[L1_W+i]=(urand()*2-1)/sqrt((double)D);
  for(int i=0;i<F;i++)P[L1_B+i]=0;
  for(int i=0;i<D*F;i++)P[L2_W+i]=(urand()*2-1)/sqrt((double)F);
  for(int i=0;i<D;i++)P[L2_B+i]=0;
  for(int i=0;i<D;i++){P[N1G+i]=1;P[N1B+i]=0;P[N2G+i]=1;P[N2B+i]=0;}
  for(int i=0;i<D;i++)P[FW+i]=(urand()*2-1)/sqrt((double)D);
  P[FB]=0;
}
static inline double dotd(const double*a,const double*b,int n){double s=0;for(int i=0;i<n;i++)s+=a[i]*b[i];return s;}
static void mvd(const double*w,int rows,int cols,const double*x,const double*b,double*out){for(int r=0;r<rows;r++){double s=0;for(int c=0;c<cols;c++)s+=w[r*cols+c]*x[c];out[r]=s+b[r];}}
static void lnd(const double*x,const double*g,const double*b,double*out,double*mu,double*var){double m=0;for(int i=0;i<D;i++)m+=x[i];m/=D;double v=0;for(int i=0;i<D;i++){double d=x[i]-m;v+=d*d;}v/=D;double inv=1.0/sqrt(v+1e-5);for(int i=0;i<D;i++)out[i]=(x[i]-m)*inv*g[i]+b[i];*mu=m;*var=v;}
static void softd(const double*s,int n,double*out){double m=s[0];for(int i=1;i<n;i++)if(s[i]>m)m=s[i];double z=0, e[T];for(int i=0;i<n;i++){e[i]=exp(s[i]-m);z+=e[i];}for(int i=0;i<n;i++)out[i]=e[i]/z;}
static void projectd(const double toks[T][D],int nt,const double*w,int rows,const double*b,double out[T][D]){for(int t=0;t<nt;t++)mvd(w,rows,D,toks[t],b,out[t]);}
static void mha_f(const double xin[T][D],int nt,Cache*c){const double*inw=P+IN_W,*inb=P+IN_B,*ow=P+OUT_W,*ob=P+OUT_B;const int hd=D/H;for(int t=0;t<nt;t++){mvd(inw,D,D,xin[t],inb,c->q[t]);mvd(inw+D*D,D,D,xin[t],inb+D,c->k[t]);mvd(inw+2*D*D,D,D,xin[t],inb+2*D,c->v[t]);}memset(c->araw,0,sizeof(c->araw));for(int h=0;h<H;h++){int off=h*hd;for(int i=0;i<nt;i++){double sc[T];for(int j=0;j<nt;j++){double ss=0;for(int d=0;d<hd;d++)ss+=c->q[i][off+d]*c->k[j][off+d];sc[j]=ss/sqrt((double)hd);}softd(sc,nt,c->attn[h][i]);for(int j=0;j<nt;j++)for(int d=0;d<hd;d++)c->araw[i][off+d]+=c->attn[h][i][j]*c->v[j][off+d];}}projectd(c->araw,nt,ow,D,ob,c->mha);}
static void block_f(const double xin[T][D],int nt,Cache*c){memcpy(c->xin,xin,sizeof(double)*D*nt);c->nt=nt;mha_f(xin,nt,c);for(int t=0;t<nt;t++){for(int d=0;d<D;d++)c->pre1[t][d]=xin[t][d]+c->mha[t][d];lnd(c->pre1[t],P+N1G,P+N1B,c->x1[t],&c->mu1[t],&c->var1[t]);mvd(P+L1_W,F,D,c->x1[t],P+L1_B,c->f1pre[t]);for(int i=0;i<F;i++)c->f1[t][i]=c->f1pre[t][i]>0?c->f1pre[t][i]:0;mvd(P+L2_W,D,F,c->f1[t],P+L2_B,c->f2[t]);for(int d=0;d<D;d++)c->pre2[t][d]=c->x1[t][d]+c->f2[t][d];lnd(c->pre2[t],P+N2G,P+N2B,c->x2[t],&c->mu2[t],&c->var2[t]);}}
static void ln_back(const double*x,const double*dy,const double*g,double*dx,double*dg,double*db,int n,double mu,double var){double inv=1.0/sqrt(var+1e-5);double sx=0,sxx=0;for(int i=0;i<n;i++){double xh=(x[i]-mu)*inv;dg[i]+=dy[i]*xh;db[i]+=dy[i];double dh=dy[i]*g[i];sx+=dh;sxx+=dh*(x[i]-mu);}for(int i=0;i<n;i++){double dh=dy[i]*g[i];dx[i]=inv*dh - (x[i]-mu)*inv*inv*inv*sxx/n - inv*sx/n;}}
static void block_b(Cache*c,const double dx2[T][D],double dxin[T][D]){int nt=c->nt;double dpre2[T][D],dx1[T][D],df2[T][D],df1[T][F],df1p[T][F],dmha[T][D],daraw[T][D];for(int t=0;t<nt;t++)ln_back(c->pre2[t],dx2[t],P+N2G,dpre2[t],G+N2G,G+N2B,D,c->mu2[t],c->var2[t]);for(int t=0;t<nt;t++){for(int r=0;r<D;r++){G[L2_B+r]+=dpre2[t][r];for(int c1=0;c1<F;c1++)G[L2_W+r*F+c1]+=dpre2[t][r]*c->f1[t][c1];}for(int c1=0;c1<F;c1++){double s=0;for(int r=0;r<D;r++)s+=P[L2_W+r*F+c1]*dpre2[t][r];df1[t][c1]=s;}for(int c1=0;c1<F;c1++)df1p[t][c1]=c->f1pre[t][c1]>0?df1[t][c1]:0;for(int r=0;r<F;r++){G[L1_B+r]+=df1p[t][r];for(int c1=0;c1<D;c1++)G[L1_W+r*D+c1]+=df1p[t][r]*c->x1[t][c1];}for(int c1=0;c1<D;c1++){double s=0;for(int r=0;r<F;r++)s+=P[L1_W+r*D+c1]*df1p[t][r];dx1[t][c1]=dpre2[t][c1]+s;}}
double dpre1[T][D];for(int t=0;t<nt;t++)ln_back(c->pre1[t],dx1[t],P+N1G,dpre1[t],G+N1G,G+N1B,D,c->mu1[t],c->var1[t]);for(int t=0;t<nt;t++)for(int d=0;d<D;d++){dxin[t][d]=dpre1[t][d];dmha[t][d]=dpre1[t][d];}
for(int t=0;t<nt;t++){for(int r=0;r<D;r++){G[OUT_B+r]+=dmha[t][r];for(int c1=0;c1<D;c1++)G[OUT_W+r*D+c1]+=dmha[t][r]*c->araw[t][c1];}for(int c1=0;c1<D;c1++){double s=0;for(int r=0;r<D;r++)s+=P[OUT_W+r*D+c1]*dmha[t][r];daraw[t][c1]=s;}}
double datt[MAXH][T][T],dv[T][D];memset(dv,0,sizeof(dv));const int hd=D/H;for(int h=0;h<H;h++){int off=h*hd;for(int i=0;i<nt;i++)for(int j=0;j<nt;j++){double ss=0;for(int d=0;d<hd;d++)ss+=daraw[i][off+d]*c->v[j][off+d];datt[h][i][j]=ss;for(int d=0;d<hd;d++)dv[j][off+d]+=c->attn[h][i][j]*daraw[i][off+d];}}
double ds[T][T],dq[T][D],dk[T][D];memset(dq,0,sizeof(dq));memset(dk,0,sizeof(dk));for(int h=0;h<H;h++){int off=h*hd;for(int i=0;i<nt;i++){double wr=0;for(int j=0;j<nt;j++)wr+=c->attn[h][i][j]*datt[h][i][j];for(int j=0;j<nt;j++){ds[i][j]=c->attn[h][i][j]*(datt[h][i][j]-wr);for(int d=0;d<hd;d++){dq[i][off+d]+=ds[i][j]*c->k[j][off+d]/sqrt((double)hd);dk[j][off+d]+=ds[i][j]*c->q[i][off+d]/sqrt((double)hd);}}}}
for(int t=0;t<nt;t++){for(int r=0;r<D;r++){G[IN_B+r]+=dq[t][r];G[IN_B+D+r]+=dk[t][r];G[IN_B+2*D+r]+=dv[t][r];for(int c1=0;c1<D;c1++){G[IN_W+r*D+c1]+=dq[t][r]*c->xin[t][c1];G[IN_W+(D+r)*D+c1]+=dk[t][r]*c->xin[t][c1];G[IN_W+(2*D+r)*D+c1]+=dv[t][r]*c->xin[t][c1];}}for(int c1=0;c1<D;c1++){double s=0;for(int r=0;r<D;r++)s+=P[IN_W+r*D+c1]*dq[t][r]+P[IN_W+(D+r)*D+c1]*dk[t][r]+P[IN_W+(2*D+r)*D+c1]*dv[t][r];dxin[t][c1]+=s;}}
}
static double train_case(int c){int nt=1+train_nv[c];double img[196];for(int i=0;i<196;i++)img[i]=train_img[c][i];double tok[T][D];mvd(P+IMG_W,D,196,img,P+IMG_B,tok[0]);for(int vi=0;vi<train_nv[c];vi++)mvd(P+RULE_W,D,16,train_feat[c][vi],P+RULE_B,tok[1+vi]);double drop[T][D];for(int t=0;t<nt;t++)for(int d=0;d<D;d++){drop[t][d]=(DROP>0.0)?1.0/(1.0-DROP):1.0;if(DROP>0.0&&urand()<DROP){tok[t][d]=0.0;drop[t][d]=0.0;}}Cache cs[NLAYER];for(int l=0;l<NLAYER;l++){block_f(tok,nt,&cs[l]);memcpy(tok,cs[l].x2,sizeof(double)*D*nt);}double out[T];for(int vi=0;vi<train_nv[c];vi++)out[vi]=dotd(P+FW,tok[1+vi],D)+P[FB];
double loss=0;double dout[T];for(int vi=0;vi<train_nv[c];vi++){double y=train_y[c][vi];double sig=1.0/(1.0+exp(-out[vi]));double lossv=-(y*POSW*log(sig+1e-15)+(1-y)*log(1-sig+1e-15));loss+=lossv;dout[vi]=(sig-y)*(y>0.5?POSW:1.0)/(double)RULE_COUNT;}
double dtok[T][D];memset(dtok,0,sizeof(dtok));for(int vi=0;vi<train_nv[c];vi++){for(int d=0;d<D;d++){G[FW+d]+=dout[vi]*tok[1+vi][d];dtok[1+vi][d]+=dout[vi]*P[FW+d];}G[FB]+=dout[vi];}
for(int l=NLAYER-1;l>=0;l--){double dxin[T][D];block_b(&cs[l],dtok,dxin);memcpy(dtok,dxin,sizeof(double)*D*nt);}
for(int t=0;t<nt;t++)for(int d=0;d<D;d++)if(drop[t][d]==0.0)dtok[t][d]=0.0;for(int r=0;r<D;r++){G[IMG_B+r]+=dtok[0][r];for(int i=0;i<196;i++)G[IMG_W+r*196+i]+=dtok[0][r]*img[i];for(int vi=0;vi<train_nv[c];vi++){G[RULE_B+r]+=dtok[1+vi][r];for(int i=0;i<16;i++)G[RULE_W+r*16+i]+=dtok[1+vi][r]*train_feat[c][vi][i];}}
return loss/(double)RULE_COUNT;}
static void adam(int step){double b1=0.9,b2=0.999,eps=1e-8;for(int i=0;i<PSIZE;i++){M[i]=b1*M[i]+(1-b1)*G[i];V[i]=b2*V[i]+(1-b2)*G[i]*G[i];double mh=M[i]/(1-pow(b1,step)),vh=V[i]/(1-pow(b2,step));double lr=LR; if(SCHED) lr=LR*0.5*(1.0+cos(3.141592653589793*(double)sched_step/(double)SCHED_STEPS)); P[i]-=lr*(mh/(sqrt(vh)+eps)+WD*P[i]);}}
static void zero_g(void){memset(G,0,sizeof(G));}
static void knn_case(int c,long*td,long*tl,int*tn){for(int p=0;p<POOL_COUNT;p++){long d=0;for(int i=0;i<196;i++){long x=case_bits[c][i]-pool_bits[p][i];d+=x*x;}int pos=*tn;for(int j=0;j<*tn;j++)if(d<=td[j]){pos=j;break;}if(pos<5){int lim=*tn<5?*tn:4;for(int j=lim;j>pos;j--){td[j]=td[j-1];tl[j]=tl[j-1];}td[pos]=d;tl[pos]=pool_labels[p];if(*tn<5)(*tn)++;}}}
static int predict(int c){int nt=1+train_nv[c];double img[196];for(int i=0;i<196;i++)img[i]=train_img[c][i];double tok[T][D];mvd(P+IMG_W,D,196,img,P+IMG_B,tok[0]);for(int vi=0;vi<train_nv[c];vi++)mvd(P+RULE_W,D,16,train_feat[c][vi],P+RULE_B,tok[1+vi]);Cache cs[NLAYER];for(int l=0;l<NLAYER;l++){block_f(tok,nt,&cs[l]);memcpy(tok,cs[l].x2,sizeof(double)*D*nt);}long td[5],tl[5];int tn=0;knn_case(c,td,tl,&tn);long cnt[10]={0};for(int i=0;i<tn;i++)cnt[tl[i]]++;int best=-1;double bs=-1e300;for(int vi=0;vi<train_nv[c];vi++){double s=dotd(P+FW,tok[1+vi],D)+P[FB]+4.0*(prior_log[cnt[rule_heads[train_valid[c][vi]]]]/65536.0);if(s>bs){bs=s;best=vi;}}return train_valid[c][best];}
int main(void){int correct=0;sched_step=0;for(int fold=0;fold<10;fold++){init_params(fold_seed+fold);int step=0;for(int ep=0;ep<NEPOCH;ep++){zero_g();int nc=0;double loss=0;for(int c=0;c<10;c++)if(c!=fold){loss+=train_case(c);nc++;}for(int i=0;i<PSIZE;i++)G[i]/=nc;step++;sched_step++;adam(step);if(ep%5==0)printf("FOLD %d EP %d LOSS %.6f\n",fold,ep,loss/nc);}int pick=predict(fold);printf("FOLD %d PICK %d\n",fold,pick);}
printf("DONE 10\n");return 0;}
