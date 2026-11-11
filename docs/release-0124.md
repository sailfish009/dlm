# Release 0.0124 — proof-carrying sparse routing and a discrete routing policy

- Date: 2026-11-07
- Predecessor: 0.0123. Candidate, not promoted.
- Runtime: reuses the promoted 0.0116 release `20261107T064706Z-31624`.
- Scope: CPU-native candidate generation/execution. **Not** “attention on the
  CPU”, not full recursive self-supervision, and not a grammar extension.

## The direction in one paragraph

LLM attention is a dense differentiable routing+mixing operator fitted to
labels. DLM fixes the observations E and moves a discrete basis B. The useful
borrowing is the **interface**, not the numerics:

```text
Q  candidate pattern / roles
K  exact predicate/arity/position/value index
V  binding + witness/proof
routing   exact key lookup + unification (no softmax)
mixing    join + union of alternatives (no weighted average)
depth     definitions as compiled plans/views
cache     plan and index reuse, invalidated by evidence/basis changes
learning  discrete B updates, plus a small CPU routing policy over features
```

No dense N×N matrix, softmax, gradient or embedding is in the core.

## Added in 0.0122–0.0124

| version | change |
|---|---|
| 0.0122 | `d107-index.l`: predicate/arity/position/value indexes, indexed joins, indexed pair/triple candidates, record-scoped support, counters, candidate/join caps → `incomplete107` |
| 0.0123 | compiled definition plans (`p107-def-plan`) and active 2-atom views (`p107-views`); plans cached by exact body, never evidence facts |
| 0.0124 | discrete routing policy (`support`, `atoms`, `vars`, `cost` features); linear CPU weights updated by admission reward; ranking only, checker remains the gate; `(dlm 'route)` reports weights |

## Evidence

```text
indexed patterns2 == exhaustive patterns2
indexed patterns3 == exhaustive patterns3
indexed support    == exhaustive support (q2, q3), record-scoped
ordered roles       p(x,y) != p(y,x)
retraction          support 2 -> 1, matches reference
candidate cap       incomplete107; agenda surfaces incomplete; tick classifies unknown
plan reuse          compiled steps == stored body; reuse counter advances
views               active b1 becomes a 2-atom view; no facts added
routing             default zero; reward raises support and lowers atoms/vars/cost;
                    ranking does not bypass p107-def-ok?
```

Resident demo after 0.0124:

```text
[dlm] learned b1
[dlm] learned b2
status mode waiting round 4 definitions 2
(dlm 'route) -> route107 ((support 4) (atoms -4) (vars -4) (cost -4)) updates 4
```

```text
native normal      251 ok / 0 FAIL
native safety-2    251 ok / 0 FAIL
Python             16 tests OK
contract oracle    256/256 PASS (seed 116)
manifests          sources 78 / tests 30
```

The native small-suite time is not a speed claim: index building and routing
features add overhead on tiny records. The counters exist so larger-record
experiments can measure probes/joins rather than assume a win.

## What this does not do

- No grammar extension: still 2→3 atoms; `b1 + atom → b2`, then waiting.
- No deeper `c0→c1→c2`; F2 (nested admitted-call execution) remains open.
- No self-generated observations/goals, no self-evaluation/curriculum, no
  provenance tier.
- F1 (answer proof gate) remains open.
- No MLIR-native path; current Maru is LLVM. A future relational dialect is a
  separate compiler project.
- No claim that joins are attention or that this solves GPU-scale training; it
  removes the dense differentiable core from the deductive path.

## Reproduce

```sh
./scripts/run.sh test
MARU="$PWD/runtime/safety2/maru" ./scripts/run.sh test
python3 -m unittest discover -s tests -p 'test_d107.py' -v
./scripts/selfssl.sh --demo /tmp/model124.sexp
# maru> (dlm 'status) (dlm 'route) (dlm 'stop)
```
