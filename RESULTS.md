# DLM v0.0001 — RESULTS

Every number carries its **provenance**: artifact path, command, and split.
Nothing here is best-of-sweep; each run is a single configuration.

## R1. Environment / feasibility (R3 honesty check)

| Quantity | Value | Provenance |
|---|---|---|
| Device | NVIDIA GeForce RTX 2060 | `artifacts/vram_probe.json` |
| torch | 2.14.1+cu130, CUDA True | same |
| torch total memory | 6,030,557,184 B (**5751 MiB**) | same |
| nvidia-smi total | 6144 MiB | `nvidia-smi` |
| Peak reserved (decider forward/step) | 23,068,672 B (**22.0 MiB**) | same |
| Peak allocated | 17,281,024 B (**16.5 MiB**) | same |
| Headroom factor | **261×** | same |
| Verdict | `fits_6gb` | same |

> torch reports 5751 MiB while nvidia-smi reports 6144 MiB. The discrepancy is
> reported, not hidden; the feasibility verdict is unchanged either way.

Command: `python3 probe_vram.py`.

## R2. Exact engine checks (Tier 2)

| Check | Result | Provenance |
|---|---|---|
| Forward closure == SLD answers | all ground atoms agree | `tests/test_dlm.py::test_forward_backward_agree` |
| SLD proves `ancestor(alice,dave)` | yes, proof depth ≥ 3, ≥ 3 leaves | `test_proof_trace_is_a_tree` |
| Unsafe rule rejected | `ValueError` raised | `test_unsafe_rule_rejected` |
| Full test suite | **9 passed** | `python3 -m pytest tests -q` |

## R3. Induction (Tier 2)

From `parent/2` facts and 3 positives + 3 negatives, the learner recovered:

```
grandparent(?G2, ?G3) :- edge(?G2, ?E0), edge(?E0, ?G3).
```

- Positives derived: **3/3**; negatives covered: **0/3** (P2 holds).
- Provenance: `artifacts/demo_metrics.json` → `induced_rules`;
  `tests/test_dlm.py::test_induce_grandparent`.

## R4. Decider gate, matched arms (Tier 1)

Identical KB, identical candidate set, identical engine; only the gate differs.
Domain: a 4-edge chain, 10 positive `reach` queries, 10 negative queries.

| Metric | `no_decider` | `with_decider` |
|---|---|---|
| Positives answered | **10/10** | **10/10** |
| Negatives falsely answered | 4/10 | 4/10 |
| Candidates selected (fast path) | 50/50 | **20/50** |
| System-2 fallbacks | 0 | **6** |
| Rules dropped by gate | — | `reach_far`, `reach_jump`, `reach_step` |

Provenance: `artifacts/demo_metrics.json` →
`part_A_noninstantiable_distractors`; command `python3 run_demo.py`.

**Reading**: the gate cuts the fast-path candidate set to 40% with **zero recall
loss** (fallback restores the recursive rule it wrongly dropped). The gain is
efficiency, not answers.

## R5. Negative result — P4 confirmed (pre-registered null)

`reach_rev` (`reach(y,x) :- edge(x,y)`) is instantiable, same shape as the good
`reach_base`, and semantically wrong. The 8 hand features give it an **identical**
feature vector to `reach_base` with the opposite label, so no v0.0001 decider can
separate them. False positives from it persist in **both** arms (4/10 above).

This is a **registered null**, not a tuning target. The v0.0002 work item is
query-anchored / semantic features (does a rule's body actually connect to the
query's constants?).

## R6. What is *not* claimed

- No language understanding, no open-domain coverage, no generation.
- No quantum or physical resource (this is not a `qvm_v*`/`testq_v*` run).
- No scale claim beyond the toy domains tested.
- No "advantage" over an LLM; the comparison is architectural, not empirical.