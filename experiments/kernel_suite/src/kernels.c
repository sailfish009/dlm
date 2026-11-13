#include "array_view.h"
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#define Q16 65536L
static long qmul(long a,long b){return (a*b)>>16;}
static long qdiv(long a,long b){return b?(a*Q16)/b:0;}
static long qsqrt(long x){if(x<=0)return 0; long r=0; while((r+1)*(r+1)<=x)r++; return r;}
static long getv(const MaruArrayView*v,long i){return (long)mav_get(v,i);}
static void setv(const MaruArrayView*v,long i,long x){uint8_t*p=(uint8_t*)v->data+i*v->stride;for(long b=0;b<v->elem_size;b++)p[b]=(uint8_t)((x>>(8*b))&255);}
static void matvec(const MaruArrayView*w,long rows,long cols,const MaruArrayView*x,const MaruArrayView*b,long*out){for(long r=0;r<rows;r++){long s=0;for(long c=0;c<cols;c++)s+=qmul(getv(w,r*cols+c),getv(x,c));out[r]=s+getv(b,r);}}
static void batched(const MaruArrayView*w,long rows,long cols,const MaruArrayView*x,const MaruArrayView*b,long nt,long*out){for(long t=0;t<nt;t++){MaruArrayView xt=*x;xt.data=x->data+t*cols*x->stride;xt.length=cols;matvec(w,rows,cols,&xt,b,out+t*rows);}}
static void softmax(const MaruArrayView*x,long n,const MaruArrayView*y){double m=getv(x,0)/65536.0;for(long i=1;i<n;i++){double v=getv(x,i)/65536.0;if(v>m)m=v;}double e[64],s=0;for(long i=0;i<n;i++){e[i]=exp(getv(x,i)/65536.0-m);s+=e[i];}for(long i=0;i<n;i++)setv(y,i,(long)((e[i]/s)*Q16));}
static void layernorm(const MaruArrayView*x,long n,const MaruArrayView*g,const MaruArrayView*b,const MaruArrayView*y){long s=0;for(long i=0;i<n;i++)s+=getv(x,i);long mu=s/n;long v=0;for(long i=0;i<n;i++){long d=getv(x,i)-mu;v+=qmul(d,d);}v/=n;long inv=qdiv(Q16,qsqrt(v+1));for(long i=0;i<n;i++)setv(y,i,qmul(qmul(getv(x,i)-mu,inv),getv(g,i))+getv(b,i));}

/* ---- Phase 2: fused single-head attention block (array-view, Q16) ---- */
#define AD 4
#define AT 3
static long adot(const long*a,const long*b,long n){long s=0;for(long i=0;i<n;i++)s+=qmul(a[i],b[i]);return s;}
static void fused_attention(const MaruArrayView*tok,const MaruArrayView*inw,const MaruArrayView*inb,
                            const MaruArrayView*ow,const MaruArrayView*ob,
                            const MaruArrayView*gamma,const MaruArrayView*beta,
                            const MaruArrayView*out){
  long q[AT][AD],k[AT][AD],v[AT][AD],a[AT][AD],res[AT][AD],tmp[AT][AD];
  for(long t=0;t<AT;t++){
    MaruArrayView xt=*tok; xt.data=tok->data+t*AD*tok->stride; xt.length=AD;
    long qv[AD],kv[AD],vv[AD];
    MaruArrayView qb=*inb; qb.length=AD;
    matvec(inw,AD,AD,&xt,&qb,qv);
    MaruArrayView kb=*inb; kb.data=inb->data+AD*inb->stride; kb.length=AD;
    MaruArrayView kwi=*inw; kwi.data=inw->data+AD*AD*inw->stride; kwi.length=AD*AD;
    matvec(&kwi,AD,AD,&xt,&kb,kv);
    MaruArrayView vb=*inb; vb.data=inb->data+2*AD*inb->stride; vb.length=AD;
    MaruArrayView vwi=*inw; vwi.data=inw->data+2*AD*AD*inw->stride; vwi.length=AD*AD;
    matvec(&vwi,AD,AD,&xt,&vb,vv);
    for(int d=0;d<AD;d++){q[t][d]=qv[d];k[t][d]=kv[d];v[t][d]=vv[d];}
  }
  for(long t=0;t<AT;t++){
    long sc[AT],w[AT];
    for(long u=0;u<AT;u++)sc[u]=qdiv(adot(q[t],k[u],AD),131072);
    MaruArrayView sv={(uint8_t*)sc,AT,8,8},wv={(uint8_t*)w,AT,8,8};
    softmax(&sv,AT,&wv);
    for(int d=0;d<AD;d++){long s=0;for(long u=0;u<AT;u++)s+=qmul(v[u][d],w[u]);a[t][d]=s;}
  }
  for(long t=0;t<AT;t++){
    MaruArrayView at={(uint8_t*)a[t],AD,8,8},ot={(uint8_t*)tmp[t],AD,8,8};
    matvec(ow,AD,AD,&at,ob,tmp[t]);
    for(int d=0;d<AD;d++){res[t][d]=getv(tok,t*AD+d)+tmp[t][d];}
    MaruArrayView rv={(uint8_t*)res[t],AD,8,8},ov={(uint8_t*)a[t],AD,8,8};
    layernorm(&rv,AD,gamma,beta,&ov);
    for(int d=0;d<AD;d++) setv(out,t*AD+d,a[t][d]);
  }
}
static void fused_attention_ref(const long*tokp,const long*inwp,const long*inbp,
  const long*owp,const long*obp,const long*gp,const long*bp,long*outp){
  long q[AT][AD],k[AT][AD],v[AT][AD],a[AT][AD],tmp[AT][AD],res[AT][AD];
  MaruArrayView FIW={(uint8_t*)inwp,3*AD*AD,8,8},FIB={(uint8_t*)inbp,3*AD,8,8};
  MaruArrayView FOW={(uint8_t*)owp,AD*AD,8,8},FOB={(uint8_t*)obp,AD,8,8};
  MaruArrayView FG={(uint8_t*)gp,AD,8,8},FB={(uint8_t*)bp,AD,8,8};
  for(int t=0;t<AT;t++){
    MaruArrayView xt={(uint8_t*)(tokp+t*AD),AD,8,8};
    long qv[AD],kv[AD],vv[AD];
    MaruArrayView b0=FIB,b1=FIB,b2=FIB; b0.data=FIB.data;b0.length=AD;
    b1.data=FIB.data+AD*8;b1.length=AD;
    b2.data=FIB.data+2*AD*8;b2.length=AD;
    MaruArrayView kw=FIW,vw=FIW; kw.data=FIW.data+AD*AD*8; kw.length=AD*AD; vw.data=FIW.data+2*AD*AD*8; vw.length=AD*AD;
    matvec(&FIW,AD,AD,&xt,&b0,qv);
    matvec(&kw,AD,AD,&xt,&b1,kv);
    matvec(&vw,AD,AD,&xt,&b2,vv);
    for(int d=0;d<AD;d++){q[t][d]=qv[d];k[t][d]=kv[d];v[t][d]=vv[d];}
  }
  for(int t=0;t<AT;t++){
    long sc[AT],w[AT];
    for(int u=0;u<AT;u++)sc[u]=qdiv(adot(q[t],k[u],AD),131072);
    MaruArrayView sv={(uint8_t*)sc,AT,8,8},wv={(uint8_t*)w,AT,8,8};
    softmax(&sv,AT,&wv);
    for(int d=0;d<AD;d++){long ss=0;for(int u=0;u<AT;u++)ss+=qmul(v[u][d],w[u]);a[t][d]=ss;}
  }
  for(int t=0;t<AT;t++){
    MaruArrayView at={(uint8_t*)a[t],AD,8,8};
    matvec(&FOW,AD,AD,&at,&FOB,tmp[t]);
    for(int d=0;d<AD;d++)res[t][d]=tokp[t*AD+d]+tmp[t][d];
    MaruArrayView rv={(uint8_t*)res[t],AD,8,8},ov={(uint8_t*)a[t],AD,8,8};
    layernorm(&rv,AD,&FG,&FB,&ov);
    for(int d=0;d<AD;d++)outp[t*AD+d]=a[t][d];
  }
}


/* ---- Phase 3: top-k / candidate ranking ---- */
static void topk(const MaruArrayView*s,long n,long k,const MaruArrayView*ids,
                 const MaruArrayView*out_ids,const MaruArrayView*out_scores){
  long oi[64],os[64]; for(long i=0;i<k;i++){oi[i]=-1;os[i]=-999999999;}
  for(long i=0;i<n;i++){
    long v=getv(s,i);
    long pos=k;
    for(long j=0;j<k;j++)if(v>os[j]){pos=j;break;}
    if(pos<k){
      for(long j=k-1;j>pos;j--){os[j]=os[j-1];oi[j]=oi[j-1];}
      os[pos]=v; oi[pos]=ids?getv(ids,i):i;
    }
  }
  for(long i=0;i<k;i++){setv(out_ids,i,oi[i]);setv(out_scores,i,os[i]);}
}
static long argmax(const MaruArrayView*s,long n){long bi=0,bv=getv(s,0);for(long i=1;i<n;i++){long v=getv(s,i);if(v>bv){bv=v;bi=i;}}return bi;}


/* ---- Phase 4: valid-rule mask + indexed candidate retrieval ---- */
static long mask_scores(const MaruArrayView*s,const MaruArrayView*valid,long n,const MaruArrayView*out){
  long nv=0;for(long i=0;i<n;i++){long ok=getv(valid,i);long v=getv(s,i);setv(out,i,ok?v:-999999999);if(ok)nv++;}return nv;
}
static void build_index(const MaruArrayView*keys,long n,long hsize,const MaruArrayView*heads,const MaruArrayView*next){
  for(long b=0;b<hsize;b++)setv(heads,b,-1);
  for(long i=0;i<n;i++){long b=getv(keys,i)%hsize;setv(next,i,getv(heads,b));setv(heads,b,i);}
}
static long index_lookup(const MaruArrayView*keys,long n,const MaruArrayView*heads,long hsize,const MaruArrayView*next,long q,const MaruArrayView*out){
  long b=q%hsize,c=0;for(long i=getv(heads,b);i>=0;i=getv(next,i))if(getv(keys,i)==q)setv(out,c++,i);return c;
}


/* ---- Phase 5: proof-frontier traversal ---- */
static long frontier_closure(const MaruArrayView*facts,long n,
                             const MaruArrayView*head,const MaruArrayView*bmask,long nr,
                             const MaruArrayView*out){
  unsigned char known[64]={0};
  for(long i=0;i<n;i++)known[i]=getv(facts,i)!=0;
  long nout=0;int changed=1;
  while(changed){
    changed=0;
    for(long r=0;r<nr;r++){
      long h=getv(head,r);
      if(known[h])continue;
      unsigned long long m=(unsigned long long)getv(bmask,r);
      int ok=1;
      for(long b=0;b<n;b++)if((m>>b)&1ULL)if(!known[b]){ok=0;break;}
      if(ok){known[h]=1;setv(out,nout++,h);changed=1;}
    }
  }
  return nout;
}
static long frontier_missing(const MaruArrayView*facts,long n,
                             const MaruArrayView*head,const MaruArrayView*bmask,long nr,
                             const MaruArrayView*out){
  long c=0;for(long r=0;r<nr;r++){
    long h=getv(head,r);if(getv(facts,h))continue;
    unsigned long long m=(unsigned long long)getv(bmask,r);
    int open=0;for(long b=0;b<n;b++)if(((m>>b)&1ULL)&&!getv(facts,b)){setv(out,c++,b);open=1;break;}
    if(open)setv(out,c++,h);
  }
  return c;
}


/* ---- Phase 6: BFS / topo / union-find / bitset closure ---- */
static long bfs(const MaruArrayView*adj,long n,long src,const MaruArrayView*out){
  long seen[64]={0},q[64],qh=0,qt=0,c=0;seen[src]=1;q[qt++]=src;
  while(qh<qt){long u=q[qh++];setv(out,c++,u);unsigned long long m=(unsigned long long)getv(adj,u);for(long v=0;v<n;v++)if((m>>v)&1ULL)if(!seen[v]){seen[v]=1;q[qt++]=v;}}
  return c;
}
static long topo(const MaruArrayView*eu,const MaruArrayView*ev,long m,long n,const MaruArrayView*out){
  long indeg[64]={0},q[64],qh=0,qt=0,c=0;
  for(long e=0;e<m;e++)indeg[getv(ev,e)]++;
  for(long v=0;v<n;v++)if(indeg[v]==0)q[qt++]=v;
  while(qh<qt){long u=q[qh++];setv(out,c++,u);for(long e=0;e<m;e++)if(getv(eu,e)==u){long v=getv(ev,e);if(--indeg[v]==0)q[qt++]=v;}}
  return c;
}
static long uf_find(long*p,long x){while(p[x]!=x){p[x]=p[p[x]];x=p[x];}return x;}
static long uf_union(long*p,long a,long b){a=uf_find(p,a);b=uf_find(p,b);if(a==b)return 0;p[b]=a;return 1;}
static void bitset_closure(const MaruArrayView*adj,long n,const MaruArrayView*out){
  unsigned long long r[64];for(long i=0;i<n;i++)r[i]=(unsigned long long)getv(adj,i);
  for(long k=0;k<n;k++)for(long i=0;i<n;i++)if((r[i]>>k)&1ULL)r[i]|=r[k];
  for(long i=0;i<n;i++)setv(out,i,(long)r[i]);
}


/* ---- Phase 7: incremental index update ---- */
static void index_add(const MaruArrayView*keys,const MaruArrayView*heads,long hsize,const MaruArrayView*next,long id,long key){
  long b=key%hsize;setv(keys,id,key);setv(next,id,getv(heads,b));setv(heads,b,id);
}
static long index_remove(const MaruArrayView*keys,long id){long old=getv(keys,id);setv(keys,id,-1);return old;}


/* ---- Phase 8: BCE loss / backward matvec / Adam ---- */
static long bce_q16(long logit,long target){
  double z=(double)logit/(double)Q16;double y=(double)target/(double)Q16;
  double l=-(y*log(1.0/(1.0+exp(-z)))+(1.0-y)*log(1.0-1.0/(1.0+exp(-z))));
  return (long)(l*(double)Q16);
}
static void backward_matvec(const MaruArrayView*w,long rows,long cols,
                            const MaruArrayView*dy,const MaruArrayView*dx){
  for(long c=0;c<cols;c++){long s=0;for(long r=0;r<rows;r++)s+=qmul(getv(w,r*cols+c),getv(dy,r));setv(dx,c,s);}
}
static long adam_step(long p,long g,long*m,long*v,long t,long lr,long b1,long b2,long eps){
  double b1d=(double)b1/(double)Q16,b2d=(double)b2/(double)Q16;
  double md=((double)(*m))/(double)Q16,vd=((double)(*v))/(double)Q16,gd=(double)g/(double)Q16,lrd=(double)lr/(double)Q16;
  md=b1d*md+(1.0-b1d)*gd; vd=b2d*vd+(1.0-b2d)*gd*gd;
  double mh=md/(1.0-pow(b1d,(double)t)), vh=vd/(1.0-pow(b2d,(double)t));
  double pd=(double)p/(double)Q16 - lrd*mh/(sqrt(vh)+(double)eps/(double)Q16);
  *m=(long)(md*(double)Q16); *v=(long)(vd*(double)Q16);
  return (long)(pd*(double)Q16);
}


/* ---- Phase 9: fused linear/ReLU and linear/LN ---- */
static void fused_linear_relu(const MaruArrayView*w,const MaruArrayView*b,long nout,long nin,
                              const MaruArrayView*x,const MaruArrayView*out){
  long tmp[64];matvec(w,nout,nin,x,b,tmp);
  for(long i=0;i<nout;i++)setv(out,i,tmp[i]>0?tmp[i]:0);
}
static void fused_linear_ln(const MaruArrayView*w,const MaruArrayView*b,long nout,long nin,
                            const MaruArrayView*x,const MaruArrayView*g,const MaruArrayView*be,
                            const MaruArrayView*out){
  long tmp[64];matvec(w,nout,nin,x,b,tmp);
  MaruArrayView T={(uint8_t*)tmp,nout,8,8};layernorm(&T,nout,g,be,out);
}


/* ---- Phase 11: integrated ranking + proof-gated derivation ---- */
static long integrated_derive(const MaruArrayView*facts,long n,
                              const MaruArrayView*head,const MaruArrayView*bmask,
                              const MaruArrayView*score,long nr,const MaruArrayView*derived){
  unsigned char known[64]={0};for(long i=0;i<n;i++)known[i]=getv(facts,i)!=0;
  long ids[64],scores[64],rank[64],rsc[64];
  for(long r=0;r<nr;r++)ids[r]=r;
  long nout=0;int changed=1;
  while(changed){
    changed=0;
    for(long r=0;r<nr;r++){
      long h=getv(head,r);long sc=getv(score,r);
      if(known[h])sc=-999999999;
      else{
        unsigned long long m=(unsigned long long)getv(bmask,r);
        for(long b=0;b<n;b++)if(((m>>b)&1ULL)&&!known[b]){sc=-999999999;break;}
      }
      scores[r]=sc;
    }
    MaruArrayView IDS={(uint8_t*)ids,nr,8,8},SC={(uint8_t*)scores,nr,8,8};
    MaruArrayView RK={(uint8_t*)rank,nr,8,8},RS={(uint8_t*)rsc,nr,8,8};
    topk(&SC,nr,nr,&IDS,&RK,&RS);
    for(long i=0;i<nr;i++){
      long r=rank[i];if(rsc[i]<=-999999999)break;
      long h=getv(head,r);if(known[h])continue;
      known[h]=1;setv(derived,nout++,h);changed=1;
    }
  }
  return nout;
}

int main(void){long w[6]={Q16,0,0,0,Q16,0},x[3]={Q16,2*Q16,3*Q16},b[2]={100,200};MaruArrayView W={(uint8_t*)w,6,8,8},X={(uint8_t*)x,3,8,8},B={(uint8_t*)b,2,8,8};long out[2];matvec(&W,2,3,&X,&B,out);long r0=100+qmul(Q16,Q16),r1=200+qmul(Q16,2*Q16);printf("MATVEC %s %ld %ld\n",(out[0]==r0&&out[1]==r1)?"PASS":"FAIL",out[0],out[1]);long xx[6]={Q16,2*Q16,3*Q16,2*Q16,3*Q16,4*Q16};MaruArrayView XB={(uint8_t*)xx,6,8,8};long bo[4];batched(&W,2,3,&XB,&B,2,bo);printf("BATCH %s\n",(bo[0]==r0&&bo[1]==r1)?"PASS":"FAIL");long sx[3]={0,Q16,2*Q16},sy[3];MaruArrayView SX={(uint8_t*)sx,3,8,8},SY={(uint8_t*)sy,3,8,8};softmax(&SX,3,&SY);long sum=0;for(int i=0;i<3;i++)sum+=sy[i];printf("SOFTMAX %s sum=%ld\n",(sum>=65534&&sum<=65538)?"PASS":"FAIL",sum);long lx[3]={Q16,2*Q16,3*Q16},g[3]={Q16,Q16,Q16},lb[3]={0,0,0},ly[3];MaruArrayView LX={(uint8_t*)lx,3,8,8},G={(uint8_t*)g,3,8,8},LB={(uint8_t*)lb,3,8,8},LY={(uint8_t*)ly,3,8,8};layernorm(&LX,3,&G,&LB,&LY);long mean=0;for(int i=0;i<3;i++)mean+=ly[i];printf("LAYERNORM %s mean=%ld\n",(mean<10&&mean>-10)?"PASS":"FAIL",mean);long ftok[AT*AD],fiw[3*AD*AD],fib[3*AD],fow[AD*AD],fob[AD],fg[AD],fb[AD],fout[AT*AD],fref[AT*AD];
  for(int i=0;i<AT*AD;i++)ftok[i]=((i*37)%100-50)*256;
  for(int i=0;i<3*AD*AD;i++)fiw[i]=((i*13)%200-100)*128;
  for(int i=0;i<3*AD;i++)fib[i]=((i*7)%50-25)*64;
  for(int i=0;i<AD*AD;i++)fow[i]=((i*11)%200-100)*128;
  for(int i=0;i<AD;i++){fob[i]=i*10;fg[i]=Q16;fb[i]=0;}
  MaruArrayView FT={(uint8_t*)ftok,AT*AD,8,8},FIW={(uint8_t*)fiw,3*AD*AD,8,8},FIB={(uint8_t*)fib,3*AD,8,8},FOW={(uint8_t*)fow,AD*AD,8,8},FOB={(uint8_t*)fob,AD,8,8},FG={(uint8_t*)fg,AD,8,8},FB={(uint8_t*)fb,AD,8,8},FO={(uint8_t*)fout,AT*AD,8,8};
  fused_attention(&FT,&FIW,&FIB,&FOW,&FOB,&FG,&FB,&FO);
  fused_attention_ref(ftok,fiw,fib,fow,fob,fg,fb,fref);
  int fok=1;for(int i=0;i<AT*AD;i++){if(fout[i]!=fref[i]){printf("DIFF %d %ld %ld\n",i,fout[i],fref[i]);fok=0;}}
  printf("FUSED-ATTENTION %s\n",fok?"PASS":"FAIL");
  long ts[5]={5,1,9,3,7},ti[5]={10,11,12,13,14},toi[3],tos[3];MaruArrayView TS={(uint8_t*)ts,5,8,8},TI={(uint8_t*)ti,5,8,8},TOI={(uint8_t*)toi,3,8,8},TOS={(uint8_t*)tos,3,8,8};topk(&TS,5,3,&TI,&TOI,&TOS);int tok=(toi[0]==12&&toi[1]==14&&toi[2]==10&&tos[0]==9&&tos[1]==7&&tos[2]==5);printf("TOPK %s\n",tok?"PASS":"FAIL");printf("ARGMAX %s\n",(argmax(&TS,5)==2)?"PASS":"FAIL");long ms[4]={5,6,7,8},mv[4]={1,0,1,1},mo[4];MaruArrayView MS={(uint8_t*)ms,4,8,8},MV={(uint8_t*)mv,4,8,8},MO={(uint8_t*)mo,4,8,8};long nmv=mask_scores(&MS,&MV,4,&MO);int mok=(nmv==3&&mo[0]==5&&mo[1]==-999999999&&mo[2]==7&&mo[3]==8);printf("MASK %s count=%ld\n",mok?"PASS":"FAIL",nmv);
long ik[4]={3,7,3,9},ih[8],in[4],io[4];MaruArrayView IK={(uint8_t*)ik,4,8,8},IH={(uint8_t*)ih,8,8,8},IN={(uint8_t*)in,4,8,8},IO={(uint8_t*)io,4,8,8};build_index(&IK,4,8,&IH,&IN);long c3=index_lookup(&IK,4,&IH,8,&IN,3,&IO),c9=index_lookup(&IK,4,&IH,8,&IN,9,&IO);int iok=(c3==2&&c9==1&&io[0]==3);printf("INDEX %s c3=%ld c9=%ld\n",iok?"PASS":"FAIL",c3,c9);
long pff[6]={1,1,0,0,0,0},pfh[3]={2,3,5},pfm[3]={(1ULL<<0)|(1ULL<<1),(1ULL<<2),(1ULL<<4)},pfo[6];MaruArrayView PFF={(uint8_t*)pff,6,8,8},PFH={(uint8_t*)pfh,3,8,8},PFM={(uint8_t*)pfm,3,8,8},PFO={(uint8_t*)pfo,6,8,8};long nf=frontier_closure(&PFF,6,&PFH,&PFM,3,&PFO);int pfok=(nf==2&&pfo[0]==2&&pfo[1]==3);printf("FRONTIER %s derived=%ld\n",pfok?"PASS":"FAIL",nf);
long pmf[6]={1,0,0,0,0,0},pmo[6];MaruArrayView PMF={(uint8_t*)pmf,6,8,8},PMO={(uint8_t*)pmo,6,8,8};long nm=frontier_missing(&PMF,6,&PFH,&PFM,3,&PMO);printf("FRONTIER-MISSING %s missing=%ld\n",(nm==6&&pmo[0]==1&&pmo[1]==2)?"PASS":"FAIL",nm);
long ba[4]={0b0010,0b0100,0,0},pbo[4];MaruArrayView BA={(uint8_t*)ba,4,8,8},PBO={(uint8_t*)pbo,4,8,8};long nb=bfs(&BA,4,0,&PBO);int pbok=(nb==3&&pbo[0]==0&&pbo[1]==1&&pbo[2]==2);printf("BFS %s n=%ld\n",pbok?"PASS":"FAIL",nb);
long ptu[3]={0,1,0},ptv[3]={1,2,3},pto[4];MaruArrayView PTU={(uint8_t*)ptu,3,8,8},PTV={(uint8_t*)ptv,3,8,8},PTO={(uint8_t*)pto,4,8,8};long nt=topo(&PTU,&PTV,3,4,&PTO);int ptok=(nt==4&&pto[0]==0);printf("TOPO %s n=%ld\n",ptok?"PASS":"FAIL",nt);
long pp[4]={0,1,2,3};long u1=uf_union(pp,0,1),u2=uf_union(pp,2,3),u3=uf_union(pp,1,2);int uok=(u1==1&&u2==1&&u3==1&&uf_find(pp,0)==uf_find(pp,3));printf("UNION-FIND %s\n",uok?"PASS":"FAIL");
long ca[4]={0b0010,0b0100,0,0},co[4];MaruArrayView CA={(uint8_t*)ca,4,8,8},CO={(uint8_t*)co,4,8,8};bitset_closure(&CA,4,&CO);int cok=(co[0]==0b0110&&co[1]==0b0100);printf("BITSET-CLOSURE %s\n",cok?"PASS":"FAIL");
long qk[5]={3,7,3,9,-1},qh2[8],qn[5],qo[5];MaruArrayView QK={(uint8_t*)qk,5,8,8},QH={(uint8_t*)qh2,8,8,8},QN={(uint8_t*)qn,5,8,8},QO={(uint8_t*)qo,5,8,8};build_index(&QK,4,8,&QH,&QN);index_add(&QK,&QH,8,&QN,4,3);long qa=index_lookup(&QK,5,&QH,8,&QN,3,&QO);long qr=index_remove(&QK,0);long qb=index_lookup(&QK,5,&QH,8,&QN,3,&QO);int qok=(qa==3&&qr==3&&qb==2);printf("INDEX-UPDATE %s add=%ld remove=%ld after=%ld\n",qok?"PASS":"FAIL",qa,qr,qb);
long bl1=bce_q16(0,Q16),bl0=bce_q16(0,0);int blok=(bl1>45000&&bl1<46000&&bl0>45000&&bl0<46000);printf("BCE %s %ld %ld\n",blok?"PASS":"FAIL",bl1,bl0);
long bw[4]={Q16,0,0,Q16},bdy[2]={2*Q16,3*Q16},bdx[2];MaruArrayView BW={(uint8_t*)bw,4,8,8},BDY={(uint8_t*)bdy,2,8,8},BDX={(uint8_t*)bdx,2,8,8};backward_matvec(&BW,2,2,&BDY,&BDX);int bok2=(bdx[0]==2*Q16&&bdx[1]==3*Q16);printf("BACKWARD-MATVEC %s\n",bok2?"PASS":"FAIL");
long am=0,av=0;long ap=100*Q16;for(long t=1;t<=3;t++)ap=adam_step(ap,10*Q16,&am,&av,t,3277,58982,64225,655);int aok=(ap<100*Q16&&ap>0);printf("ADAM %s p=%ld\n",aok?"PASS":"FAIL",ap);
long lw[4]={Q16,0,0,Q16},lb2[2]={0,-2*Q16},lx2[2]={Q16,Q16},lo[2];MaruArrayView LW={(uint8_t*)lw,4,8,8},LB2={(uint8_t*)lb2,2,8,8},LX2={(uint8_t*)lx2,2,8,8},LO={(uint8_t*)lo,2,8,8};fused_linear_relu(&LW,&LB2,2,2,&LX2,&LO);int lok=(lo[0]==Q16&&lo[1]==0);printf("LINEAR-RELU %s %ld %ld\n",lok?"PASS":"FAIL",lo[0],lo[1]);
long lw3[9]={Q16,0,0,0,Q16,0,0,0,Q16},lb3[3]={0,0,0},lx3[3]={Q16,2*Q16,3*Q16},lg3[3]={Q16,Q16,Q16},lbe3[3]={0,0,0},lnout[3];MaruArrayView LW3={(uint8_t*)lw3,9,8,8},LB3={(uint8_t*)lb3,3,8,8},LX3={(uint8_t*)lx3,3,8,8},LG3={(uint8_t*)lg3,3,8,8},LBE3={(uint8_t*)lbe3,3,8,8},LNO={(uint8_t*)lnout,3,8,8};fused_linear_ln(&LW3,&LB3,3,3,&LX3,&LG3,&LBE3,&LNO);long lsum=0;for(int i=0;i<3;i++)lsum+=lnout[i];int lnok=(lsum<10&&lsum>-10);printf("LINEAR-LN %s sum=%ld\n",lnok?"PASS":"FAIL",lsum);
long pif[6]={1,1,0,0,0,0},pih[3]={2,3,5},pibm[3]={(1ULL<<0)|(1ULL<<1),(1ULL<<4),(1ULL<<0)},pisc[3]={100,300,200},pider[6];MaruArrayView PIF={(uint8_t*)pif,6,8,8},PIH={(uint8_t*)pih,3,8,8},PIBM={(uint8_t*)pibm,3,8,8},PISC={(uint8_t*)pisc,3,8,8},PID={(uint8_t*)pider,6,8,8};long pni=integrated_derive(&PIF,6,&PIH,&PIBM,&PISC,3,&PID);int ph2=0,ph5=0,ph3=0;for(long i=0;i<pni;i++){if(pider[i]==2)ph2=1;if(pider[i]==5)ph5=1;if(pider[i]==3)ph3=1;}int piok=(pni==2&&ph2&&ph5&&!ph3);printf("INTEGRATE %s n=%ld\n",piok?"PASS":"FAIL",pni);printf("PROOF-GATE %s invalid=%d\n",!ph3?"PASS":"FAIL",ph3);
printf("KERNEL-SUITE-PHASE11\n");return 0;}
