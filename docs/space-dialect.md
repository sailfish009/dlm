# Space dialect v0 — executable front-end, not upstream MLIR

## Status and boundary

DLM 0.0081 adds a **Python, MLIR-shaped textual front-end** in
`adapters/space_dialect.py`. This is an initial lowering/translation-validation
stage, NOT a registered LLVM MLIR dialect. It does not provide TableGen ODS,
`mlir-opt` integration, MLIR bytecode, a C++ plugin, or MLIR passes. MLIR tools
were not available on PATH in the implementation environment. Do not feed the
example `.mlir` directly to upstream MLIR tools.

The implementation uses Maru as its reference interpreter, not an independently
implemented second event machine. Tests compare manually written direct Maru
calls with lowered code, including entire intermediate states. This tests the
translation, not independent semantic equivalence of two runtimes.

## Run

```
./scripts/dialect.sh verify experiments/space/dialect.mlir
./scripts/dialect.sh explain experiments/space/dialect.mlir
./scripts/dialect.sh format experiments/space/dialect.mlir
./scripts/dialect.sh lower experiments/space/dialect.mlir > /tmp/dialect.l
./scripts/run.sh proof /tmp/dialect.l
./scripts/dialect.sh run experiments/space/dialect.mlir
```

No compiler or existing store is required to understand the front-end syntax.
Executing lowered code needs the existing Maru runtime. The old direct `.l`
execution path has no Python or dialect dependency.

## Representation

A module is `space.module @name { ... }`. An operation occupies one logical
line, with multiline parenthesized data permitted. `//` comments outside strings
are ignored. Names, problems, signatures and formulas are data-only S-expressions.
Strings remain strings; symbol and string identities are preserved by lowering.

```
space.module @example {
  %s0 = space.new : !space79.space
  %s1 = space.prove %s0 j (problem classical-prop-v1 ((p 0))
    (sequent classical-prop-v1 ((pred p ())) ((pred p ())))) : !space79.space
  %s2 = space.run %s1 100 : !space79.space
  space.dump %s2 full_state
}
```

`!space79.space` denotes the full persistent state, including queue ordering,
unit IDs, waiters, contexts, job results, definitions and statistics. No lossy
projection is used between operations. Earlier SSA values remain immutable and
available; explicit forks from an earlier state are allowed. There is no
implicit join of independently forked state values.

The current single state type is coarse. Unit, job and certificate types are
not separate dialect types yet. Structural verification checks operation arity,
SSA definition/use, result types, literal kinds and run bounds. Logical formulas,
signatures, capacity and job admission remain checked by the Maru implementation;
front-end verification alone is not proof of runtime admission. A rejected Maru
transition is not a valid space state and must not be used as one downstream.

## Operations and effects

| Operation | Operands after state, if any | Meaning |
|---|---|---|
| `new` | none (no state operand) | Create empty space |
| `define` | name, signature, body | Guarded fresh naming |
| `use` | job name, definition name, premises | Activate definition with checks |
| `prove` | job name, problem | Submit proof obligation |
| `program` | job name, tasks | Submit scoped nondeterministic program |
| `interpolate` | job name, signature, A, B | Proof-based Craig job |
| `beth` | job name, signature, theory, target | Conditional definition job |
| `run` | integer budget 0..20000 | Advance bounded events |
| `resume` | job name, true/false | Resume/next program alternative |
| `dump` | label | Print entire state (no SSA result) |
| `job` | label, job name | Print job (no SSA result) |
| `definitions` | label | Print definition table (no SSA result) |

All non-observation operations require one SSA result. Effects are conservative
metadata exposed by `explain`: creation, state write/read, queue enqueue/step and
proof checking. They are **not** MLIR `MemoryEffectOpInterface` implementations.
No optimizer uses them; no CSE/reordering/dead-state elimination is performed.
Observable printing is ordered in source order.

## Semantics, resource limits and persistence

Lowering emits only whitelisted API calls and quotes validated data; source data
is never evaluated as code. SSA names use a restricted identifier grammar. All
scope isolation, AND obligations, failure/exhaustion, incomplete budgets,
certificate verification and capacity rules are inherited from space79.
Snapshots remain in the existing native format. The dialect is neither a new
snapshot codec nor a migration tool. Modules do not contain file-open/eval ops.
There is no roundtrip codec for native snapshot data in this release. Canonical
**module text** roundtrips preserving lowering and effects.

## Verification and self-host

Seven new Python tests exercise syntax rejection, canonical module roundtrip,
example execution, quoted data, immutable earlier states, manually written direct
Maru versus lowered full states, and 30 seeded intermediate event slices. Existing
native tests, independent logic oracles and snapshot/replay tests remain enabled.

`src/maru`, the bootstrap seed, Maru code generation, and the trusted DLM kernel
are unchanged from v0.0080. Python is optional at the application front-end, never
part of the compiler bootstrap chain. `compiler.sh reproduce` followed by
`compiler.sh verify ID` builds next and third generations, compares LLVM text and
stripped binaries, and runs native/store/runtime/Python/differential suites.
This preserves the existing self-reproducing compiler boundary, still dependent
on external clang/linker. It does not make Python or this front-end self-hosted.

## Remaining work for an actual MLIR dialect

1. Implement and build a registered dialect/ODS types and operations against a
   pinned LLVM/MLIR toolchain, with actual verifier/effect interfaces.
2. Parse/print native MLIR syntax and lower its typed ops to this Maru boundary.
3. Extend translation validation to generated programs, runtime rejection paths,
   snapshot continuations and independent effect/region checks.
4. Only then add optimization passes with stated observational invariants.

The compiler must remain able to reproduce itself without these optional tools.
