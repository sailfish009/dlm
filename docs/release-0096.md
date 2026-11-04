# Release 0.0096 — first structured-web bridge into cumulative basis formation

## Bottom line

A real pinned web CSV now reaches the existing Basis91 learner through an
independently checked, source-grounded observation bridge. The same learner forms
R1, applies it to later observations, admits R2 using R1, and executes R2 -> R1.
This closes a narrow acquisition/interpretation/formation/application path that
was absent in 0.0095. It is not general web-text interpretation or discovery of
a new geographic law; the result is conservative inference organization.

## Preservation boundary

The actual 0.0095 nonignored inventory contained **598 files**, including its
existing dirty/untracked work, not an assumed historical manifest. They were
hashed before copying with `cp -a --reflink=auto`, checked in 0.0096 before edits,
and the root README was archived as `README-0095.md`. Final checks compare every
predecessor inventory hash, its complete Git status, the compiler and README.
No reset or commit was made.

Exactly eight inherited paths change relative to that copy-time inventory:

```text
README.md
VERSION
scripts/run.sh
adapters/web.py
src/dlm/basis91-ir.l
src/dlm/basis91-session.l
src/dlm/composition95-ir.l
src/dlm/composition95-session.l
```

The compiler symlink and binary remain unchanged:

```text
maru-compiler -> runtime/releases/20261022T043320Z-15600/maru
SHA-256 2cbe804829509f5386933d832cbba2fef1bad367b7510a543b5d3f5818136fc9
```

## Implementation

- `src/dlm/web96-{bytes,extract,session}.l`: bounded native SHA-256, CSV byte spans,
  declared-schema extraction gate, same-owner source lifecycle and execution.
- `adapters/web96.py`: actual old CachedWeb acquisition record -> proposed
  observations; stdlib only, no external model or learner.
- `adapters/web96_experiment.py`: sequential runs and separate raw-CSV assignment /
  original-fact-witness oracle, not runtime answer repair.
- `adapters/web96_lifecycle.py`: reproducible revision/withdrawal/recovery and
  fresh-process checks, with explicitly synthetic revision fixtures.
- `experiments/web96/`: data-only driver, source notices, lifecycle and standalone
  experiments. `tests/test_web96.py`: 26 new tests.

The old HTTP adapter also now checks declared Content-Length against bounded
reads and catches `http.client.HTTPException`, including IncompleteRead. Mocked
truncation/cache tests run offline. This does not certify the entire legacy HTTP
stack, crawler, native web74 integrity path or arbitrary web format.

Provenance extends the existing typed95 facet; Basis91 remains the only library,
state, audit, session, checkpoint and admission owner. Direct logic is the main
web representation. Legacy state/core shapes remain valid; numeric95/composite95
remain usable in the same global-ID library. No standalone EML93 learner is used.

## Data and learned structure

Actual source: datasets/country-codes at commit
`2d84034a0cae19ea5444b78c2131304a5c7f4bb9`, file `data/country-codes.csv`.
133,991 original bytes, 249 records, SHA-256
`bb199ebc9636b9872705e8216f1f849359f136a7668ebfa23a3c58048462ab92`.
[Provenance and licensing notices](../experiments/web96/source/README.md).

The fixed decoder reads M49/subregion/region/global codes. It does not learn the
schema, language meaning, physical units or identifier types. An explicitly
hand-written selection/visibility curriculum chooses initial countries 004/008
and later countries 012/016. Four records enter formation, 244 eligible records
are held out from formation, and Antarctica remains explicitly unresolved.
Records share one acquired source and hierarchy; they are not independent sources.

The actual main logical definitions are:

```lisp
(basis91 1
  ((country-subregion96 0 1) (subregion-region96 1 2))
  ((fact91 country-subregion96 (0 1))
   (fact91 subregion-region96 (1 2))))

(basis91 2
  ((country-subregion96 0 1) (subregion-region96 1 2) (region-global96 2 3))
  ((call91 1 (0 1 2))
   (fact91 region-global96 (2 3))))
```

These bodies are discovered by existing data-pattern interpretation, support,
prior-guided planning, candidate scoring and checked rewriting. They are not
supplied in the web packet. They denote source-relation conjunctions while
preserving every role, not projected labels or inferred new geographic axioms.

## Tests

- New web tests: **26 passed**, 46.862 s.
- Full offline Python/native-driver suite: **290 passed**, 1153.744 s.
- Six legacy loopback-HTTP tests excluded by the existing offline socket guard.
  This guard is not an OS-wide network sandbox.
- Native `run.sh test`, store, runtime and graph-store suites: all exit 0.

Coverage includes real pinned input, SHA-256 against stdlib on boundary/random
bytes, CSV quotes/newlines/CRLF, missing rows, 400 malformed packet/core/model
trees, wrong/omitted extraction and byte evidence, query-worker omission, no
reference filling, duplicate fetches, full source-token CAS, revisions,
withdrawal/restoration, frozen models, shared numeric interoperability,
source-aware checkpoints/locks, failed-publication atomicity and input EOF/code
injection rejection. Synthetic small CSV/unit numeric fixtures are explicitly
separate from real-source evidence. Cache absence fails, not silently fabricates
or skips the real-source test.

## Sequential actual-source experiment

All regression suites finished before measurement. **10 fresh native processes**:
five arms x two repeats. Each run attempts 244 excluded-from-formation views x two
query patterns x two execution policies (`adaptive92`, `raw96`) = 976 queries.
Every complete binding and original fact witness is compared with the external
raw-CSV assignment oracle. Policies execute the same frozen standalone core.

| Arm | Runs | Definitions | Complete queries | Unknown | Complete rows | Mismatches |
|---|---:|---:|---:|---:|---:|---:|
| logical96 | 2 | 2 | 1,952 | 0 | 1,952 | 0 |
| eml96 | 2 | 2 | 1,952 | 0 | 1,952 | 0 |
| no-prefix96 | 2 | 1 | 1,952 | 0 | 1,952 | 0 |
| no-formation96 | 2 | 0 | 1,952 | 0 | 1,952 | 0 |
| no-extraction96 | 2 | 0 | 0 | 1,952 | 0 | not applicable |
| **Total** | **10** | — | **7,808** | **1,952** | **7,808** | **0** |

There are 9,760 attempts. Unknown controls are not counted correct. This is a
finite, one-artifact check, not a universal accuracy/generalization theorem.

Interpretation of controls:

- **No admitted extraction:** worker extraction claims are omitted. The native
  checker can decode the source but rejects rather than installs its reference
  observations. No admitted source/learned basis; web queries remain unknown.
- **No formation:** source observations enter the same model, but no definitions
  form. Primitive reasoning still solves the goals. Acquisition success and
  answer correctness alone therefore do not establish learning.
- **No earlier prefix:** skip initial interpretation/admission; one later learn
  step admits R1 but not yet R2. This has fewer admissions, not equal total
  formation compute. A separate extra ordinary learn step recovers R2 from the
  same raw observations: it is a changed formation trajectory, not impossibility.
- **Logical versus EML:** same source/schema/selection and two definitions; only
  checked executable relation representation changes. EML is not required for
  this web-learning path and no EML-specific learning advantage is established.

Measured medians (two repeats; complete-query count is 976 per successful run):

| Arm | Whole-process median | Compact core JSON bytes |
|---|---:|---:|
| logical96 | 93.0748 s | 1,567 |
| eml96 | 126.3495 s | 2,965 |
| no-prefix96 | 91.1753 s | 1,414 |
| no-formation96 | 89.7410 s | 1,265 |
| no-extraction96 | 10.7663 s | 94 |

Main logical range: 92.4851–93.6646 s; EML range: 125.4749–127.2242 s. Maximum
native-child high-water RSS across the batch: **94,756 KiB**. The logical arm is
smaller/faster here; two repeats on one small source do not establish a robust
performance law or EML-specific learning superiority.

Exact full-precision process times, core JSON sizes, operation metrics and query
hashes are in [web96-experiment.json](web96-experiment.json). Whole-process costs
include startup, source-byte transfer, native hashing/CSV/claim checks, formation,
admission, scope refresh, replay, all queries and output; Python extraction and
external oracle/JSON analysis are outside the native timer. Complete packet
validation is deliberately repeated at query boundaries; the runtime cache
avoids repeated SHA/CSV computation, not all deep claim comparisons. Fuel/worker
counters do not account for all this validation, allocation or controller work.
This is not a pure learning- or inference-kernel benchmark. Faster unknown/no-
formation controls are not evidence of useful learned-solving speedups. JSON
bytes and child RSS are not learned parameter counts or learned-memory size.

## Source and causal interventions

[Native interventions](web96-interventions.sexp) demonstrate:

- Main application uses the stored hierarchy, including actual R2 -> R1 calls.
- Duplicate fetches return unchanged; omitted extraction is rejected without a
  changed snapshot; omitted query work and tiny fuel expose unknown, never
  reference-filled rows.
- Withdrawal disables current application, preserves the two definitions and
  leaves a historical model usable with its historical source.
- Restoration is a new source admission; an old active token is rejected even
  though the source bytes/digest are identical.
- An **explicitly synthetic local revision**, not an upstream update, changes
  country 020's subregion/region fields. Current results and provenance follow
  the new artifact; stale documents are unknown. Definitions remain two.
- Restoring the actual original source restores its results; replay succeeds.
- A delayed additional ordinary learn recovers R2 in the no-prefix trajectory.

Counterexamples here change source facts/applicability, not general definitions
or invented empirical conditions. A source checksum is not remote-origin
attestation, political truth or authority. Rejected updates preserve the last
admitted state; automatic fetch monitoring/withdrawal is not implemented.

## Fresh-process core-only check

A separate native process receives only the compact admitted core (no episodes
or readings) and the source query bytes. Its verification cache initially starts
empty; live model owners, replay and learner entry points are removed/disabled.
It performs another **976 complete queries / 976 binding-and-witness rows**, with
zero mismatches or unknowns against the external oracle. See
[standalone.json](web96-evidence/standalone.json). Its whole-process time was
90.3858 s, including fresh source verification and 976 queries; subtracting it
from another run does not isolate a learning-kernel cost. Source bytes are query
input, not an answer archive; whole-file acquisition is not claimed unseen. The cached
native extraction contains atomic source facts, never compound answers.

### Serialization correction retained in evidence

The initial fresh-process launcher incorrectly round-tripped the analytical JSON
model into an S-expression. JSON loses `sexp.Symbol` versus quoted-string types,
and native validation correctly rejected this model before running queries.
The corrected lifecycle tool extracts the actual typed `model96` form from the
companion native `web96-demo.sexp`, checks its JSON projection against the
analytical model, and supplies that native core to the fresh process. The failed
attempt is retained as `web96-evidence/standalone-json-roundtrip-failure.stderr`;
the corrected standalone run above passed. Analysis JSON is not a native snapshot
format; do not convert every string to a symbol because source/object identifiers
must remain strings.

## Reproduce lifecycle and integrity checks

After the explicit acquisition and main experiment in the root README:

```sh
python3 -B adapters/web96_lifecycle.py interventions \
  --output /tmp/web96-interventions.sexp
python3 -B adapters/web96_lifecycle.py standalone \
  --experiment docs/web96-experiment.json --output /tmp/web96-standalone.json
python3 -B docs/web96-evidence/final_check.py
sha256sum -c docs/web96-evidence/source.sha256
sha256sum -c docs/web96-evidence/SHA256SUMS
```

Published full-experiment results contain answer hashes, counts and metrics
rather than a redistributed table of every geographic binding. Limited native
examples are in [web96-demo.sexp](web96-demo.sexp). Hash manifests establish file
consistency, not experimental truth or observation authenticity.

## Remaining limits

One fixed schema/source slot and a fixed small curriculum. No free-text semantics,
autonomous schema or condition discovery, general noisy-source/conflict learning,
new numerical law discovery, signed source origin, universal latent axioms or
long-term growth is established. The original broader research goal remains
partially implemented. See [the design](web96-design.md) for exact contracts,
bounds, checker-independence limits, licensing and trust boundaries.
