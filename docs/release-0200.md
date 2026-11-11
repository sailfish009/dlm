# Release 0.0200 — multi-round self-supervision in one Maru process (candidate)

- Date: 2026-11-10
- Predecessor: 0.0199. Candidate, not promoted.
- Scope: run repeated self-label → re-induce rounds in one Maru process on actual
  web subclass facts, with saturation reporting.
- Analysis: `/research/analysis-selfssl-0200.md`.

## Changes

New `src/dlm/selfssl.l`:

```text
ssl-round     synthesize → basis axiom → closure self-label → new positives
ssl-new-pos
```

`scripts/selfssl.sh` now:

```text
generate web_data.l
→ run one Maru process with three rounds
```

The old stale `learn` mode call is gone.

## Experiment

```text
ROUND 1 pos=8 new=5 rules=2
ROUND 2 pos=8 new=0 rules=2
ROUND 3 pos=8 new=0 rules=2
FINAL pos=8 rules=6 HELD 3/3 NEG fail
done-selfssl
```

Round 1 adds five self-labeled positives; rounds 2–3 add none. The loop
saturates. Held-out web paths remain proved; negative remains rejected.

## Self-host

```text
compiler.sh reproduce
→ 20261110T111647Z-29851
compiler.sh verify 20261110T111647Z-29851
→ Verified
```

## Measured

```text
native normal   66 checks / 0 FAIL
native safety-2 66 checks / 0 FAIL
self-host       verified
```

## Finding

Each round adds another basis axiom with the same two rules: final active rules
= 6. The proof result is unchanged. This is why axiom CSE/DCE should be applied
to the accumulated basis before the next round.

## Still not

- batch process, not idle REPL resident loop
- no start/pause/stop REPL lifecycle
- duplicate basis axioms accumulate (rules 6)
- no autonomous query/curriculum generation
- proof remains the truth gate
