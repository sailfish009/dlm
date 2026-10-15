# `experiments/abstraction` — the L5–L9 abstraction ladder

v0.0041 generalizes the **understanding vocabulary** (`trains`, `backpropagates`,
…) across a corpus, but its concepts are *propositional*: a conjunction of unary
subject features. v0.0042 (`dlm/compose.py`) climbs the ladder that
`../mnist/ABSTRACTION_COMPARISON.md` showed was still empty — composition,
architecture, intent, cause, and transfer.

Only **L8 is fully propositional**, but it is *certified* from acquired facts.
**L7 is deliberately never certified**: intent is read from the program's own text
and reported as a hypothesis. Everything else is a *proposal whose firing the
kernel checks* (`dlm.proof.verify`), with transfer to a held-out program as the
falsification.

| level | procedure | trust |
|---|---|---|
| L5 composition | `compose.induce_patterns` — connected conjunctive patterns over the structural vocabulary | kernel-derived instances |
| L6 architecture | `compose.motifs`/`forward_ops`/`layer_kinds` — ordered **role** motifs in `forward` | mined + transfer + new-shape discriminant |
| L7 intent | `INTENT_CUES` over docstrings / `argparse help=` / `description=` | **hypothesis, never certified** |
| L8 causal | `explains(F,S) :- calls(F,S), api_effect(S,E)` over acquired `API_EFFECTS` | certified (sound as the acquired facts) |
| L9 transfer | `compose.transfer_patterns` on held-out programs | deductive transfer + analogies |

## Run

```bash
./abstraction.sh                 # or from the repo root:
./experiments/abstraction/abstraction.sh
../../northstar.sh --offline --check   # runs mnist + generalize + abstraction
```

Writes `reports/abstraction/<stamp>/result.json` and prints `report: <path>`.

## What it measures (last run)

* **L5** recovers `calls(X,Y),calls(Y,Z)` — *“X delegates to a routine that itself
  calls things”* — which hits `main`; plus the connected variants
  `calls(Y,X),calls(Z,Y)` etc. Each is non-degenerate and irredundant.
* **L6** recovers the motif `['conv','relu']`; it **transfers** to the real
  `main.py` forward pass and is **discriminated** on a held-out dropout-only
  shape (no conv ⇒ no hit).
* **L7** yields 11 hypotheses (`classifies handwritten digits`,
  `is a reference example`, …), all `certified: False`.
* **L8** derives 9 certified “why” sentences (e.g. *“optimizer.zero_grad in order
  to prevents_gradient_accumulation”*).
* **L9** transfers every L5 pattern to `northstar` and `s_dropout`.
* `abstraction_score` = **1.0** against the human checklist. It counts items
  produced *with support*, not depth — a PASS is a **soundness** PASS.

## Honest limits

* L7 is text-cued and can be fooled; it is never allowed into the closure.
* L8 is exactly as sound as the acquired `API_EFFECTS`; it is not inferred from
  the code.
* The patterns are flat and one-level; recursive IR-TREE macros over
  `abstract_theory` and a *learnable* bridge remain open.