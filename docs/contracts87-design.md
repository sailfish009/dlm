# Contracts87: Silicon-inspired finite contract verification in native Maru

## Scope and provenance

This is a fresh, small Maru implementation of contract checking and verified
procedure reuse, informed by the Silicon analysis in `docs/silicon-analysis.md`.
No Silicon Scala/MPL source is copied or translated. It is not a Viper frontend,
SMT-based verifier, full Silicon port, full separation logic or dependent type
system. No external solver, LLM or neural component is required.

The source programs contain symbolic Boolean variable names, but the algorithm
is **complete finite-state enumeration**, not SMT path solving. It checks all
modeled inputs and independently validates local trace certificates. Its guarantee
is relative to this finite IR and the small shared Boolean/store/typing primitives.
Tests are evidence, not a formal proof of the verifier implementation itself.

## IR and operational meaning

```
(contract87 NAME VARIABLES PRE BODY POST WRITES)
```

- VARIABLES: at most6 distinct string/symbol names, each Boolean0/1.
- Expressions: `(bool 0|1)`, `(var x)`, `(not e)`, `(and e e)`, `(or e e)`,
  `(eq e e)`; `(old x)` is allowed in POST only.
- Statements: `(assign x e)`, `(assert e)`, `(if e THEN ELSE)`, `(call name)`.
- BODY is a list of statements; syntactic block depth8, total statement count128,
  individual blocks32 statements, expression-depth16.
- WRITES is a subset of VARIABLES. Every assignment and callee's declared writes
  must fit it. Final certificates also check unchanged frame variables.
- Calls use the same ordered Boolean variable interface, not general argument
  passing. Callees must be earlier checked modules; no recursion or forward call.

The loop-free finite language terminates structurally. There is no heap, aliasing,
integer arithmetic, array, quantified resource, external nondeterministic event,
OS action or dynamic permission model. WRITES is a static effect footprint, not
Silicon fractional permission. Reusable knowledge is not consumed by reading it.

`old` means the current procedure's input store. A called procedure's table was
checked relative to ITS input; a caller's POST still refers to the caller's own
original state. Each initial valuation has an isolated immutable store.

## Universal verification versus existential generation

The verifier enumerates at most64 initial states. For each state satisfying PRE,
it executes the selected runtime-if branch and must establish assertions,
callee preconditions and POST. All such input states must pass. A feasible bad
else is therefore a counterexample even when then succeeds.

By contrast, synthesis uses the existing space79 choose machine to find ONE
candidate program whose entire finite contract verifies. Search OR and runtime
verification AND are different semantics. Unsupported statements are invalid IR,
not false assertions. An inconsistent PRE yields `inapplicable87`; it cannot
enter the procedure library as a useful vacuous solution.

## Explorer and independent local checker

`contracts87-ir.l` owns bounded typing, Boolean evaluation, finite domains, frame
checks and summary lookup. `contracts87-check.l` has two distinct traversals:

- `c87-execute`: source interpreter producing assignments/assertion/branch/call
  events and a final environment;
- `c87-trace`: consumes source+recorded events, independently recomputes each local
  transition and rejects missing/extra/mismatched steps. It never calls execute.

A certificate is `(certificate87 CONTRACT DEPENDENCY-CONTRACTS CASES)`.
Each case binds exact canonical input, output and trace. The checker enumerates
PRE-satisfying inputs itself: duplicate/missing/reordered/extra cases cannot hide
an input branch. It checks output, POST and frame. Explorer and checker share
Boolean evaluation/IR typing as trusted primitives; the independent Python oracle
helps catch errors in these shared semantics.

A counterexample records contract/dependencies/input/trace/reason. The checker
must establish PRE on that input and independently verify an assertion failure,
call-precondition failure, or false POST. Unknown is not converted into refutation.

Public `c87-verify` first proposes a certificate/witness, then passes it through
the checker before returning `verified87` or `refuted87`. Result categories:

- `verified87`: checked exhaustive certificate for this finite contract;
- `refuted87`: checked finite witness;
- `inapplicable87`: no admissible initial input (not a solved plan);
- `unknown87`: exhausted fuel or missing internal summary, not logical false;
- `invalid87`: malformed/unsupported/type-invalid input or checker disagreement.

Fuel0..200000 counts input scans and source/trace steps, including repeated
library checks across proposing/checking. It does not count every expression,
table traversal, syntax check, file operation or primitive instruction. There is
no hard wall-time guarantee. Default public fuel is20000.

## Verified modules and effects

The library is `(library87 ((module87 CONTRACT CERTIFICATE) ...))`, max8 modules.
Each module is verified against the preceding prefix. A caller must satisfy the
callee PRE and may use the exact output row for its current input; it does not
assume an arbitrary POST without evidence. No body re-execution is needed for
that call step, but the library's prefix certificates are validated first.

Certificates bind the complete preceding contract list structurally, not just
names or body hashes. Changing a dependency's body/spec/effects invalidates old
certificates. This is conservative: adding unrelated contracts can also invalidate
a separately cached proof expecting a smaller context. Stored module proofs are
always checked in their original prefix order. Fresh contract names are required
for verify/admit/learn; use `check-library` to recheck existing registered modules.

Finite input/output summaries and their checked traces are not external observed
facts or generic axioms. They are procedure semantics for a stated Boolean domain.
Calling real-world APIs would require a separate trusted/verified operational
model. This prototype does not certify that web documents are true.

## Generated programs and learning

`contracts87-runtime.l` creates at most16 candidate bodies from a fixed grammar:
skip, earlier compatible module calls, constant/variable assignments, short
sequences and conditionals. The deterministic cap can exclude later grammar
forms; generation is not complete. Failure to find a program is
`unknown87 bounded-generation`, never proof that no program exists.

Each candidate becomes a real space79 alternative:

```
(verify87 (CONTRACT LIBRARY FUEL))
(accept CONTRACT)
```

The native verify87 action stores a checked result in branch-local context.
Provisional accepts need a matching checked result, and a separate final
`c87-check` gate validates the selected proof before publication. A forged
provisional verified ticket with empty cases is rejected. Records of candidate
outcomes are returned for inspection; this release does not train a new UCB
policy from these contract outcomes.

`learn` expands the checked procedure library, changing later generation: after
learning setx and sety, a stronger `(and (var x) (var y))` goal is solved by
`((call setx) (call sety))`. This is a verified reusable composition, not a claim
of unrestricted program induction or general recursive functions.

## Original REPL API

```
./scripts/run.sh repl
```

```
(contracts 'verify CONTRACT [FUEL])
(contracts 'admit CONTRACT [FUEL])
(contracts 'synth EMPTY-BODY-TEMPLATE [FUEL])
(contracts 'learn EMPTY-BODY-TEMPLATE [FUEL])
(contracts 'library)
(contracts 'check-library)
(contracts 'snapshot)
(contracts 'restore DATA)
(contracts 'save "/tmp/contracts87.sexp")
(contracts 'load "/tmp/contracts87.sexp")
(contracts 'reset)
```

`admit/learn` publish only after verification. A template must have an empty body;
there is no silent replacement of a supplied program. The library cap is8.
Synthesis fuel is per candidate verification and final gate, not a combined
16-candidate primitive budget. Engine event budget256 is sufficient for this
bounded two-instruction branch grammar but does not bound verifier action time.

The existing DLM77/Screamer relation learner and its shell remain unchanged.
The new contract API uses the same original REPL/shared nondeterministic machine,
but it does not autonomously choose contract goals in the relation idle loop.
It does not implement human-question parsing or web-axiom extraction.

## Native proof-carrying storage

`(contract-store87 1 LIBRARY)` is a separate explicit format, not a hidden change
to existing DLM77/space79 stores. Every load/restore rechecks all module proofs,
finite-case coverage and dependency prefixes. Data is read, not evaluated.
Replacing a nonempty in-memory library requires reset unless identical.

Save acquires an advisory native file lock, validates the current and existing
snapshot, writes/readbacks `.next`, retains `.previous`, checks the old file has
not changed, then atomically renames. Corrupt existing data is not overwritten.
Failure does not publish a replacement library. Load uses the same lock boundary.
No fsync, authentication, hostile-filesystem sandbox or distributed transaction is
claimed. The library is NOT included in `(dlm 'save)`; use explicit contract save.

## Demonstrations and tests

```
./scripts/run.sh proof experiments/space/contracts87.l
python3 -m unittest discover -s tests -p test_contracts87.py -v
```

The native demonstration generates setflag, reuses it via call, generates setready
and composes both to establish the stronger conjunction. It rejects a missing-else
program with witness flag=0,ready=0, and verifies a toggle preserving ready/old.
Candidate programs contain actual failed and successful branches. No speedup is
claimed: enumeration, per-candidate proof checking and library revalidation cost
real work; compare correctness before performance optimization.

Eleven tests cover:

1. feasible-else rejection and PRE-restricted branches;
2. frame/old semantics;
3. vacuity/fuel separation;
4. missing coverage and forged trace rejection;
5. checker independence when explorer is disabled;
6. checked calls, preconditions, effects and stale dependencies;
7. generation, learned reuse and stronger-goal module composition;
8. forged provisional ticket refusal;
9. native save/load/corrupt-store refusal in fresh processes;
10. unsupported IR and actual original-REPL use;
11.200 seeded programs over four possible input valuations each, compared with
   an independent Python interpreter (zero status mismatches).

The full test suite reaches100 tests. Maru compiler/platform sources are unchanged;
no Scala/SMT dependency enters self-hosting. Matching final manifests and
three-generation reproduction are recorded in `docs/release-0087.md`.

## Deferred work

Arithmetic, heaps/permissions, loop invariants/termination, arguments/locals,
nondeterministic runtime effects, general state joins, incremental library
validation, automatic contract-goal curriculum and natural-language/web grounding
remain future tasks. In particular this does not claim full Silicon compatibility.
