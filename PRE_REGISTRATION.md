# DLM v0.0001 — PRE-REGISTRATION

> Governed in spirit by `/research/GUIDELINES.md`. DLM is not a `qvm_v*`/`testq_v*`
> version, so no quantum resource is claimed. Claim tiers are still declared.

## 0. Identity

- **Project**: DLM — Deductive Logic Model (`/research/dlm_v0.0001`).
- **Contrast**: LLM = Large + Language (inductive statistics); VLM = Vision + Language;
  DLM = Deductive + Logic. Non-generative: it derives answers and emits a proof,
  it does not produce free text.
- **Difference from Cyc**: Cyc hand-authors rules. DLM *induces* rules from
  positive/negative examples, then deduces. Rule acquisition is a first-class step.

## Claim tiers

| Component | Tier | Why |
|---|---|---|
| Deduction engine (forward fixpoint + SLD) | **Tier 2** | exact symbolic semantics; soundness is consistency-checked, not a performance gate |
| Rule induction (`generalize.py`) | **Tier 2** | exact anti-unification + bounded search; outputs are Horn clauses |
| Decider head (`decider.py`) | **Tier 1** | learned inductive bias over hand features |
| Whole system | **no Tier 3** | no physical/hardware advantage is claimed |

**R2.3 compliance**: no "advantage" language. The 6 GB result is a *feasibility
constraint*, not an advantage.

## 1. Goal link

Provide a local, non-generative reasoning system for closed domains: from a
retrieved knowledge base, induce general rules and derive answers with an
auditable proof. It is the deductive counterpart to the LLM's inductive mode.

## 2. Preserved / changed

- **Preserved**: the `/research` discipline — claim tiers, matched arms,
  exact checks, a negative ledger, a `work.txt` resume log.
- **Changed**: the object is a symbolic Horn program with a discriminative
  gate, not a differentiable attention model.

## 3. Single core variable / controls

The only variable is the **decider gate**. Both arms use the identical KB, the
identical candidate set, and the identical deduction engine:

| Arm | Selection |
|---|---|
| `no_decider` | all retrieved candidates |
| `with_decider` | candidates with calibrated P ≥ 0.5, then System-2 fallback to all candidates if no answer |

`fallback=True` is a soundness-preserving design: the decider may not reduce
recall. Recall loss is reported as a failure, not smoothed over.

## 4. Resources and their definitions (non-quantum)

- Resource under test: **the discriminative gate** (does ranking retrieved
  candidates change cost or answers?).
- Matched control: `no_decider`, same candidates.
- No invariance/function-class claim beyond the feature vector's stated order.

## 5. Postulates (predictions, written before the run)

- **P1**: forward closure and SLD answers agree on all ground atoms (exact).
- **P2**: induction recovers a consistent rule for `grandparent` and never
  covers a declared negative.
- **P3**: the decider's fast path keeps all true-positive answers (via fallback).
- **P4 (null expected)**: the 8 hand features do **not** separate an
  instantiable, same-shape, semantically wrong rule from a good one; false
  positives from such a rule persist in both arms.

## 6. Judgement / stop rules

- **Survival** of the decider gate: fast-path candidate reduction with zero
  recall loss and a reported fallback rate.
- **Null**: P4 confirmed → register in `RESULTS.md` and record as the top
  v0.0002 work item (semantic/anchor features), not as "needs more tuning".
- Ties are reported as ties. No best-of-sweep ranking without the seed/split.

## 7. Scale and limits

- Toy domains only (a few dozen facts, dim-free). No claim beyond tested scale.
- Retrieval recall bounds what the pipeline can ever answer.

## 8. Next decision this run informs

If the decider gate survives, keep it and invest in features (v0.0002). If the
engine's induction is the only durable contribution, pivot to rule-learning
coverage rather than gate tuning.