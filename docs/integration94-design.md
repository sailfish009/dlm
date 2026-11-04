# 0.0094: one learned basis model, checked EML representations

## Architectural boundary

The central object remains `basis-state91` and its `execution-core91` projection.
There is **no integration94 model, state, learned library, numeric episode store,
or second checkpoint owner**. New experiment commands call the existing
`basis91` / `attention92` APIs. `eml93` remains a separately runnable historical
experiment; its learned numerical library and empirical source bindings are not
imported as logical theorems.

This revision deliberately changes inherited Basis91/Attention92 code. Preserving
predecessor directories is not the same as freezing every inherited module in the
successor. 0092/0093 are references and compatibility paths, not separate engines
whose results are concatenated and called integration.

The cumulative path is:

```text
source facts
 -> prior-basis-first interpretation (existing Basis91 pattern pool)
 -> Attention92 frozen-context execution and independent admission
 -> existing reading91 rows/plans with original witnesses
 -> existing support/candidate/proposal/admission rules
 -> same basis91 library, now with an executable EML body
 -> existing queries and subsequent interpretation/formation
```

What is integrated: Basis91 relational basis formation, Attention92 application
control/admission, and EML93's native EML arithmetic and expression vocabulary.
What is not integrated: EML93's separate empirical numeric learner; arbitrary
propositional/contracts/web semantics; general predicate/condition invention.
The result is a cumulative relational subsystem extension, not a claim that all
historical DLM APIs now have a single semantics or that latent axioms are solved.

## Representation and authority

Existing shapes remain unchanged:

```lisp
(basis91 ID PATTERN BODY)
(basis-state91 1 SIGNATURE EPISODES LIBRARY READINGS AUDIT EPOCH)
(execution-core91 SIGNATURE EPISODES LIBRARY VIEWS EPOCH)
```

`BODY` may be an ordinary leaf plan, or:

```lisp
(encoded91 eml94 BRANCH LEAF-PLAN (circuit94 NODES OUTPUT-REF))
```

The leaf plan contains the same typed `fact91` / prefix-only `call91` operators.
It is an explicit semantic interface, **not a pre-solved answer table or alternate
full-goal execution path**. Existing pattern expansion checks preserve every
role, repeated-variable constraint and primitive conjunct. Prefix checking rules
out self/forward/cyclic dependencies. EML nodes operate on these leaf predicates.

Nodes are `(eml93 LEFT-REF RIGHT-REF)`, topologically ordered; references are
`one93`, `(x93 SLOT)` and `(wire94 EARLIER-NODE)`. Runtime arithmetic nodes invoke
only native `e93-eml`, not hidden multiply/log/exp constructors or Python. The
compiler uses named mathematical helper functions to construct this EML-only
code, not to execute its arithmetic. Equal subexpressions share DAG wires.
Canonical compiler equality rejects dead/foreign/altered code. Exhaustive finite
certificates additionally check the whole bit-input domain for this machine
implementation and branch, not just selected examples. A certificate is cached
only after all cases complete, keyed by full canonical code/input count/branch;
there are at most six such keys. No source-result cache is shared across scopes.

Logical status remains **conservative definition**: these bodies abbreviate the
same positive conjunction, not an induced universally true world implication.
Encoding an existing basis does not add support or count as new knowledge.
It must not turn `empirical93` numerical fits into logical authority.

## Zero-safe Boolean encoding

A predicate's membership in a completely enumerated *finite selected fact view*
is encoded as false=1, true=2. Missing membership in that view is not a claim of
world-level falsity. A partial view can propose rows, but only the independent
full-source coverage gate can authorize them.

For n leaves, use their product. Possible codewords are `1,2,...,2^n` restricted
to powers of two. Accept only `2^n`. No zero-valued logarithm operand is required.
A code result must be within max-component 0.002 of an allowed codeword; all
other values, undefined arithmetic or spent fuel produce `unknown`, not false.
Leaf statuses are separate from their values: an unknown leaf never becomes 1.
Each completed prefix call returns a Boolean, re-encoded as exactly 1 or 2 for
its parent; raw approximate numeric values are not accumulated across basis
calls. Thus finite-domain gate checks compose through the checked prefix DAG.
This preserves a scoped Boolean computation, not a proof of a new world law.

The compiler uses:

\[
X(x)=E(x,1),\qquad L(x)=E(1,E(E(1,x),1)),
\]
\[
D(x,y)=E(L(x),X(y)),\qquad c=E(1,1),
\]
\[
A(u,v)=D(c,D(D(c,u),v)),\qquad M(a,b)=X(A(L(a),L(b))).
\]

On the admitted positive finite inputs, these correspond to exp, log, difference,
sum and product. They are **fixed compilation rules**, not newly discovered
functions, and are not used as unconditional identities on arbitrary complex
inputs. With up to 3 inputs, the running product is at most 8 and the logarithm
arguments used for addition stay in the safe range. The compiled circuits have
0/20/36 EML nodes for 1/2/3 leaves. Each ordinary learned basis in this version
still has two constructor leaves, even if it expands to three primitive facts.

Both `principal93` and `lower93` contexts are serialized and tested. This codec's
reachable logarithm operands are positive real, so these branches are expected
to agree. It does not solve the negative-axis discrepancy from 0093. Independent
`cmath` evaluation checks all 28 finite cases and operand domains. Numerical
approximation is explicit; no general complex identity/error theorem is claimed.

## Worker versus checker

The shared encoded worker:

1. Executes **one anchor leaf** with Attention92's existing primitive/basis worker.
2. Extends unbound role slots over the selected finite domain, preserving all
   pre-existing bindings and aliases. This is an over-approximate candidate set,
   not a solved full-goal join. Workspace is capped at 512.
3. Tests each leaf at each full binding against visible original facts; a prefix
   leaf executes its own stored body recursively, including legacy/EML mixtures.
4. Executes the EML circuit on the resulting 1/2 inputs; only accepted candidates
   become proposed rows. False candidates are counted and actually rejected by
   EML, rather than feeding a solved answer table through an all-ones decoration.
5. Retains native worker fuel, reads, attempts, call counts and called basis IDs.

Attention92 still independently checks full-source coverage and exact row sets
with the predecessor primitive evaluator. Wrong or omitted rows are rejected;
reference answers never fill them. Provisional scoped emptiness requires widening.

Basis91's regular query/run/infer path now performs the same independent full-row
check when its library contains encoded bodies. This closes the omission risk
that mere witness validation would leave for a new arithmetic backend. Non-EML
legacy paths remain unchanged. Checker fuel is deducted, no partial rows are
published, and encoded-worker failure never silently switches to a raw solver.
A controller may initially choose a primitive plan instead of a basis; that is
existing explicit plan selection, not repair of a failed EML worker.

Independence is limited: the new worker and old checker share typed source and
binding utilities, and the codec relies on EML93's numeric primitive. Separate
control paths are not a formal proof of the whole native implementation. Python
assignment enumeration and `cmath` provide separately implemented finite oracles.
The 6,144 graph checks cover 256 subsets of a selected 8-fact/two-node universe,
6 patterns, 2 native paths and 2 branches, not all possible bounded databases.

## Formation feedback and migration

New operations on the **existing API**:

```lisp
(basis91 'encode ID 'eml94 BRANCH)
(basis91 'proposal 'eml94 BRANCH)
(basis91 'learn 'eml94 BRANCH)
(basis91 'interpret-controlled EPISODE FUEL POLICY)
```

Ordinary no-argument `proposal`/`learn` and existing `interpret` remain compatible.

`encode91` replaces only the selected body's representation after validating the
whole same library. Pattern, ID, dependents, readings, witnesses and logical
basis count remain intact. The predecessor epoch continues to mean the number
of definitions, **not** a unique representation revision. The full core and audit
record the encoding change; frozen contexts retain their exact historical body.
Do not use scalar epoch alone as a representation hash/authentication token.

`interpret-controlled91` tries the same prior-basis-first data-led pattern pool
as ordinary interpretation, but uses Attention92 for actual execution. Each query
has an immutable model/source context. Only after *all* attempted patterns finish
and are independently checked does the event install readings in the existing
state. Failed policy, worker, budget or admission publishes no partial readings.
The actual committed plans become the constructor plans for existing formation.

`learn ... eml94` uses the **existing** candidate/support/scoring/rewrite/admission
algorithm. It encodes the chosen body before the same `learn91` commit. The
method does not add a second discovery algorithm or claim broader reach than the
logical representation control. New bodies may call previously learned bases;
old-style and encoded bases can coexist during incremental migration.

## Causal experiment and its limits

Four fixed families: chain, fork, common target, two-edge cycle. Initial data has
two applications of a 2-atom structure. Learn one ordinary basis, migrate it in
place, observe a later source with two applications of a 3-atom extension, run
controlled interpretation, then attempt one further formation step. Existing
prefix support makes that 3-atom pattern a two-constructor candidate.

Arms share source facts and the same formation algorithm/controller:

- `logical94`: ordinary bodies throughout, a strong meaning/formation control.
- `eml94`: migrate the first basis; subsequent bodies use the EML representation.
- `no-prefix94`: omit initial formation. The 3-atom structure is not a supported
  two-constructor candidate *at the same subsequent step*; a smaller basis can
  form instead. More later steps may recover it; this is not impossibility.
- `no-feedback94`: observe later data but withhold controlled interpretation.
  No later readings/support are installed and no second basis forms.
- `no-execution94`: disable the encoded Attention92 worker after migration.
  Later interpretation fails atomically instead of fabricating feedback. Some
  heldout queries can still complete if the existing controller initially
  selects primitive operators; the report counts actual complete/unknown cases.

This is evidence that representation, existing execution and later formation
are connected. Equal final answers in an ablation do not imply equal learned
organization: the raw relation engine could already solve these positive goals.
The work does **not** show EML-specific improvement in learning capability or
speed. The logical control is expected to learn the same definitions. EML circuit
shape is compiled, not freely searched or invented by the learner. Data drives
which roles/operators/prefix compositions become stored bases.

## Persistence, provenance and safety

No new persistence scheme: all updates use Basis91's existing expected-file
compare, native lock, `.next`/`.previous` staging, replay and full-core comparison.
Encoding and controlled-interpretation events replay through the same rules.
A checkpoint must succeed before publication; failed close retains ownership.
Attention92 snapshots keep the complete encoded model and command replay.
Well-formed pure cores are not cryptographically authenticated learned-origin
claims. No fsync/power-loss recovery is promised.

Retraction removes source-specific readings/witnesses, not conservative function
definitions. Re-observed sources get new versions and are evaluated afresh.
Old explicitly frozen contexts remain historical, not automatically revoked.
Original fact IDs, all variable roles and source versions remain in returned
witnesses; heldout query cores contain only new facts, the shared definitions and
no training answer rows. Queries do not mutate the learner.

All paths are CPU-native. No GPU, external model, API, gradients or network is
used. Python is an experiment/input/oracle harness only. The offline test runner
has a Python socket guard, not an OS-wide network sandbox. Six legacy loopback
HTTP tests are excluded. Inherited native web hash/span/HTTP issues are not fixed.

## Accounting

`eml-metrics94`: circuit evaluations, EML nodes, accepted/rejected complete
candidates, ground prefix calls, candidate bindings. These are diagnostic worker
counters, not a second model, learned parameters or replay authority. Certificate
checks and canonical compiler validation do not increment worker counters.

Native fuel charges worker steps/EML nodes and the existing controller/checker
units, but not every allocation/list walk/numeric series instruction/compiler or
replay validation. Existing `metrics91` includes charged checker units when used
with encoded libraries; it is not a pure arithmetic instruction count. `metrics92`
keeps checker units separate. Do not compare these units as wall time.

Whole-process times include startup, shared formation, checks, snapshot replay,
queries and output. Benchmarks run sequentially without concurrent test jobs.
Serialized core JSON bytes are a representation-size proxy, not learned parameter
count or native heap usage. Child peak RSS is a separate whole-process measure.

## Reproduction

```sh
./scripts/run.sh integrate94
./scripts/run.sh integrate94-input < experiments/integration94/input-example.sexp
python3 -B -m unittest discover -s tests -p 'test_integration94.py' -v
python3 -B tests/run_offline.py
./scripts/run.sh test
bash tests/store-tests.sh
bash tests/runtime-tests.sh
bash tests/graph-store-tests.sh
python3 -B adapters/integration94_experiment.py --output /tmp/integration94.json
python3 -B docs/integration94-evidence/final_check.py
sha256sum -c docs/integration94-evidence/source.sha256
sha256sum -c docs/integration94-evidence/SHA256SUMS
```

Results: [release-0094.md](release-0094.md), [integration94-experiment.json](integration94-experiment.json).
Version boundary and actual predecessor inventories: [integration94-evidence/](integration94-evidence/).
Prior references: [attention92-design.md](attention92-design.md), [eml93-design.md](eml93-design.md).
