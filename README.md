# DLM v0.0047 — closed-world deduction: certified negatives, and the first non-monotonic kernel

A **deductive logic model**: knowledge lives in an external knowledge base and
answers come from *proof*, abstaining when it cannot prove. This is a **fresh,
minimal rebuild** (not a continuation of the v0.0036/37 layer stack) around a
single question:

> **What is the learning structure for deduction?**

v0.0046 raises the **level of the final natural-language output** itself. Earlier
versions ended with a flat list of relation facts plus (from v0.0043) a single
core-concept line. v0.0046 adds `dlm/narrative.py`, an untrusted *leveled
realizer*, and `experiments/reading/`, which runs LAST and emits a reading whose
every sentence is tagged with its abstraction level and carries the kernel atoms
that entail it:

```
N1 fact          “main imports torch.”
N2 meaning       “Net defines a Conv2d layer.”
N3 idiom         “train performs a training step.”
N4 composition   “Inside train, one gradient step runs in a fixed order:
                  zero_grad -> forward/loss -> backward -> update.”
N5 architecture  “Net.forward is a conv -> relu -> ... -> softmax network.”
N6 causal        “train calls loss.backward in order to compute the gradients.”
N7 purpose       “main trains a neural-network model to recognize handwritten digits.”
N8 analogy       “train and test are the same routine in two regimes: both call
                  data.to, F.nll_loss, format, but train backpropagates and
                  updates the parameters, while test runs in no-grad mode.”
```

v0.0043 closed the *"a pile of facts is not an understanding"* gap of the north
star. v0.0042's pipeline reduced a program to concrete facts and another layer
listed its L5–L9 abstractions, but it never **deduced the one-line core concept**
("what *is* this program?") and it had no loop for **unknown knowledge**. v0.0043
adds `dlm/gist.py` (given conceptual rules that turn structure + acquired meaning
into a gist atom) plus a **search-driven relearning loop**
(`experiments/concept/`):

```
ROUND 1  reduce -> acquire meanings -> learn -> close -> gist attempt
         (the gist layer reports a HOLE: what does `datasets.MNIST` CONTAIN?)
SEARCH   look the hole up (Wikipedia primary, Stack Exchange cross-check),
         reduce the result to `dataset_of(MNIST, handwritten_digit)`, cache w/ provenance
ROUND 2  re-learn + re-close on the ENLARGED knowledge base -> the kernel now
         derives `recognizes(main, handwritten_digit)` with a verified proof
```

The concept is asserted only after the kernel proves it; **stripping the acquired
domain knowledge makes the kernel abstain** (the honesty ablation). The one-line
result on the PyTorch MNIST example is
**“main trains a neural-network model to recognize handwritten digits”**
(`(recognizes main handwritten_digit)`, `concept_score` 1.0). See §5.11.

v0.0042 climbs the **abstraction ladder** beyond v0.0041's propositional
concepts (`dlm/compose.py`, §5.10): **L5 composition** (relational patterns with
interface variables, e.g. `calls(X,Y),calls(Y,Z)` = “X delegates to a routine that
itself calls things”), **L6 architecture** (recurring ordered motifs in the
forward pipeline, normalized to roles), **L7 intent** (purpose hypotheses read
from the program's own text — never certified), **L8 causal** (“why” sentences
from *acquired* API-effect facts), and **L9 transfer** (the patterns applied to
held-out programs, reported as analogies).

v0.0041 closed the last honesty gap of the north star (§5.6): on a **single**
program the understanding predicates are extensionally degenerate, so nothing can
be generalised. v0.0041 adds **generalization over a corpus** (`dlm/generalize.py`,
§5.9): it mines conjunctions of understanding predicates that recur across many
programs, **invents a predicate** for each, and lets the **kernel re-derive** it on
a held-out program — deduction as the falsification test.

v0.0040 closes the honesty gap of v0.0039's north-star slice: the *meaning* of the
library symbols a program uses is now **acquired from the web** (the docs' own
object inventory + a web-search service), reduced to `meaning(symbol, concept)`
facts, and injected into the kernel — instead of being hard-wired. See §5.6 and
[`COMPOSITION.md`](COMPOSITION.md) §18. v0.0041 then generalises that acquired
understanding across a program corpus (§5.9, §19).

The LLM answer is *attention × continuous space × statistical signal*. This
version tests a different answer:

> **Ground (immutable, non-referential axioms) + Experience (conservative learned
> rules) + an open entity universe.** Lisp is the symbolic *medium*; the kernel is
> the *judge*.

- **`dlm/__init__.py`** (~130 lines) — the **trusted kernel**: function-free Horn
  substrate (`Const`/`Var`/`Term`/`Atom`/`Rule`), `closure` (the least fixpoint =
  truth), `entails`, `unify`, `description_length`.
- **`dlm/lisp.py`** (~240 lines) — **untrusted** symbolic medium: reads/writes
  s-expressions, matches pronominal rules (`?x`, `_`), evaluates forms, macros.
  The automation API (`findall`, `prove`/`why` → proof form, `verify`, `abstain`)
  lets a lisp program think and self-check; only `query`/`verify` read truth, and
  only through the kernel.
- **`dlm/ground.py`** (~180 lines) — **untrusted** learner: `Ground`,
  `Experience`, and `learn` (greedy covering with a kernel soundness gate).
- **`dlm/accumulate.py`** — **untrusted** accumulating learner: keeps what it
  learned, **retracts** a rule that new evidence falsifies, dedupes, MDL-compresses,
  and round-trips through `theory.py`. This is what a long run needs.
- **`dlm/ir.py`** — the canonical IR *is* the **Form tree** (v0.0039): walk it,
  canonicalise patterns up to variable renaming, read features, project to/from
  `Atom`/`Rule`. Read-only: it never asserts.
- **`dlm/proof.py`** — **proof as data** (v0.0039): a `Proof` is a certifying
  derivation tree; `verify` re-checks it against the kernel, `proof_ir` makes it a
  form (the DLM analogue of an LLM token sequence), `form_to_proof` is its inverse.
- **`dlm/abstract.py`** — **label-free abstraction** (v0.0039): fold a recurring
  body conjunction into an invented predicate; the kernel certifies the closure is
  preserved and the form-tree description length shrinks.
- **`dlm/theory.py`** — **checkpoint/resume** (v0.0039): `Theory` (Ground +
  Experience + facts + meta) round-trips through JSON; loading asserts nothing.

```bash
./test.sh          # 84 passed
```

---

## 1. Why a fresh rebuild

The v0.0036/37 line had a trusted two-file core plus **14 untrusted layers**
(~6,400 lines). Measurement said the bottleneck was not representation but
**search/proposal budget**, and that the layers accumulated epiphenomenal weight
and documentation debt. v0.0038 goes back to the smallest base that can still
express the confirmed architecture:

    Ground        (immutable, non-referential)   -- trusted, external
    Experience    (mutable, conservative)         -- learned
    entity universe D                             -- open, from input

## 2. The trust boundary

| medium | role | may it assert? |
|---|---|---|
| `dlm/__init__.py` kernel | decides truth by `closure` | **yes** |
| `dlm/lisp.py` | represents, matches, evaluates | no (only `query` reads the kernel) |
| `dlm/ground.py` | proposes rules | no (admitted only if the kernel agrees) |

* `dlm/__init__.py` imports **only** `dataclasses`/`typing` — it never imports the
  untrusted modules (AST-checked invariant).
* Function-free Horn: terms are **constants and variables only**. Embedded
  clauses are flattened, never nested.
* Positive Horn; an unnormalisable input **abstains**. No weights, no softmax in
  the assertion path.

## 3. Ground, Experience, and the learning signal

* **Ground** is immutable and **non-referential**: its rules carry pronouns
  (`(rule (ancestor ?x ?y) (parent ?x ?y))`), not specific objects. A pronominal
  rule is a **promise over an open universe**: every new referent is a fresh,
  non-self-referential test.
* **Experience** is a *conservative extension*: `Experience.to_kb(base)` copies
  Ground's facts/rules and only adds rules, so Ground's closure is never lost.
* **Signal = epistemic debt.** With `Exp_n` the rules after round *n*:
  * under-general: a positive `g ∈ E⁺` with `G ∪ Exp_n ⊬ g` → generalize;
  * over-general: a negative `a ∈ E⁻` with `G ∪ Exp_n ⊢ a` → reject.

`learn(ground, facts, positives, negatives, *, max_body=2, extra_vars=2,
max_rules=8, callback=None) -> LearnResult` does greedy covering: each round
`_induce` finds the **shortest kernel-sound generalization** that covers an
uncovered positive and derives no negative. `callback(experience, rule)` fires
after every admitted rule, which is how the stream experiment scores each round.

The open universe is what makes learning non-idempotent. A single join/closure is
idempotent (`closure(closure(T)) == closure(T)`): on a *closed* entity dictionary
a rule is only ever tested on its own instances, so the residual is identically
zero. New **referents** (not new facts) are the external target that keeps the
residual alive.

## 4. Lisp as the symbolic medium

Lisp does four jobs; the kernel stays the only judge.

```lisp
(rule (ancestor ?x ?y) (parent ?x ?y))     ; represent a pronominal ground axiom
(query (ancestor n0 n1))                    ; read truth (kernel closure only)

;; declare new notation: a macro rewrites a form into a form (code that writes code)
(defmacro trans (?p) (rule (?p ?x ?y) (?p ?x ?z) (?p ?z ?y)))
(trans subclass_of)                         ; expands to a `rule` form, then evaluates
```

`match_form`/`subst_form` operationalize the pronouns: `(parent ?x ?y)` matched
against `(parent n0 n1)` yields `(ancestor n0 n1)`, and against a **never-seen**
`(parent n7 n8)` yields `(ancestor n7 n8)`. `macroexpand`/`quasiquote_form` let
the medium define new notation; expansion is **pure rewriting** and can never
assert past the kernel — the expanded form is evaluated by the same `eval_form`.

**Boundaries.** (1) Lisp is a medium, not the judge — `eval_form`'s `query` is the
only reader of truth. (2) Ground must lower to **function-free Horn** to be
kernel-verifiable. (3) "Ground" means *fixed foundation*, not *variable-free* —
Ground must stay variable-carrying.

## 5. Experiments

| experiment | question | result |
|---|---|---|
| `experiments/ground` | does one generalization transfer? | Ground-only 0/28; one learned rule transfers to 28/28, `false=0` |
| `experiments/web` | can real web facts be learned? | induced transitivity; held-recovery **1.0** vs identity 0.64–0.88; `false=0`; deterministic |
| `experiments/stream` | does Experience *accumulate*? | round-by-round held-out curve; see below |
| `experiments/abstract` | can a theory abstract itself, label-free? | closure preserved, DL **132→82** (−38%), fixed-budget coverage up |
| `experiments/online` | what is the streaming trajectory? | `plain` rises 0.51→1.00 on unseen entities with an over-generalisation transient; the recovery is a same-distribution artifact, **not** soundness (see stream seed 3); §5.4 |
| `experiments/code` | can code facts be learned from GitHub too? | induced transitivity on the module import graph; held-out **repos** 0.31–0.35 → **1.000**, `false=0`; §5.5 |
| `experiments/mnist` | can one program go code → learn → understand → IR-TREE → NL? | PyTorch MNIST example, meaning **acquired from the web** (17/57 symbols, all 9 targets correct): 239 facts, induced+ground closure, IR form, all 32 sentences verified, `false_final=0`; §5.6 |
| `experiments/train` | can the learner accumulate + retract + resume for a long run? | accumulation **retracts** 6 over-general rules the memoryless refit cannot; both end sound (recovery 1.0, `false_final=0`, no duplicate rules); §5.7 |

### 5.1 Web (`experiments/web`)

Fetch random Wikipedia/Wikidata class hierarchies (no human labels), induce the
transitivity law on the train subgraph, score on held-out pairs:

```bash
./experiments/web/web_learn.sh                 # online, seeds 1 2 3
OFFLINE=1 CACHE=... ./experiments/web/web_learn.sh
```

| seed | entities | identity | learned | false |
|---|---|---|---|---|
| 1 | 243 | 0.638 | **1.000** | 0 |
| 2 | 248 | 0.833 | **1.000** | 0 |
| 3 | 262 | 0.882 | **1.000** | 0 |

### 5.2 Stream — the actual test of the learning structure (`experiments/stream`)

Entities are split into **disjoint train/test** sets (open universe). A law is
induced only on train entities and scored **after every round** on unseen test
entities. Domain: transitive `subclass_of` / `part_of` / `located_in` + inverse
`country_of(X,Y) :- country(Y,X)`; `Ground` is empty.

```bash
./experiments/stream/stream.sh
```

| seed | identity | r1 | r2 | r3 | r4 | false_max | verdict |
|---|---|---|---|---|---|---|---|
| 1 | 0.231 | 0.252 | 0.479 | 0.756 | **1.000** | 0 | OK |
| 2 | 0.249 | 0.272 | 0.535 | 0.747 | **1.000** | 0 | OK |
| 3 | 0.249 | 0.272 | 0.281 | 0.548 | 0.788 | **9** | FAIL |

* **Accumulation is real** (seeds 1–2): each new clause lifts held-out recovery
  on entities the induction never saw, soundly.
* **But the soundness gate is only empirical.** Seed 3 admitted
  `located_in(X,Y) :- country(Y,E0), subclass_of(X,Y)` — sound on the sampled
  *train* negatives, false on unseen test entities. In an open universe a finite
  negative sample **cannot prove universal soundness**.

### 5.3 Abstract — the theory compresses itself, label-free (`experiments/abstract`)

No labels (no positives/negatives). From a theory + facts alone, a recurring body
conjunction is folded into an **invented predicate** over its *interface* variables
(internal existentials stay quantified inside the definition), then the kernel
re-derives the closure and the form-tree DL is compared:

```bash
./experiments/abstract/abstract.sh        # 6 rules sharing a 4-edge core
```

| metric | value |
|---|---|
| closure preserved (kernel, original signature) | **true** |
| form-tree DL | **132 → 82** (−37.9%) |
| invented | `inv0` (support 6, uses 6) |
| fixed join-work budget | abstracted recovers **1.0** of the closure vs baseline 0.53 at the same budget |

Conservative abstraction cannot derive *more* atoms, so the only honest coverage
claim is **under a fixed inference budget** (DreamCoder): measured on *join work*,
not rule applications (a baseline rule joins four literals in one application, which
hides the win). There is a **seed cost** — the definition must be derived before any
folded rule fires — so the abstracted theory lags at tiny budgets and dominates past
the crossover (~budget 300). Honest result, not a promotion.

### 5.4 Online — the streaming trajectory (`experiments/online`)

Referents arrive one batch at a time (an *online* open universe). Each round the
arm **refits on the cumulative revealed set** (for `abstract` it then folds
recurring subgoals), and the theory is scored on **unseen test entities**. One
rich JSONL row per round records many facets of learning — coverage, soundness,
generalisation gap, theory growth (DL), body lengths, proof-tree depth, cost, and
the held-out curve *after each admitted rule* — and `--analyze` reads them back as
a multi-aspect report.

```bash
./experiments/online/online.sh                 # 4 arms x 3 seeds x 5 rounds (bigger data)
./experiments/online/online.sh --big           # more data (slower)
./experiments/online/online.sh --quick         # tiny smoke test
./experiments/online/online.sh --analyze reports/online/<stamp>
```

Arms: `frozen` (no learning) · `plain` (learn) · `abstract` (learn + abstract)
· `random` (control: random positives). Logs land in a timestamped
`reports/online/<stamp>/` (`<arm>_s<seed>.jsonl`, `summary.json`, `analysis.txt`).

Default data: `n_train=24` entities × `chains=3` × `chain_len=6` over three
transitive relations + an inverse, `rounds=5`, `max_rules=6` (~60 revealed facts,
~4k sampled negatives by the last round). `--big` scales to 30/4/7/8.

Report sections: **coverage** (held-out by round, mean over seeds) · **soundness**
(false asserts by round) · **generalisation** (train fit vs unseen, clause/DL growth)
· **dynamics** (per-round held-out gain, max proof depth, total seconds) ·
**intra-round** (held-out after each admitted rule) · **verdict**.

Measured (default, 3 seeds): held-out recovery rises **0.508 → 0.508 → 0.749 →
0.960 → 1.000** for `plain`, while `frozen`/`random` stay flat at identity 0.247.
At round 4 the refit over-generalises (false asserts 23 / 68 / 0 on unseen entities)
before round 5's added negatives reject the unsound clause.

**This "recovery" is a same-distribution effect, not soundness — read it as a
gate-reliability monitor, not a convergence claim.** The learner is memoryless
(each round refits from scratch); the only thing that changes is the growing
*in-distribution* negative sample, and online train/test share one generator, so
a counterexample in the revealed population predicts one in the unseen one. When
the counterexample lies *outside* the revealed distribution the same gate never
recovers: `experiments/stream` seed 3 admits `located_in(X,Y) :- country(Y,E0),
subclass_of(X,Y)` and `false` grows and **persists** (`0,1,9,9`). Increasing the
sample cannot fix this; structural soundness (closure-subset, mode declarations)
or treating learned rules as unverified hypotheses can.

**Honest note (invented=0).** `learn`ed rules rarely share a body pattern, so
`abstract` reports `invented=0` here and tracks `plain` exactly; the recurring
subgoals in `experiments/abstract` are *built*, not *induced*. This is orthogonal
to the trajectory and does not affect the analysis above.

### 5.5 Code — GitHub repos as facts (`experiments/code`)

The same pipeline, fed **source code** instead of web claims: download small
random Python repos from GitHub, extract the module import graph with the stdlib
`ast` (no dependency), and learn the transitivity law — with **whole repos** held
out, so it is a cross-distribution test, not §5.4's same-distribution effect.

```bash
./experiments/code/code_learn.sh                 # 6 random repos, seed 1
./experiments/code/code_learn.sh --synthetic     # network-free smoke test
./experiments/code/code_learn.sh --offline       # replay from cache
```

| seed | held pairs | identity | learned | scrambled | false |
|---|---|---|---|---|---|
| 1 | 309 | 0.346 | **1.000** | 0.346 | 0 |
| 2 | 115 | 0.313 | **1.000** | 0.313 | 0 |

The induced rule is exactly `imports(G0,G1) :- imports(G0,E0), imports(E0,G1)`.
Induced on 4 train repos, it recovers the **full** transitive import closure of 2
*unseen* repos (identity keeps only direct edges) and derives zero false pairs;
the scrambled control stays at identity. Same kernel, same `learn`, code facts.

**Honest limit.** This is a dependency-closure task: it shows code facts plug into
the kernel and the law transfers across repos, not that the model *understands*
code. Extraction is the import graph only (a call graph needs a scope-aware
resolver). Soundness here is structural for this relation, not a general fix for
§5.4's gate problem.

### 5.6 The north star — one program end to end (`experiments/mnist`)

The fixed goal: take one real program and run `acquire → reduce → learn →
understand → IR-TREE → natural-language sentence`. Target: the PyTorch MNIST
example. `extract.py` **reduces** `main.py` to function-free Horn facts plus a
`labels` map; `knowledge.py` looks the used **library symbols up on the web** (the
docs' object inventory, corroborated by a web-search service) and reduces the
verbatim definitions to `meaning(symbol, concept)` facts; `dlm.ground.learn`
induces a call rule over the structural vocabulary; `semantics.py` bridge rules
(GIVEN, no library symbol) plus the acquired meanings derive the understanding set
through the trusted kernel; `run.py` emits it as one IR *form* (with a nested
`(proof …)` tree); `realize.py` glosses it into sentences, each carrying the atoms
that entail it — a sentence is emitted only if its support is in the kernel
closure. Strip the acquired meanings and every semantic sentence disappears
(`tests/test_mnist_knowledge.py`), so the understanding provably rides on the
acquired facts.

```bash
./experiments/mnist/mnist.sh              # fetch or reuse cache
./experiments/mnist/mnist.sh --offline    # replay from cache
```

Measured: 17/57 used library symbols acquire a meaning (all 9 targets correct:
`nn.Module→module_base`, `Conv2d`/`Linear`/`Dropout→layer`, `DataLoader→
data_loading`, `loss.backward→backpropagation`, `optimizer.step→parameter_update`,
`model.eval→evaluation`, `torch.no_grad→gradient_free`, `torch.save→
serialization`); 239 facts, 87-pair call closure, 277 atoms derived, `false_final =
0`, all 32 sentences verified, the `(calls main loss_backward)` proof re-verifies.
Honest limit: one file cannot identify the general call
law (all multi-hop pairs share the entry point `main`), so
`general_law_identifiable_from_one_file = false`; that law is learned across repos
in §5.5 and merely applied here. The bridge from concept to structure
(`semantics.py`) is still given, but names no library symbol.

### 5.7 The accumulating learner — retraction and resume (`experiments/train`)

`dlm/ground.learn` is memoryless: it refits on whatever has been revealed, so it
cannot express "this rule used to hold". `dlm/accumulate.py` adds the missing
half. Each round it merges new facts/positives/negatives, **retracts** any rule
the *full revealed negative complement* now falsifies, induces for still-uncovered
positives (deduping up to variable renaming), optionally MDL-compresses recurring
bodies, and records `false_final` over the full complement — never a sample. The
whole `Learner` round-trips through `dlm/theory.py`, so a run can stop and resume.

```bash
./experiments/train/train.sh                 # seeds 1 2 3
SEEDS="1 2 3 4 5" ROUNDS=6 ./experiments/train/train.sh
NO_COMPRESS=1 ./experiments/train/train.sh   # ablation
```

Measured (default, controlled multi-relation domain, disjoint test entities,
negatives revealed progressively): accumulation admits over-general rules early
(a symmetry rule `located_in(X,Y) :- located_in(Y,X)`, cross-predicate
`subclass_of(X,Y) :- part_of(X,Y)`, …) and **retracts 6 of them** as the
counterexamples arrive, converging to exactly the true laws; the memoryless refit
records **0 retractions**. Both end sound (`false_final=0`) with full held-out
recovery and no duplicate rules. Two deterministic probes always run: a micro-
ladder that guarantees a retraction fires (and the learner then abstains), and a
checkpoint/resume round-trip that must match the uninterrupted path.

The honest point is not that accumulation scores higher — they converge — it is
that accumulation gives **retraction and resume**, which a long run needs and a
refit cannot represent.

### 5.8 The three v0.0039 layers

| layer | file | object | kernel role |
|---|---|---|---|
| **IR** | `dlm/ir.py` | the Form tree (code = data); projections to `Atom`/`Rule` | none (read-only) |
| **proof** | `dlm/proof.py` | derivation tree (`atom`, `rule`, premises) | `verify` re-derives it |
| **abstraction** | `dlm/abstract.py` | invented predicate + definition | `closure_preserved` certifies |

### 5.9 Generalizing the understanding across a corpus (`experiments/generalize`)

On *one* program the understanding predicates are **extensionally degenerate**:
`trains`, `backpropagates`, `optimizes` hold of exactly `{main, train}`;
`evaluates`, `uses_grad_free` of `{main, test}`. Every conjunction equals one of
its members, so `abstract_theory` and even a fact-level concept inventor find
**0** concepts. `dlm/generalize.py` works where a corpus exists: it mines
conjunctions of subject-features that recur across programs, keeps only the
**irredundant** and **non-degenerate** ones, and invents a predicate for each. The
falsification is **deductive transfer**: the kernel re-derives each invented
concept on a **held-out** program.

```bash
./experiments/generalize/generalize.sh    # or: ./northstar.sh --offline --check
```

Measured: 13 programs, 11 train / 2 held out (`northstar` = the real PyTorch
MNIST example, and `p11`). 8 concepts invented; the headline one is
`concept0(X) :- backpropagates(X), optimizes(X)` — **“a training step”** — learned
from the corpus, not written by hand, re-derived by the kernel on `northstar`
(`main` and `train`). Controls: the *same* miner on `main.py` alone finds **0**
concepts (`single_program_finds_nothing`); the invention is definitionally sound
(adding the rules leaves the original-vocabulary closure unchanged); the miner is
deterministic; and `p11` (a conv-only net) correctly **rejects** the
`conv2d ∧ linear` concept. Each abstracted sentence is backed by a verified kernel
proof `concept_i(subject)`.

### 5.10 The L5–L9 abstraction ladder (`experiments/abstraction`)

v0.0041's concepts are **propositional** (a conjunction of unary subject features).
v0.0042 (`dlm/compose.py`) climbs the ladder the north star was still missing
(see [`experiments/mnist/ABSTRACTION_COMPARISON.md`](experiments/mnist/ABSTRACTION_COMPARISON.md)):

| level | what | how it is justified |
|---|---|---|
| **L5 composition** | connected conjunctive patterns with interface variables | kernel derives each instance; irredundant + non-degenerate + transfers |
| **L6 architecture** | recurring ordered **role** motifs in the forward pipeline | mined on the corpus, **transfers** to the real program, **discriminates** an unseen shape |
| **L7 intent** | purpose read from docstrings/`help=` text | explicitly a **hypothesis** — never certified |
| **L8 causal** | “why” — `f calls s in order to <effect>` | follows from **acquired API-effect facts** + observed calls |
| **L9 transfer** | patterns applied to held-out programs | deductive transfer + program analogies |

```bash
./experiments/abstraction/abstraction.sh   # or: ./northstar.sh --offline --check
```

Measured: 12-program corpus, held out `northstar` (real `main.py`) + a new shape.
L5 recovers `calls(X,Y),calls(Y,Z)` == **“main delegates to a routine that itself
calls things”** (hits `main`). L6 recovers the motif `['conv','relu']` and it
**transfers** to `main.py`'s forward pass and is **discriminated** on the unseen
`dropout`-only shape. L7 yields 11 hypotheses (`classifies handwritten digits`,
`is a reference example`, …), all marked uncertified. L8 derives 9 certified “why”
sentences. A human-checklist `abstraction_score` is reported (currently 1.0) — it
measures *presence with support*, not depth.

### 5.11 Core-concept (gist) capture + knowledge search (`experiments/concept`)

v0.0042 can list *what a program uses* and *how its abstractions generalize*, but
it still cannot answer **“what is this program?”** in one sentence, and it has no
way to fill knowledge it lacks. v0.0045 (`dlm/gist.py`, §21) adds both:

* **`dlm/gist.py`** — three GIVEN conceptual rules (the interpreter seam, naming
  no library symbol) that connect structure + acquired meaning to a gist atom.
  The strongest is
  `recognizes(?p, ?a) :- trains(?p), builds_model(?p), creates(?p, ?d), dataset_of(?d, ?a)`.
  `dataset_of` is the *only* premise no reading of the code can supply — an
  **external hole** the layer reports as a question so the reader can search.
* **`experiments/concept/run.py`** — the two-round loop above. Round 1 closes the
  base facts and reports `gaps=['mnist']`; the reader searches (Wikipedia summary
  primary, Stack Exchange cross-check; `experiments/mnist/domain.py`) and caches
  `dataset_of(mnist, handwritten_digit)` with provenance; round 2 re-learns and
  re-closes, and the kernel derives the concept.

```bash
./experiments/concept/concept.sh            # or: ./northstar.sh --offline --check
```

Measured on the real `main.py`: 222 concrete facts reduced, gap detected,
Wikipedia reduced `MNIST → “a large database of handwritten digits”` to
`handwritten_digit`, and the certified core concept is
`(recognizes main handwritten_digit)` → **“main trains a neural-network model to
recognize handwritten digits (from the MNIST dataset)”**. Control: with the
acquired domain facts removed, `recognizes` is **not derivable** and the reader
abstains. `concept_score` 1.0 (all seven produced/verdict checks).

### 5.12 The leveled final reading (`experiments/reading`)

Answering “what is this program?” in one line is not the same as *speaking about
it* at a high level. v0.0046 makes the final output's **sentence level** a
measured quantity. `dlm/narrative.py` is an untrusted realizer with one function
per level `N1..N8`; `experiments/reading/run.py` extracts, acquires knowledge,
closes, and realizes the closure. **Every sentence carries `support` — the atoms
that entail it — and a sentence whose support is not in the kernel closure is
marked uncertified and never asserted.** The level is not decoration: N4 must
find a *bounded* optimisation window (a gradient reset → forward/loss → backward
→ update), N5 must emit a *role-normalised* forward topology, N6 a “why” backed
by an acquired `api_effect` fact **and** an observed direct call, N7 the gist from
§5.11 (which requires SEARCHED domain knowledge), and N8 a *structural analogy*
that reads off two certified facts plus a certified difference — never an
asserted similarity. In particular `_n8` only pairs routines with **disjoint**
regime predicates, so the orchestrator `main` (which carries both regimes) is not
mistaken for an analogy and the honest pair `train`/`test` is emitted.

```bash
./experiments/reading/reading.sh --offline   # or: ./northstar.sh --offline --check
```

Measured on the real `main.py`: **reading level N8, score 1.0** (all eight levels
present), every sentence kernel-certified. Honesty ablation is built in: remove
the acquired domain knowledge and the N7 `recognizes` sentence disappears (the
reader abstains), while everything the structure supports stays.
Measuring stick (defined before implementing): the pre-v0.0044 output was flat
N3; v0.0044 reached N5, v0.0045 N6–N7, v0.0046 N8.

### 5.13 Closed-world deduction (`experiments/closedworld`)

The v0.0044–46 reading raised the *presentation* ladder (N3→N8) but every
conclusion was a Horn positive. v0.0047 raises the **deduction** ladder instead:
the trusted kernel can now derive a *certified negative* over a GIVEN universe,
and its closure is **non-monotonic**. `dlm/__init__.py` gains `NegAtom` and
`strata`, and `closure()` auto-routes: with no negation it is the unchanged
semi-naive Horn evaluator; with negation it evaluates strata in ascending order to
a fixpoint. A theory with a **negative dependency cycle is rejected**
(`ValueError`), and a negated literal whose variables are not ground after the
positive join is **pruned, never guessed**.

`dlm/closedworld.py` (untrusted) proposes the only rule the experiment needs:

```
absent(?m, ?l) :- is_module(?m), candidate_layer(?l), not has_layer(?m, ?l)
```

The closed-world assumption is scoped to `candidate_layer` — the one universe we
claim to have enumerated. Three probes (all in `experiments/closedworld/run.py`)
show the kernel stays sound:

* **retraction**: add `has_layer(net, maxpool2d)` and `absent(net, maxpool2d)`
  disappears — a conclusion pure Horn can never retract;
* **stratification**: a negative self-cycle is refused, not approximated;
* **safety**: an unbound negated literal asserts nothing.

Measured on the real `main.py`: the kernel certifies six absences
(`attention, batchnorm2d, gru, layernorm, lstm, maxpool2d`) beside the three
layers it has, and the retraction probe succeeds.

```bash
./experiments/closedworld/closedworld.sh --offline   # or: ./northstar.sh --offline --check
```

## 6. Honest status

The learning structure now *works as a proposer*: it generalizes, accumulates,
retracts falsified rules, and transfers to unseen referents. It is **not yet a
sound judge**: the gate checks a finite negative sample (now over the full
*revealed* complement, but still only what has been seen), so it can admit an
empirically-sound, universally-false rule until the counterexample arrives. The
trust invariant says it should **abstain**, not assert.

Next direction (in order of preference):

1. **Mode/type declarations** in `Ground` (standard ILP) so the proposer's
   literal universe is restricted *by construction* — the seed-3 rule becomes
   unrepresentable.
2. **Structural soundness** (closure-subset / subsumption) instead of sampled
   negatives.
3. A **long-run harness** (`experiments/train`) that runs time/round-based with
   periodic held-out evaluation and checkpoint/resume — the accumulating learner
   and `theory.py` are its bricks; the sweep is the next step.

## 7. Layout

```
dlm/
  __init__.py      trusted kernel: Horn substrate + closure (truth)
  lisp.py          untrusted symbolic medium: forms, macros, and the automation API (query, findall, prove/why -> proof form, verify, abstain)
  ir.py            the Form tree IS the IR (read-only views + features)
  proof.py         proof as data (derive, verify, measure, proof <-> form)
  ground.py        untrusted Ground / Experience / learn
  accumulate.py    untrusted accumulating learner (merge, retract, dedupe, compress, resume)
  abstract.py      untrusted label-free abstraction (kernel-certified)
  generalize.py    untrusted corpus generalization: mine recurring feature conjunctions, invent predicates, deductive transfer
  gist.py          untrusted core-concept rules + external-hole report (kernel-certified)
  narrative.py     untrusted leveled realizer (N1..N8); every sentence carries kernel support
  closedworld.py   untrusted closed-world absence rule over a GIVEN candidate universe
  api_semantics.py (experiments/mnist) acquired API-effect facts for certified “why” (N6)
  theory.py        checkpoint/resume a theory (Ground + Experience + facts, JSON)
experiments/
  ground/          one generalization transfers (synthetic)
  web/             real Wikipedia/Wikidata class hierarchies
  stream/          multi-relation accumulation, round-by-round open-universe curve
  abstract/        recurring subgoal -> invented predicate; DL + budget coverage
  online/          streaming trajectory: learn each round, score on unseen entities
  code/            real GitHub repos -> import graph -> cross-repo transfer
  mnist/           one program: reduce -> acquire meaning from the web -> learn -> understand -> IR-TREE -> NL
  generalize/      corpus of programs -> induced concepts -> deductive transfer to the north star
  abstraction/     L5 composition .. L9 transfer, with an abstraction_score
  concept/         concrete facts -> detect gap -> SEARCH domain knowledge -> re-learn -> certify the core concept
  reading/         closure -> leveled final NL reading (N1..N8), every sentence certified
  closedworld/     certified absences; non-monotonic retraction + stratification + safety probes
  train/           accumulating learner + closure benchmark (the long-run harness seed)
tests/             119 tests (network-free)
test.sh            PYTHONPATH=. python -m pytest -q
```

## 8. Version

`0.0.47` — closed-world deduction in the trusted kernel (stratified negation over a
GIVEN universe; non-stratified theories rejected, unsafe negations pruned, closure
non-monotonic), on top of v0.0039 (IR-TREE, proof as data, label-free abstraction),
web-acquired meaning for the north-star slice (v0.0040), corpus-level concept
generalization with deductive transfer (v0.0041), the L5–L9 abstraction ladder
(`dlm/compose.py`, v0.0042), core-concept (gist) capture with a search-and-relearn
loop for missing domain knowledge (`dlm/gist.py` + `experiments/concept/`, v0.0043),
and the **leveled final reading** raising the output to N8 (`dlm/narrative.py` +
`experiments/reading/`, v0.0044→v0.0046).
Licensed under
Apache-2.0 (see `LICENSE`).
Design notes: [`COMPOSITION.md`](COMPOSITION.md).