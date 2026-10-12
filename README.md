# DLM v0.0030 — the fused two-file core + tree-native IR + verifiable-reward self-supervision + IO boundary + a grounded representation vector + bounded execution control + goal-conditioned control + a Lisp seam + an explanation/abstraction layer

A restart from the smallest possible base. The **trusted** part is exactly two
files. DLM is a **deductive logic model**: knowledge lives in an external KB, and
answers come from *proof*, abstaining when it cannot. Its attention analogue is
one learned order over an exact interaction (unification):

    propose  ->  unify  ->  verify

Attention routes *content* by a learned bilinear score; DLM routes *inference* by
a learned order while the interaction itself stays **exact**.

## The fusion

The whole point of the fused core is that there is **one object**, not several:

* a **`Clause`** is a Horn rule the kernel uses (**truth**) *and* the same
  clause is a weighted feature the scorer uses (**order**);
* a **`Theory`** is an ordered set of clauses — it is the rule set, the feature
  set and the model at once;
* matching is one-way **subsumption** (a clause pattern's variables bind, the
  matched rule/atom's variables stay opaque), so the scorer is a weighted
  unification pattern matcher sharing the engine's term machinery;
* induction (LGG) **adds** clauses, `learn` **reweights** them, and inference is
  the kernel's `prove`.

Everything serialises to one form:

```
(theory ancestor
  (clause lgg_ancestor_0 +0.333 (ancestor ?G0 ?G1) (parent ?G0 ?G1))
  (clause lgg_ancestor_1 +0.667 (ancestor ?G0 ?G1) (ancestor ?G0 ?E0) (parent ?E0 ?G1)))
```

**Trust invariant (structural).** A clause's *structure* is truth; its *weight*
is order. A weight never reaches the kernel and can never make an unprovable atom
provable. The substrate is **positive Horn** (v0.0019 removed the negative-literal
side table); an unnormalisable input abstains.

## IR-SSL — language self-supervision over an intermediate representation

`dlm/ssl.py` (v0.0020) is a **separate, untrusted** layer. Text and logic never
touch each other directly; they meet at an explicit **intermediate
representation** whose canonical form is a plain **symbol tree** — a `Form`, the
same type atoms, rules and theories serialise to:

```
(ir <name> (rel <cue>...) (subj <tok>...) (obj <tok>...) <order> <head>...)

sentence --frame_of/ir_of--> IR tree --rank--> Atom   (reading,  NL -> logic)
Atom --rank--> IR tree --render--> sentence           (realizing, logic -> NL)
```

The `Frame` dataclass `(rel, subject, obj, order)` is only a *view* of that tree
(`ir_from_form`); a reader can learn straight off the tree
(`reader_tree_features`), so adding a head to the grammar adds features without
editing a feature table. In the tree, `rel` are the relational *cue* tokens (the
wording that selects the predicate), `subj`/`obj` are argument-name tokens or
`probe` in a masked / de-identified view, and `order` records which mention came
first. Because the cue and the arguments are separated in the IR, a reader can be
trained on *wording* alone — which is what stops it collapsing onto an entity's
majority predicate.

Both directions are one dependency-free `LinearRanker`. Self-supervision has two
label sources and neither is human:

* **reading** — distant supervision + the kernel: a frame is anchored to a web
  fact, the candidate atom is positive iff the kernel entails it, every sibling
  is a negative;
* **realizing** — bidirectional consistency: a frame for an atom is positive iff
  the *current reader* reads it back to the same predicate.

Neither head asserts. The kernel still decides; IR-SSL only orders.

## The self-supervised loop — a kernel verdict is a verifiable reward

RLVR-style training uses a verifiable checker as the reward. DLM's checker is the
kernel itself, and it is exact and free, so the loop needs no policy gradient: it
is **expert iteration / rejection sampling over programs**. `dlm/selfsup.py`
(v0.0024) is a third **untrusted** layer that fuses the pieces into one loop:

```
propose a program (clauses = Lisp-like code)
      -> the kernel verifies it   (closure of kb + program)
      -> the reward filters it    (false_assert is a HARD gate)
      -> only verified programs are promoted into the theory
      -> the grown theory is the next round's environment
```

A program is a set of `Clause`s; a promoted clause is *structure* only (its
weight stays order and never reaches the kernel), so the proposer can never
assert. The reward is `coverage − cost·size`, collapsed to `−1` by any false
assertion. Arms: `learn` (the method), `no_promote` (no feedback), `scramble`
(misaligned labels), `random` (reward-blind), `reward_hacking` (gate removed).

## IO — the data boundary (text, datasets, media)

`dlm/io.py` (v0.0021) is the second **untrusted** layer: the single place where
world data meets the logic, in both directions.

```
bytes/str --decode--> Block --(caller)--> atoms / frames / KB
DLM result --encode--> bytes/str, incl. natural-language sentences
```

A `Block` is a frozen, ordered, JSON-serialisable record carrying whichever of
sentences, IR frames, logic atoms, `Rule`s, table rows, media metadata and raw
bytes the payload has. Codecs are registered **per media type**, so a real
vision/speech model can replace a default reader without touching callers:

| input | decoded into |
| --- | --- |
| `text/plain` | sentences + IR frames |
| `text/csv`, `text/tab-separated-values` | columns/rows **+ ground atoms** (role columns) |
| `application/json`, `application/x-ndjson` | atoms / sentences |
| `application/x-dlm` | atoms + rules + frames (the one form) |
| `image/png`, `image/gif`, `image/jpeg` | dimensions + bytes |
| `audio/wav`, `video/mp4` | format metadata + bytes |
| `application/octet-stream` | size + sha1 + bytes |

`media_atoms(block)` turns any media block into descriptor atoms
(`(width map.png 1024)`) so metadata can enter the KB. On the way out,
`encode(value, "text/plain")` renders atoms as natural-language sentences (an
unknown predicate falls back to its own words), while `text/csv` /
`application/json` / `application/x-dlm` emit structured data. **IO only proposes
and renders; it never asserts — the kernel still decides.**

## Representation — a vector the model can read

`dlm/vector.py` (v0.0026) is the fourth **untrusted** layer. v0.0025 placed IR
trees in a learned 3D lattice, but over a *hashed* feature code: a hash has no
named coordinates, so the lattice cell was an opaque prototype the model could
not read back. v0.0026 keeps the placement idea and fixes the representation
half — an IR tree maps to a sparse **symbolic vector** whose every coordinate is
a *named symbol the model already knows*, and which reverses exactly:

```
tree  --tree_vector-->  SymbolVector  --vector_tree-->  tree     (exact inverse)
```

A coordinate is a declared role plus a token taken straight from the tree:

```
name=alan  rel[0]=born  subj[0]=alan  obj[0]=paris  order=0
```

`ROLES` are `name`, `rel`, `subj`, `obj`, `order`, `extra` — the same structural
axes `dlm.ssl.tree_features` walks, so the representation invents no private
vocabulary. The vector reads as logic: `vector_features` returns the role+token
symbols (plus the role lengths) a reader or the kernel can consume directly.

The algebra is small and closed: `bundle` superposes two trees (union of
coordinates, weights added) and `restrict(role)` unbinds one role, so composing
many trees is a later step built on this same algebra. For dense consumers,
`Basis.of(vectors)` fixes an ordered coordinate system whose index `i` still
resolves to a *named* `Symbol` (`encode`/`decode` round-trip exactly). A vector
serialises to the same one form as everything else:

```
(vec (sym rel 0 1.0 born) (sym subj 0 1.0 alan) (sym obj 0 1.0 paris) (sym order 0 1.0 0))
```

**A vector only proposes; the kernel still asserts.**

## Execution control — the learned order finally runs the model

The self-supervised loop learned to *add* clauses, but a clause's weight never
reaches the kernel and `closure` is complete — so the learned order could reorder
a candidate list and nothing more. It was **epiphenomenal**. `dlm/execute.py`
(v0.0027) is the fifth **untrusted** layer and gives the order something to
control: a bounded backward-chaining interpreter that, at every goal, tries the
theory's best-ranked clauses first and spends a fixed budget of clause attempts.

```
execute(kb, theory, goals, budget=B)
   at each goal: facts (free) -> clauses by (-weight, name) -> recurse on the body
   leaves a readable trace: (goal, clause, ok, depth) for every attempt
```

The trace is the missing observation. `credits` reads which clause closed a proof
(a *hit*) and which only spent budget (*waste*); `apply_credit` nudges each
clause's weight by its own net credit; `run_control_loop` runs propose → kernel
gate → promote → execute → credit, so the order the executor uses next round is
shaped by its own experience. Nothing asserts except the kernel: `check_sound`
re-checks every proved goal against `closure`, and every proof is still the same
symbols `verify` re-checks.

This is also where the fused perceptron's `matched` view proved too coarse: a
general clause *subsumes* every over-specific rule beneath it, so a pair-based
`reweight` smears a decoy's waste onto the very clause that should win. Exact
per-step credit fixes it — the trace already knows which clause fired.

## Goal-conditioned control — the order can route

v0.0027 made the learned order control *execution*, but the order was still a
single **global** weight per clause. A global weight cannot route: it cannot say
"clause C is right for *this* goal and wrong for *that* one", which is exactly
what backward chaining needs — the same clause can close one goal cheaply and burn
the budget on another. `dlm/control.py` (v0.0028) is the sixth **untrusted**
layer and adds the missing *context*.

```
context_features(kb, goal, clause)
   sup:<pred>    body literal is backed by a fact once the head is matched to the goal
   unsup:<pred>  not;  nsup=k / frac=all|some|none;  clen / cname / cpred / goal / garity
ControlScorer  =  a learned linear model over those features
```

The decisive feature is a one-step, **goal-conditioned** lookahead: whether each
body literal has a fact behind it. `ControlScorer` is fit from the same exact
per-step credit v0.0027 introduced, but read as *context* labels —
`train_control(ControlScorer(), examples_from_execution(kb, theory, trace), kb=kb)`.
An `EpisodicMemory` records per-`(goal-signature, clause)` hits and waste and
feeds a `memo:` feature. The scorer only *orders* clause attempts: `execute` still
memoises proved ground goals, still spends the same budget, and `check_sound`
re-checks every proof against `closure`. A small additive `scorer=` seam was added
to `dlm/execute.py`; nothing else there changed.

**A vector is not understanding; neither is a weight. Routing is.**

## The Lisp seam — the substrate reads and writes itself

The IR/vector/loop layers all speak S-expressions, but every bridge to the kernel
was a named, one-directional function and the model never *evaluated* a form.
`dlm/lisp.py` (v0.0029) is the seventh **untrusted** layer and closes six gaps in
one language seam:

```
1  eval_form        one evaluator, dispatch on the head symbol
2  match_form       structural matching of a code pattern against a code tree
3  quote/quasiquote  macros that write forms, which eval_form then evaluates
4  theory_source    emit -> re-read -> require equal; the selfsup loop re-enters
                    through its own source (run_source_loop)
5  proof_to_form    a certificate is a term: emit, re-read, re-verify
6  tree_atoms       reify an IR tree into facts the kernel can prove about
```

Only registered heads evaluate (`fact`, `rule`, `clause`, `theory`, `query`,
`verify`, `quote`, `quasiquote`, `defmacro`, `do`, …); an unknown head **abstains**
with `EvalError` and never guesses. Only `query` reaches the kernel, and it only
ever calls `prove`.

```
(rule rec (t ?x ?y) (e ?x ?z) (t ?z ?y))
(query (t n0 n5))                 ; -> a re-checkable Proof, or None
```

The code algebra has metavariables (`?x`), a wildcard (`_`) and structural
unification over nested tuples, so a macro can generate a clause:

```
(defmacro chain-rule (?name ?edge) (clause ?name 1.0 (t ?x ?y) (?edge ?x ?y)))
(chain-rule c_step e)   ; -> (clause c_step 1.0 (t ?x ?y) (e ?x ?y)) -> a Clause
```

**The kernel stays function-free.** This is a *code-level* evaluator above the
logic, not function symbols, lambdas or a general `eval` of arbitrary code in the
kernel; the two algebras meet only at `form_to_atom` / `tree_atoms`. That meeting
is where a full homoiconic closure (term = form) would go next.

## The explanation layer — self-interpretation at scale

Every earlier layer made the model *more* inspectable clause by clause; v0.0030
adds the missing half of "extreme interpretability": reviewing a theory that has
gotten **large**. A million readable clauses are as opaque as a black box, so
`dlm/explain.py` treats explanation as a first-class, kernel-checked output:

```
description length  clauses + literals + signature = the reader's review budget
provenance          why is each clause believed?  (witnesses, round, parent)
abstraction         group clauses into named modules; review by hierarchy
compression         drop a clause only if the kernel's closure is unchanged
explanation         a goal + its re-checkable proof + clauses + provenance + a
                    counterfactual ("which clause is load-bearing?")
```

A belief answers *"why?"* with a **term**, not a scalar: `certify_from_tasks`
computes each clause's marginal contribution with the kernel (`closure` with the
clause minus `closure` without it) and records the witnesses. Compression is
decided the same way — the short clause `anc(x,y):-e(x,y)` structurally
*subsumes* the long `anc(x,y):-e(x,z),e(z,y)` but is **not** logically stronger,
so redundancy is defined operationally (remove it and re-check the closure), never
by the structural proxy. The layer is **read-only** over the trusted core: it
imports `dlm` one way, never asserts, and the kernel stays function-free.

## Layout

| File | Role |
| --- | --- |
| `dlm/__init__.py` | **trusted substrate** + public surface (logic, sexp, unify, kb, kernel, engine) |
| `dlm/deductive.py` | **the fused core**: `Clause`, `Theory`, `subsumes`, induction, `learn`, `solve` |
| `dlm/ssl.py` | **untrusted IR-SSL language layer** (tree-native IR, features, reader/realizer, forms) |
| `dlm/io.py` | **untrusted data boundary** (codecs, `Block`, NL/structured output) |
| `dlm/selfsup.py` | **untrusted verifiable-reward self-supervised loop** (propose → kernel verify → promote) |
| `dlm/vector.py` | **untrusted grounded representation vector** for one IR tree (named coordinates, exact inverse) |
| `dlm/execute.py` | **untrusted bounded executor + experience-fed proof credit** (order-sensitive backward chaining, readable trace, kernel-sound) |
| `dlm/control.py` | **untrusted goal-conditioned control layer** (context features, learned scorer, episodic memory; ranks each `(goal, clause)` pair) |
| `dlm/lisp.py` | **untrusted Lisp seam** (one evaluator over forms, code matching, macros, proofs as terms, source round-trip, tree reification) |
| `dlm/explain.py` | **untrusted explanation / abstraction layer** (description length, proof-carrying hypotheses, modules, exact kernel-checked compression, re-checkable explanations) |
| `experiments/webssl/` | the web IR-SSL experiment (`web.py`, `bridge.py`, `run.py`) |
| `experiments/webloop/` | random-web **dual-ability** loop (deduction + conversation), `run.py` |
| `experiments/ir_tree/` | tree-as-IR reader comparison, `run.py` |
| `experiments/selfsup/` | verifiable-reward self-supervised loop (program composition), `run.py` |
| `experiments/vector/` | grounded IR-tree representation check (round-trip / grounding / readout), `run.py` |
| `experiments/execution/` | bounded execution control + experience feedback (budgeted composition with decoys), `run.py` |
| `experiments/control/` | goal-conditioned control vs every global order (routing task + episodic-memory cache), `run.py` |
| `experiments/lisp/` | the six Lisp seams exercised end-to-end (eval, match, macro, source loop, proof-as-data, tree→proof), `run.py` |
| `experiments/explain/` | explanation of a learned theory + exact compression of a lemma library (with a random-removal control), `run.py` |
| `experiments/io_demo/` | heterogeneous-in → kernel → NL/structured-out demo |

The fused-core API is re-exported from `dlm`, so `from dlm import …` is unchanged.
The core imports only the trusted substrate; `dlm.ssl`, `dlm.io`,
`dlm.selfsup`, `dlm.vector`, `dlm.execute`, `dlm.control`, `dlm.lisp` and
`dlm.explain` import `dlm` (and each other, one way) and never the other way round.

## Run the core experiment

```
PYTHONPATH=. python -c "import json, dlm; print(json.dumps(dlm.run_experiment(), indent=2))"
```

It trains on the first half of a parent chain and holds out the rest. The LGG
learner writes a base clause and a recursive clause; `learn` separates the
recursive clause from a reversed decoy by shape alone; the kernel then proves
**51/51** held-out positives with **0** held-out negatives falsely asserted, and
the single `(theory …)` form round-trips (rules + weights).

## Run the web IR-SSL experiment

```
cd /research/dlm_v0.0030
PYTHONPATH=. python experiments/webssl/run.py --offline          # uses experiments/webssl/cache
```

Offline cache: 24 docs / 409 web facts / 939 hierarchy facts → 1 340 base atoms,
kernel closure **19 918** (18 578 derived). Entity-level 4-fold; the only thing
that changes between arms is the reader's features:

| arm | recall@1 |
| --- | --- |
| untrained / surface (predicate-blind) | 0.000 |
| majority baseline | 0.653 |
| scrambled labels (control) | 0.333 |
| **IR reader (cue-only)** | **0.747** |
| IR reader (de-identified) | 0.720 |
| IR reader, softmax objective | 0.747 |

Cue ablation drops the reader to 0.507 (below the majority baseline), kernel
`accept@1 = 0.747` with **0** false asserts, and a learned realizer reads held-out
atoms back at round-trip@3 = 0.686. Honest reading: the language-side gain is
real but modest — **+0.093 over the best baseline** on 75 aligned examples.

## Run the tree-as-IR experiment

```
cd /research/dlm_v0.0030
PYTHONPATH=. python experiments/ir_tree/run.py --offline            # mask=obj
PYTHONPATH=. python experiments/ir_tree/run.py --offline --mask all
```

Same data, same entity-level folds, same candidates and the same `IrReader`; only
the feature source changes — `hand` uses the hand-written `reader_features` over
a `Frame`, `tree` uses `reader_tree_features` straight off the symbol tree.

| arm | recall@1 | macro | per-fold spread |
| --- | --- | --- | --- |
| untrained | 0.000 | 0.000 | — |
| majority baseline | 0.653 | — | — |
| **hand features** | **0.653** | **0.525** | 0.267 |
| tree features | 0.573 | 0.240 | 0.690 |
| scrambled (control) | 0.307 | 0.240 | — |

Honest reading: the tree-as-IR mechanism works — a reader *does* fit the tree
(0.987 train recall, 0.933 macro) and on one fold the tree beats hand (0.840 vs
0.600). But across folds it is **high-variance and no better on average**: the
generic walk exposes argument/entity *leaves* (`leaf=ir/subj=<entity>`), which
leak across folds and crowd out the transferable cue features under hard-negative
perceptron training. The hand table's value is exactly that it *abstracts
arguments away* (`subj_seen`/`obj_seen`, never the tokens). So making the tree the
IR is mechanically clean, but it does not by itself fix the feature design — the
representation and the features have to be abstracted together.

## Run the representation-vector experiment

```
cd /research/dlm_v0.0030
PYTHONPATH=. python experiments/vector/run.py --offline                    # 400 synthetic trees
PYTHONPATH=. python experiments/vector/run.py --corpus web --offline       # 75 real IR trees
```

It checks the three operational senses of "the model understands the vector":
**faithful** (`vector_tree(tree_vector(t)) == t`), **grounded** (every coordinate
is a declared role + a token from the tree), and **useful** (a transparent
symbol-overlap kNN, against an opaque hashed-code kNN and a majority baseline).

Synthetic corpus (400 trees, basis dim 469, 7.27 active coordinates on average):

| check | grounded vector | opaque hash code |
| --- | --- | --- |
| exact round-trip | **1.000** | — |
| feature-link / dense round-trip | **1.000** | — |
| injective (distinct vectors) | **1.000** | 399/400 (collision 0.003) |
| named coordinates / invertible | **all / yes** | 0 / no |
| kNN recall@1 | **1.000** | 0.970 (majority 0.195) |

Honest reading: on the synthetic corpus the syntactic win is total — the grounded
vector is exactly invertible and named, and the hashed code collides and cannot
be read back. On the 75-tree **real** web corpus the representation guarantees
still hold (round-trip 1.000, grounded 1.000) but the readout does not separate:
symbol kNN 0.598 vs hash kNN 0.582 vs majority 0.624. The value of v0.0026 is
*interpretability and exactness* of the representation, not a readout-accuracy
claim on a small corpus.

## Run the goal-conditioned control experiment

```
cd /research/dlm_v0.0030
PYTHONPATH=. python experiments/control/run.py           # 40-node routing task
PYTHONPATH=. python experiments/control/run.py --quick   # smoke run
```

A chain of adjacent pairs is split into two disjoint families — even-start edges
are `a` facts, odd-start edges are `b` facts — and two clauses share the goal
predicate `t`: `c_a: t(x,y) :- a(x,y)` and `c_b: t(x,y) :- b(x,y)`. *Which* clause
proves a goal depends on the goal, not the clause, so no global order is optimal.
Budget = 1.2× the held goals.

| arm | held coverage | clause attempts | routing accuracy |
| --- | --- | --- | --- |
| global_fixed (equal weight, `a` first) | 0.789 | 22 | 0.526 |
| global_learned (v0.0027 credit) | 0.737 | 22 | 0.474 |
| control_untrained (zero scorer) | 0.789 | 22 | 0.526 |
| **control (learned)** | **1.000** | **19** | **1.000** |
| oracle (perfect lookahead) | 1.000 | 19 | 1.000 |
| random order (5 seeds) | 0.747 | 22 | 0.526 |

The learned scorer's top feature weights are exactly the lookahead: `sup:a` and
`sup:b` positive, `unsup:a`/`unsup:b` negative, `nsup=1` positive and `nsup=0`
negative. The episodic-memory demo (same predicate, one true clause and one silent
decoy) shows memory transferring to **new constants**: the first pass spends 38
attempts, the memory-informed second pass spends 19 — one attempt per goal — at
coverage 1.000 and kernel-sound.

Honest reading: goal-conditioned control reaches the oracle ceiling and beats
every global order on a task a global order *cannot* solve, but the gain is again
**bounded-resource** — one attempt per goal instead of two, not a new proof.
Episodic memory keyed by a constant-free signature transfers only *within one
predicate*; when both regimes share a predicate it cannot route (which is why the
experiment uses the lookahead scorer for routing and memory for the repeated-regime
cache). Open-vocabulary **invention** is a *proposer* concern and remains
deferred.

## Run the Lisp seam experiment

```
cd /research/dlm_v0.0030
PYTHONPATH=. python experiments/lisp/run.py            # all six seams
PYTHONPATH=. python experiments/lisp/run.py --quick    # 6-node smoke run
```

It evaluates a whole program with one `eval_sexp`, matches a code pattern against
a code tree, lets a macro generate a clause the kernel then uses, emits a theory
and requires the re-read to be equal, runs the self-supervised loop **through its
own source** (`run_source_loop`: 2 rounds, coverage 1.000, `false_assert` 0, source
stable), emits a proof as a term and re-verifies it (tampering fails), and reifies
an IR tree into facts so a leaf can be *proved* (`(leaf tree.2.1 born)`). All eight
checks pass deterministically (JSON byte-identical across runs).

Honest reading: this is a **language seam**, not new reasoning power. It does not
add function symbols or a general `eval` to the kernel — the logic stays
function-free — and the tree still is not readable as logic (`form_to_atom` raises
on a nested tree). What it *does* make possible is a loop that reads and rewrites
its own source, and a certificate that travels as data and re-verifies.

## Run the explanation / abstraction experiment

```
cd /research/dlm_v0.0030
PYTHONPATH=. python experiments/explain/run.py           # learned theory + lemma library
PYTHONPATH=. python experiments/explain/run.py --quick   # 24-node smoke run
```

**A · a learned theory.** The selfsup loop grows a composition theory (`t1 =
distance 2`, `t2 = t1∘t1`, …); `certify_from_tasks` then witnesses every clause
from its kernel-computed marginal contribution (each of the four clauses gets 20
train witnesses), and a held goal `t4(n0,n16)` is answered with a re-checkable
proof of 31 steps over all four clauses, with a counterfactual confirming each
used clause is load-bearing and a minimal proof that is smaller and still sound.

**B · an exact compression.** A lemma library `{cdirect, crec, ctwo, cthree}`
contains two genuinely derivable lemmas. Exact compression drops exactly them:

| quantity | before | after |
| --- | --- | --- |
| clauses | 4 | 2 (`cdirect`, `crec`) |
| description length | 16 | 7 |
| review budget | 17 | 8 |
| held coverage (distance-3 `anc`) | 5/5 | 5/5 |
| kernel closure | unchanged (verified) | |

Control: of all **6** ways to remove the same *number* of clauses, only **1**
leaves the closure unchanged — and it is exactly the subset compression found.
Honest reading: this is **not** a proof of logical equivalence in all models and
not new reasoning power; it is a behaviour-preserving reduction *on the given KB*,
decided entirely by the kernel. The value is a smaller thing to trust: fewer
clauses, a named module, and a proof that still re-checks.

## Run the execution-control experiment

```
cd /research/dlm_v0.0030
PYTHONPATH=. python experiments/execution/run.py           # 64-node chain, budget 400
PYTHONPATH=. python experiments/execution/run.py --quick   # smoke run
```

The v0.0024 composition task, with one **over-specific decoy** injected per
predicate: the correct body plus the unsatisfiable literal `e(z,z)`. The decoy is
*sound* (it derives nothing false) but can never fire, so it is pure wasted
budget. The induced clause and the decoy carry equal weight, and the decoy sorts
first by name, so the frozen order tries every decoy before the real clause.

| arm | held coverage | clause attempts | false asserts |
| --- | --- | --- | --- |
| frozen (no feedback) | 0.755 | 1084 | 0 |
| **feedback** | **1.000** | **832** | 0 |
| scramble (credit swapped) | 0.755 | 1084 | 0 |
| random order (5 seeds) | 0.918 | 995 | 0 |

Budget sweep (frozen → feedback): 200: 0.633 → 0.857 · 400: 0.755 → **1.000** ·
800: 0.898 → **1.000** · 2000: 1.000 → 1.000. A readable trace of one execution:

```
OK zcorrect <- (t1 n0 n2)
OK zcorrect <- (t1 n3 n5)
```

Honest reading: this is a **bounded-resource** gain, not a new correctness. At a
large budget the gap closes (both arms prove everything) — feedback just spends
832 attempts where frozen spends 2860. The scrambled-credit arm ties the frozen
floor (mislearned order keeps the decoys first), random order sits in between,
and on a clean run with no decoys feedback changes nothing (it cannot hurt). So
the claim is narrow and exact: **experience lets the learned order choose what to
run under a budget, while the kernel still decides what is true.**

## Run the self-supervised loop experiment

```
cd /research/dlm_v0.0030
PYTHONPATH=. python experiments/selfsup/run.py           # 80-node chain, 5 rounds
PYTHONPATH=. python experiments/selfsup/run.py --quick   # 40-node smoke run
```

A controlled, kernel-labelled program-composition task: a chain `e(n0,n1), …` is
the only base fact, and round `r` asks for `t_r` = pairs at distance `2**r`. One
induction pass may use body length ≤ 2, so it can express distance 2 but not
4…32; the loop **composes** verified clauses (`t1(x,y):-e(x,z),e(z,y)`,
`t2(x,y):-t1(x,z),t1(z,y)`, …). Zero human labels.

| arm | held-out coverage | false asserts | params |
| --- | --- | --- | --- |
| `learn` | **1.000** | **0** | 5 |
| oracle law (ceiling) | 1.000 | 0 | 5 |
| `no_promote` (no loop) | 0.000 | 0 | 0 |
| `scramble` (misaligned reward) | 0.000 | 0 | 0 |
| `random` (reward-blind) | 0.000 | 0 | 0 |
| `reward_hacking` (gate off) | 0.275 | **152** | 5 |

The loop writes a program it could not write in one shot:

```
(theory selfsup
  (clause lgg_t1_0 +1.0 (t1 ?G0 ?G1) (e  ?G0 ?E0) (e  ?E0 ?G1))
  (clause lgg_t2_0 +1.0 (t2 ?G0 ?G1) (t1 ?G0 ?E0) (t1 ?E0 ?G1))
  ...)
```

Honest reading: on this controlled benchmark the loop generalises perfectly and
the controls stay at the floor, which shows the *mechanism* (promote only
verified programs) is what carries the gain. It is expert iteration, not policy
gradient, and it does **not** invent predicates outside the given vocabulary —
the next work is exploration for genuinely new programs.

## Run the random-web dual-ability experiment

```
cd /research/dlm_v0.0030
PYTHONPATH=. python -m experiments.webloop.run --offline          # uses experiments/webloop/cache
PYTHONPATH=. python -m experiments.webloop.run --quick            # fast smoke test
PYTHONPATH=. python -m experiments.webloop.run --online --docs 120 --seed 3   # fetch more
```

Per-ability wrappers (offline by default, timestamped report in `reports/`):

```
cd /research/dlm_v0.0030/experiments/webloop
./A_deduction.sh --quick          # ability A: induce the subclass law
./B_conversation.sh --quick       # ability B: sentence <-> relation
./A_deduction.sh --online --docs 120 --seed 3
```

One pipeline, one label source (the kernel), **no human labels**:

```
random Wikipedia article -> Wikidata claims + P279 hierarchy + prose
      |                                       |
      | (A) deduction  -> kernel-derived pairs -> induce the law
      | (B) conversation -> sentence <-> relation (IR reader / realizer)
      v                                       v
held-out entities  <---- generalisation ----  kernel gate (abstain, never guess)
```

Offline cache (`n=60, seed=1`): 60 docs / 139 web facts / 962 hierarchy edges /
132 sentences. Entity-level folds, kernel = only label source.

**(A) deduction.** The transitivity law is never given. From ground facts plus
the kernel's own derived pairs the learner rediscovers it, verbatim:

```
(rule lgg_subclass_of_1 (subclass_of ?G0 ?G1) (subclass_of ?G0 ?E0) (subclass_of ?E0 ?G1))
```

| arm | held-out recovery |
| --- | --- |
| facts only (floor) | 0.060 |
| **law induced from kernel labels** | **1.000** |
| oracle law (ceiling) | 1.000 |
| shuffled labels (control) | 0.060 |

**0** false derivations: a fabricated clause could never be *asserted* — weights
never reach the kernel.

**(B) conversation.** Sentence ↔ relation on 45 aligned examples: untrained 0.044 /
surface 0.044 / scrambled 0.111 / **IR reader 0.378** / majority 0.444. Cue
uablation 0.289, realizer round-trip@3 0.200, invented-predicate control
(learned 0.378 vs untrained 0.044) confirms the harness has signal. Honest
reading: on this small corpus the reader is still **below the majority baseline**
and cue leakage remains — the deduction side generalises cleanly, the language
side does not yet.

**Unexpected behaviour.** The `--json` report keeps the invented rules verbatim,
the raw web graph's contradictions (4 two-cycles, 7 self-loops), kernel abstention
on an unprovable atom, and a deduction→sentence→deduction compositional
round-trip (1.000): an atom the *deduction* side derived is verbalised and read
back as the same relation.

## Run the IO boundary demo

```
cd /research/dlm_v0.0030
PYTHONPATH=. python -m experiments.io_demo.run
```

It decodes one text file, one CSV dataset, a PNG and a WAV; builds a KB from the
atoms; proves a rule; and renders the closure back to natural language and to
CSV/JSON/DLM forms.

## Run the tests

```
cd /research/dlm_v0.0030
./test.sh           # or: PYTHONPATH=. python -m pytest -q
```

217 tests (192 through v0.0029, plus 25 for `dlm/explain.py`).

## What was removed (and why)

v0.0017 had ~2 650 lines and seven parallel/duplicate stacks — evidence that the
fusion had not been done. v0.0018 fused them into **~1 412 lines**; v0.0019 then
slimmed the *trusted substrate* to exactly what the core needs (**~1 315 lines**):

* the general negative-literal side table (`Literal`, `holds`, KB `add_negation` /
  `is_negated` / `negations` / `remove_negation`, the `not` form bridge) is gone:
  the Horn engine is positive and the fused core never used negation;
* the stranded bulk-certificate API (`derivations`, `prove_from_support`) and the
  unused `dump_all` / `_match` indirection are removed; `prove` now inlines the
  support lookup it needs.

v0.0018's fusion (kept): `model_*` / `WeightedRule` / `Theory` collapse into
`Clause` + `Theory`; two feature mechanisms collapse into `Theory.matched`; the
proposer registry and judge stack collapse into `solve`; the vestigial
schema/frame/state grounder/retriever seams are gone; the two experiments merge
into one `run_experiment`.

v0.0020 adds back the *language* side, but not the old stacks: the v0.0014
`nlssl.py` / `reader.py` / `grammar.py` / `selfsup.py` / `ssl_objectives.py`
(≈1 800 lines of parallel readers, grammars, scorers and objectives) are replaced
by **one** IR-SSL module that unifies reading and realizing on a single explicit
intermediate representation. The trusted core is unchanged.

v0.0021 adds the IO boundary (`dlm/io.py`) as another *untrusted* layer, again
without touching the core — the fused two-file substrate and core are unchanged
since v0.0018.

v0.0023 makes the IR a **symbol tree**. `dlm/ssl.py` gains `ir_form` / `is_ir` /
`ir_get` (a head-addressed, extensible `(ir ...)` grammar), a generic `tree_features`
walk, `reader_tree_features`, and `aligned_tree_examples`; the `Frame` dataclass
becomes a thin *view* (`ir_from_form`) and `frame_to_form`/`frame_from_form`
delegate to the tree. The trusted core is untouched except its version banner —
all new code is untrusted. The experiment (`experiments/ir_tree/`) shows the
mechanism works but a naive structural walk does not beat the hand abstraction.

All removed code is preserved in the earlier snapshots (`dlm_v0.0017` and before).

v0.0024 adds the **self-supervised loop** (`dlm/selfsup.py`) as a third *untrusted*
layer: the missing piece was never the reward (the kernel verdict already was
one) but the *loop* that promotes only verified programs back into the theory.
It fuses `induce_clauses` (propose) + `closure` (verify/reward) + `learn`
(reweight) + `Theory` (the grown program) into expert iteration over Lisp-like
clauses, with the `false_assert == 0` gate as a hard constraint. The controlled
composition experiment shows the loop composes a program single-pass induction
cannot, while four controls stay at the floor and a gate-off arm fabricates 152
false facts — evidence that the gate, not the loop, is what keeps it sound. The
trusted core stays byte-identical except its version banner.

v0.0025 tried the other half of a brain — a learned 3D topographic lattice
(`dlm/brain.py`, a Kohonen SOM) that *placed* IR trees so similar content landed
near similar content, with the placement itself stored as one S-expr form. It
worked mechanically, but the code it placed was a **hash**: a lattice cell was an
opaque prototype with no named coordinates, so the model could neither read the
cell nor recover the tree that landed there.

v0.0026 keeps the placement goal and fixes the representation, replacing
`dlm/brain.py` with `dlm/vector.py`: an IR tree becomes a **grounded symbolic
vector** whose coordinates are named role+token symbols (`rel[0]=born`) drawn
from the same vocabulary `tree_features` exposes, with an exact inverse
(`tree_vector`/`vector_tree`), a fixed named `Basis` for dense consumers, and the
`bundle`/`restrict` algebra for composing trees later. No hashing, no lost order,
no opaque dimensions. All new code is untrusted; the trusted two-file core is
unchanged except its version banner. The retired `dlm/brain.py` and its
experiment are preserved in the `dlm_v0.0025` snapshot.

v0.0027 adds **execution control** (`dlm/execute.py`) as the fifth *untrusted*
layer. The v0.0024 loop learned rules but its order was epiphenomenal: `closure`
is complete and weights never reach the kernel, so a good order could only
reorder a candidate list. The new module gives the order real leverage — a
bounded backward-chaining executor, a readable per-attempt trace, per-clause
hit/waste credit, and a loop that feeds that credit back into the weights. The
experiment injects sound-but-unsatisfiable decoys that tie the induced clause and
sort first, so the frozen order wastes its budget on them; feedback pushes the
firing clause above them and raises held-out coverage under the same budget
(0.755 → 1.000), while scrambled credit ties the floor and a clean run is
unaffected. The gain is bounded-resource only (at a large budget the gap closes),
which is exactly the honest claim: **experience shapes what the model runs, the
kernel still decides what is true.** Two findings worth keeping: (i) the fused
perceptron's `matched` view is too coarse for credit assignment — a general clause
subsumes every over-specific rule beneath it, so a pair-based update smears the
decoy's waste onto the winner, which forced exact per-step credit; and (ii)
backward chaining needs memoisation of proved ground goals, or deep composition
blows the budget exponentially. The trusted two-file core is unchanged except its
version banner; all new code is untrusted and imports `dlm` one way.

v0.0028 adds **goal-conditioned control** (`dlm/control.py`) as the sixth
*untrusted* layer. v0.0027 gave the order control over execution, but the order was
still a single global weight per clause, which cannot route — it cannot prefer a
clause for one goal and penalise it for another. The new layer learns
`score(goal, clause)` as a linear model over **context features**: the clause/goal
shape plus a one-step lookahead (`sup:<pred>` / `unsup:<pred>` — is the body
literal fact-backed once the head is matched to the goal?). It is fit from the
same exact per-step trace credit v0.0027 introduced (`train_control` +
`examples_from_execution`), and an `EpisodicMemory` adds a `memo:` feature. The
experiment is a routing task where two clauses share the goal predicate and the
correct one depends on the goal — so *no* global order is optimal: the global and
untrained arms sit at coverage 0.74–0.79 with ~0.5 routing accuracy, the learned
control reaches 1.000 coverage, 1.000 routing accuracy and the oracle ceiling, and
a random order is worse. The episodic-memory demo transfers a winner to new
constants (spent 38 → 19, one attempt per goal). The gain is bounded-resource, not
new correctness: the scorer only *orders* clause attempts (a small additive
`scorer=` seam in `dlm/execute.py`), the executor still memoises proved ground
goals, and `check_sound` re-checks every proof against `closure`. Two honest
limits: episodic memory keyed by a constant-free signature transfers only within
one predicate, and open-vocabulary **invention** is a proposer concern deferred to
v0.0029. The trusted two-file core is unchanged except its version banner; all new
code is untrusted and imports `dlm` one way.

v0.0029 adds **the Lisp seam** (`dlm/lisp.py`) as the seventh *untrusted* layer.
The S-expr substrate was shared by every layer, but there was no place where a form
was *evaluated*, no code-pattern matcher, no macro, no readable proof, and
perception (the IR tree) and reasoning (the kernel) were disjoint dialects. The new
layer adds, in one place: (1) `eval_form`, a single evaluator that dispatches on the
head symbol and **abstains** on an unknown head; (2) a code algebra with
metavariables and a wildcard, `match_form`/`subst_form`, that unifies nested tuples;
(3) `quote`/`quasiquote` and `DefMacro`/`macroexpand` — code that writes code; (4)
`theory_source`/`source_theory`/`source_roundtrip` and `run_source_loop`, so the
self-supervised loop re-enters through its own source and the re-read theory must
equal the grown one; (5) `proof_to_form`/`form_to_proof`/`verify_form`, making a
certificate a term that emits, re-reads and re-verifies (a tampered proof fails);
and (6) `tree_atoms`/`tree_kb`/`query_tree`, reifying an IR tree into ground facts
the kernel can prove about. Only `query` reaches the kernel, and only through
`prove`. The kernel stays function-free; the code algebra lives above it and the
two meet only at `form_to_atom`/`tree_atoms`. The experiment's eight checks pass
deterministically. The trusted two-file core is unchanged except its version
banner; all new code is untrusted and imports `dlm` one way.

v0.0030 adds **the explanation / abstraction layer** (`dlm/explain.py`) as the
eighth *untrusted* layer — the second half of "extreme interpretability". v0.0029
made the substrate read and write itself, but a grown theory was still only
inspectable one clause at a time, and a million readable clauses are as opaque as
a black box. The new layer adds: (1) an explicit **description length** and
**review budget** (`profile`, `TheoryProfile`); (2) **proof-carrying hypotheses**
(`certify`, `certify_from_tasks`) — a `Provenance` registry records *why* each
learned clause is believed, with kernel-computed witnesses, its round and parent,
so a belief answers "why?" with a term, not a scalar; (3) **abstraction**
(`abstract_theory`, `summarize`) grouping clauses into named modules so a large KB
is reviewed by hierarchy; (4) **exact compression** (`compress`, `redundant`,
`closure_preserved`) that drops a clause only after re-computing the kernel
closure without it and finding it unchanged — decided operationally because the
structural `subsumes` proxy is *not* logical strength; and (5) **explanations**
(`explain`, `counterfactual`, `minimal_explanation`, `verify_explanation`) — a goal
answered with its re-checkable proof, the clauses it used, their provenance, and
which clause is load-bearing. The experiment grows a composition theory with the
selfsup loop, witnesses all four clauses (20 witnesses each) and explains a
31-step held proof, then compresses a lemma library from 4 clauses / DL 16 to the
minimal `{cdirect, crec}` / DL 7 with the closure verified unchanged and held
coverage intact, while a control shows only **1 of 6** random removals of the same
size preserves the closure (exactly the subset compression found). All ten checks
pass deterministically (JSON byte-identical across runs). Honest limit:
compression is behaviour-preserving *on the given KB*, not a proof of logical
equivalence in all models, and the layer adds no new reasoning power — it is
read-only over the core, every verdict comes from the kernel (`closure` /
`verify`), and the kernel stays function-free. The trusted two-file core is
unchanged except its version banner; all new code is untrusted and imports `dlm`
one way.
