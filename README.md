# DLM v0.0075: Maru graph reasoning layer

0075 implements a graph execution layer in Maru. It takes design inspiration
from NeuroSymbolic-IR's typed operations/provenance/traces and GraphReasoning's
relation-path exploration. Neither project is imported or required at runtime.
No LLM, tokenizer, embedding, PyTorch, GPU, NetworkX or Z3 dependency is added.

## Run

```sh
cd /research/dlm_v0.0075
./scripts/run.sh graph                 # diamond paths, proof/retraction tests, learned transfer
./scripts/run.sh test                  # all 100 Maru assertions
./scripts/graph.sh                     # persistent diamond fixture, starts empty
./scripts/graph.sh my-actions.sexp 100  # apply a data-only action batch
bash tests/graph-store-tests.sh        # restart/retraction/forged snapshot tests
python3 tests/graph-differential.py    # optional 20-case independent Python0066 oracle
```

`STORE=/path` selects an isolated graph store. `graph.sh` uses an exclusive lock,
reads data without eval, verifies the previous snapshot by event replay, and
atomically replaces `state.sexp` only after every action succeeds. Dated snapshots
retain previous full states. Empty action list `()` verifies/resumes without a
model update. Repeating the fixture does not add new observations; it does append
idempotent transition events. Budgets count fixpoint passes, not primitive work.

## Implemented

- One immutable graph value carries interned entity/predicate/claim nodes,
  observation/rule records, active claim ids, supports, indexes and event history.
- Equal claims share a node while multiple observation sources and derivations
  retain separate supports. Supports reference premise ids rather than copying
  proof trees. Predicate arity is checked across facts and rules.
- Predicate and bound-argument indexes drive rule-body joins. The function-free
  Horn engine computes a synchronous least fixed point with explicit
  `complete` / `incomplete` results.
- Directed binary path enumeration uses bounded BFS and retains alternative
  paths. A path is a search candidate, NOT permission to compose relations.
- Queries distinguish `entailed`, `contradicted`, `conflict`, `unknown`,
  `incomplete`. Positive answers carry a finite witness checked by the existing
  membership-checking Horn kernel. Graph supports may be cyclic; proof witnesses
  must be acyclic. Unsupported cycles disappear when their seed is withdrawn.
- Observation/rule retraction rebuilds closure and supports from active seeds.
  Surviving alternatives are preserved; catalog ids remain as inactive entries.
- Learned rule transitions reject incomplete evaluation or explicit
  counterevidence. This gate is applied during replay as well as normal updates.
  Passing finite evidence is NOT a proof of a universally true learned rule.
- 0073's two learned composition rules execute through the new graph engine on
  unseen entity names and extra joins: 14/14 goals, zero explicit violations.
  Held-out target labels do not enter those graphs as premises.

## Representation and APIs

Implementation: `src/dlm/graph.l` and `src/dlm/graph-query.l`.

```lisp
;; Provenance has a source id, optional span, and an admission category.
(observation ab positive (atom edge (a b))
  (provenance fixture () observed))

(rule-record base
  (rule (atom reach ((var x) (var y)))
        ((atom edge ((var x) (var y)))))
  (provenance fixture () given))
```

Core operations:

```lisp
(gr-new)
(gr-apply graph '(observe OBSERVATION) 100)
(gr-apply graph '(rule RULE-RECORD) 100)
(gr-apply graph '(retract-observation ab) 100)
(gr-apply graph '(retract-rule base) 100)
(gr-apply graph '(recompute closure) 100)
(gr-query graph '(atom reach (a d)))
(gr-paths graph 'a 'd '(edge) 4 100 10)
(gr-supports-for graph '(atom reach (a d)))
(gr-verify-state graph)
```

`OBSERVATION` and `RULE-RECORD` above stand for complete data records; the fixture
is `experiments/graph/actions.sexp`. Invalid actions return `(graph-error ...)`
without modifying the input graph. `gr-admit-rule` offers a stricter consistent
finite-evidence gate for proposed rules, including supplied rules.

An `observed` record means a trusted caller has admitted a scoped observation.
It is not a cryptographic source certificate or a claim of world truth. Acquired
web documents cannot automatically become observations. A caller that can forge
`observed` records remains inside the trust boundary. New contradictory
observations are retained and exposed as conflicts, not silently resolved by
confidence scores; existing rules are not automatically deleted on conflict.
`given` rules are explicit assumptions, not newly learned truths.

## Compared with the reference projects

- NeuroSymbolic-IR: borrowed separation of typed records, source metadata and
  reasoning traces, not its confidence-preferred conflict deletion or built-in
  domain property assumptions. This is not full compatibility with its JSON ISA.
- GraphReasoning: borrowed graph/path exploration, not embedding-based node
  identity, LLM-generated hypotheses or unconditional transitive interpretation.
- Graph topology, source observations and validated Horn derivations remain
  distinct. No similarity score becomes an equality or proof.

## Persistence, costs and limitations

IDs are stable within one event history, not content hashes or globally canonical
ids across independently ordered histories. Serialization remains S-expression;
the runtime representation is an explicit id-referenced graph, not recursive
expression duplication. Lookup/index structures are still immutable lists, not
hash tables, and can be expensive. Index filtering is not a demonstrated speedup.

The diamond example takes 3 passes, 25 indexed match attempts, and keeps two
supports for reach(a,d). Metrics omit list scans, index rebuilds, proof checking,
allocation and snapshot replay costs; they are not total operation counts.
Retraction currently does full recomputation rather than a selective incremental
truth-maintenance algorithm. Proof extraction can expand shared witnesses.

Each graph snapshot retains the full event log. Replay grows with history; no
compact journal/checkpoint or fsync crash durability is claimed. Validation is
bounded shape checking, not hostile-code or arbitrary cyclic-memory safety.

Graph75 is versioned separately from symbolic-state73 and web-state74. A unified
model-wide journal/migration is not implemented. Raw-text semantic extraction,
category/predicate discovery, learned graph search ordering, structural analogy
learning, arbitrary negation, general compound terms and MLIR integration remain
future work. The representation has explicit types, references, pure transitions
and provenance boundaries suitable for a later DLM dialect, but no MLIR dialect
or LLVM lowering is claimed in this release.

## Verification record

Active source-built release: `20261019T071252Z-31029`.

- 100 Maru/DLM assertions pass; 6 local-HTTP acquisition tests pass.
- 20 seeded graph closures match the independent Python0066 oracle; every
  graph conclusion also yields a kernel-checked witness.
- Existing 20 Horn differential cases pass.
- Graph persistence checks restart, retraction, string/escape roundtrip, invalid
  action atomicity and forged snapshot rejection. Serialization uses `dump`, not
  human-readable `print`; serialized candidates are replay-verified before commit.
- Candidate -> next -> third images have identical LLVM and stripped binaries.
- Source-free symbolic runtime and inherited experience store checks pass.

## Preserved features

```sh
./scripts/run.sh symbolic
./scripts/selfssl.sh 3
./scripts/web.sh --url https://raw.githubusercontent.com/python/cpython/main/README.rst
python3 -m unittest discover -s tests -p test_web.py -v
bash tests/store-tests.sh
bash tests/runtime-tests.sh
python3 tests/differential.py
```

Python stdlib is required only for web acquisition and optional developer oracles.
Fetched documents remain unresolved; no automatic raw-text-to-graph admission is
introduced. Compiler lifecycle gates still check three generations; no Maru
compiler/evaluator semantics changed in 0075.

Maru license/provenance: `LICENSE.maru` / `maru.lock`. No source from
NeuroSymbolic-IR or GraphReasoning was copied into the implementation. DLM
publication licensing remains to be confirmed.
