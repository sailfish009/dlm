# DLM 0.0096 — Source-grounded web-to-basis learning

A CPU-only, local deductive-learning research prototype. Version 0.0096 adds a
**narrow, reproducible bridge from an actual structured web artifact into the
existing cumulative DLM learner**. It does not introduce a separate web learner.

> **What this establishes:** source acquisition → checked structured observations
> → existing basis formation → prefix-guided subsequent formation → source-scoped
> execution, revision and withdrawal.
>
> **What it does not establish:** arbitrary web-text understanding, discovery of
> new geographic laws, general empirical condition invention, or a completed
> theory of latent axioms. The schema and experimental curriculum are fixed.

## What is learned?

The source is a pinned, public country/region-code CSV. A declared decoder reads
four columns and supplies source-claimed relations:

```text
country → subregion → region → global group
```

The existing Basis91 learner discovers and admits conservative definitions:

```text
R1(a,b,c)   := country-subregion96(a,b) ∧ subregion-region96(b,c)
R2(a,b,c,d) := R1(a,b,c) ∧ region-global96(c,d)
```

Neither definition body is supplied as a training program. R1 is learned from an
initial two-edge view. Applying it to later observations changes interpretation
and makes it a constructor for R2. Execution then actually calls **R2 → R1**.
All variable roles and original fact witnesses remain visible; this is not a
projection to an unexplained country-to-world label.

These are reusable logical definitions of source relations, **not newly inferred
universal truths**. Primitive reasoning already answers the same finite goals.
The demonstrated change is the model's inference organization and cumulative
formation path, not a new set of logically impossible-before conclusions.

## What data was used?

Pinned source:

- Repository: [`datasets/country-codes`](https://github.com/datasets/country-codes)
- Commit: `2d84034a0cae19ea5444b78c2131304a5c7f4bb9`
- File: `data/country-codes.csv`
- Original bytes: **133,991**; records: **249**
- SHA-256: `bb199ebc9636b9872705e8216f1f849359f136a7668ebfa23a3c58048462ab92`

Four eligible records enter the formation episodes; **244** are held out from
formation. One record, Antarctica, is unresolved for this schema because its
subregion/region fields are missing. Missing is not interpreted as false.

The selection rule is hand-written and deterministic: sort country codes, choose
two distinct-region records for the first view, then two more for the next view.
This is not learned curriculum generation. All rows come from **one artifact**;
held-out rows are not unseen websites, statistically independent sources or
transfer to a new ontology. The full CSV is parsed for extraction/selection, but
only the selected four records enter the learner's support/interpretation tables.

**Licensing:** the upstream file combines data with restricted or unclear terms.
Its software/arrangement license does not automatically license all source data.
Raw bytes and full input packets are kept in a private local cache or temporary
files, not bundled in this product. Reproduction requires explicit initial
acquisition. See [source provenance and notices](experiments/web96/source/README.md).

## Architecture

```text
existing CachedWeb HTTP/cache record
 → Python stdlib CSV extraction worker
 → data-only packet containing original bytes and proposed byte-span evidence
 → native SHA-256 + independent byte-CSV/extraction checker
 → atomic source admission in the existing Basis91 state/session/audit
 → existing interpretation / learn91 / global-ID library / Attention92 execution
```

Added native files:

```text
src/dlm/web96-bytes.l      bounded bytes, SHA-256 and CSV record/cell spans
src/dlm/web96-extract.l    declared schema, canonical observations, no-repair gate
src/dlm/web96-session.l    same-owner admission, source lifecycle and queries
```

Source provenance is an optional extension of the existing typed95 facet. There
is **no second learned library, model owner, session or checkpoint format**.
Direct logic is the main representation; EML is a comparison arm, not a required
web-learning engine. Existing numeric95/composite95 learning remains available in
the same global library. Numeric interoperability tests use synthetic data and
must not be described as numeric learning from this web source.

The historical general `web-state74` ingestion path remains uninterpreted for
other formats. This bridge reuses its actual acquisition-record implementation;
it does not claim to integrate all historical DLM subsystems or arbitrary URLs.

## Integrity, evidence and source lifecycle

- The native checker recomputes SHA-256 and separately parses the original bytes.
  Wrong/omitted facts, rows, unresolved records or byte ranges **reject ingress**;
  reference output never fills incomplete worker output.
- Each complete web answer is marked `source-claims96`, with source version/hash,
  original row numbers, original fact IDs and zero-based, half-open cell byte
  ranges. Codes are object identifiers, never implicit numeric measurements.
- Missing rows, stale source artifacts, inactive sources and exhausted query fuel
  produce explicit `unknown` states with no unfinished answer rows.
- Byte-identical refetches at the same URL add no event or support. Source CAS
  tokens include URL, digest, admission version **and activity**, not digest alone.
- Valid revisions replace both managed episodes/readings atomically. Withdrawal
  disables current web application while keeping conservative definitions.
  Restore is a checked new admission; frozen historical models do not mutate.
- Generic observe/retract cannot mutate bridge-managed episodes. Existing shared
  checkpoint/replay/locking and failure-atomic publication are reused.
- Hash agreement proves consistency with supplied bytes, not website truth or
  authenticated remote origin. A malicious caller can fabricate consistent bytes
  and relabel a URL. No signed origin or adversarial-host security claim is made.

This tracks the **last admitted artifact**, not a continuously monitored web. A
rejected update leaves that state intact. A caller who knows a source changed but
cannot interpret its new content must explicitly withdraw the old source or keep
it labeled historical. There is no automatic crawler/refresh/revocation service.

## Reproduce

The preserved native compiler is used unchanged. No GPU, external model, LLM/API
runtime or neural-gradient training is involved. Python handles acquisition,
worker extraction, orchestration and an external oracle; learning/execution are
native Maru. Network access is needed only for explicit initial acquisition.

```sh
cd /research/dlm_v0.0096

# Once: allow HTTPS acquisition of the pinned source into a private cache.
python3 -B adapters/web96.py --online --output /tmp/web96.sexp

# Subsequently, cache-only. Override the cache with --cache or DLM_WEB96_CACHE.
python3 -B adapters/web96.py --output /tmp/web96.sexp
./scripts/run.sh web96-input < /tmp/web96.sexp > /tmp/web96-native.sexp

# Full sequential comparison, after regression tests have finished.
python3 -B adapters/web96_experiment.py \
  --queries 244 --repeats 2 --output /tmp/web96-experiment.json

# Tests; the real-source test requires the already acquired offline cache.
python3 -B -m unittest discover -s tests -p 'test_web96.py' -v
python3 -B tests/run_offline.py
./scripts/run.sh test
bash tests/store-tests.sh
bash tests/runtime-tests.sh
bash tests/graph-store-tests.sh
```

Cache default: `~/.cache/dlm-web96`. A cache miss is an error, not a silent switch
to synthetic data. The input launcher reads exactly one datum and checks EOF;
external content is never evaluated as Maru code.

## Public source API

Within the existing Basis91 API:

```lisp
(basis91 'init '(country-subregion96 subregion-region96 region-global96))
(basis91 'web-token)                       ; missing96, or source-token96
(basis91 'web-import DOCUMENT EXPECTED-TOKEN)
(basis91 'web-source)                      ; compact current source manifest
(basis91 'web-retract EXPECTED-TOKEN)
(basis91 'web-query VIEW-ID PATTERN FUEL POLICY)
(basis91 'web-infer MODEL DOCUMENT VIEW-ID PATTERN FUEL POLICY)
```

Use the ordinary `interpret`, `interpret-controlled` and `learn` commands for
formation. Web policies are existing Attention92 policies or `raw96` for the
primitive comparison route. A model's definition-count epoch is not its exact
source revision; preserve the full source token/core identity.

## Validation and experimental results

**26 new tests and all 290 offline tests passed**; native, store, runtime and
graph-store suites also passed. Six legacy local-HTTP tests were excluded.

Ten sequential fresh-process runs (five arms x two repeats) attempted **9,760
queries** on the actual source. There were **7,808 complete queries / 7,808
binding-and-witness rows, zero mismatches**, and 1,952 expected unknowns in the
no-admitted-extraction control. Unknowns are not counted as correct answers.
A separate fresh-process, empty-cache, archive/learner-free check completed
another **976 queries / 976 rows**, also with zero mismatches.

Main whole-process medians for formation/replay plus 976 queries were **93.07 s
for direct logic** and **126.35 s for EML**. Compact core JSON sizes were 1,567
and 2,965 bytes respectively. These results do not establish an EML advantage.
The maximum native-child high-water RSS across the sequential batch was 94,756
KiB; it includes the runtime and transient source/checker data, not just bases.

Detailed evidence and final counts are in:

- [Release and results](docs/release-0096.md)
- [Design, contracts and limitations](docs/web96-design.md)
- [Sequential experiment data](docs/web96-experiment.json)
- [Compact native demonstration](docs/web96-demo.sexp)
- [Lifecycle and causal interventions](docs/web96-interventions.sexp)
- [Fresh-process core-only evidence](docs/web96-evidence/standalone.json)
- [Final preservation and integrity checks](docs/web96-evidence/final-checks.json)

Controls distinguish no extraction, no formation, prior absent at the later
formation step, and logical versus EML representation. Unknown controls are not
counted as correct answers. The no-prefix arm is a staged intervention, not an
equal-total-compute impossibility claim: a separate extra ordinary learning step
recovers R2 from the same observations.

The new tests include native SHA/CSV checks against Python, real pinned input,
source/worker forgeries, omission, duplicate refetches, version-sensitive CAS,
revision/withdrawal/restoration, frozen cores, source-aware persistence/locks and
failed publication. Whole-process time, child RSS and JSON bytes are reported as
their actual quantities, **not learned parameter counts or kernel-only costs**.

## Remaining research boundaries

Free-text interpretation, autonomous schema/curriculum invention, general
empirical conditions and definition revision, noise/conflict handling, physical
units, new numeric laws from web measurements, multi-source trust and larger
continual growth remain open. EML-specific superiority is not established by
this structured-relation experiment.

The predecessor is preserved in `README-0095.md`; earlier design/history is
available in the inherited archives. No user work was reset or committed.
