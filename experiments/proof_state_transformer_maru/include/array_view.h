#ifndef MARU_ARRAY_VIEW_H
#define MARU_ARRAY_VIEW_H
#include <stdint.h>
#include <stddef.h>

/* Maru array-view ABI: one contiguous buffer plus element layout. */
typedef struct {
  const uint8_t *data;
  long length;
  long stride;
  long elem_size;
} MaruArrayView;

static inline int mav_valid(const MaruArrayView *v) {
  return v && v->data && v->length >= 0 && v->stride >= (long)v->elem_size &&
         (v->elem_size == 1 || v->elem_size == 2 || v->elem_size == 4 || v->elem_size == 8);
}

static inline uint64_t mav_get(const MaruArrayView *v, long i) {
  const uint8_t *p = v->data + i * v->stride;
  uint64_t x = 0;
  for (long b = 0; b < v->elem_size; b++) x |= ((uint64_t)p[b]) << (8 * b);
  return x;
}
#endif
