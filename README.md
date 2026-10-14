# DLM v0.0038 — Ground + Experience + an open entity universe

A **deductive logic model**: knowledge lives in an external knowledge base and
answers come from *proof*, abstaining when it cannot prove. This is a **fresh,
minimal rebuild** (not a continuation of the v0.0036/37 layer stack) around a
single question:

> **What is the learning structure for deduction?**

The LLM answer is *attention × continuous space × statistical signal*. This
version tests a different answer:

> **Ground (immutable, non-referential axioms) + Experience (conservative learned
> rules) + an open entity universe.** Lisp is the symbolic *medium*; the kernel is
> the *judge*.

- **`dlm/__init__.py`** (~130 lines) — the **trusted kernel**: function-free Horn
  substrate (`Const`/`Var`/`Term`/`Atom`/`Rule`), `closure` (the least fixpoint =
  truth), `entails`, `unify`, `description_length`.
- **`dlm/lisp.py`** (~130 lines) — **untrusted** symbolic medium: reads/writes
  s-expressions, matches pronominal rules (`?x`, `_`), evaluates forms. Only
  `query` reads truth, and only through the kernel.
- **`dlm/ground.py`** (~180 lines) — **untrusted** learner: `Ground`,
  `Experience`, and `learn` (greedy covering with a kernel soundness gate).

```bash
./test.sh          # 14 passed
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

Lisp does three jobs; the kernel stays the only judge.

```lisp
(rule (ancestor ?x ?y) (parent ?x ?y))     ; represent a pronominal ground axiom
(query (ancestor n0 n1))                    ; read truth (kernel closure only)
```

`match_form`/`subst_form` operationalize the pronouns: `(parent ?x ?y)` matched
against `(parent n0 n1)` yields `(ancestor n0 n1)`, and against a **never-seen**
`(parent n7 n8)` yields `(ancestor n7 n8)`.

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

## 6. Honest status

The learning structure now *works as a proposer*: it generalizes, accumulates, and
transfers to unseen referents. It is **not yet a sound judge**: the gate checks a
finite negative sample, so it can admit an empirically-sound, universally-false
rule. The trust invariant says it should **abstain**, not assert.

Next direction (in order of preference):

1. **Mode/type declarations** in `Ground` (standard ILP) so the proposer's
   literal universe is restricted *by construction* — the seed-3 rule becomes
   unrepresentable.
2. **Structural soundness** (closure-subset / subsumption) instead of sampled
   negatives.
3. Treat `Experience` rules as **unverified hypotheses**, re-checked by the
   kernel at query time.

## 7. Layout

```
dlm/
  __init__.py      trusted kernel: Horn substrate + closure (truth)
  lisp.py          untrusted symbolic medium (pronouns, forms, query)
  ground.py        untrusted Ground / Experience / learn
experiments/
  ground/          one generalization transfers (synthetic)
  web/             real Wikipedia/Wikidata class hierarchies
  stream/          multi-relation accumulation, round-by-round open-universe curve
tests/             14 tests (network-free)
test.sh            PYTHONPATH=. python -m pytest -q
```

## 8. Version

`0.0.38` — fresh minimal rebuild. Licensed under Apache-2.0 (see `LICENSE`).
Design notes: [`COMPOSITION.md`](COMPOSITION.md).