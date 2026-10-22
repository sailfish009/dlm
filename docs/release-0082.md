# DLM 0.0082

Release: `20261022T043320Z-15600` (reproduce, verify, promote completed).

New native modules: `src/dlm/ground-space.l`, `src/dlm/ground-session.l`.
The existing launcher loads them after space79. Existing stores/APIs and all
previous version directories are preserved. Compiler sources `src/maru` are
unchanged from v0.0081. The optional Python dialect is unchanged.

Implemented: stable formula IDs, explicit observation provenance, independently
checked conditional derivations, alternative supports, least-fixed-point
activation after evidence retraction, separately revisioned 3D placement,
rebuildable cell index, incomplete local versus complete fallback queries,
budgeted local dependency-distance/crowding relaxation, and data-only snapshot
replay with exact full-state comparison. See `ground82-design.md` for contracts.

Verification: full compiler verify passed, including 61 Python tests in 80.867s,
native/store/runtime/graph-store suites, sibling0066 differential oracles, and
three-generation equality of LLVM outputs and stripped binary images. Logs and
matching manifests are in `verification.log`, `release.sources.sha256` and
`release.tests.sha256`; full artifacts are under the release directory.

Demo: `./scripts/run.sh proof experiments/space/ground82.l`;
recorded output `docs/ground82-demo.sexp`. Its two-unit layout cost changes
400 -> 1 while complete retrieval and semantic graph remain invariant. It is not
a throughput or net-efficiency benchmark.

Limits: observation metadata is caller-supplied, not independently authenticated
or checked against source content. No acquisition/consistency admission policy,
learned neural latent space, measured speedup, predicate/hash/octree index,
co-use learning, incremental reverse-dependency engine, file-store launcher or
actual LLVM MLIR dialect is claimed. Geometry is an optional approximate candidate
index; it never confers truth. Replayed snapshot data is provided, not new
crash-safe file persistence. The existing Maru self-host chain is preserved.

Inherited earlier-version release notes and logs remain historical. This file
and current release verification identify v0.0082 checks.
