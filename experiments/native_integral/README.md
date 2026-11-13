# Native Integral-Credit Composition (Maru + LLVM IR)

Native implementation (C/LLVM IR + Maru oracle; **no Python/PyTorch**) of the
deductive-learning vision: an accumulated axiom base + combinatorial proof
composition guided by integral credit. Tests the key hypothesis from the 0241
discussion:

> 0241 showed integral ≈ single for **exact** single-rule utility (a potential
> difference — greedy is already optimal). Here credit is **partial proof
> participation** (noisy per episode). Does accumulating it over many episodes
> (the integral) beat a single episode (greedy/single) on **combinatorial**
> budget-limited composition?

## Architecture (the vision, native)

- **Axiom base**: Horn rule pool — 8 topics × 3-chain rules + 8 decoys (32 rules,
  40 atoms, bitset). Rules deterministically shuffled so index order is
  uninformative.
- **Composition**: budget-limited forward closure, rule order guided by learned
  weights (higher credit first). Budget = 6 firings → order matters; goals need
  3-rule chains (combinatorial).
- **Exact oracle**: Maru `p-close` on the same ground theory (parity gate).
- **Integral learning**: accumulate proof-participation credit over 400 train
  episodes → weights guide 400 held-out test episodes.

Credit is **partial**: a rule is credited iff it fired on the backward path to a
reached goal, computed under a **tight budget** (noisy participation). Modes:
`integral` (running sum, denoises) / `single` (one noisy episode) / `random` /
`uniform`.

## Result (3 seeds × 400 test episodes, goals reached within budget)

```text
seed  integral  single  random  uniform   integral−single
777   36.60%    25.62%  18.94%  20.05%    +10.98pp
778   37.88%    19.90%  18.54%  19.90%    +17.98pp
779   38.06%    20.81%  18.45%  20.81%    +17.25pp
```

**Integral beats single by +11–18pp on every seed**, and beats random/uniform by
~17–19pp. With noisy partial participation credit, accumulation denoises and
guides combinatorial search substantially better than a single episode. This is
the regime where the integral earns its keep — contrasting 0241's exact-credit
null. The learned weights also recover the latent structure (hot-topic rules
outweigh cold).

## Gates (`verify.sh`, computed, bash+awk — no Python)

- C kernel parity fixture: `PARITY2 derived=6 reached=2 known=63`.
- Maru oracle parity: same theory via `p-close` → `MARU-PARITY-PASS`.
- LLVM O0/O2/O3 byte-identical; IR emitted (`-S -emit-llvm`), `opt`/`llc`.
- Discriminative: integral > single+3pp AND > random AND > uniform, all 3 seeds.
- Determinism: seed 777 re-run byte-identical.

## Files

```text
include/array_view.h   Maru array-view ABI (frozen copy)
src/icredit.c          integer Q16 kernel: closure, credit, learning, LLVM-friendly
src/parity.l           Maru p-close ground-closure oracle
run.sh                 build O0/O2/O3 + LLVM IR matrix + 3 seeds + Maru parity
verify.sh              computed gates
run_all.sh             run + verify
```

## Run

```bash
./run_all.sh
```

## Limits

- Propositional ground Horn, 40 atoms / 32 rules, bitset (≤64). Synthetic
  topics with hot/cold structure; the integral learns this stable latent core.
- Participation credit is a binary backward-path signal, not full deep_credit;
  richer credit (depth-weighted, failure-frontier blame) is future work.
- The matcher here is credit-weighted rule ordering, not a learned transformer;
  it demonstrates the integral-learning principle natively. A transformer
  matcher over a large axiom base (the full vision) is the next scale step.
- 3 seeds; the +3pp margin is a pre-registered heuristic, not a significance test.
- Integer-only kernel; a `fired[]` buffer-overflow UB (NATOMS vs NRULES) was
  caught by the O0/O2/O3 identity gate and fixed.