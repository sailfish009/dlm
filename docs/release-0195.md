# Release 0.0195 — persistent web recursive self-supervision (candidate)

- Date: 2026-11-10
- Predecessor: 0.0194. Candidate, not promoted.
- Scope: actual web data → recursive self-supervision → persistent basis →
  held-out proof in a fresh process.
- Analysis: `/research/analysis-web-recursive-persist-0195.md`.

## Loop

```text
actual Simple Wikipedia pages (7)
→ 7 subclass edges
→ 5 training edges + path labels
→ recursive rule program R1
→ self-labeled closure (8 positives)
→ recursive re-induction R2
→ persist basis
→ fresh process load
→ held-out web paths
```

## Experiment

Process 1:

```text
SAVE /tmp/dlm-web-recursive-basis.l rules=2
done-rec-persist-p1
```

Process 2:

```text
LOAD (0 2)
HELD 3/3 NEG fail RULES 2
done-rec-persist-p2
```

Held-out: `dog→living-thing`, `sparrow→living-thing`, `plant→living-thing`.
Negative: `living-thing→dog` rejected.

## Self-host

```text
compiler.sh reproduce
→ 20261110T101357Z-14054
compiler.sh verify 20261110T101357Z-14054
→ Verified
```

## Measured

```text
native normal   61 checks / 0 FAIL
native safety-2 61 checks / 0 FAIL
self-host       verified
```

## Still not

- 7 pages, heuristic extraction
- manual held-out edge split
- full-store dump, no journal/atomicity
- self-labeling is training-graph closure, not transformer behavior
- no contradiction/lock policy
