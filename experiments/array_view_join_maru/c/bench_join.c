#include "array_view.h"
#include <stdio.h>
#include <stdint.h>
#include <time.h>

long maru_index_build(const uint8_t*, long, long, long, long);
long maru_join_many(long, const uint8_t*, long, long, long, long);
long maru_join_checksum(long, const uint8_t*, long, long, long, long);
void maru_index_free(void);

static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec + t.tv_nsec/1e9; }

int main(void){
  enum { N=300, REP=4096 };
  uint8_t left[N], right[N];
  for(int i=0;i<N;i++){ left[i]=i%32; right[i]=i%32; }
  double t0=now();
  long h=maru_index_build(right,N,1,1,31);
  double t1=now();
  long c=maru_join_many(h,left,N,1,1,REP);
  double t2=now();
  long s=maru_join_checksum(h,left,N,1,1,REP);
  double t3=now();
  printf("C-BUILD %.6f s\n", t1-t0);
  printf("C-JOIN4096 %.6f s\n", t2-t1);
  printf("C-CHECK4096 %.6f s\n", t3-t2);
  printf("C-COUNT %ld\n", c);
  printf("C-SUM %ld\n", s);
  maru_index_free();
  return 0;
}
