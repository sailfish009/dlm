# Integral Learning — Integrability + Deductive-vs-Gradient Verification

Research lab (Python CPU; gradient arm uses PyTorch). Tests the NOTE 87 thesis
(`BACKUP/dlm_v0.0035/dlm/integrate.py`, `credit.py`):

> Induction learns by **differentiation** (parameterised map, loss, gradient).
> Deduction learns by **integration** (closure = forward integral, debt = loss,
> exact per-clause credit, running-sum update = "gradient flow without a
> gradient", Z = Σ exp(−E)).

The symbolic kernel decides all truth; no learned component asserts anything.

## E1 — credit-field integrability (`integrability.py`)

Foundational precondition: for integral learning to define a SINGLE objective,
the credit field must be integrable — a scalar potential F(theory) with
credit(T,r) = F(T+r) − F(T). The discrete obstruction is the plaquette curl
(curvature / holonomy):

```
curl_c(T,r1,r2) = [c(T,r1)+c(T+r1,r2)] − [c(T,r2)+c(T+r2,r1)]
```

Four exact-credit signals over 2400 plaquettes (60 worlds × 40):
- **structure**: goal gain, closure gain, MDL utility — expected integrable.
- **order**: depth-weighted proof credit — expected path-dependent (alternative
  proof paths of different length).

Scalar-objective control: goal/atom/util curl MUST be 0 and MUST equal an
explicit potential difference (validates the apparatus). Depth curl is the
finding, not a gate.

## E2 — integral learning vs gradient (`integral_learn.py`)

Online rule acquisition to close goals. The **integral** learner accumulates
kernel-exact utility credit over rounds (NO gradient, NO parameters; "weights"
are accumulated credit) and admits through the kernel gate. Matched against a
gradient-trained set ranker (M1-style) closed-loop, plus controls:

| arm | mechanism |
|---|---|
| integral | running sum of exact credit (discrete path integral) |
| single | this round's credit only (memoryless) |
| scramble | running sum of swapped credit (mislearned order) |
| permute | fixed permuted credit (corrupted content) |
| random / prior | random pick / static head prior |
| gradient | pre-trained SetRanker, closed-loop top-1 |

3 seeds (777/778/779) × 80 test worlds. Metrics: success rate (all goals
closed), coverage, **loss_integral = trapezoidal ∫debt dt** (NOTE 87), rounds
given success, kernel evaluations, false assertions.

**Compute fairness**: credit-based arms evaluate exact kernel credit for all
live candidates to rank; gradient/random/prior rank without kernel credit and
pay only the single gate check. The gradient arm additionally pays offline
training (180 worlds × 120 epochs).

**Metric caveat**: raw ∫debt dt rewards early stopping (a learner that gives up
has a short, low-area trajectory). It is only a fair efficiency comparison at
matched success; we therefore report success rate and rounds-given-success
alongside, and read ∫debt dt only among successful runs.

## Gates (`verify.py`) — computed, direction-aware

- E1 apparatus control (integrable structure credit + potential identity).
- E2 discriminative: integral success > scramble+0.3 AND > permute+0.3 on every
  seed. This is the 0223 fix: PERMUTE must degrade, else credit content is
  unproven.
- E2 soundness: false_assert == 0 (kernel gate invariant).
- Determinism: E2 seed 777 re-run byte-identical.

Findings (integral vs gradient, integral vs single) are REPORTED with numbers,
not gated into a desired answer.

## Provenance

- `world.py`: byte-identical frozen copy of `../structure_discovery/world.py`
  (sha256 d4231ab78907cdf94c9a69a07603e92c1240cbec3b7f32e3033e621f52d323c3).
- `models.py`: byte-identical frozen copy of `../structure_discovery/models.py`.
- Credit/integral definitions follow NOTE 87 `integrate.py`/`credit.py`
  (forward integral = closure, loss = debt, exact credit, running-sum update,
  trapezoidal loss_integral). Reimplemented self-contained on M1 worlds.

## Run

```bash
./run_all.sh    # E1 -> E2 x3 seeds -> repeat -> verify
```

## Limits

- Propositional unary Horn worlds; small candidate pools (24). Kernel credit
  evaluation is cheap here; at large candidate spaces (cf. M4's 8.8M) the
  online kernel cost of integral learning grows — indexed retrieval required.
- Entity-held-out only; 3 seeds; success-rate margins are pre-registered
  heuristics, not significance tests.
- The gradient arm is the M1 set ranker; stronger statistical baselines are
  future work.
- E2's integral-vs-single null is task-specific: with noisy or non-integrable
  credit, accumulation could earn its keep (not tested here).