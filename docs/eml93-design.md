# EML93: data-led formation over an EML foundation

## Research position

The requested experiment treats EML as the **foundation**, not a calculator
plug-in. It tests whether numeric data can select a persistent internal EML
organization that solves new cases and becomes material for further formation.
It is not a minimal world-axiom algorithm, a theorem of latent axioms, or a claim
that finite observations deductively imply a universal law. Candidate selection
from finite observations is empirical model identification; expansion and
role-preserving program checks are deductive structural checks.

This version instantiates the earlier working proposal as follows:

- I93: supplied numeric input/output columns and predefined sign-cell roles;
  no automatic web/free-text semantic extraction.
- B93: learned partial-function definitions whose bodies expand to EML trees.
- G93: prefix dependencies and active (source,version,cell)→plan connections.
- U93: bounded discrete construction, empirical matching, structural/numeric
  admission and source-driven replacement of active applicability maps.

A person need not supply the desired basis body. They may supply additional
observations, choose a branch convention, inspect partial results, or replace a
source version. These interventions are distinguishable from automatic search.

## Native components

- `src/dlm/eml93-numeric.l`: bounded integer implementation of complex EML.
- `eml93-ir.l`: grammar, expansion, library/core validation and context cells.
- `eml93-execution.l`: recursive worker, primitive checker and core-only inference.
- `eml93-formation.l`: candidate grammar, search, source interpretation and gate.
- `eml93-session.l`: immutable transitions, replay and checkpointed publication.

No compiler/runtime changes. No Python numerical service is called by Maru.

## Representation

```text
one93
(x93 VARIABLE-ID)
(eml93 LEFT RIGHT)
(call93 PREFIX-ID (ARG ...))

(basis93 ID ARITY BODY PRIMITIVE-EXPANSION)
(episode93 ID VERSION ARITY ROWS)
(row93 ID ((z93 RE IM) ...) (z93 RE IM))
(view93 SOURCE VERSION ARITY SIGN-CELL ACTIVE-PLAN)

(eml-state93 1 BRANCH EPISODES LIBRARY VIEWS EVENTS EPOCH)
(eml-core93 1 BRANCH LIBRARY VIEWS EPOCH)
(eml-session93 1 BRANCH CORE EVENTS)
```

Variables are contiguous0..arity-1. Every learned body must retain every role
syntactically, and calls bind ordered explicit argument terms. This is not a
proof that every argument has an independent causal influence: cancellation can
make an input irrelevant semantically. No silent role projection is admitted.

Library IDs are consecutive; calls reference a validated prefix only. An
independently validated EML-only expansion accompanies each definition. Expanded
node construction is capped *during substitution*, not only after allocation.
The core holds no training target values, rows or search history. Its source
pointers are not cryptographic proofs of real-web provenance.

## Numeric semantics

The concrete primitive approximates E(a,b)=exp(a)-log(b). Components are integer
multiples of10^-6. Squared-modulus logs, normalized real-log series, bounded exp
series, atan and sin/cos series implement the complex primitive on CPU. Taking
log of the squared modulus avoids rounding a tiny modulus to a whole grid unit
before log; tiny and near-component-limit complex inputs are regression-tested. Exact
encoded quadrantal phases avoid spurious negative-axis sides from rounded sin(pi).

- `principal93`: negative-axis log has imaginary part+pi.
- `lower93`: negative-axis log has imaginary part-pi.
- pi is encoded3141593; half/quadrant constants are fixed approximations.
- Input/output component absolute values≤10^9 units (1000).
- exp real-part absolute value≤6; log(0) is undefined.
- Overflow/domain failure produces `undefined93`, propagated as unknown in queries.

There is **no uniform error theorem** for arbitrary nested trees. Independent
oracles check the finite workloads. Fixed-point evaluation can accumulate error
or cross a branch boundary. Matching tolerance is max component difference1000
units (0.001); heldout checks use complex absolute error≤0.002. These are
experimental tolerances, not proof tolerances for universal identities.

Term expansion equality preserves exact syntactic computation under this VM.
It does not prove the fixed-point VM equals exact complex EML everywhere. Nor
may pure real identities be applied without their domain/branch obligations.

## Search and formation

Only1 and input variables are initial terminals. At each exact constructor cost,
search adds EML nodes and calls to learned prefix definitions. Each call costs
one constructor plus its argument constructors; its retained body is additional
model structure, not free computation. At equal cost, unary learned constructors
precede raw EML. Traversal is deterministic; input order may affect which cell
is learned first.

The experiment allows cost1..3, at most5000 candidates per cost level, and at
most200000 worker node visits. Pool construction, expansion/validation, numeric
series instructions and independent checking are **not fully metered by fuel**.
A truncated no-match returns unknown; a complete bounded-space no-match returns
`no-fit`, never a global impossibility result. A fit found in a complete earlier
cost level can be admitted even if a later pool level was truncated.

1. Observe numeric rows with distinct IDs and distinct full input tuples.
2. Partition by predefined sign cells. Each cell needs≥3 distinct inputs.
3. Reuse existing definitions that match **every** observation in a cell.
4. Otherwise enumerate programs and evaluate against observations; no target
   expression, named function template, gradients or teacher model is supplied.
5. Independently validate prefix expansion, complete prediction list, all rows,
   and the resulting active view map. A lying worker is rejected, not repaired.
6. Publish the new library and active map only after the gate/checkpoint succeeds.
7. New definitions participate in the next search grammar as well as inference.

These are empirical candidate-function/source correspondences. Three is an
experimental admission threshold, not a measure of logical truth or source trust.
Identical inputs cannot inflate support. There is no general ambiguity resolution
or noise model: an unresolved or contradicted cell is left unknown.

## Reorganization

The active organization is recomputed from current source versions, definitions,
and all observed rows of each cell using the primitive checker. A new basis
installs executable source bindings where the old model had residual obligations.
A newly observed cell can activate an existing basis; a counterexample withdraws
the affected binding. Definitions remain valid descriptions of their own EML
functions even when an empirical application ceases to fit.

This is not an equivalent rewrite of a complete world theory. The explicit
changes demonstrated are newly constructed function bodies, hierarchical
construction dependencies, and installed/withdrawn/extended applicability maps.

In the demo, B3 subtraction is not in the cost≤3 primitive-only search space,
but is found using learned B1/B2. B4 then uses learned B3. This is distinct from
reordering a fixed Basis91 query, although it is still a restricted kind of
program/function learning rather than general semantic reorganization.

## Inference and epistemic status

`e93-infer` validates the explicit core, selects a source and learned cell, runs
the active plan, and checks its value through an EML-only expansion path. It
never consults archived answers or invokes discovery. A worker omission or
wrong output is rejected; the checker does not fill it in.

```text
(answer93 complete VALUE empirical93 PLAN RUNTIME SCOPE)
(answer93 unknown REASON ...)
```

Complete means the program's numeric evaluation completed. `empirical93` is
retained even on a heldout success. The attached scope records source/version,
sign cell and branch. Uncovered source/cell, undefined arithmetic and exhausted
fuel do not become falsehood or global negatives.

The worker and checker share the numeric primitive, so they are not independent
implementations of complex analysis. Python `cmath` is an independent numeric
oracle in tests/experiments only. A core shape check establishes semantic
well-formedness, not learned-origin authentication; snapshot replay is stronger
history admission but still not cryptographic provenance.

## Persistence and bounds

Accepted events≤32, sources≤6, rows/source≤12, bases≤8, arity1..2, term validation
depth≤12, primitive expansion≤96 EML nodes, query fuel0..200000, input queries≤256.
The top-level corpus driver interprets typed data commands and rejects trailing
input; it never evals supplied text.

Snapshot admission reconstructs from branch and events, reruns formation, and
compares the complete core. Native locking, expected-file comparisons and atomic
rename checkpoint before live publication. Failed close keeps attachment/lock.
No automatic corruption repair, source authentication, power-loss/fsync guarantee
or full wall-clock metering is claimed. Replay can repeat substantial search.
Explicit frozen cores retain historical source contexts after live retraction.

## Experiment versus future work

The28 initial observations and heldout data are synthetic and noiseless; the four
reference functions and the curriculum were chosen by the experiment author.
They are visible in the Python oracle but never passed to native discovery.
This isolates whether EML-based formation works before claiming semantic web
learning. It does not establish unsupervised natural-language interpretation,
general rule induction, arbitrary predicate invention, global identifiability,
completeness, broad generalization, or superiority to neural models.

A later web experiment must keep actual sources/spans/meaning alternatives and
expose its extraction assumptions; the present numeric-input layout must not be
relabelled as an automatically learned interpretation of web documents.

Reference: Andrzej Odrzywołek, arXiv2603.21852v2, especially§2 bootstrap,
§4.1 branch issues,§4.2 expression grammar and§4.3 structural input choices.
Our candidate selection is discrete and non-gradient; the paper's Adam method
and its theorem/benchmarks are not reproduced here.
