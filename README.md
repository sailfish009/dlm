# DLM v0.0056 — self-evaluation + weakness-targeted curriculum

A **deductive logic model**: knowledge lives in an external knowledge base and
answers come from *proof*, abstaining when it cannot prove. This is a **fresh,
minimal rebuild** (not a continuation of the v0.0036/37 layer stack) around a
single question:

> **What is the learning structure for deduction?**

v0.0056 closes the loop the model was still missing: **it evaluates its own
ability and improves its own weak spots**. From the kernel closure alone it reads
which deduction targets its rules promise but cannot yet conclude (`dlm/ability.py`),
identifies the missing premise that only acquired knowledge can supply, asks the
web for exactly that premise, re-closes through the kernel, re-assesses, and stops
on a *named* reason (`dlm/curriculum.py`). The target set is **discovered from the
theory**, not a fixed goal list: whatever the model's rules can conclude is the
agenda. The north-star slice shows the reader proving `trains` but unable to prove
`recognizes(<program>, <what>)` until it finds the `dataset_of` gap *itself* and
searches for it; a synthetic multi-gap theory shows the loop iterating one weak
spot per round; scramble / no-web controls prove the *content* (re-checked by the
kernel) is what helps — a scrambled fact improves nothing, and with acquisition
removed the model abstains. `Reader.self_improve` owns the loop inside the model.

v0.0055 adds **recursive self-supervised learning** (`dlm.recursive`): the model
feeds its own kernel-certified output back as the next round's input. Each round
closes the relation it currently has (starting from the base edges) under two
definitional level rules — inherit + self-join — and reifies the certified
extension as a new predicate, so the model bootstraps reachability to arbitrary
depth in **O(log diameter)** rounds with **no labels** and the kernel as the only
judge. It is *not* given the relational transitive rule: a single composition
provably cannot reach the closure, which is the falsifier that recursion is
required (`experiments/recursive`). A round that adds nothing is the fixpoint, and
the model abstains.

v0.0054 makes the **model the subject, not the harness**. The automation that lets
a deductive model improve without a human — web access (`dlm.web`), generic search
providers (`dlm.search`), the acquisition subject (`dlm.acquire`), and the
autonomous reader + self-supervised loop (`dlm.agent`) — moves out of
`experiments/` and **into the model**:

* `dlm.web.Web` is the model's one web primitive: a URL in, cached bytes out,
  byte-for-byte replayable offline, abstaining (`None`) on any failure. The
  internet is the model's *senses*, not its judgment;
* `dlm.search` holds the generic providers (Sphinx object inventory, Wikipedia,
  Wikidata/MediaWiki, Stack Exchange) — ways to *look things up*, never facts;
* `dlm.acquire` is the acquisition subject: candidates → web search → reduce
  evidence → `meaning`/`dataset_of` fact(+provenance) → cache. It names no
  library and no dataset; the caller supplies only the GIVEN cue vocabulary;
* `dlm.agent.Reader` owns the whole loop — perceive → acquire → search → induce →
  close → read — and `run_loop` repeats it over a sequence of sources, stopping on
  a named policy reason (`saturated` / `max_rounds`) with the **kernel as the only
  judge**.

Everything the web brings back is still **untrusted**: the kernel consumes every
acquired fact like any other and re-checks whatever it concludes. Experiments keep
only the GIVEN, domain-specific pieces (a reducer, bridge/gist rules, cue
lexicons, a signature builder) and the falsifier harnesses — they no longer own
the subject that reaches the web. The measured north-star output is unchanged
(239 facts / 87-pair closure / 615 atoms / 42 certified sentences / level N9).

v0.0053 **integrated** the leveled final reading into the north-star BODY. v0.0050
built the N1..N9 realizer (`dlm/narrative.py`) and v0.0044–46 raised its level, but
the body (`experiments/mnist/run.py`) still used its own private flat realizer
(`realize.py`, now deleted) and emitted only ~32 structural sentences — while the
purpose/gist rung ("…to recognize handwritten digits") lived **only** in a side
experiment that the harness ran last. So the body's own final output never reached
N7, and `'recognizes' in mnist_report → False`. v0.0053 removes that split:

* the body and the falsifier experiment (`experiments/reading/`) now share **one
  pipeline** (`mnist.run.pipeline`), so there is a single realizer and a single
  path from structure → reading;
* the body's own `narrative` **is** the N1..N9 reading, built over structure +
  acquired `meaning` + **searched** `dataset_of` + acquired `api_effect` + the
  D5 (closed-world) / D7a (equality) absence layer;
* the body reports `northstar_purpose` (the exact falsifier) and
  `all_sentences_verified`; `experiments/reading` keeps the honesty ablation, the
  D6 typed-gate falsifier, and the D5 non-monotonicity probe;
* `analyze_sentences` (read-only) classifies each rung's KIND (presentation vs
deduction vs knowledge-dependent) and checks every support atom is really in the
kernel closure. No kernel change.

v0.0052 **measures** the integrators instead of only *defining* them. v0.0049
showed the evidence/order integrals are **well-posed** (normalized, gauge-
invariant, holonomy-nonzero) — but every one of its 18 verdicts was a
*definition/consistency* check, and no pipeline consumed the modules. That answers
"is it defined?", not "**is it effective?**". v0.0052 adds the untrusted
`dlm/effective.py` and `experiments/effective/`, which turn the integrals into
**predictions** and **decisions** under an **equal budget** with control arms, and
records the honest result:

* **B — the evidence integral as a predictor.** Prior works over a *single* MAP
theory; the integral averages over every rule-subset weighted by its train
evidence. On a fully ambiguous posterior (two theories **energy-tied** at
`[1.0, 1.0]`, `posterior=[0.5, 0.5]`) MAP must commit to one and is wrong half the
time (**Brier 1.00**), while the marginal hedges to **p=0.5** (**Brier 0.25**). On
the natural online domain, where the learned theory set has no harmful
multiplicity, the marginal **ties** MAP — no gain, *no loss*.
* **C — the order/credit integral as a controller.** At the *same* goal budget
(20), static order and random order prove **2/12** goals; integrated credit proves
**12/12**. The path integral over learned priorities recovers the full gain
(`path_first=2 → path_final=12`).

So the integral is effective **exactly when multiplicity exists**, and never worse
in these settings. Fifteen falsifiers all pass (`evidence_marginal_not_worse_than_map`,
`multiplicity_evidence_strictly_beats_map_under_multiplicity`, `credit_beats_static`,
`credit_beats_random`, `path_improves_over_static`, …); see §5.18. The kernel is
untouched — this is a *measurement of the signal*, not a new deduction level.

v0.0050 makes the **deduction ladder visible in the final output**. The reading
(v0.0044–46) had plateaued: v0.0046/47/48/49 emitted *byte-identical* sentence
lists because the realizer never consumed the D5/D6 conclusions. v0.0050 wires
them in: **N9** realizes a **certified NEGATIVE** — “Net does not contain an
attention layer.” — derivable only by stratified closed-world negation over a
GIVEN candidate universe, and **non-monotonic** (adding one `has_layer` fact
retracts the sentence). Pure Horn deduction can never produce it. **D6 typing is
deliberately NOT a sentence level**: the reader is closed under a GIVEN
typed/moded `Signature`, so an ill-typed theory makes it **abstain** instead of
deriving — typing *gates admission*, it never asserts a truth. The three honesty
probes (`negative_needs_closed_world`, `nonmonotonic_negative_retracts`,
`typed_gate_binds`) are all true on the real program; see §5.16.

v0.0051 adds the first **equality** rung (D7a). v0.0050's N9 exposed a real false
negative: the reading certified *“Net does not contain a maxpool2d layer.”* while
the forward pass literally calls **`F.max_pool2d`**. The cause was a vocabulary
gap — positive evidence arrives under library **aliases** (`f_max_pool2d`,
`nn_conv2d`) while the candidate universe uses canonical layer **kinds**
(`maxpool2d`, `conv2d`), and nothing tied the two. Equality is exactly what a
function-free Horn theory cannot say, so v0.0051 supplies it as a **finite
congruence** (`dlm/equality.py`): the alias relation `same_kind` plus `uses_layer`
(definition, method-call, or direct call) feeding the *same* closed-world shape.
The extension is **conservative** — it adds only `same_kind`/`uses_layer` and
changes no positive Horn conclusion — and the false negative is now blocked
(§5.17). This is D7a: a genuine deduction-level raise (a new kind of conclusion),
with function symbols still deliberately out of scope.

v0.0049 answers a sharper question: **does deduction need a *loss* the way induction
does?** No — it needs **integration**, in three layers, and only two of them are
potentials. (A) The **forward integral**: `closure` is the least fixed point of the
immediate-consequence operator, so it is path-*independent*, and its **debt**
(targets it fails to reach) is kernel-decided. (B) The **evidence integral**
`Z = Σ_T exp(−E(T))` over candidate theories — a *measure* ("how many good
theories are there?"), which a single MAP theory cannot see; `F ≤ E_MAP` and
`Σ posterior = 1` are built-in falsifiers. (C) The **order integral**: under a
bounded search, per-rule credit depends on the order rules are tried, and the
field it sweeps has **nonzero holonomy** (`curl ≠ 0`) — so credit is a
*connection*, not the gradient of any scalar, and learning it is a **path
integral**. A scalar control has exactly zero circulation, and the curl is
gauge-invariant. Two untrusted integrators make this measurable:
`dlm/integral.py` and `dlm/connection.py` (`experiments/integral/`, §5.15). This is
the *signal*, not a new deduction level — the kernel is untouched.

v0.0048 raises the **deduction** level (not the wording): the trusted kernel now
checks a theory against a typed, moded **signature** *before* any derivation
(`dlm.Signature`, `type_errors`, `closure(kb, sig)`). Type soundness, range
restriction and mode anability are enforced statically, so an ill-shaped clause
is **rejected, not tested** — while for a well-typed theory the signature is a
no-op on truth. This is D6 on the deduction ladder, right after D5 (closed-world
negation, v0.0047); see §5.14.

v0.0046 raised the **level of the final natural-language output** itself. Earlier
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
N9 absence       “Net does not contain an attention layer.”   (a certified NEGATIVE)
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
| `experiments/mnist` | can one program go code → learn → understand → IR-TREE → NL? | PyTorch MNIST example, meaning **acquired from the web** (17/57 symbols, all 9 targets correct): 239 facts, 615 atoms, IR form, N1..N9 reading (42 sentences verified, N7 purpose + 5 N9 absences), `false_final=0`; §5.6 |
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
`(proof …)` tree) and then glosses it with the shared `dlm.narrative.reading` into
the N1..N9 reading, each sentence carrying the atoms that entail it — a sentence
is emitted only if its support is in the kernel closure. Strip the acquired
meanings and every semantic sentence disappears (`tests/test_mnist_knowledge.py`),
so the understanding provably rides on the acquired facts.

```bash
./experiments/mnist/mnist.sh              # fetch or reuse cache
./experiments/mnist/mnist.sh --offline    # replay from cache
```

Measured: 17/57 used library symbols acquire a meaning (all 9 targets correct:
`nn.Module→module_base`, `Conv2d`/`Linear`/`Dropout→layer`, `DataLoader→
data_loading`, `loss.backward→backpropagation`, `optimizer.step→parameter_update`,
`model.eval→evaluation`, `torch.no_grad→gradient_free`, `torch.save→
serialization`); 239 facts, 87-pair call closure, 615 atoms derived, `false_final =
0`, **42 sentences verified** across all nine levels (N1..N9, including the N7
purpose sentence "…to recognize handwritten digits" and five certified N9
absences), and the `(calls main loss_backward)` proof re-verifies. `northstar_purpose
= true`; the body and `experiments/reading` share one pipeline.
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
per level `N1..N9`; `experiments/reading/run.py` extracts, acquires knowledge,
closes, and realizes the closure. **Every sentence carries `support` — the atoms
that entail it — and a sentence whose support is not in the kernel closure is
marked uncertified and never asserted.** The level is not decoration: N4 must
find a *bounded* optimisation window (a gradient reset → forward/loss → backward
→ update), N5 must emit a *role-normalised* forward topology, N6 a “why” backed
by an acquired `api_effect` fact **and** an observed direct call, N7 the gist from
§5.11 (which requires SEARCHED domain knowledge), N8 a *structural analogy*
that reads off two certified facts plus a certified difference — never an
asserted similarity, and N9 (v0.0050) a *certified absence* from closed-world
negation, non-monotonic and only sound over the GIVEN candidate universe. In
particular `_n8` only pairs routines with **disjoint** regime predicates, so the
orchestrator `main` (which carries both regimes) is not mistaken for an analogy
and the honest pair `train`/`test` is emitted.

```bash
./experiments/reading/reading.sh --offline   # or: ./northstar.sh --offline --check
```

Measured on the real `main.py`: **reading level N9, score 1.0** (all nine levels
present), every sentence kernel-certified. Honesty ablation is built in: remove
the acquired domain knowledge and the N7 `recognizes` sentence disappears (the
reader abstains), while everything the structure supports stays.
Measuring stick (defined before implementing): the pre-v0.0044 output was flat
N3; v0.0044 reached N5, v0.0045 N6–N7, v0.0046 N8, v0.0050 N9.

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

### 5.14 Typed/moded signatures, checked before derivation (`experiments/typed`)

v0.0047 gave the kernel negation, but the learner still admits a candidate rule as
soon as the kernel derives no sampled negative with it — a *sound* gate that is
blind to the **shape** of a clause. v0.0048 raises the deduction ladder again:
the kernel now checks a theory against a typed, moded **signature** *before* any
derivation. `dlm.Signature` gives each predicate position a type and a mode
(`in`/`out`/`any`); `dlm.type_errors(rule, sig)` returns every reason a rule is
inadmissible, and `closure(kb, sig)` rejects an ill-typed theory with `TypeError`.
Four independent checks: predicate/arity, **type soundness** (one variable at two
incompatible types; a constant outside its slot's type), **range restriction** (a
head or negated variable bound by no positive body literal), and **mode anability**
(an `in` position nothing produces). Types are a small acyclic lattice
(`module <: fn <: callable`, `layer <: symbol`, …); two types unify only when one
is a subtype of the other, so `module` and `symbol` clash even though both sit
under `callable`.

The point is not decoration: the D5 closed-world rule is now checkable
statically, and a seed-3-style unsound clause (a module where a symbol is
required, a head variable bound by no body literal, an unbound negated literal,
an input never produced) becomes **inexpressible** — it never enters the
candidate set. Typing only *forbids*: for the honest theory the signature is a
no-op on truth (`closure(kb, sig) == closure(kb)`), and the same gist and the same
six absences are derived. The experiment also measures the pruning: of 189,216
arity-valid candidate clauses, 127,584 already pass the learner's head-binding
filter and **105,330 of those (82%)** are rejected on type/mode grounds before the
kernel is ever asked.

```bash
./experiments/typed/typed.sh --offline   # or: ./northstar.sh --offline --check
```

### 5.15 Deduction needs integration, not a loss (`experiments/integral`)

Induction learns by **differentiation**: a scalar loss and its gradient. v0.0049
asks whether deduction needs the same, and makes the answer precise by building
the three integrals and giving each a falsifier. The result: two layers are
genuine potentials, the third is a connection.

**A — the forward integral (a potential).** `closure` is the least fixed point of
the immediate-consequence operator: the union of its iterates, a discrete integral
over derivation depth, and it is **path-independent** (the experiment closes the
theory under two rule orders and checks the closures are equal). Its *debt* — the
target atoms it cannot reach — is read off the kernel, not a proxy. On the
north-star theory (239 base facts, 41 derived) the full rule set reaches every
target with `false_assert = 0`; dropping the induced `calls` law opens a debt of
**27** targets. So `E = content_loss + MDL` is a real scalar potential, and
*structure* learning (find rules that lower DL) is a legitimate descent.

**B — the evidence integral (a measure).** `Z = Σ_T exp(−E(T))` over a set of
candidate theories, with `F = −log Z`. This is not an objective to minimise; it
answers *"how many candidate theories are good?"*. A single best theory (MAP) is
blind to that — the gap `E_MAP − F ≥ 0` is the **multiplicity reward**. For two
identical-energy theories the reward is exactly `log 2` (the experiment checks
this to `1e-3`). `Σ posterior = 1` and `F ≤ E_MAP` are invariant checks that can
only fail if the integral is wrong.

**C — the order integral (a connection).** Under a *bounded* backward-chaining
search, per-rule credit depends on the order rules are tried. The experiment
sweeps the two rule priorities over a grid and reads the credit field: its
discrete circulation (`curl`) is **nonzero** on the diagonal cells and the 2×2
block holonomy is **4.0**. A scalar's gradient has circulation *identically zero*
(checked on two scalar controls), so **no scalar `Φ(W)` has credit as its
gradient**: credit is a connection, and learning it is a path integral (parallel
transport), whose invariants are holonomies, not potential differences. Adding a
constant to every priority is a gauge transform and cannot change the curl
(checked). Deep (proof-DAG) credit differs from shallow credit exactly where the
order mattered: a rule that succeeds on a locally-provable subgoal but sits on a
dead branch gets no credit, and the failure frontier is blamed instead.

The honest conclusion: **putting a loss on the credit/order sector is a category
error** — it would be a fake gradient on a non-integrable field. Integration is
the right primitive everywhere in deduction; a loss is right only where the field
really is a potential (structure/MDL), and the experiment says exactly where that
is.

```bash
./experiments/integral/integral.sh --offline   # or: ./northstar.sh --offline --check
```

### 5.16 The reading speaks the deduction ladder (`experiments/reading`, N9 + typed gate)

v0.0044–46 raised the *presentation* ladder to N8, but v0.0046/47/48/49 emitted
**byte-identical** sentence lists: the realizer listed positive Horn conclusions
only and never consumed the D5/D6 conclusions the kernel had just learned to
derive. v0.0050 closes that gap, and it is the first time the **deduction**
ladder shows up in the final natural-language output.

**N9 — a certified negative.** `dlm/narrative.py` gains `_n9`, which realizes the
closed-world atom `absent(M, L)` as *“M does not contain an L layer.”* This is the
first NEGATIVE sentence in the line. It is not a fact lookup: `absent` is
derivable **only** by stratified negation (§5.13) over the GIVEN `candidate_layer`
universe, and it is **non-monotonic** — presenting one `has_layer(M, L)` fact
retracts the matching sentence. The `negative_needs_closed_world` probe makes this
a real falsifier: with `close_world=False` the reader emits no `absent` at all. On
the real program the reader certifies six absences (attention, batchnorm2d, gru,
layernorm, lstm, maxpool2d) beside the three layers it has (conv2d, dropout,
linear).

**Typing (D6) is a gate, not a rung.** It would be a **category error** to turn
the type checker into a sentence level: typing decides *admissibility*, not
*truth* (§5.14). So instead of printing a “typed” sentence, `experiments/reading`
closes the theory under a GIVEN typed/moded `Signature` (`build_signature`). An
ill-typed theory makes `closure` raise `TypeError`, i.e. the reader **abstains**
instead of deriving from an inadmissible rule, while for the honest theory the
closure is **identical** with and without the signature (`typed_gate_binds` and
`typing_does_not_change_truth`).

```bash
./experiments/reading/reading.sh --offline   # or: ./northstar.sh --offline --check
```

Measured on the real `main.py`: **reading level N9, score 1.0**, every sentence
kernel-certified, with all sixteen verdicts holding — including
`negative_absence_sentence`, `negative_needs_closed_world`,
`nonmonotonic_negative_retracts`, `typed_gate_binds`, `typing_does_not_change_truth`.
The honesty ablation is unchanged: strip the searched domain facts and the N7
`recognizes` sentence disappears.

### 5.17 Equality as a finite congruence (`experiments/equal`, D7a)

v0.0050's reading exposed a **false negative**: it certified `absent(net, maxpool2d)`
even though the forward pass calls `F.max_pool2d`. The positive evidence lives under
library **aliases** (`f_max_pool2d`, `nn_conv2d`, `transforms_normalize`) while the
closed-world candidate universe uses canonical layer **kinds** (`maxpool2d`,
`conv2d`, ...). A function-free Horn theory cannot state that two symbols denote the
*same* thing — that is equality.

`dlm/equality.py` (D7a, untrusted) supplies it as a **finite congruence** over the
given symbol set:

* `same_kind` — the equivalence classes of a canonical kind after stripping the
  library prefixes (`f_`, `nn_`, `transforms_`) and mapping aliases
  (`max_pool2d → maxpool2d`). Reflexive, symmetric and transitive *by construction*,
  and finite because the symbol set is given.
* `uses_layer(m, L)` — a module uses a layer kind if it **defines** it
  (`has_layer`), one of its **methods calls** it, or it calls it directly.

Both feed the *same* closed-world shape as v0.0050
(`absent(m,L) :- is_module(m), candidate_layer(L), not uses_layer(m,L)`), so the
kernel stays function-free and nothing here asserts truth.

The claim is **conservative**: restricting the new closure to the old predicates
equals the base positive closure exactly. The falsifiers (`experiments/equal/run.py`):
`false_negative_reproduced` (D5 alone still yields `absent(net, maxpool2d)`),
`false_negative_fixed` (with equality it is gone and `uses_layer(net, maxpool2d)`
holds), `equality_is_congruence`, `conservative_extension`, `aliases_recognised`,
`remaining_absences_are_unused`, `present_layers_kept`. The reading's N9 is now
sound: the six v0.0050 absences drop to **five** (attention, batchnorm2d, gru,
layernorm, lstm) — max-pool is correctly *used*.

```bash
./experiments/equal/equal.sh --offline   # or: ./northstar.sh --version v0.0051 --offline --check
```

This is D7a on the deduction ladder. **D7b (function symbols)** would break the
function-free invariant and is deliberately deferred: no falsifier has yet shown it
is needed.

### 5.18 The integral, measured: well-posed is not effective (`experiments/effective`)

v0.0049 proved the integrals are **well-posed** (`Σ posterior = 1`, `F ≤ E_MAP`,
gauge invariance, nonzero holonomy) — but every verdict was a definition check and
**nothing consumed the modules**. That answers *"is it defined?"*, not *"is it
effective?"*. v0.0052 adds `dlm/effective.py` (untrusted) and
`experiments/effective/`, which make the two integrals into a **predictor** and a
**controller**, then falsify them at **equal budget** with control arms:

**B — the evidence integral as a held-out predictor.** A single MAP theory commits
to one theory; the posterior **marginal** averages predictions over every
rule-subset weighted by its evidence (`marginal_prediction`). The falsifier
`multiplicity_probe` builds two theories that are **energy-tied** (`E=[1.0,1.0]`,
`posterior=[0.5,0.5]`) and disagree on the held-out target: any MAP must pick one,
so it is wrong half the time (**Brier 1.00**, `map_commits_to_wrong_theory`), while
the marginal predicts `p=0.5` (**Brier 0.25**) —
`multiplicity_evidence_strictly_beats_map_under_multiplicity`. On the natural
**online** domain there is no harmful multiplicity, so the marginal **ties** MAP
(delta `+0.000` in §5.4's `[integral]` block) — no loss. On a held-out transfer
split the marginal is never *worse* than MAP (`evidence_marginal_not_worse_than_map`)
and strictly beats the empty theory (`brier 0.000` vs `0.085`,
`evidence_beats_empty`); every committed `≥0.5` atom is in the kernel closure
(`evidence_committed_sound`). The proper score is **Brier**, not thresholded
recall: under an MDL prior the marginal may *commit to fewer atoms yet calibrate
better*, so both are reported, never conflated.

**C — the order/credit integral as a controller.** `experiments/effective` also
runs the bounded executor (§5.15-C) on a goal set where a cheap useful rule competes
with decoys, at a **fixed goal budget** (`order_matters_at_equal_budget`):

| arm | goals proved (of 12) | spent |
|-----|--------------------:|------:|
| static (declaration order) | 2 | 20 |
| random order | 2 | 20 |
| integrated credit | **12** | 12 |
| path integral (learned priorities) | **12** | — (first round 2) |

`credit_beats_static`, `credit_beats_random`, `path_recovers_credit` and
`path_improves_over_static` all hold. The path integral learns the priorities from
credit accumulated over rounds, so the *first* round is the static baseline and the
final round recovers the integrated-credit result.

The honest reading: the integral is effective **exactly when multiplicity exists**
(a genuine choice among good theories, or a search whose order matters) and never
worse in these settings. All **15** verdicts pass.

```bash
./experiments/effective/effective.sh          # or: ./northstar.sh --version v0.0052 --offline --check
```

## 6. Honest status

The learning structure now *works as a proposer*: it generalizes, accumulates,
retracts falsified rules, and transfers to unseen referents. It is **not yet a
sound judge**: the gate checks a finite negative sample (now over the full
*revealed* complement, but still only what has been seen), so it can admit an
empirically-sound, universally-false rule until the counterexample arrives. The
trust invariant says it should **abstain**, not assert.

v0.0048 closes the first half of that gap: **typed/moded signatures** now reject
an ill-shaped clause *before* the finite-sample gate ever runs, so the seed-3
rule is unrepresentable rather than merely unrefuted. What remains is the other
half:

1. **Structural soundness** (closure-subset / subsumption) instead of sampled
   negatives, so soundness is a proof, not a test.
2. **Equality and functions** (D7) — the deduction-level raise. **Equality (D7a)
   is done in v0.0051** as a finite congruence (`dlm/equality.py`); what remains is
   **function symbols (D7b)**, which would break the function-free invariant and is
   deferred until a falsifier shows it is needed.
3. A **long-run harness** (`experiments/train`) that runs time/round-based with
   periodic held-out evaluation and checkpoint/resume — the accumulating learner
   and `theory.py` are its bricks; the sweep is the next step.
4. **Integration effectiveness** — v0.0049 only showed the integrals are
   *well-posed*. **v0.0052 measures them** (§5.18): under equal budget the evidence
   marginal never loses to MAP and strictly wins under multiplicity, and integrated
   credit proves 12/12 vs 2/12. What is *not* yet shown: that the integral beats a
   **strong non-integral baseline** on a large task, or that the MDL cost is the
   right prior. The falsifier stands and the controls are in place.

### 5.19 Recursive self-supervised learning (`experiments/recursive`, v0.0055)

The model's own kernel-certified output becomes the next round's **input**. Given a
directed graph as `edge` facts and **not** the relational transitive rule, each
round closes the relation it currently has under two GIVEN definitional level
rules and reifies the certified extension as a new predicate:

```
r_{k+1}(X,Y) :- r_k(X,Y).                 -- inherit
r_{k+1}(X,Z) :- r_k(X,Y), r_k(Y,Z).       -- compose (self-join)
```

Because a round doubles the path length the relation spans, the model reaches the
**full transitive closure in O(log diameter)** rounds, then abstains when a round
adds nothing (fixpoint). Nothing is invented: the kernel derives the extension and
the model feeds its own conclusion back — recursion, no labels, the kernel the
only judge. `dlm.recursive.one_shot` is the depth-1 control; on any graph with a
path longer than two hops it provably fails to reach the closure, which is the
falsifier that recursion is required. Run:

```
./experiments/recursive/recursive.sh
```

Measured (chain of 25 nodes, diameter 24): derived 300/300 true pairs, false 0,
depth 6 (bound 7), one-shot 47; (16-node DAG, diameter 4): 120/120, depth 3. All
verdicts true.

### 5.20 Self-evaluation + weakness-targeted curriculum (`experiments/selfimprove`, v0.0056)

v0.0054 put web access and self-supervision *inside* the model, and v0.0055 made the
model's own output its next input — but the model still did not **evaluate itself**
or **choose** what to improve. v0.0056 adds the missing controller:

* `dlm/ability.py` reads the kernel closure ONLY and reports, for every **deduction
target the model's rules promise** (`target_predicates`: all rule heads plus
observed fact predicates — no fixed goal list), whether it is proved or blocked and
by which absent premises. A premise the web can supply (`dataset_of`, `task_of`)
is **actionable**; the rest are structural gaps. `weak_spots` orders the agenda
(actionable first) and `improvement` scores a round **at the target level** — only
actual kernel derivations count, so a scrambled fact can never look like progress;
* `dlm/curriculum.py` runs the closed loop — assess → ask → acquire(web) → re-close
→ re-assess — and stops on a *named* reason (`saturated`, `no_actionable`,
`acquire_empty`, `no_progress`, `max_rounds`). Acquisition abstains (no fact) when
evidence is missing, so replay is byte-for-byte deterministic and nothing is
invented. `dlm.agent.Reader.assess` / `Reader.self_improve` expose it as the
model's own capability.

The north-star slice: the reader proves `trains` but cannot prove
`recognizes(<program>, <what>)` until it discovers the `dataset_of` gap *itself* and
searches for it — one self-directed acquisition fixes it (`weakness_identified`,
`improvement_from_web`). A synthetic three-gap theory shows the loop **iterating**
one weak spot per round to `saturated`. Controls: a scrambled fact yields
`no_progress` (nothing proved), and with acquisition removed the loop stops at
`acquire_empty` (abstains, invents nothing). Run:

```
./experiments/selfimprove/selfimprove.sh
```

Honest limit: the **agenda** is predicate-level (`dataset_of` is missing
*somewhere*); only the **kernel** is argument-level. A scrambled fact can silence a
weak spot without proving the target — the model stops asking, but it never asserts
anything false. That is the conservative direction (abstain, don't invent).

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
  narrative.py     untrusted leveled realizer (N1..N9); every sentence carries kernel support; analyze_sentences reports each rung's kind
  closedworld.py   untrusted closed-world absence rule over a GIVEN candidate universe
  equality.py      untrusted equality as a finite congruence (D7a): alias classes + uses_layer
  api_semantics.py (experiments/mnist) acquired API-effect facts for certified “why” (N6)
  signature.py     (experiments/mnist) GIVEN typed/moded signature + adversarial clauses (D6)
  theory.py        checkpoint/resume a theory (Ground + Experience + facts, JSON)
  integral.py      untrusted integrators: forward closure + debt, evidence measure Z
  connection.py    untrusted connection: bounded order-sensitive search, credit, holonomy
  effective.py     untrusted measurement: evidence marginal predictor + order path integral
  web.py           the model's web primitive: cached HTTP (the senses), abstains, offline-replayable
  search.py        generic providers: Sphinx objects.inv, Wikipedia, Wikidata/MediaWiki, Stack Exchange
  acquire.py       the acquisition subject: candidates -> web search -> reduced fact(+provenance) -> cache
  agent.py         the autonomous Reader (perceive->acquire->search->induce->close->read) + self-supervised run_loop + self-improvement
  recursive.py     recursive self-supervised learning: reify the kernel-certified self-composition level by level (log-depth closure)
  ability.py       self-evaluation: deduction targets (rule heads) proved / blocked, and actionable externally-acquirable gaps
  curriculum.py    weakness-targeted loop: assess -> ask -> acquire(web) -> re-close -> re-assess, to a named stop
experiments/
  ground/          one generalization transfers (synthetic)
  web/             real Wikipedia/Wikidata class hierarchies (web access delegated to dlm.web/dlm.search)
  stream/          multi-relation accumulation, round-by-round open-universe curve
  abstract/        recurring subgoal -> invented predicate; DL + budget coverage
  online/          streaming trajectory: learn each round, score on unseen entities
  code/            real GitHub repos -> import graph -> cross-repo transfer (transport delegated to dlm.web)
  mnist/           one program: reduce -> acquire meaning from the web -> learn -> understand -> IR-TREE -> N1..N9 reading (the body's final output; shares one pipeline with reading/)
  generalize/      corpus of programs -> induced concepts -> deductive transfer to the north star
  abstraction/     L5 composition .. L9 transfer, with an abstraction_score
  concept/         concrete facts -> detect gap -> SEARCH domain knowledge -> re-learn -> certify the core concept
  reading/         falsifier harness for the body's reading (honesty ablation, typed gate, non-monotonicity)
  closedworld/     certified absences; non-monotonic retraction + stratification + safety probes
  typed/           typed/moded signature: type/range/mode checks + candidate-space pruning
  equal/           equality/congruence: reproduce and fix the D5 false negative
  integral/        forward integral + evidence measure + credit holonomy (the three layers)
  effective/       equal-budget held-out falsification of the integrals (predictor + controller)
  recursive/       recursive self-supervised learning: bootstrap reachability from the model's own output, one-shot control
  selfimprove/     model evaluates its own ability, finds its weak spot, searches for the missing premise (scramble/no-web controls)
  train/           accumulating learner + closure benchmark (the long-run harness seed)
tests/             220 tests (network-free)
test.sh            PYTHONPATH=. python -m pytest -q
```

## 8. Version

`0.0.56` — **self-evaluation + weakness-targeted curriculum** (`dlm/ability.py`,
`dlm/curriculum.py`). The model reads its own ability off the kernel closure
(which deduction targets its rules promise but cannot conclude), identifies the
missing premise only acquired knowledge can supply, asks the web for exactly that
premise, re-closes through the kernel, re-assesses, and stops on a named reason.
Targets are discovered from the theory, not a fixed list; improvement is measured
at the target level, so a scrambled fact improves nothing and a removed web
abstains (`experiments/selfimprove`).

`0.0.55` — **recursive self-supervised learning** (`dlm/recursive.py`). The model
feeds its own kernel-certified output back as the next round's input: each round
closes its current relation under two definitional level rules (inherit +
self-join) and reifies the certified extension as a new predicate, so reachability
is bootstrapped to arbitrary depth in O(log diameter) rounds with no labels, then
abstains at the fixpoint. It is not given the relational transitive rule; a single
composition cannot reach the closure, which is the recursion falsifier
(`experiments/recursive/recursive.sh`).

`0.0.54` — **the model is the subject, not the harness**. The automation that
lets a deductive model improve without a human moves out of `experiments/` and
into the model: `dlm/web.py` (the model's one web primitive — cached HTTP, the
senses, abstaining, offline-replayable), `dlm/search.py` (generic providers:
Sphinx object inventory, Wikipedia, Wikidata/MediaWiki, Stack Exchange — ways to
look things up, never facts), `dlm/acquire.py` (the acquisition subject:
candidates → web search → reduced `meaning`/`dataset_of` fact with provenance →
cache; names no library or dataset), and `dlm/agent.py` (`Reader` owns
perceive → acquire → search → induce → close → read, and `run_loop` repeats it
over sources with a named stop reason, the kernel the only judge). The web
residue in the experiments is now thin glue: `experiments/mnist/{knowledge,domain}.py`
carry only the GIVEN PyTorch cue vocabulary and delegate acquisition to
`dlm.acquire`; `experiments/mnist/run.py::pipeline` drives the model's `Reader`;
`experiments/web/` and `experiments/code/` delegate all transport to `dlm.web`.
Everything acquired is still untrusted (the kernel re-checks what it concludes),
and the measured north-star output is unchanged (239 facts / 87-pair closure /
615 atoms / 42 certified sentences / level N9). No kernel change.

`0.0.53` — **the reading is the body's final output**. The north-star BODY
(`experiments/mnist/run.py`) had used a private flat realizer (`realize.py`, now
deleted) and emitted only ~32 structural sentences, while the N1..N9 reading lived
**only** in the side experiment `experiments/reading` that the harness ran last — so
the body's own output never reached the N7 purpose rung (`'recognizes' in
mnist_report → False`). This version removes the split: the body and the falsifier
share **one pipeline** (`mnist.run.pipeline`), and the body's `narrative` IS the
N1..N9 reading (42 sentences, N1..N9; N7 purpose + 5 certified N9 absences;
`all_sentences_verified`, `false_final=0`), built over structure + acquired
`meaning` + searched `dataset_of` + acquired `api_effect` + the D5/D7a absence
layer. `dlm.narrative` gains `LEVEL_NOTE` and the read-only `analyze_sentences`
report; the `concept` type now spans the GIVEN decoder vocabulary (so an
under-acquired tiny program still type-checks). No kernel change.

`0.0.52` — **measures the integrators** instead of only defining them. `dlm/effective.py`
(untrusted) makes the evidence integral a held-out **predictor** (posterior marginal
over rule-subsets) and the order/credit integral a **controller** (path integral over
learned priorities); `experiments/effective/` falsifies both at **equal budget**
against MAP / static / random controls. Result: the marginal **ties** MAP on the
natural domain and **strictly beats** it when two theories are energy-tied
(Brier `1.00 → 0.25`), while integrated credit proves **12/12** goals where static
and random prove **2/12**; 15 verdicts pass. The online experiment gains an
`integral` arm and logs the marginal's Brier score, and the reading reports a
per-sentence analysis (`experiments/reading`). Well-posedness (v0.0049) is not
effectiveness — this version measures the second. On top of the
leveled reading **N9** (v0.0050), the untrusted **integrators** (v0.0049:
`dlm/integral.py`, `dlm/connection.py` — forward integral, evidence measure, credit
holonomy), typed/moded signatures (v0.0048, D6), and closed-world deduction
(v0.0047, D5).

`0.0.51` — adds the first **equality** rung (**D7a**): `dlm/equality.py` closes the
world over a FINITE congruence (`same_kind` alias classes + `uses_layer`) instead of
raw symbol identity, which **fixes a real false negative** — v0.0050 certified
`absent(net, maxpool2d)` though the program calls `F.max_pool2d`. The extension is
conservative (it adds only `same_kind`/`uses_layer` and no positive Horn conclusion);
the reading's N9 now correctly drops max-pool from its absences. On top of the
leveled reading **N9** (v0.0050), the untrusted **integrators** (v0.0049:
`dlm/integral.py`, `dlm/connection.py` — forward integral, evidence measure, credit
holonomy), typed/moded signatures (v0.0048, D6), and closed-world deduction
(v0.0047, D5).

`0.0.50` — makes the **deduction ladder visible in the final output**: the level
realizer gains **N9**, a certified NEGATIVE realized from a closed-world `absent`
atom (non-monotonic; only sound over the GIVEN candidate universe), and the reader
is closed under a GIVEN typed/moded `Signature`, so an ill-typed theory makes it
**abstain** instead of deriving (typing gates admission, never truth). This is the
first version where the D5/D6 conclusions the kernel learned in v0.0047/48 actually
appear in the natural-language reading, which had been byte-identical across
v0.0046–49. On top of the two untrusted **integrators** that make the
deduction-learning question precise: `dlm/integral.py` (forward integral = closure
+ kernel-decided debt; evidence integral `Z = Σ_T exp(−E(T))` over candidate
theories) and `dlm/connection.py` (order-sensitive credit under a bounded search,
whose discrete circulation is a nonzero holonomy — credit is a connection, learned
by a path integral, not a loss). On top of typed/moded signatures in the trusted
kernel (D6:
type soundness, range restriction and mode anability checked before any
derivation; ill-typed theories rejected, truth unchanged for the honest theory),
on top of closed-world deduction
(v0.0047: stratified negation over a GIVEN universe; non-stratified theories
rejected, unsafe negations pruned, closure non-monotonic), on top of v0.0039 (IR-TREE,
proof as data, label-free abstraction),
web-acquired meaning for the north-star slice (v0.0040), corpus-level concept
generalization with deductive transfer (v0.0041), the L5–L9 abstraction ladder
(`dlm/compose.py`, v0.0042), core-concept (gist) capture with a search-and-relearn
loop for missing domain knowledge (`dlm/gist.py` + `experiments/concept/`, v0.0043),
and the **leveled final reading** raising the output to N9 (`dlm/narrative.py` +
`experiments/reading/`, v0.0044→v0.0050).
Licensed under
Apache-2.0 (see `LICENSE`).
Design notes: [`COMPOSITION.md`](COMPOSITION.md).