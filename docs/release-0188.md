# Release 0.0188 — web observation boundary (candidate)

- Date: 2026-11-10
- Predecessor: 0.0187. Candidate, not promoted.
- Scope: fetch a simple-English web page, cache it, extract one observation with
  URL/quote, convert it to an NL fact, and answer an English query through the
  proof boundary.

## Changes

```text
src/dlm/web.l
  w-observation ID URL QUOTE SUBJ OBJ
  w-to-records

adapters/web_nl.py
  cached Simple Wikipedia fetch
  sentence extraction

scripts/web_nl.sh
  fetch → generated web_observations.l → Maru query
```

## Experiment

```text
WEB OBS 1
url=https://simple.wikipedia.org/api/rest_v1/page/summary/Dog
WEB QUOTE Dogs are mammals
WEB1 proved Yes, a dog is a mammal.
WEB2 unknown I cannot prove that a dog is a plant.
done-web
```

## Self-host

```text
compiler.sh reproduce
→ 20261110T075901Z-5684
compiler.sh verify 20261110T075901Z-5684
→ Verified
```

## Measured

```text
native normal   57 checks / 0 FAIL
native safety-2 57 checks / 0 FAIL
self-host       verified
```

## Still not

- one cached page, one simple sentence pattern
- observations are per-run, not a persistent store
- no web rule induction yet
- no multi-page source/contradiction handling
- proof remains the truth gate
