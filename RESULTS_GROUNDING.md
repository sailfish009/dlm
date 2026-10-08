# DLM v0.0003 — Grounding branch (L1–L4) results

**Scope.** This branch adds the natural-language front-end that DLM was missing:
a grounder that maps a user sentence to a predicate atom. It is measured, not
asserted. Everything here is **Tier 2** (fixed test set, exact match) except the
retrieval/threshold steps, which are Tier 1.

**Hardware / dependency constraint.** The host has `torch` and `numpy` but no
`transformers`, `sentencepiece`, `tokenizers`, or `bs4`. There are no pretrained
LM weights available: `/research/MeowLLM` (~3.5M, pure torch, MIT) ships an
architecture and a tokenizer but **no checkpoint**, and `/research/tinyLLM`
(0.51B) needs the absent HF stack. So the NL front-end is trained **from
scratch** on the 6GB RTX 2060.

## Design (fixed before looking at the numbers)

* **No generation in the answer path.** The T2 grounder is *retrieval*: embed the
  sentence, take the nearest candidate atom, or **abstain** below a threshold.
  Nothing is generated; there is no free text.
* **Bootstrapping.** The deterministic T1 `GrammarGrounder` synthesizes
  `(sentence, atom)` pairs; T2 learns from them. T1 stays a fallback / validator.
* **Matched faces.** Every arm sees the same sentences and the same candidate
  atom set (64 atoms = 4 relations × 16 ordered entity pairs). Train/val/test use
  disjoint *surface phrasing* of the same relations, so no test atom is missing
  from the index.
* **Threshold on val only**, frozen for test.
* **Borrowed structure** (not code) from CLM/pyssl: a projection head trained with
  a bidirectional in-batch InfoNCE and a learnable `logit_scale` (CLM
  `_clm_loss` shape), with group masking so two sentences with the same atom are
  not mutual negatives. Stage 0 SSL (pyssl) remains optional future work.

## Modules

| # | Module | What it is | Tests |
|---|---|---|---|
| L1 | `dlm/byte_tokenizer.py` | dependency-free byte tokenizer (vocab 260) | 8 |
| L2 | `dlm/tiny_encoder.py` | MeowLLM blocks vendored (MIT) as a 3.08M encoder; pad-invariant, freeze/unfreeze | 9 |
| L3 | `dlm/grounder_learn.py` | `ProjectionHead`, `LearnedGrounder`, `CharNgramGrounder`, `AtomIndex`, `synthesize_pairs`, `pattern_split` | 11 |
| L4 | `run_grounding_eval.py` | matched-arm eval, val-tuned threshold, `artifacts/grounding_eval.json` | 6 |

Full suite: **59 tests pass** (`python3 -m pytest`).

## Main result (test split, 128 sentences, 64 candidates)

| arm | coverage | exact atom | exact\|covered | relation\|covered |
|---|---|---|---|---|
| `t1_train` (deterministic grammar, train phrases) | 0.000 | 0.000 | 0.000 | 0.000 |
| `lexical` (char-3gram, **no learning**) | 1.000 | **0.547** | 0.547 | 0.625 |
| `t2_trained` (encoder + head trained) | 1.000 | 0.352 | 0.352 | 0.484 |
| `t2_frozen` (random frozen encoder + trained head) | 1.000 | 0.195 | 0.195 | 0.477 |

chance exact = 0.0156; majority-relation = 0.250. T1 abstains on **all** test
sentences by construction (their phrasing is unseen), which is exactly the gap
T2 was built to fill.

### Judgment — `control_favored` (see `NEGATIVE_LEDGER.md` NL-6)

The learned grounder is **below the trivial lexical baseline** (0.352 < 0.547) on
this benchmark. It is not a failure of *learning*: the trained arm beats the
frozen-encoder control (0.352 > 0.195) and chance by a wide margin. But it does
not reproduce CLM's frozen-pretrained-encoder advantage — because there is no
pretrained encoder here, only 128 training pairs, and 2 phrases per relation.

`by_phrase` breakdown (exact atom accuracy) shows *why* the lexical control wins:

| test phrase | lexical | t2_trained |
|---|---|---|
| `is {e} a parent to {e}` | 1.00 | 0.19 |
| `is {e} a grandparent to {e}` | 1.00 | 0.06 |
| `are {e} and {e} siblings` | 0.94 | 0.00 |
| `is {e} a brother or sister of {e}` | 1.00 | 0.00 |
| `does {e} have {e} as their child` | 0.44 | 0.12 |
| `is {e} above {e} in the family tree` | 0.00 | 0.00 |
| `does {e} come before {e} in the family tree` | 0.00 | 0.00 |
| `is {e} the mother or father of a parent of {e}` | 0.00 | 0.19 |

The lexical arm wins where the entity pair alone nearly determines the atom
(names are high-signal 3-grams). Both arms fail when the relation word changes
(`above`, `come before`). The transformer never recovers that.

### Engineering conclusion (adopted)

Use the dependency-free **lexical grounder as the default T2 fallback**, and keep
`LearnedGrounder` behind the same `Grounder` protocol, promoted **only if** it
beats the lexical baseline on the same split. This keeps the answer path honest
and cheap on 6GB.

## Claim tiers

| claim | tier | evidence |
|---|---|---|
| T1 grammar grounds seen phrasings exactly | 2 | 11 tests + deterministic |
| T2 encoder/harness works and learns (trained > frozen > chance) | 2 | `grounding_eval.json` |
| T2 beats a lexical baseline | **not claimed** (control favored) | NL-6 |
| Retrieval/threshold changes KB contents | 1 | — |
| Any quantum / 6GB advantage | **none** | 6GB is a constraint |

## Reproduce

```bash
cd /research/dlm_v0.0003
python3 -m pytest -q                         # 59 tests
python3 run_grounding_eval.py --quick        # ~20 epochs, sanity
python3 run_grounding_eval.py --epochs 150   # writes artifacts/grounding_eval.json
```

Artifacts: `artifacts/grounding_eval.json` (full report incl. `by_phrase`),
`artifacts/learned_grounder.pt` (last trained T2, `save()`/`load()` verified).

## Next (reopen conditions for NL-6)

1. More supervision (≥ ~10× pairs; more phrases per relation).
2. Stage 0 SSL pretraining (pyssl-style) on unlabeled text, then freeze + InfoNCE.
3. Entity-name masking and/or a learned BPE tokenizer so the model must use the
   relation word.
4. A **harder, entity-held-out** split so the lexical name-matching shortcut is
   removed and the comparison is about relation meaning.

No provisional observation above is a settled fact; the negative is registered
and the reopen path is explicit (R5.2).