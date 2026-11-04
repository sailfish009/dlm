# Web96: a narrow source-grounded bridge into the cumulative DLM

## Scope and epistemic contract

Version 0.0096 connects a real, pinned structured-web acquisition to the existing
Basis91 interpretation, formation, admission, application and replay lifecycle.
It does **not** turn arbitrary web sentences into axioms or learn a new geographic
law. The admitted relational bases are conservative, all-role-exporting path
definitions. Ground atoms mean **claims in a specified source artifact**.

The declared schema supplies the meanings of four CSV columns and three binary
predicates. This fixed decoder is not learned semantic extraction. Country and
region codes are object identifiers in separate namespaces, never numeric
measurements. The intermediate-region column is not used: `country-subregion96`
denotes the membership explicitly stated by the selected columns, not necessarily
an immediate administrative-parent relation.

## Actual path

```text
pinned HTTPS URL
  -> existing adapters/web.py CachedWeb record
     (URL, final URL, fetched time, media type, SHA-256, original bytes)
  -> adapters/web96.py: stdlib CSV extraction worker + byte-span proposals
  -> ASCII, data-only web-document96 packet
  -> native SHA-256 + separate byte CSV parser + canonical extraction comparison
  -> ONE atomic web-import96 event in Basis91
  -> existing observe-equivalent episodes / interpretation / learn91 admission
  -> same global-ID relational/numeric/composite library
  -> source-scoped queries using existing Attention92 worker and independent gate
```

The old general `web-state74` path remains acquired-uninterpreted. This is a new
**declared-schema bridge from its existing acquisition-record implementation**,
not a claim that every old acquisition format or historical DLM subsystem has
been integrated. There is no new web learner, learned-library owner, scheduler or
checkpoint wrapper. The only new global data is a bounded runtime verification
cache, not model state.

## Source and curriculum

The experiment uses the country-codes CSV at Git commit
`2d84034a0cae19ea5444b78c2131304a5c7f4bb9` in `datasets/country-codes`.
Original artifact: 133,991 bytes, 249 records. SHA-256:
`bb199ebc9636b9872705e8216f1f849359f136a7668ebfa23a3c58048462ab92`.
A GitHub Contents API blob identifier was also compared with the downloaded Git
blob SHA-1; that is artifact consistency, not proof of the table's real-world
truth or unrestricted licensing.

Required columns: `M49`, `Sub-region Code`, `Region Code`, `Global Code`.
Codes must be ASCII decimal 1..999, with at most three digits. They are normalized
to three-character identifiers in country/subregion/region/global namespaces.
Other columns remain uninterpreted original bytes. Missing or unsupported codes
produce explicit unresolved-row metadata; they do not become false facts.
Duplicate required identities, duplicate headers, malformed CSV and limits are
not silently normalized away.

A hand-written deterministic curriculum, not a learned teaching policy:

1. Sort eligible records by normalized M49 country code.
2. Select the first two countries with distinct regions for a two-edge view.
3. Excluding those countries, select the next two with distinct regions for a
   three-edge view.
4. Keep all remaining eligible countries outside formation episodes.

The actual initial countries are 004/008; the later countries are 012/016. Four
records enter the formation episodes, 244 eligible records are held out from
formation, and one record (Antarctica) is unresolved for this schema. All records
belong to **one acquired artifact**: held-out rows are not unseen documents,
independent websites, independent statistical samples or an unseen ontology. The
full source is scanned for deterministic extraction/selection; only the four
selected records enter the learner's interpretation/support tables.

## Representations and integration

```lisp
(web-document96 "country-codes96" PINNED-URL UTC-TIME SHA256
  m49-csv96 ORIGINAL-BYTES-HEX EXTRACTION-CLAIM)

(extraction96 m49-csv96 TRAIN-VIEW NEXT-VIEW HELDOUT-VIEWS
  UNRESOLVED-ROWS ORIGINAL-RECORD-COUNT)
(view96 ID EDGE-DEPTH ORIGINAL-RECORD-NUMBERS FACTS EDGE-EVIDENCE)
(edge96 ORIGINAL-FACT-ID RECORD-NUMBER RECORD-START RECORD-END
  LEFT-COLUMN LEFT-START LEFT-END RIGHT-COLUMN RIGHT-START RIGHT-END)
```

Byte ranges are zero-based, half-open, in the **original UTF-8 byte stream**,
not character offsets or reserialized CSV. CSV parsing supports quoted commas,
escaped quotes, quoted newlines, LF and CRLF. Header and numeric semantics are
fixed; the native byte parser does not claim general Unicode/NL interpretation.

The existing optional typed95 facet gains a final provenance field:

```lisp
(typed95 BRANCH CALIBRATIONS CHANNELS NUMERIC-SCOPES
  (web96 VERIFIED-DOCUMENT ADMISSION-VERSION ACTIVE?))
(typed-core95 BRANCH NUMERIC-SCOPES
  (web-core96 SOURCE-ID URL FETCH-TIME SHA256 SCHEMA ADMISSION-VERSION ACTIVE?
    VIEW-BINDINGS UNRESOLVED-ROWS))
```

Old five-field typed95 and three-field typed-core95 values remain accepted.
Basis91's state/core/session tags and global definition IDs are unchanged. The
empty numeric facet is initialized for provenance compatibility; direct-logical
web learning does not invoke EML93's learner or require numerical bases. Synthetic
unit tests cover numeric formation both before and after web formation in this
same global library. Those tests are **not** numeric learning from web data.

`web-import96` installs both views atomically, checked against native extraction;
it never installs the reference extraction in place of omitted/wrong worker
claims. Interpretation and learning remain the existing `interpret91`, checked
`interpret-controlled91`, and `learn91` events. Prefix R1 participates in later
interpretation, construction of R2, rewriting and actual R2 -> R1 execution.

## Source lifecycle

Source compare-and-swap token:

```lisp
(source-token96 URL SHA256 ADMISSION-VERSION ACTIVE?)
```

`missing96` identifies an uninitialized source. Hash-only CAS would miss a
withdraw/restore cycle of identical bytes; admission version and activity are
therefore part of the token. The audit ordinal supplies source/episode versions;
the model epoch still counts definitions, not source or encoding revisions.

A valid revision replaces the two managed episodes and their readings in one
transition. Old definitions remain conservative definitions; current queries
use current source facts and the new source version. A withdrawal removes the
managed episodes/readings and deactivates web application. Restore is a checked
new admission. Generic observe/retract cannot mutate the managed episode names.
Unrelated compatible state, numeric scopes and definitions are retained.

Same URL and byte-identical content, with a current token, returns `unchanged96`:
no new event, support, episode version or definition. A different URL with the
same bytes may revise provenance, but replaces rather than accumulates the
managed observations. There is only one active source slot for this prototype.

A rejected update or failed checkpoint does not publish partial state. This
tracks the **last admitted artifact**, not a continuously monitored web truth.
If a fetched newer artifact cannot be interpreted, the caller must explicitly
withdraw the old source or keep it labeled historical; no autonomous refresh or
quarantine/revocation service is implemented. A query supplied with a stale
artifact is not silently repaired using the current one.

Frozen models deliberately retain historical semantics. Withdrawing a source
from today's model does not mutate previously exported models. Generic Basis91
inference on explicit user premises is not a source-revocation service; the
source activity/version contract is enforced by the web query/infer API.

## Execution, checker and budgets

`web-infer` validates the artifact's hash/extraction and its match to the model's
active source, constructs a fresh finite episode from the requested view, then
runs existing Attention92 application. Its independent primitive coverage/row
gates reject omissions and wrong work; `raw96` uses the existing primitive route.
Query-worker rejection/budget failure is surfaced as unknown with no unfinished
rows. Source-extraction failure rejects admission, with the old snapshot intact.

A complete answer is `source-claims96`, not a theorem of geography. It includes
all logical roles, original fact IDs, source digest/version, row numbers and cell
byte ranges. A missing/unresolved row is unknown, not a globally empty relation.
A complete empty result is only finite nonmembership under supplied complete
premises. An external Python raw-CSV assignment/witness oracle checks final
results without using worker projections or learned definitions. The Python
worker and external oracle share the standard-library CSV reader and declared
schema; their binding enumeration is separate. Native worker/checker paths also
share some binding/type utilities. These are independent control paths and
finite external checks, not a proof of wholly independent implementations.

Native verification caches at most two entries. Keys include copied full hex
bytes and copied digest, not only source ID/digest or a mutable worker alias.
The cached value contains decoded atomic observations, not compound answers or
learned definitions. Source bytes remain permitted query input in core-only
experiments; training support tables, learner/live owners and replay are not.

Bounds: 262,144 original bytes, 512 CSV records including header, 80 columns,
8,192 raw bytes per field, one source slot, two managed episodes. Existing limits
remain: signature <=4, episodes <=4, facts/nodes <=8, patterns <=3 atoms/4 roles,
global library <=8 definitions, audit <=32, fuel <=200000. No unbounded web crawl,
large/noisy corpus or long-term continual growth is demonstrated.

## Trust and licensing

SHA-256 and native extraction establish agreement with supplied bytes, **not**
that a URL claim was authenticated or that a website is correct. The trusted
stdlib HTTPS acquisition uses normal TLS validation, a repository/path/commit
URL allowlist, restricted redirects, size/timeout limits and a verified local
cache. Native replay proves consistency with recorded inputs, not remote origin.
A malicious caller can fabricate consistent bytes and relabel their URL; signed
origin attestations and an adversarial-host security boundary are out of scope.

The upstream table combines sources with restricted or unclear terms, as its
README and attribution explain. Raw bytes and full packets remain in a private
local cache/temporary files and are not part of the product inventory. Public
experiment artifacts record aggregate checks and limited examples, not a bundled
copy of the table. Reproduction requires prior explicit acquisition. Do not
assume the project's software license covers the external data or commercial
redistribution. See `experiments/web96/source/` for pinned provenance/notices.

## Experimental interpretation

The meaningful result is a checked **web source -> same learner -> changed
reusable inference organization** path. It is not merely a cache ingest, but it
also does not establish the broader latent-axiom hypothesis. Fixed schema,
selection curriculum, conservative definition grammar and admission rules are
foundations, not newly invented semantics/conditions.

Controls distinguish no admitted extraction, no formation, prior absent at the
later formation step, and EML versus direct-logical representation. The
`no-extraction96` arm omits the worker extraction claim: the checker can decode
the source, but must reject rather than install its own reference observations. Raw inference can
already answer these conjunctions. The staged no-prefix arm has one rather than
two admissions and is not an equal-total-compute impossibility result: a separate
intervention supplies one additional ordinary learn step and recovers R2.

Future work includes genuinely new empirical conditions/definition revision,
richer schemas, ambiguity/noise and source conflict, real numeric observables,
source-independent transfer and only later broader text interpretation. None is
silently delegated to an external LLM or manually prepared semantic answers.
