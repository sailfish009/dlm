#include "array_view.h"

#define AJ_MAXN 4096
#define AJ_MAXKEY 256

typedef struct {
  long n;
  long maxkey;
  int active;
  long start[AJ_MAXKEY + 2];
  long order[AJ_MAXN];
  long pos[AJ_MAXKEY + 1];
} JoinIndex;

static JoinIndex g_index;

void maru_index_free(void) {
  g_index.active = 0;
}

long maru_index_build(const uint8_t *keys, long n, long stride, long elem, long maxkey) {
  MaruArrayView rv = { keys, n, stride, elem };
  if (!mav_valid(&rv) || rv.elem_size != 1 || n > AJ_MAXN || maxkey < 0 || maxkey > AJ_MAXKEY) return 0;
  g_index.active = 0;
  g_index.n = n;
  g_index.maxkey = maxkey;
  for (long k = 0; k <= maxkey + 1; k++) g_index.start[k] = 0;
  for (long i = 0; i < n; i++) {
    long k = (long)mav_get(&rv, i);
    if (k <= maxkey) g_index.start[k + 1]++;
  }
  for (long k = 0; k <= maxkey; k++) g_index.start[k + 1] += g_index.start[k];
  for (long k = 0; k <= maxkey; k++) g_index.pos[k] = g_index.start[k];
  for (long i = 0; i < n; i++) {
    long k = (long)mav_get(&rv, i);
    if (k <= maxkey) g_index.order[g_index.pos[k]++] = i;
  }
  g_index.active = 1;
  return 1;
}

long maru_join_many(long h, const uint8_t *left, long n, long stride, long elem, long reps) {
  if (h != 1 || !g_index.active || !left || n < 0 || reps < 0) return -1;
  MaruArrayView lv = { left, n, stride, elem };
  if (!mav_valid(&lv) || lv.elem_size != 1) return -1;
  long total = 0;
  for (long r = 0; r < reps; r++) {
    for (long i = 0; i < n; i++) {
      uint64_t k = mav_get(&lv, i);
      if ((long)k <= g_index.maxkey)
        total += g_index.start[(long)k + 1] - g_index.start[(long)k];
    }
  }
  return total;
}

long maru_join_checksum(long h, const uint8_t *left, long n, long stride, long elem, long reps) {
  if (h != 1 || !g_index.active || !left || n < 0 || reps < 0) return -1;
  MaruArrayView lv = { left, n, stride, elem };
  if (!mav_valid(&lv) || lv.elem_size != 1) return -1;
  long sum = 0;
  for (long r = 0; r < reps; r++) {
    for (long i = 0; i < n; i++) {
      uint64_t k = mav_get(&lv, i);
      if ((long)k <= g_index.maxkey)
        for (long p = g_index.start[(long)k]; p < g_index.start[(long)k + 1]; p++)
          sum += g_index.order[p];
    }
  }
  return sum;
}

long maru_index_size(long h) {
  return (h == 1 && g_index.active) ? g_index.n : -1;
}
