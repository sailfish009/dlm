# Release 0.0244 — native proof-state transformer for deductive learning

- Date: 2026-11-14
- Predecessor: 0.0243
- Type: candidate research release
- Runtime: `20261114T001318Z-27176` (reused; `src/` unchanged)

## What changed

- Added `experiments/proof_state_transformer_maru/`: a torch-free
  (C/LLVM + Maru Q16) proof-state transformer lab on the M1 proof-state fixture
  semantics, with six variants, beam search, a gradient check, paired controls
  and gate coverage.
- VERSION 0.0244; `capabilities.json` version and new capability entries.
- `scripts/verify_release.sh` now runs the proof-state lab gate.

## Why

0.0242/0.0243 settled the credit-composition question (accumulated participation
prior vs no accumulation) but left the transformer question open. The prior
variant work was either PyTorch-trained (`m1_proof_state`) or ran on the MNIST
10-case fixture where the kNN prior saturates the task, so variants could not be
distinguished. This release moves the non-saturated proof-state fixture into the
native line and tests deduction-motivated variations there.

## Native architecture

- World/oracle/features ported from `m1_proof_state/world.py`; parity against
  the reference implementation is a gate (state, candidate features, kernel
  utility, rollout best; max abs error 5e-7 on 1.6k candidate evaluations).
- Set transformer: state token + candidate tokens, 2 pre-LN blocks, D=32, 4
  heads, FFN 64, GELU, type embeddings; 18,403 parameters.
- Manual backprop with a finite-difference gradient check (rel. error to the
  largest gradient 1e-10).
- AdamW (lr 1e-3, wd 1e-4), listwise utility CE (temp 0.8) + top-1 pairwise
  softplus (0.5), gradient clip, val-based checkpoint.
- Maru Q16 inference of the trained model: exported weights + cases, forward in
  Maru (`maru/pst_infer.l`), identical picks on 6/6 cases (max score error
  0.0056).

## Result (5 seeds, 100 entity-held-out worlds)

```text
arm          top1   hit    proof  full   proof_beam  full_beam
base         1.619  0.407  0.656  0.420  0.690       0.468
utilhead     1.649  0.422  0.650  0.402  0.679       0.438
mask         1.611  0.412  0.649  0.414  0.684       0.470
goalx        1.685  0.437  0.641  0.380  0.692       0.460
loop         1.611  0.408  0.650  0.422  0.693       0.472
bind         1.633  0.407  0.655  0.416  0.683       0.458

support policy 0.620 proof / top1 1.331   prior 0.360   random 0.267
untrained 0.127   shuffled features 0.000   oracle policy 0.787
```

Findings:

1. The native transformer is an effective deductive ranker on this fixture:
   +3.6pp proof success over the support heuristic, +0.29 top-1 utility, and
   +24pp over the head prior, with the oracle policy at 78.7%.
2. Beam search over the same scores adds +3.4pp proof and +4.8pp full success;
   search-level variation is the reliable lift.
3. The five architecture variants stay inside seed noise (±0.07 top1, ±2pp
   proof). Reported as a null result for architecture variation on a unary
   world where binding has nothing to bind.

## Verification

```bash
cd /research/dlm_v0.0244/experiments/proof_state_transformer_maru
./run.sh && ./verify.sh && ./maru_check.sh     # V0244-PROOF-STATE-TRANSFORMER-PASS
cd /research/dlm_v0.0244 && ./scripts/verify_release.sh
```

## Limits

- Unary predicate world; relational binding (binary predicates with variables)
  is the next fixture, and the only place a binding-aware variant can be
  separated from a predicate-only one.
- 180 training worlds leaves a val/test gap (val top-1 ~2.1 vs test 1.6).
- Beam width 3 over 4 steps, no value model or learned search controller.
- Maru covers inference; training is native C/LLVM.
