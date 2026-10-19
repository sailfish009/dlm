# DLM v0.0074: external web acquisition for the Maru application

0074 adds the cached Python HTTP acquisition pattern from
`dlm_v0.0065/dlm/web.py`. There is no import or runtime dependency on old DLM
versions. Python supplies documents; DLM remains a Maru application.
The 0073 symbolic rule-learning demo is preserved, unchanged in semantics.

## Fetch and ingest

```sh
cd /research/dlm_v0.0074
./scripts/web.sh --url https://raw.githubusercontent.com/python/cpython/main/README.rst
./scripts/web.sh --query 'deductive logic' --provider github --limit 2
./scripts/web.sh --query 'Horn clause' --provider wikipedia --limit 2

# Replay cached responses without network; a miss is a recorded failure.
./scripts/web.sh --url https://raw.githubusercontent.com/python/cpython/main/README.rst --offline

# Explicitly ask for a new network observation of a previously cached URL.
./scripts/web.sh --url https://raw.githubusercontent.com/python/cpython/main/README.rst --refresh
```

`STORE=/path` chooses a separate acquisition store. `--offline` and `--refresh`
are mutually exclusive. Defaults: 20-second socket timeout, 262144 bytes per HTTP
response, 3 acquired documents per call; `--limit` accepts 1..20. Discovery adds
HTTP calls and therefore this is not a total request/time budget. Duplicate URL
arguments are fetched once. Documents beyond `--limit` are not acquired.

## Boundary

```text
Python stdlib: URL/query -> bounded HTTP/cache -> acquisition datum
Maru DLM: read DATA -> source-document checks -> deduplicated memory + events
Future: sourced interpretation candidates -> evidence gate -> rule learning
```

- Supports explicit HTTP(S) URLs, GitHub repository README discovery, and
  Wikipedia summary discovery. Search results themselves are not truth labels.
- Retains requested/final URL, first fetch time, media type, SHA-256 and exact
  response bytes. Wikipedia responses are retained as JSON bytes, not silently
  converted to world facts. Other HTTP bodies are also stored without semantic
  extraction or HTML execution.
- Cache records are checked against content hashes before reuse. Explicit refresh
  can add a new content version; older committed documents remain in memory.
- Mirror content shares a content-hash source group. This detects exact mirrors,
  not independent corroboration. Same URL+hash is one document; repeat fetch
  timestamps and failures remain in acquisition events.
- All external fields are ASCII hex symbols in the S-expression bridge. Input is
  consumed with `read`, never `eval`; strings that resemble Lisp are only bytes.
- Maru stores status `acquired-uninterpreted`. Reports explicitly show
  `(admitted-facts 0)` and `(interpretation unresolved)`.

**Fetching does not yet train the deductive model from raw text.** Claim/mention
extraction, polarity/modality/condition/attribution handling, byte-to-text IR
interpretation and an independent evidence gate are still needed. The existing
synthetic self-SSL corpus is not replaced by fetched documents. No model-owned
query selection, automatic acquisition loop or general semantic parser is claimed.

## Files and persistence

- `adapters/web.py`: stdlib HTTP/cache, provider discovery and data-only bridge.
- `src/dlm/web.l`: source memory, deduplication, schema checks and replay.
- `experiments/web/ingest.l`, `report.l`: thin Maru drivers.
- `scripts/web.sh`: locked transport + ingestion + atomic state replacement.
- `experiments/web/store/cache/fetch/*.json`: cached raw response and provenance.
- `batch.sexp` and `batch.sexp.json`: latest acquisition and inspectable metadata.
- `state.sexp`: current complete source memory/event log; dated `.sexp` files
  retain previous committed generations. Source content is also retained there.

Restart replays acquisition events and checks the snapshot before admitting new
data. Failure does not delete previous documents or fabricate a replacement.
Snapshots are local integrity/replay checks, not signed evidence. Python checks
SHA-256; Maru does not independently implement cryptographic hashing. Stores and
adapter are trusted local components. The HTTP client is not an SSRF sandbox:
explicit URLs may address local networks. There is no fsync crash durability,
strict total memory budget, incremental compact journal or hostile-input sandbox.

## Verify

```sh
./scripts/run.sh test
python3 -m unittest discover -s tests -p test_web.py -v
bash tests/store-tests.sh
bash tests/runtime-tests.sh
python3 tests/differential.py   # optional sibling 0066 developer oracle
```

Measured checks: 66 Maru/DLM assertions, 6 deterministic local-HTTP Python tests,
20 optional seeded Horn differential cases. HTTP tests cover exact bytes and
redirect provenance, offline replay/miss, oversized/error responses, cache hash
corruption, data/code separation, mirrors, refresh, process restart and forged
snapshot rejection. A live CPython README acquisition and offline replay both
succeeded: one retained document, zero admitted facts.

The compiler lifecycle remains `scripts/compiler.sh rebuild|reproduce|verify ID|
promote ID|rollback`. Verify also runs web-adapter tests and checks three image
generations. No Maru evaluator/compiler semantics were changed in 0074.

## Existing recursive learning experiment

```sh
./scripts/run.sh symbolic
./scripts/selfssl.sh 3
```

Synthetic relational held-out results remain: cold0/14, one round8/14,
recursive14/14, scrambled0/14, explicit violations0. Internal symbolic-state73
and store73 codecs deliberately remain frozen; web-state74 is a separate source
memory until a validated interpretation bridge is implemented. This release does
not yet provide one unified model-state journal for both.

Maru license/provenance remain `LICENSE.maru` / `maru.lock`. Adapter implementation
is adapted from the local 0065 line, not copied from Bio/Screamer. DLM publication
licensing remains to be confirmed.
