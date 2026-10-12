# DLM v0.0024 — the fused two-file core + tree-native IR + verifiable-reward self-supervision + IO boundary

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

## Layout

| File | Role |
| --- | --- |
| `dlm/__init__.py` | **trusted substrate** + public surface (logic, sexp, unify, kb, kernel, engine) |
| `dlm/deductive.py` | **the fused core**: `Clause`, `Theory`, `subsumes`, induction, `learn`, `solve` |
| `dlm/ssl.py` | **untrusted IR-SSL language layer** (tree-native IR, features, reader/realizer, forms) |
| `dlm/io.py` | **untrusted data boundary** (codecs, `Block`, NL/structured output) |
| `dlm/selfsup.py` | **untrusted verifiable-reward self-supervised loop** (propose → kernel verify → promote) |
| `experiments/webssl/` | the web IR-SSL experiment (`web.py`, `bridge.py`, `run.py`) |
| `experiments/webloop/` | random-web **dual-ability** loop (deduction + conversation), `run.py` |
| `experiments/ir_tree/` | tree-as-IR reader comparison, `run.py` |
| `experiments/selfsup/` | verifiable-reward self-supervised loop (program composition), `run.py` |
| `experiments/io_demo/` | heterogeneous-in → kernel → NL/structured-out demo |

The fused-core API is re-exported from `dlm`, so `from dlm import …` is unchanged.
The core imports only the trusted substrate; `dlm.ssl`, `dlm.io` and
`dlm.selfsup` import `dlm` and never the other way round.

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
cd /research/dlm_v0.0024
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
cd /research/dlm_v0.0024
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

## Run the self-supervised loop experiment

```
cd /research/dlm_v0.0024
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
cd /research/dlm_v0.0024
PYTHONPATH=. python -m experiments.webloop.run --offline          # uses experiments/webloop/cache
PYTHONPATH=. python -m experiments.webloop.run --quick            # fast smoke test
PYTHONPATH=. python -m experiments.webloop.run --online --docs 120 --seed 3   # fetch more
```

Per-ability wrappers (offline by default, timestamped report in `reports/`):

```
cd /research/dlm_v0.0024/experiments/webloop
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
cd /research/dlm_v0.0024
PYTHONPATH=. python -m experiments.io_demo.run
```

It decodes one text file, one CSV dataset, a PNG and a WAV; builds a KB from the
atoms; proves a rule; and renders the closure back to natural language and to
CSV/JSON/DLM forms.

## Run the tests

```
cd /research/dlm_v0.0024
./test.sh           # or: PYTHONPATH=. python -m pytest -q
```

133 tests.

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