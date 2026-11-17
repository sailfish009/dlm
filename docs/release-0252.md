# Release 0.0252 — integration (path + prior) and lifted predicate tokens

- Date: 2026-11-15
- Predecessor: 0.0251 (preserved)
- Type: candidate research release
- Runtime: `20261114T001318Z-27176` (reused; `src/` Maru core unchanged)

## Motivation

User direction: discover a deduction-specific transformer-like structure by rearranging
components and adding mechanisms, rather than adapting the LLM transformer. Two designated
sources were read and verified before implementing:

- `/research/2605.04193v2.pdf` (ANDRE): conjunction = softmin attention `C = Σ softmax(−βB)·B`
  (eq 7/8), disjunction = softmax attention (eq 9); Appendix B proves softmin upper-approximates
  min and product t-norm lower-approximates it with larger error, for **some finite β\*** (an
  existence claim); Table 4 ablation operator→product drops 0.92→0.76; prob-sum activation eq 5;
  range-restricted/connected syntactic losses eq 14/15.
- `/research/retention`: linear-attention state `S = φ(K)ᵀV` plus normalizer `s`, decay gating
  `log_G`, power expansion `deg`; state size independent of context length.

This release implements the **P0 (integration) + P1 (generalization)** steps of the design on the
native proof-state ranker (`experiments/proof_state_transformer_maru`). The binding+AND+shared-repeat
deduction cell (design P4) remains `not-implemented`; it is the next structural step after this evidence.

## What was added (all compile-time additive; default build byte-identical to 0251)

| Flag | Mechanism |
|---|---|
| `INTEGRAL=1` | 3 candidate features: path-integral support **time-average** `A_t(r)/wsum`, support **growth** `support_t − support_0`, and a **per-rule prior** (mean train utility). `A_t(r) = Σ_τ γ^{t−τ} support_τ(r)`, `γ=PATH_GAMMA` (default 1.0 = monotone retention). |
| `LIFTED=1`, `LIFT_RHO=ρ` | Scale the predicate-id one-hot block (candidate cols 8..25) by ρ in the embedding: `h = W_type·cf_type + ρ·W_id·cf_id`. ρ=1 ≡ base; ρ=0.25 main arm; ρ=0 type-only control. |
| `PRIOR_SHUF=1` | Derange the per-rule prior (offset 37, coprime with 90): identity-destroying control. |
| `--holdout 45` | Predicate-held-out protocol: train/val worlds have **no** goal in {4,5}; test worlds have **all** goals in {4,5}. Requires `--goal-scan`. Recorded in the weights header. |

### Design decisions grounded in the lab

- **Path integral is a kernel-consistent state function.** It is recomputed by replaying the
  committed-rule prefix (`fill_path_features`), identically at train (oracle prefix) and eval
  (policy prefix, including each beam branch). This avoids the teacher/policy exposure confound:
  the feature depends only on `(facts, committed set)`, which the lab already recomputes per state.
- **Prior is train-only.** `rule_prior_from_train` uses split 0 utilities only (no val/test leakage).
  Utilities are prior-independent, so a clean two-pass fill avoids circularity.
- **γ=1 default.** Decay (γ<1) is forgetting and conflicts with deductive monotonicity; it is left
  as a one-build ablation (`PATH_GAMMA`), not the default.

## Structural gates (all PASS)

- `GRADCHECK` integral / lifted / both: rel_to_max_grad ~2e-10..6e-10.
- `RHO1-EQUIV-PASS`: lifted(ρ=1) pchk == base pchk (8393.390580) — the lifted projection is exactly
  the base model at ρ=1.
- `PATH-CHECK`: independent incremental accumulator vs prefix replay, `path_maxdiff=0`,
  `prior_maxdiff=0` (831 candidate-steps).
- `DEFAULT-BYTE-COMPAT`: 0252 default build == 0251 on a fixed short train (diff clean).
- `HARNESS-REGRESSION-PASS`: bal arm reproduces the pinned 0251 ladder (d2b4 0.7832).
- `BOTH-LLVM-MATRIX` O0/O2/O3 byte-identical; `INTEGRAL-ASAN+UBSAN` clean at budget 6 / depth 4.
- `HOLDOUT-FILTER-PASS`: train excludes {4,5}, test all-in; scans 566/2557 ≪ 20000 guard, all genuine.
- `probe_stats` schema check on all 6 ladder arms + 4 held-out arms.

## Results (5 seeds, train d2/b4, `--balance-reward`, paired-by-seed 2SE)

### Integration axis (integral = path + prior vs bal)

Ladder (goal coverage):

| cfg | bal | integral | Δ |
|---|---|---|---|
| d2 b4 | 0.7832 | 0.7846 | +0.0014 |
| d3 b4 | 0.5977 | 0.5440 | −0.0537 |
| d4 b4 | 0.1159 | 0.1000 | −0.0159 |
| d2 b6 | 0.9524 | 0.9626 | +0.0102 |
| d4 b6 | 0.6651 | 0.6079 | −0.0572 |

Paired contrasts `integral−bal`: d2b4 +0.0014±0.0038, d4b4 −0.0159±0.0205, d4b6 greedy
−0.0572±0.0598, d4b6 beam +0.0397±0.0482 — **all INCONCLUSIVE at 2SE**.

**Reading (observed, not proven):** on this unary ranker fixture the integration features add no
reliable gain. This is consistent with 0241 (exact integrable credit is a potential difference, so
accumulation adds nothing over greedy) and 0243 (the prior gain appeared under *tight-budget noisy*
credit, a regime this rich-feature ranker does not occupy). The path integral is largely redundant
with current support at shallow depth; the per-rule prior is redundant with the existing goal/support
features. The integration axis is **not supported here**; it is not refuted for the noisy-credit regime.

### Generalization axis (lifted tokens) and controls

Ladder (goal coverage), 5 seeds:

| cfg | bal | lifted ρ=.25 | lifted ρ=0 | both | priorshuf |
|---|---|---|---|---|---|
| d2 b4 | 0.7832 | 0.7985 | 0.7875 | 0.7956 | 0.7795 |
| d3 b4 | 0.5977 | 0.5897 | 0.6092 | 0.5257 | 0.5440 |
| d4 b4 | 0.1159 | 0.1254 | 0.1381 | 0.1397 | 0.1317 |
| d2 b6 | 0.9524 | 0.9780 | 0.9780 | 0.9751 | 0.9560 |
| d4 b6 | 0.6651 | 0.7873 | **0.8048** | 0.6143 | 0.6206 |

Paired contrasts at d4b6 (goal):

| contrast | mean ± SE | range | verdict |
|---|---|---|---|
| lifted0 − bal | **+0.1397 ± 0.0525** | [+0.024, +0.294] | **SIGNIFICANT, all 5 seeds positive** |
| lifted(ρ=.25) − bal | +0.1222 ± 0.0586 | [−0.103, +0.214] | SIGNIFICANT (one negative seed) |
| lifted0 − lifted(ρ=.25) | +0.0175 ± 0.0619 | [−0.175, +0.175] | INCONCLUSIVE |
| both − lifted | −0.1730 ± 0.0913 | [−0.429, +0.095] | INCONCLUSIVE (large negative) |
| priorshuf − integral | +0.0127 ± 0.0377 | [−0.103, +0.135] | INCONCLUSIVE |

ID (d2b4): lifted − bal +0.0154±0.0061 (significant, small); lifted0 − bal +0.0044±0.0124 (ns).

**Reading (observed):** down-weighting or removing candidate-side predicate identity improves
depth+budget generalization. The type-only arm (ρ=0) is the robust winner: +14pp at d4b6 with every
seed positive, ID unchanged. Predicate identity still enters through the **state-token goal one-hots**
and the **relational `head==goal_pred` features** (RELOB), which are not scaled by LIFTED — so the model
matches rules to goals relationally without memorizing absolute predicate ids. This is the lifted-token
generalization hypothesis working on the depth ladder.

Two caveats: (1) adding the integration features to lifted (`both`) erases the gain at d4b6
(0.787→0.614, one seed −0.43) — the extra path/prior dimensions appear to add overfitting noise; the
integration and generalization axes do not compose here. (2) The prior identity is irrelevant
(priorshuf ≈ integral), so the per-rule prior carries no useful identity-specific signal on this fixture.

### Held-out predicate transfer (train d2 ho{4,5} → test goals all in {4,5})

Goal coverage on goals whose predicates were never seen in training:

| arm | ho d2 b4 | ho d2 b6 |
|---|---|---|
| bal | 0.7725 | 0.9383 |
| integral | 0.7686 | 0.9353 |
| lifted ρ=.25 | 0.7902 | 0.9735 |
| both | 0.7314 | 0.9579 |
| lifted ρ=0 | **0.8059** | **0.9794** |

Paired contrasts at ho d2b4: lifted0−bal +0.0333±0.0187 (range −0.029..+0.078), lifted−bal
+0.0176±0.0110, integral−bal −0.0039±0.0196 — **all INCONCLUSIVE at 2SE** (n=5).

**Reading (observed):** predicate-held-out transfer is already strong for the baseline (0.7725),
because the relational `head==goal_pred` features match rules to unseen-predicate goals without
memorizing predicate ids. There is little headroom, and the lifted arms' small positive point
estimates do not reach 2SE. So the lifted-token benefit measured here is **depth generalization**
(d4b6 +14pp, robust), not predicate-identity transfer (already near-ceiling). The `both` arm again
lags (0.7314), consistent with the integration features adding overfitting noise.

### Summary of the two axes

- **Integration (path + prior): null on this fixture.** No reliable gain anywhere; prior identity
  irrelevant (shuffle control); combining with lifted hurts depth. Consistent with 0241/0243.
- **Generalization (lifted / type-only tokens): positive and robust for depth OOD.** ρ=0 gives
  +14pp at d4b6 (all seeds positive), ID unchanged; predicate-held-out transfer is near-ceiling via
  relational features and shows no significant additional gain.

## Honest limits

- Unary propositional fixture; the binding/AND cell and the 2-variable relational fixture are still
  not implemented, so this release does not test the core deduction-cell hypothesis.
- ANDRE's operator theorem is ∃β\*, not ∀β: at β=4, b=(0.95,0.5) gives softmin error 0.064 > product
  error 0.025 (verified counterexample). Operator superiority is distribution-dependent at finite β;
  the graded-valuation operator separation (design-1 P1) is still pending and is a prerequisite for
  the cell, not for this ranker-level release.
- The cell's monotone `v←max(v,ĥ)` update combined with softmin's *upper* approximation of min can
  over-derive within an episode; the kernel closure remains the truth authority at evaluation.
- n=5 seeds; effects below 2SE are reported as inconclusive, following the 0251 convention.

## Verification

`cd experiments/proof_state_transformer_maru && ./run.sh && ./verify.sh` → `V0252-INTEGRAL-LIFTED-PASS`.
Release gate: `bash scripts/verify_release.sh` → `RELEASE-VERIFY-PASS version=0.0252`.