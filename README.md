# DLM v0.0001 — Deductive Logic Model

A **local, non-generative** reasoning system for closed domains.

LLM = Large **Language** Model · VLM = **Vision**–Language Model ·
**DLM = Deductive Logic Model**.

A DLM does not generate free text. It **induces** general rules from examples,
**retrieves** a knowledge base, and **derives** answers by deduction, returning
an auditable proof. Unlike Cyc, the rules are learned, not hand-authored.

Runs inside a **6 GB GPU (RTX 2060)** budget: the only learned component is a
161-parameter re-ranking head; retrieval and deduction are exact and CPU-side.

## Architecture

```
query ─▶ Retrieval ─▶ Decider (rank) ─▶ Logic engine ─▶ answer + proof
             │              │                 │
        predicate index  learned gate   forward-chain / SLD
        (exact, CPU)     (161 params)   (exact, CPU)
             └────────── System-2 fallback if the gate yields no answer ──────┘
```

1. **Enumeration / retrieval** — candidate facts and rules are pulled by
   predicate index (`retrieval.py`).
2. **Decider** — a tiny MLP scores candidates from 8 hand features and keeps
   P ≥ 0.5 (`decider.py`). It is a *gate*, not a generator.
3. **Logic** — the restricted KB is closed under forward chaining and queried
   with SLD resolution, producing a `Proof` tree (`deduce.py`).
4. **Induction** — `generalize.py` learns Horn rules by anti-unification over
   positive/negative examples, bounded in body length.

## Quickstart

```bash
cd /research/dlm_v0.0001
python3 -m pytest tests -q          # 9 unit tests
python3 examples/induction_demo.py  # recover a rule from examples
python3 examples/deduction_demo.py  # derive an answer + proof trace
python3 run_demo.py                 # end-to-end demo -> artifacts/demo_metrics.json
python3 probe_vram.py               # 6 GB feasibility probe -> artifacts/vram_probe.json
python3 tools/build_upload.py       # clean GitHub web-upload bundle
```

Install as a package: `python -m pip install -e .` (add `[gpu]` for the torch
mirror used by the VRAM probe).

## Module map

| File | Role |
|---|---|
| `dlm/terms.py` | Terms, atoms, unification (Robinson + occurs-check). No function symbols → finite Herbrand base. |
| `dlm/rules.py` | Horn clauses (`Rule`), facts, alpha-renaming. |
| `dlm/kb.py` | Indexed knowledge base, Datalog safety check. |
| `dlm/deduce.py` | Forward fixpoint + SLD backward chaining with proof trace. |
| `dlm/generalize.py` | LGG-based inductive rule learning. |
| `dlm/retrieval.py` | Predicate-indexed retrieval + 8-feature vectors. |
| `dlm/decider.py` | NumPy MLP gate (+ a torch mirror for the VRAM probe). |
| `dlm/pipeline.py` | End-to-end orchestration and training-data collection. |

## Claim tiers (see `PRE_REGISTRATION.md`)

- Engine + induction: **Tier 2** (exact symbolic semantics).
- Decider: **Tier 1** (learned bias over hand features).
- System: **no Tier 3**, no hardware advantage claimed. 6 GB is a constraint.

## Honest limitations (v0.0001)

- **Features do not separate same-shape semantic distractors.** A rule that is
  instantiable but wrong (`reach_rev`) shares identical features with a good
  rule; false positives persist in both arms. See `RESULTS.md` and P4.
- Induction is limited to small, binary/unary, function-free Horn theories.
- Retrieval recall upper-bounds achievable accuracy.
- Toy scale only; no claim beyond a few dozen facts.

## Resume log

`work.txt` holds GOAL / DECISIONS / NEXT STEP. v0.0002 top item: semantic/anchor
features so the gate can drop `reach_far`/`reach_step` without fallback.