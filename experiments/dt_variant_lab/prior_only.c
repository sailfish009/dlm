#include "../dt_full_port_no_mlir/train_fixture.h"
#include "../dt_full_port_no_mlir/fixture_all.h"
#include <stdio.h>
static void knn(int c,long*td,long*tl,int*tn){for(int p=0;p<POOL_COUNT;p++){long d=0;for(int i=0;i<196;i++){long x=case_bits[c][i]-pool_bits[p][i];d+=x*x;}int pos=*tn;for(int j=0;j<*tn;j++)if(d<=td[j]){pos=j;break;}if(pos<5){int lim=*tn<5?*tn:4;for(int j=lim;j>pos;j--){td[j]=td[j-1];tl[j]=tl[j-1];}td[pos]=d;tl[pos]=pool_labels[p];if(*tn<5)(*tn)++;}}}
int main(void){for(int c=0;c<10;c++){long td[5],tl[5];int tn=0;knn(c,td,tl,&tn);long cnt[10]={0};for(int i=0;i<tn;i++)cnt[tl[i]]++;int best=-1;long bp=-999999;for(int vi=0;vi<train_nv[c];vi++){int k=train_valid[c][vi];long p=prior_log[cnt[rule_heads[k]]];if(p>bp){bp=p;best=k;}}printf("PRIOR %d %d\n",c,best);}return 0;}
