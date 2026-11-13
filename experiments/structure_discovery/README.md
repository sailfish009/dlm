# Structure Discovery — P0 qualification + P1 directional variants

Research adapter (PyTorch CPU). The symbolic closure oracle produces all
labels; no learned component decides truth. This lab moves structural
variants OFF the prior-saturated MNIST 10-case fixture (where prior-only =
full DT = 8/10 ground truth and 0229's difference-only gate passed on
accuracy degradation) ONTO the M1 proof-state worlds, where learning is
demonstrated against controls.

## P0 — fixture qualification (`qualify.py`)

Computed margins on 80 held-out worlds (seed 999): oracle ceiling vs support
heuristic >= 0.5, ceiling vs learned prior >= 1.0, support vs random >= 0.5,
entity splits disjoint. A fixture that fails these margins cannot register
structure and is not used.

## P1 — single-axis variants (`models.py`, `train.py`)

| variant | axis | hypothesis | params |
|---|---|---|---|
| base | — | M1 SetRanker replica (2 independent layers, 4 heads, no PE, bidirectional) | P |
| a1_cross | candidate↔candidate attention blocked at TRAIN time | if inter-candidate comparison is recruited, blocking it degrades learning curves | P (same) |
| a2_pe | learned positional embeddings | NULL control: set semantics ⇒ PE should not help | P + 2080 |
| a3_tied2 | one shared block × 2 loops | recurrent depth vs capacity | P₁ |
| a3_indep1 | one independent block | param-matched, init-identical control for a3_tied2 (same params, half compute) | P₁ |

3 seeds (11/12/13) × 180/40/40 worlds × 120 epochs, identical data pipeline,
loss (listwise utility CE + top-1 pairwise), optimizer and checkpoint
selection as M1. Validation curves logged from before training (epoch −1)
every 10 epochs. Controls per run: train-derived prior, support heuristic,
random, untrained, shuffled-features.

## Gates (`verify.py`) — all computed, direction-aware

1. P0 margins + disjoint splits.
2. **Base parity**: seed 11 reproduces the frozen 0238 M1 result
   (`reference_m1_seed11.json`, all metric fields abs < 1e-6) — harness drift
   control.
3. Base beats all controls with M1 margins on every seed; learning moves the
   validation metric (final − pre-training >= 0.5).
4. Parameter accounting: a1 == base; a2 == base + 2080; tied2 == indep1 < base.
5. Determinism: base seed 11 retrain byte-identical (`repeat_check.sh`).
6. Direction table: per-seed deltas vs base (same seed), mean, sd, early
   (epoch 30) deltas. **No "must differ" requirement.**

## Pre-registered effect rule

A variant shows a *consistent effect* iff all 3 seed deltas share a sign AND
|mean delta| >= 0.2 utility. Otherwise: *no consistent effect*. Consistent
effects are reported with their direction; a degradation is a finding about
recruitment, not a gate failure. A2 is expected null; a positive A2 effect
would indicate positional artifacts in the task.

## Provenance

- `world.py` is a byte-identical frozen copy of `../m1_proof_state/world.py`
  (sha256 d4231ab78907cdf94c9a69a07603e92c1240cbec3b7f32e3033e621f52d323c3).
- `reference_m1_seed11.json` is a byte-identical copy of the 0238 committed
  `m1_seed11.json` (sha256 67bcdb68d596fe4755ad1f2d65061b4d1d52e1c9b26d6170f3a6b86f53f2e180).

## Run

```bash
./run_all.sh        # qualify -> 5 variants x 3 seeds -> repeat -> verify
```

## Limits

- PyTorch research adapter, not native Q16/C (M0 path is separate).
- Synthetic propositional Horn worlds; entity-held-out only (relation-held-out
  deferred, as in M2).
- 3 seeds; the effect rule is a pre-registered heuristic, not a significance
  test. Cross-task replication (M2 conflict worlds, M3 closed loop) is P3.
- A1 masks attention at train and eval; a pure eval-only mask probe is a
  follow-up intervention.