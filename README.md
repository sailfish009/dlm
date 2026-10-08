# DLM — Deductive Logic Model (v0.0003)

**DLM = Deductive + Logic + Model.** It answers `noul` / `choice` / `score`
questions by *proof*, not by generating text. There is **no LLM in the answer
path**: the decision is a sound Horn-clause derivation over a knowledge base,
with an auditable proof trace.

    LLM = Large      + Language + Model   (inductive statistics)
    VLM = Vision     + Language + Model
    DLM = Deductive  + Logic    + Model   (induce rules, then deduce and decide)

## What changed in v0.0003

v0.0002 was the decision-engine torso (wires `noul`/`choice`/`score`). v0.0003
adds the missing **natural-language front-end**: a grounder that maps a user
sentence to a predicate atom. It is built and *measured* in four modules:

| # | module | what it is |
|---|---|---|
| L1 | `dlm/byte_tokenizer.py` | dependency-free byte tokenizer (vocab 260) |
| L2 | `dlm/tiny_encoder.py` | ~3.1M transformer encoder (MeowLLM blocks, MIT) |
| L3 | `dlm/grounder_learn.py` | CLM-style InfoNCE head, retrieval grounder, lexical control |
| L4 | `run_grounding_eval.py` | matched-arm evaluation → `artifacts/grounding_eval.json` |
| W4 | `dlm/dialogue.py` | the **dialogue loop**: ground → prove/assert → template reply |

## The honest result (read this before trusting the grounder)

On the v0.0003 benchmark the **learned** grounder is *below* a trivial
character-n-gram baseline:

| arm | coverage | exact atom (test) |
|---|---|---|
| `t1_train` deterministic grammar (seen phrasing only) | 0.000 | 0.000 |
| `lexical` char-3gram, **no learning** | 1.000 | **0.547** |
| `t2_trained` encoder + head trained | 1.000 | 0.352 |
| `t2_frozen` random frozen encoder + head | 1.000 | 0.195 |

chance exact = 0.0156; majority-relation = 0.250. Training *does* help
(0.352 > 0.195 > chance), but it does **not** beat the lexical baseline, so the
CLM frozen-pretrained-encoder advantage is **not reproduced** here — there is no
pretrained encoder, only 128 training pairs and 2 phrases per relation.

This is registered (`NEGATIVE_LEDGER.md` NL-6, judgment `control_favored`) and the
engineering consequence is adopted: the **lexical grounder is the default T2
fallback**, and `LearnedGrounder` is promoted only if it beats lexical on the same
split. See `RESULTS_GROUNDING.md` for the full `by_phrase` breakdown.

**6GB is a constraint, not an advantage.** The symbolic core is ~MB; the encoder
is ~3.1M. No claim of efficiency superiority is made.

## Talking to it, and what "learning" means

`dlm/dialogue.py` turns the parts into a loop: `DialogueSession` grounds an
utterance (via any `Grounder`), then either asserts it (KB growth, user-tagged
provenance), asks by proof, abstains, or rejects a contradiction.

```bash
python -m pytest -q                       # 89 tests
PYTHONPATH=. python examples/dialogue_demo.py    # induction + conversation + abstain
python run_dialogue_eval.py               # writes artifacts/dialogue_eval.json

dlm-chat                                  # INTERACTIVE conversation (installed)
```

To actually talk to it, install and run the console script:

```bash
python -m pip install -e '.[learn]'
dlm-chat            # or: python -m dlm.chat
```

```
you> is alice an ancestor of dave
DLM: yes — ancestor(alice, dave)   [anc_step] ; parent(alice, bob)   [fact] ; ...
you> erin is a parent of frank
DLM: noted parent(erin, frank) (KB now 4 facts)
you> who likes cake
DLM: I don't understand that sentence (no grounder produced an atom).
```
Commands: `:help :kb :facts :rules :user :quit`.

Matched arms (single variable = the grounder; intent forced with `ask`/`tell`):

| arm | coverage | exact-atom | verdict | confident-wrong | abstain |
|---|---|---|---|---|---|
| `t1_only` grammar (train phrasing) | 0.545 | 0.600 | 0.500 | 0 | 0.455 |
| `chain` T1 + lexical T2 | 0.727 | 0.800 | 0.750 | 0 | 0.273 |

Judgment `fallback_helps` (n = 11 scripted turns — a smoke test, not a general
dialogue claim). `verdict_accuracy` counts abstention as incorrect. See
`RESULTS_DIALOGUE.md`.

**Learning = symbolic, in four layers** (see `RESULTS_GROUNDING.md`):
1. **KB growth** — `tell()` adds facts. 2. **Rule induction** —
`induce_rules()` (LGG) generalizes Horn rules. 3. **Discriminative head** —
`LearnedGrounder` InfoNCE (`control_favored` vs lexical, so not the default).
4. **Active ingestion** — *not implemented yet* (W1–W3). **Conversation is not
neural generation**: replies are templates, the only dynamic text is a proof
rendering, and it **abstains** instead of guessing.

## Quickstart

```bash
pip install -e .              # symbolic core: numpy only
pip install -e '.[learn]'     # + torch, for the NL grounding branch

python -m pytest -q                       # 89 tests
PYTHONPATH=. python examples/grounding_demo.py
PYTHONPATH=. python examples/dialogue_demo.py
dlm-chat                                  # interactive grounded dialogue
python run_grounding_eval.py --epochs 150 # writes artifacts/grounding_eval.json
python run_dialogue_eval.py               # writes artifacts/dialogue_eval.json
```

## The pipeline

```
[user NL] --Grounder--> query atoms ------------------------+
                                                            v
[web/API] --Fetcher--> text --Extractor--> candidate atoms -> IngestionGate -> KB
                                                            |                  |
                                                            DLM proof <--------+
                                                                |
[answer] <--Verbalizer-- proof + provenance
```

* **Grounder tiers** behind one `Grounder` protocol: T1 deterministic grammar
  (`GrammarGrounder`, reliable but narrow), T2 learned retrieval
  (`LearnedGrounder`) / lexical (`CharNgramGrounder`), `ChainGrounder` tries them
  in order. A grounder **abstains** rather than guesses.
* **Dialogue** (`DialogueSession`) is that pipeline as a loop: query → proof,
  tell → KB growth, contradiction → reject, no grounder → abstain.
* **No generation.** Retrieval + abstain; the verbalizer is a template.
* **Logic** is function-free Horn (Datalog) with a safety check; the proof trace
  is returned with the answer.

## Claim tiers

| claim | tier |
|---|---|
| engine decision / proof | 2 |
| grounding exact-match on a fixed test set | 2 |
| confidence calibration | 1 |
| retrieval / threshold effects | 1 |
| "learned grounding beats lexical" | **not claimed** (NL-6) |
| quantum / 6GB advantage | none |

## Layout

```
dlm/                 engine + wire + grounding front-end
  terms,rules,kb,deduce,generalize,retrieval,decider   # v0.0001 core
  schema,interpreter,decision,adapter                 # v0.0002 decision engine
  grounding,byte_tokenizer,tiny_encoder,grounder_learn# v0.0003 NL front-end
  dialogue                                            # v0.0003 grounded dialogue loop
  chat                                                # dlm-chat interactive REPL
run_eval.py          v0.0002 decision-wire evaluation
run_grounding_eval.py v0.0003 matched-arm grounding evaluation
run_dialogue_eval.py v0.0003 matched-arm dialogue evaluation
tests/ examples/ tools/build_upload.py work.txt
```

## License

Apache-2.0. `dlm/tiny_encoder.py` vendors blocks adapted from
[MeowLLM](https://github.com/phanii9/MeowLLM) (MIT, © 2026 phanii9); attribution
is kept in the file header.