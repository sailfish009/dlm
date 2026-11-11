# Release 0.0137 — answer evidence chains and recursive ground-web experiment

- Date: 2026-11-08
- Predecessor: 0.0136. Candidate, not promoted.
- Scope: connect a checked answer to its web evidence and run a controlled
  recursive ground-web -> claim -> basis experiment on fixed real-web snapshots.

## Changes

- `p107-answer-evidenced` turns each answer witness id into
  `fact -> claim -> source/revision/span/quote`.
- `p107-answer-grounded?` was intended to require every witness to have a
  non-empty evidence chain. The 0.0137 implementation uses an any-witness test;
  `/research/review-0137-evidence/experiment-controls.py` reproduces the false
  positive and the missing derived-fact traversal. A fix belongs in the next
  candidate.
- New `adapters/ground_cache.py` emits a native ground store from cached real-web
  snapshots + extraction JSON. It validates SHA-256, UTF-8 byte spans and quotes;
  `--scramble` keeps spans/quotes but changes selected values for a control.
- New `experiments/ground_web/`:
  - six real Wikipedia intro snapshots with URL, revision, fetch time, sha256;
  - 23 hand-annotated claims with exact byte spans/quotes;
  - `self` arm selects the next source from the model's own first unresolved
    goal; `fixed`, `random`, `frozen`, `no-web`, `scrambled` are controls.

## Measured

```text
native normal   324 ok / 0 FAIL
native safety-2 324 ok / 0 FAIL
Python          18 tests OK
contract oracle 256/256 PASS
```

Experiment (one process and one shared session per arm):

| arm | final obs | final defs | final held solved | plan steps | plan calls | final gaps |
|---|---:|---:|---:|---:|---:|---:|
| self | 7 | 12 | 8/8 | 22 | 1 | 0 |
| fixed | 7 | 12 | 8/8 | 22 | 1 | 0 |
| random | 7 | 12 | 8/8 | 22 | 1 | 0 |
| frozen | 7 | 0 | 8/8 | 42 | 0 | 0 |
| no-web | 0 | 0 | 0/8 | 0 | 0 | 8 |
| scrambled | 7 | 12 | 4/8 | 22 | 1 | 4 |

The self arm acquired `PY,RU -> SE -> BU -> ML -> DL` over five rounds. The
random arm acquired the same final set in a different order and temporarily had
fewer definitions. The frozen arm still answered directly from observations: definitions are reuse/compression, not the truth source. On five multi-atom plan probes the raw order took 42 execution steps and the learned plan took 22, but an independent join-order-only control over all atom permutations also reaches 22. The learned basis is selecting the best join order on this probe; it is not an additional step reduction. One nested definition call remains, but does not beat the best raw order. The single-fact held answers are unchanged.

## Still not

- Extraction is hand-annotated from English Wikipedia intros; it is not a learned
  NL reader and it is not independently corroborated (`min-sources=1`).
- A matching quote proves provenance, not world truth. The scrambled arm shows
  that a structurally valid proof can rest on a semantically wrong extraction.
- The self arm did not beat the fixed natural order; no curriculum advantage is
  claimed.
- The plan probe is exact-pattern reuse, not subsumption: ground queries with
  constants do not match the fully abstract learned definitions. The 42 -> 22
  result is fully explained by join-order selection (see
  `/research/review-0137-evidence/experiment-controls.py`); it is not evidence of
  definition-level cost compression beyond ordering.
- No live web and no schema/entity held-out generalization.
