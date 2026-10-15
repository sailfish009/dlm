# `experiments/mnist` — the north-star slice: code → learning → IR-TREE → natural language

This is the fixed goal for the v0.0039+ line. Take one real program — the PyTorch
MNIST example (`pytorch/examples/mnist/main.py`) — and run the whole declared path
on it:

```
search / acquire → reduce → learn → understand → IR-TREE → natural-language sentence
```

Nothing here is an "LLM does it" shortcut. Each stage is either the trusted kernel
or a small untrusted module whose output the kernel must certify.

v0.0040 closes the biggest honesty gap of v0.0039: the *meaning* of PyTorch is no
longer hand-written. The used library symbols are **looked up on the web** and
reduced to `meaning(symbol, concept)` facts; the kernel reasons over them like any
other fact. A symbol with no acquired meaning derives nothing (abstain).

v0.0041 adds the layer this slice was missing: on **one** program the
understanding predicates are extensionally degenerate, so nothing can be
generalised. The companion experiment [`../generalize`](../generalize) learns
understanding concepts on a **corpus** and lets the kernel **re-derive** them on
this program by deduction (`./northstar.sh --offline --check` runs both).

## Pipeline

```
acquire.py          fetch (or replay cache) main.py                          untrusted I/O
extract.py          Python ast -> function-free Horn facts (the REDUCTION)    untrusted
knowledge.py        used symbols -> WEB lookup -> meaning(symbol, concept)     untrusted
semantics.py        BRIDGE_FORMS: how a meaning makes a predicate true         given
run.py              dlm.ground.learn + kernel closure -> understanding         kernel
realize.py          atoms -> sentences, each carrying its entailing atoms      untrusted
```

### 1. Reduction (not a codec)

`extract.py` turns `main.py` into function-free binary/unary Horn facts over
single-token slugs, plus a `labels` map (slug → human name) so the realizer can
speak, and `pipelines` (source-ordered call sites per owner):

```
(imports   module package)   (defines   module symbol)   (method_of class method)
(inherits  class  base)      (creates   owner  class)    (calls     owner callee)
(step_of   owner  step)      (before    step   step)
```

This is a **reduction**, deliberately lossy and purpose-directed: it does not try
to represent Python, only the relations a deductive reader needs. There is no
claim that "any language maps to the IR".

### 2. Acquire the meaning from the web (v0.0040)

The reduction tells us *which* library symbols the program uses (`nn.Module`,
`loss.backward`, `DataLoader`, …) but not what they **mean** — that is not in the
code, it is in the library's documentation. `knowledge.py` is the untrusted
acquirer. It uses two web providers:

* **`docs`** — the documentation's own object inventory
  (`https://docs.pytorch.org/docs/stable/objects.inv`, a Sphinx search index).
  It resolves a symbol to its canonical definition page; the first paragraph is
  read **verbatim**. Authoritative.
* **`search`** — a real web-search service (the Stack Exchange API). It returns
  free-text Q&A for a symbol, reduced by a cue lexicon; noisy, so it only
  *corroborates* / falls back.

The verbatim definition is then reduced to one concept from a small fixed
vocabulary by `CONCEPT_CUES` (first matching cue wins). The result is a
`meaning(symbol, concept)` fact. Everything is cached under `cache/` so an
`--offline` replay is byte-for-byte deterministic and needs no network, and every
fact carries its provenance (URL + raw definition + providers).

**No meaning is invented**: a definition with no cue yields no fact.

### 3. Two-layer semantics

`semantics.py` is split so the hand-written part no longer names any PyTorch
symbol:

* **`BRIDGE_FORMS`** — the GIVEN interpreter: how a generic `meaning(S, C)`
  statement makes a structural understanding predicate true, e.g.
  `is_module(C) :- inherits(C, B), meaning(B, module_base)` and
  `trains(F) :- calls(F, C), meaning(C, backpropagation)`.
* the **`meaning` facts** — the ACQUIRED semantics (step 2), injected as Ground
  facts.

The kernel treats both alike; the only PyTorch-specific knowledge is the acquired
fact layer, and it is the kernel that decides whether any predicate follows.

### 4. Learning from the reduction

`run.py` takes the transitive closure of the `calls` facts as positives and the
**full complement** of the constant-pair universe as negatives, then calls
`dlm.ground.learn`. The kernel admits a rule only if it derives no negative. The
law is induced over the **structural** vocabulary only (`imports`/`defines`/
`method_of`/`inherits`/`creates`/`calls`/`step_of`/`before`); letting the acquired
`meaning` predicates into the body search would yield in-sample-coincidental
rules, so they are excluded from the *body* and the result is re-checked against
the full closure.

### 5. Understanding (deduction)

`closure` derives the understanding set (`is_module`, `has_layer`, `trains`,
`evaluates`, `orchestrates`, `loads_data`, `saves_model`, …) from the reduced
facts **plus the acquired meanings**; `prove`/`verify` produce re-checkable
proofs; `dlm.abstract.abstract_theory` looks for compressible structure.

### 6. IR-TREE + natural language

The understanding set is emitted as one IR *form* — an s-expression tree whose
subtrees are `source` / `module` / `knowledge` / `facts` / `ground` / `learned` /
`derived` — built with the kernel's `atom_to_form` / `rule_to_form` and dumped
with `dlm.lisp.dump`. This is the DLM analogue of a token sequence: **proof as
data**, but tree-shaped and checkable.

`realize.py` glosses the derived atoms into sentences. It may not invent: every
sentence carries a `support` list of atoms, and `run.py` marks it `verified` only
if **all** support atoms are in the kernel closure. Where the reduction captured
nothing, there is no sentence (abstain).

## Run

```bash
./experiments/mnist/mnist.sh                 # fetch (or reuse cache)
./experiments/mnist/mnist.sh --offline       # replay from cache, no network
./experiments/mnist/mnist.sh --local path.py # any single Python file
```

Writes `reports/mnist/<stamp>/result.json` (IR form, narrative, proofs, learning
diagnostics) and prints the narrative with an `ok` mark per verified sentence.

## Measured (PyTorch MNIST example, `main.py`, offline replay)

* **17 / 57** used library symbols acquired a meaning from the web; **all 9 target
  concepts** are correct (`nn.Module → module_base`, `Conv2d`/`Linear`/`Dropout →
  layer`, `DataLoader → data_loading`, `loss.backward → backpropagation`,
  `optimizer.step → parameter_update`, `model.eval → evaluation`, `torch.no_grad →
  gradient_free`, `torch.save → serialization`). The remaining 40 explicitly
  abstain (mostly builtins and local names: `range`, `print`, `argmax`, …).
* 239 facts (incl. the acquired meanings); `calls` closure 87 pairs; 277 atoms
  derived; **false_final = 0** (the induced rule derives no `calls` pair outside
  the true closure).
* The proof for `(calls main loss_backward)` re-verifies (size 3); the abstract
  pass invents nothing.
* All 32 narrative sentences verified (`all_sentences_verified = true`), e.g.

  > Net is a PyTorch neural-network module. Net contains a Conv2d layer.
  > Train performs a training step. Main calls backpropagation (loss.backward).
  > Main runs the model in evaluation mode. Main saves the trained model.
  > Inside train the steps run in order: model.train → … → loss.backward →
  > optimizer.step → … .

  Every one of these is entailed by an **acquired** `meaning` fact; strip the
  meanings and the semantic sentences disappear (only the structural `imports`
  sentences remain). `tests/test_mnist_knowledge.py` proves exactly this.

## Honest limits

* **One file cannot identify the general call law.** All multi-hop `calls` pairs
  share the entry point `main`, so a file-local LGG rule is sound but overfit
  (`calls(main,G0) :- …`), and holding out `main` leaves no non-trivial positive
  to generalize from. `law_transfer` reports
  `general_law_identifiable_from_one_file = false`. The *general* transitivity law
  is learned across many repos in `experiments/code` (held-out repos 0.31–0.35 →
  **1.000**, false 0) and merely *applied* here.
* The **bridge** between meaning and structure is still given (`BRIDGE_FORMS`).
  v0.0040 moved the PyTorch-specific knowledge out of the code and into acquired
  facts, but *how a concept about a called symbol makes a function "train"* is a
  small hand-written interpreter. It names no library symbol; it is the analogue
  of a fixed decoder head, not of learned parameters.
* The reduction is flat-relational. A true IR-TREE reduction would carry learnable
  subtree structure (recurring bodies / macros) and be judged by deductive
  transfer. v0.0041 takes the corpus-level, deduction-judged step for the
  understanding vocabulary (`../generalize`, `COMPOSITION.md` §19); learnable
  IR-TREE macros over the structural reduction remain the next layer.