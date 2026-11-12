# DLM v0.0216 — Maru array-view ABI

## ABI

```c
typedef struct {
  const uint8_t *data;
  long length;
  long stride;
  long elem_size;
} MaruArrayView;
```

The VM wrapper passes the four fields as scalar arguments:

```lisp
(mb-join-many handle left-block n stride elem reps)
```

- `data` comes from `(<memory-block>-elements block)`.
- `length` is the number of elements.
- `stride` is bytes between elements.
- `elem_size` is 1/2/4/8 bytes.

v0.0216 uses `elem_size=1` byte keys; the getter supports wider elements for
future kernels.

## Indexed join

- Right relation keys are indexed once:
  `mb-index-build(right, n, stride, elem, maxkey) -> handle`.
- The index is persistent in the C image:
  prefix `start[maxkey+2]` plus grouped `order[n]`.
- Left keys are zero-copy from a Maru memory-block.
- `mb-join-many(handle, left, n, 1, 1, reps)` does all repetitions in one C
  call and returns the total pair count.
- `mb-join-checksum(...)` returns the sum of matched right indices, validating
  the grouped order, not only bucket sizes.
- `mb-index-free()` releases the static index; subsequent joins return `-1`.

Static limits: `n <= 4096`, `maxkey <= 256`.

## Benchmarks

Fixture: 300 keys in each relation, keys `0..31`, 4096 join repetitions.

```text
C-BUILD      0.000007 s
C-JOIN4096   0.000701 s
C-CHECK4096  0.004263 s
C-COUNT      11550720
C-SUM        1726832640
```

Maru end-to-end (including ~62 ms startup):

```text
ref only        ~170 ms   (300 x 300 nested-loop reference)
build only       ~62 ms
join4096         ~69 ms
```

So the C join kernel is sub-millisecond; the Maru-visible cost is startup,
data preparation and FFI, not the join computation.

## Correctness

```text
REF        2820
REFSUM     421590
JOIN1      2820
JOIN64     180480
JOIN4096   11550720
CHECK1     421590
CHECK64    26981760
AFTERFREE  -1
```

`JOIN4096 = REF * 4096`; `CHECK64 = REFSUM * 64`; post-free join is rejected.

## Build integration

`build-compiler-image.sh` compiles and links:

```text
source/c/array_view_join.c
```

in `rebuild` and self-host `verify` paths.
