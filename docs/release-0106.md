# Release 0.0107 — the data stays, the logical basis moves

- Date: 2026-11-06
- Predecessor: `dlm_v0.0105` preserved. Input: `/research/axiom-to-data-review-20261106.md`.
- Status: M2 (first learning transition). No attention, no gradients, no GPU.

## What the review said, and what changed

The review's core point: in 0.0105 the only way to change the logic was
`(dlm 'rules RULES)`, which **also wipes the observations** (reproduced: 1 → 0).
That is configuration, not learning. 0.0107 adds the missing direction.

```text
observations D/E preserved
  → residual structure found in the data (connected 2/3-atom patterns, one
    observation = one record)
  → a candidate unit is proposed and CHECKED (expansion equality)
  → the basis grows (b1, then b2 which CALLS b1)
  → existing query plans are reconstructed (3 steps → 2)
  → the next inference uses the new unit
  → retraction lowers support; the unit stays but stops being applied
```

Definitions are conservative: they add no fact and change no answer. What moves
is the inference unit and its plan. This is exactly the distinction the review
draws between *definition/lemma basis* (meaning-preserving) and *world laws*
(which need counterexamples and scope; not implemented here).

## Demonstrated (reproducible)

`./scripts/run.sh proof experiments/learn/run.l` — three records in which one
owner makes three distinct calls:

```text
before defs=0
plan for the 3-atom query: raw 3, planned 3 (no cover)
rows = 18
after defs=2
b1 = 2-atom unit (support 3)
b2 = 3-atom unit whose body is (call b1 ...) + one atom (support 3)
plan for the same query: raw 3, planned 2, cover b2
answers-identical = true     (rows and witnesses)
retract r2, r3 → support 1 → units remain, active=false, plan reverts to 3
revise b1 to another supported 2-atom structure → b2 dropped, calls plan uncovered
```

Native checks pin each step (basis 0→2, second unit calls the first, steps 3→2,
observations byte-identical before/after learning, answers and witnesses
unchanged, support drop, revision).

## Honest reading of the result

- **This is learning** in the review's sense: the data does not change, the basis
  does, and later inference uses it. It is not a speedup: a call expands to its
  body, so the executed joins are the same. The measured gain is **plan steps**
  (3 → 2), which is what the review asked to separate from efficiency.
- **Support is record-based** (one observation = one record). Repetition inside a
  record does not raise support; a duplicated record would, which is why the
  fixture uses three independent records.
- **Candidates are structural**: constants are abstracted to variables per
  record, and patterns are compared by the smallest serialization over all
  variable bijections (name sorting alone is not canonical).
- **Not world laws.** No non-conservative axiom is admitted; hypotheses with
  counterexamples, scope and retraction are still future work (M4).
- **No N9 or sentence-count gain is claimed.** The north star is unchanged:
  157 sentences, levels 135/10/12.

## Limits

- Enumeration is bounded to records of ≤24 facts; the 209-fact MNIST record is
  skipped, so the north-star slice forms no unit.
- Only 2- and 3-atom units, no recursion, no lemma layer, no utility-based
  demotion beyond support.
- The reduction is still an untrusted adapter with pinned hashes.
- Maru's reader still aborts on syntactically invalid bytes.

## Verification

`reproduce → verify → promote`, three-generation LLVM/stripped equality, native
and Python suites under the verified binary. See `docs/verification.log`.