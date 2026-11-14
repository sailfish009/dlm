# Native integral-credit composition — v0.0243 protocol

Native (C/LLVM IR + Maru oracle; **no Python/PyTorch on this path**) test of the
deductive-learning vision's learning principle: an accumulated axiom base +
budget-limited proof composition guided by **accumulated participation credit**.

This directory started in 0.0242. The 0.0242 review found its headline
("integral beats single by +11–18pp") confounded: `integral` consumed 400
training episodes while `single` consumed one, credit was collected under a
fixed shuffled rule index (a hidden prior), the hot/cold diagnostic indexed
shuffled rules as if unshuffled, and there were no CIs. v0.0243 keeps the
kernel and fixes the protocol.

## What changed from 0.0242

| Defect (0.0242 review) | 0.0243 protocol |
|---|---|
| `integral` = 400 episodes vs `single` = 1 | data/compute-matched `last` arm **and** the distribution of 100 single-episode policies (`SINGLEPOLICY`) |
| fixed shuffled index = hidden prior | randomized tie-break among equal-weight candidates in **both** credit collection and test search; rule shuffle varies per seed; `ABLATION` line reproduces the 0.0242 fixed-tie-break setting |
| "noise is what makes accumulation work" | `exact` arm (full-budget credit) separates accumulation from credit fidelity |
| no variance/CI, +3pp heuristic | paired per-episode wins/losses, integer z (require ≥1960), native bootstrap 95% CI, 12 seeds |
| hot/cold diagnostic wrong after shuffle | topic/chain-position from the head atom; `RULE` table emitted |
| "denoising" asserted | L1 estimation error against an independent sample, n = 1…400 (`CURVE`) |
| Maru parity only on a 6-atom toy | C emits two generated 40-atom worlds; Maru `p-close` re-derives them (`PARITY generated worlds`) |

The axiom base is read through the Maru array-view ABI (`include/array_view.h`),
so the ABI is exercised rather than only included.

## Protocol

- Worlds: 8 topics × 4-atom chains + 8 decoy rules (32 rules, 40 atoms, bitset);
  hot topics (0–3) have 85% goal probability, cold 25%; 70% seed facts; 3 noise
  facts. 400 train / 400 test / 400 independent target episodes per seed.
- Search: greedy forward closure, 6-firing budget (order matters; goals need
  3-rule chains), ties broken uniformly at random.
- Credit: binary backward **participation** — a fired rule is credited iff its
  head is an ancestor of a reached goal. `CREDITB=6` (tight, sparse) vs
  `FULLB=64` (exact) training credit.
- Arms: `prior` (accumulated tight credit), `last` (memoryless, same episodes),
  `ema` (α=1/8), `exact`/`exact_last` (full-budget credit), `online`/
  `online_exact` (accumulated weights feed back into the training closure),
  `random`, `uniform`, `hot_oracle`, `pos_oracle` (depth-first + hot-topic
  structural oracle).

## Result (12 seeds × 400 held-out episodes, goals reached within budget)

```text
seed  prior  last  exact  ema    online  pos_oracle
777   41.22  13.03 42.95  41.16  41.61   39.72
778   43.17  13.36 44.88  43.23  41.46   42.09
779   40.94  13.74 45.08  40.94  39.39   41.46
780   38.37  11.06 42.55  38.43  40.46   39.50
781   41.09  11.47 43.89  41.15  40.14   40.92
782   36.37  11.06 43.53  36.37  41.88   39.16
783   40.68  11.61 43.26  40.74  41.63   40.12
784   40.88  11.01 43.21  40.88  35.03   39.63
785   43.77  14.05 44.97  43.77  43.43   42.34
786   41.30  11.47 43.66  41.30  41.19   39.30
787   43.58  11.56 43.41  43.58  38.29   40.17
788   38.37  12.17 43.42  38.37  38.89   40.81
mean  40.81  12.13 43.73  40.83  40.28   40.43
```

- **Accumulation is the driver**: `prior` − `last` = **+28.7pp mean** (min seed
  margin +25.3pp); paired wins 346 / losses 0 (seed 777), z ≥ 1960 and bootstrap
  95% CI excluding 0 on all 12 seeds. 100 single-episode policies average
  13.45% (max 23.39%) — one episode's credit never approaches the accumulated
  prior.
- **Credit fidelity adds a little**: `exact` − `prior` = **+2.92pp mean**
  (+1.73pp at seed 777, paired z = −2545, CI [−3.13,−0.44]). Tight-budget
  "noise" is a cost, so 0.0242's "noise is what makes integral win" framing is
  retracted: accumulation helps because it estimates a stable participation
  rate, and better credit estimates help more.
- **Recency weighting is neutral**: `ema` − `prior` = +0.02pp mean; a ~8-episode
  effective window already suffices.
- **Composition feedback adds nothing here**: `online` − `prior` = −0.53pp mean
  and is unstable (seed 784: −5.85pp). Offline accumulation is invariant to the
  episode order (a scalar potential); the online arm is path dependent and its
  weight sums differ per permutation, but that path dependence does not buy
  accuracy.
- **Interpretation guard**: the learned prior matches a hand-written depth-first
  + hot-topic oracle (40.81 vs 40.43 mean), so the accumulated credit recovers
  the fixture's structural policy at this scale. It is an empirical prior over
  rule participation, not a path integral over compositions.

## Gates (`verify.sh` — computed, bash + awk, no Python)

```text
PARITY toy C==Maru (derived=6 reached=2)
PARITY generated worlds C==Maru (2 worlds, ground closure)
LLVM O0/O2/O3 byte-identical (12 seeds, full diagnostics)
DISCRIMINATIVE prior>last/uniform/random+10pp and pos_oracle>uniform+5 on 12 seeds
SIGNIFICANCE paired prior>last z>=1960 (p<0.05) on 12 seeds
BOOTSTRAP prior-minus-last 95% CI excludes 0 on 12 seeds
ACCUMULATION 1-episode mean vs prior; L1 estimation error 337->97 milli
ORDER offline prior invariant to episode order on 12 seeds
DETERMINISM re-run byte-identical
V0243-NATIVE-INTEGRAL-PASS
```

The `ABLATION` line (seed 777) reproduces the 0.0242 setting: with the fixed
tie-break the *no-learning* baseline measures 20.05%, versus 13.03% under the
randomized protocol. The 0.0242 `uniform` baseline was inflated by the fixed
table index.

## Files

```text
include/array_view.h   Maru array-view ABI (frozen copy)
src/icredit.c          integer kernel: closure, participation, arms, statistics
src/parity.l           Maru p-close oracle, hardcoded 6-atom toy
src/parity-world.l     Maru p-close oracle, GENERATED 40-atom worlds
run.sh                 O0/O2/O3 matrix + LLVM IR + Maru oracles + episode emit
verify.sh              computed gates
run_all.sh             run + verify
```

## Run

```bash
./run_all.sh        # ~20 s
```

## Limits

- Synthetic propositional ground Horn, 40 atoms / 32 rules, bitset (≤64 atoms).
  The world is generated, not read. A real axiom base would need a larger kernel.
- Credit is binary backward participation, not depth-weighted or
  failure-frontier blame; `exact` differs from `prior` only by training budget.
- The budget (6 firings) makes the task a fixed-priority search; the learned
  object is a static rule priority, so the "integral" here is an empirical prior
  estimate. Composition-coupled (online) or order-non-integrable credit is
  measured as neutral at this scale — that is a negative result, not support.
- Maru parity covers ground closure only; the credit-weighted budgeted search is
  C-side.
- 12 seeds × 400 episodes is enough to resolve +10pp differences on this
  fixture; it says nothing about larger axiom bases or many-step proofs.