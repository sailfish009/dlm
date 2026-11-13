/* Full DT-1 inference selector on the C/LLVM backend (no MLIR).
 * Numeric selector only; the Maru proof gate is applied separately. */
#include "fixture_all.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#define D 32
#define MAXTOK 64
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
static inline long fm(long a,long b){return (a*b)>>16;}
static inline long fd(long a,long b){return b?(a*Q16)/b:0;}
static long isq(long lo,long hi,long n){while(hi-lo>1){long m=(lo+hi)/2;if(m*m<=n)lo=m;else hi=m;}return lo;}
static long isqrt(long n){if(n<=0)return 0;long h=1;while(h*h<=n)h*=2;return isq(0,h,n);}
static long fsqrt(long x){return x<=0?0:isqrt(x*Q16);}
static long fexp(long x){if(x>=0)return Q16;long t=(-x)*32;long i=t>>16;long fr=t-(i<<16);if(i>=512)return 0;long y0=exp_table[i],y1=exp_table[i+1];return y0+fm(y1-y0,fr);}
static long dot(const long*a,const long*b,int n){long s=0;for(int i=0;i<n;i++)s+=fm(a[i],b[i]);return s;}
static void mv(const long*w,int rows,int cols,const long*x,const long*b,long*out){for(int r=0;r<rows;r++){long s=0;for(int c=0;c<cols;c++)s+=fm(w[r*cols+c],x[c]);out[r]=s+b[r];}}
static void proj(long toks[MAXTOK][D],int nt,const long*w,int rows,const long*b,long out[MAXTOK][D]){for(int t=0;t<nt;t++)mv(w,rows,D,toks[t],b,out[t]);}
static void ln(const long*x,const long*g,const long*b,long*out){long mu=0;for(int i=0;i<D;i++)mu+=x[i];mu/=D;long v=0;for(int i=0;i<D;i++){long d=x[i]-mu;v+=fm(d,d);}v/=D;long inv=fd(Q16,fsqrt(v+1));for(int i=0;i<D;i++)out[i]=fm(fm(x[i]-mu,inv),g[i])+b[i];}
static void softmax(const long*s,int n,long*out){long m=s[0];for(int i=1;i<n;i++)if(s[i]>m)m=s[i];long e[MAXTOK],z=0;for(int i=0;i<n;i++){e[i]=fexp(s[i]-m);z+=e[i];}for(int i=0;i<n;i++)out[i]=z?(e[i]*Q16)/z:0;}
static void mha(long t[MAXTOK][D],int nt,const long*inw,const long*inb,const long*ow,const long*ob){long q[MAXTOK][D],k[MAXTOK][D],v[MAXTOK][D],a[MAXTOK][D],z[MAXTOK][D];for(int i=0;i<nt;i++){mv(inw,D,D,t[i],inb,q[i]);mv(inw+32*D,D,D,t[i],inb+32,k[i]);mv(inw+64*D,D,D,t[i],inb+64,v[i]);}for(int i=0;i<nt;i++){long sc[MAXTOK],w[MAXTOK];for(int j=0;j<nt;j++)sc[j]=fd(dot(q[i],k[j],D),370728);softmax(sc,nt,w);for(int d=0;d<D;d++){long s=0;for(int j=0;j<nt;j++)s+=fm(v[j][d],w[j]);a[i][d]=s;}}proj(a,nt,ow,D,ob,z);memcpy(t,z,sizeof(long)*D*nt);}
static void blk(long t[MAXTOK][D],int nt,const long*m){const long*inw=m+OFF_IN_W,*inb=m+OFF_IN_B,*ow=m+OFF_OUT_W,*ob=m+OFF_OUT_B,*l1w=m+OFF_L1_W,*l1b=m+OFF_L1_B,*l2w=m+OFF_L2_W,*l2b=m+OFF_L2_B,*n1g=m+OFF_N1G,*n1b=m+OFF_N1B,*n2g=m+OFF_N2G,*n2b=m+OFF_N2B;long orig[MAXTOK][D],x1[MAXTOK][D],f1[MAXTOK][64];memcpy(orig,t,sizeof(long)*D*nt);mha(t,nt,inw,inb,ow,ob);TRACE("ATTN",t[0],D);for(int i=0;i<nt;i++){long s[D];for(int d=0;d<D;d++)s[d]=orig[i][d]+t[i][d];ln(s,n1g,n1b,x1[i]);mv(l1w,64,D,x1[i],l1b,f1[i]);for(int j=0;j<64;j++)if(f1[i][j]<0)f1[i][j]=0;long g[D];mv(l2w,D,64,f1[i],l2b,g);for(int d=0;d<D;d++)s[d]=x1[i][d]+g[d];ln(s,n2g,n2b,t[i]);TRACE("FFN",t[0],D);}}
static int body_ok(const long*b,const long*code,int n){for(int i=0;i<n;i++){long c=code[i];int idx=c>0?(int)(c-1):(int)(-c-1);int want=c>0?1:0;if(b[idx]!=want)return 0;}return 1;}
static void feats(const long*bits,int k,long*f){const long*codes=rule_bodies[k];int n=rule_lengths[k],on=0,off=0;long si=0,sat=0;for(int i=0;i<n;i++){long c=codes[i];if(c>0)on++;else off++;si+=c>0?c-1:-c-1;if(body_ok(bits,&codes[i],1))sat+=Q16;}for(int i=0;i<10;i++)f[i]=(i==rule_heads[k])?Q16:0;f[10]=fd(n>30?30:n,30);f[11]=fd(on,n);f[12]=fd(off,n);f[13]=fd(si,196*n);f[14]=sat/n;f[15]=Q16-f[14];}
static void knn(const long*bits,long*td,long*tl,int*tn){for(int p=0;p<POOL_COUNT;p++){long d=0;for(int i=0;i<196;i++){long x=bits[i]-pool_bits[p][i];d+=x*x;}int pos=*tn;for(int j=0;j<*tn;j++)if(d<=td[j]){pos=j;break;}if(pos<5){int lim=*tn<5?*tn:4;for(int j=lim;j>pos;j--){td[j]=td[j-1];tl[j]=tl[j-1];}td[pos]=d;tl[pos]=pool_labels[p];if(*tn<5)(*tn)++;}}}
int main(void){int total=0,ok=0;for(int c=0;c<10;c++){
#ifdef M0_TRACE
trace_case=c;
#endif
const long*m=models[c];const long*bits=case_bits[c];int valid[RULE_COUNT],nv=0;for(int k=0;k<RULE_COUNT;k++)if(body_ok(bits,rule_bodies[k],rule_lengths[k]))valid[nv++]=k;long t[MAXTOK][D];int nt=1;long img[196];for(int i=0;i<196;i++)img[i]=bits[i]*Q16;mv(m+OFF_IMG_W,D,196,img,m+OFF_IMG_B,t[0]);for(int vi=0;vi<nv;vi++){long f[16];feats(bits,valid[vi],f);mv(m+OFF_RULE_W,D,16,f,m+OFF_RULE_B,t[1+vi]);nt++;}TRACE("PROJ0",t[0],D);TRACE("PROJ1",t[1],D);for(int b=0;b<6;b++){
#ifdef M0_TRACE
trace_layer=b;
#endif
blk(t,nt,m);}long sel[RULE_COUNT];for(int vi=0;vi<nv;vi++)sel[vi]=dot(m+OFF_FINAL_W,t[1+vi],D)+m[OFF_FINAL_W+32];TRACE("SEL",sel,nv);long td[5],tl[5];int tn=0;knn(bits,td,tl,&tn);long cnt[10]={0};for(int i=0;i<tn;i++)cnt[tl[i]]++;long best=-999999999;int bk=-1;printf("RESULT %d VALID",c);for(int vi=0;vi<nv;vi++)printf(" %d",valid[vi]);printf(" SEL");for(int vi=0;vi<nv;vi++)printf(" %.9f",(double)sel[vi]/Q16);printf(" PICK ");for(int vi=0;vi<nv;vi++){int k=valid[vi];long sc=sel[vi]+4*prior_log[cnt[rule_heads[k]]];if(sc>best){best=sc;bk=k;}}printf("%d HEAD %d\n",bk,bk>=0?rule_heads[bk]:-1);total++;}
printf("DONE %d\n",total);return 0;}
