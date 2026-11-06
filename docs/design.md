# 0.0107 design — minimal native core, then the north star

Date: 2026-11-06. Status: M1 (proof/store) plus two review rounds, and M2's first half: the
learning transition that changes the basis while the data stays.

## 1. Why a fresh tree

The lineage analysis (`/research/analysis_20261106.md`) showed three resets that
each dropped capabilities, and a fourth pivot (0.0089) that replaced the
code-understanding line with a basis-formation line. 0.0103 therefore starts from
Maru plus a new `src/dlm`, and keeps the old trees read-only.

## 2. Decisions

| decision | reason |
|---|---|
| one state, one event log | 0.0102 had seven state owners and the 91 engine was not driven by `dlm step` |
| derived facts are never stored | replay recomputes them; a snapshot cannot smuggle a conclusion |
| proof term per atom + independent checker | a derived answer must be justifiable without rerunning the search |
| proof DAG validation | `given` only for extensional facts; every child's own stored proof must check, with a bounded walk, so neither an invalid nor a cyclic derivation supports a conclusion |
| EDB predicates cannot be rule heads | closed-world negation must stay about a base that only observation extends |
| session lock + epoch check | two writers must not silently overwrite each other |
| negation only over EDB | stratification becomes syntactic; no negative cycle can be written |
| budget exhaustion is `unknown` | keeps "not found" distinct from "false" |
| provenance at (source, record, scope) | scope isolation and retraction are tested, not asserted |
| background laws are GIVEN and hashed into the snapshot | changing the laws invalidates old evidence instead of silently reinterpreting it |
| reduction is an untrusted adapter with pinned hashes | keeps the kernel small; Python parsing is off the trusted path |

## 3. Trust boundary

```text
adapter  -> facts (data)      untrusted; hash-pinned, never evaluated as code
kernel   -> closure + proofs  trusted; the only place that answers a query
session  -> events + state    trusted for replay; storage validates by replay
reading  -> sentences         untrusted text; emitted only with a checked support
```

The reading layer is deliberately outside the kernel: a sentence is a comment on
a proof. If the proof does not check, the sentence is withheld (abstain).

## 4. What M1 measures

| measure | value |
|---|---|
| reduced facts from `main.py` | 209 (pinned `cbe0159…`) |
| closure size | 231 |
| readable facts | 157 (N1 135, N2 10, N3 12) |
| sentences whose support checks | 157 / 157 |
| library-only view | 121 (N1 99, N2 10, N3 12) |

0.0062 reported 42 sentences across N1–N9 on the same source, but selected them;
0.0103 reports all readable facts. The numbers are therefore **not** a parity
claim. The comparable property is: every emitted sentence has a checked proof.

## 4b. The learning transition (0.0107)

```text
observations (unchanged) → residual structure → candidate unit → checked
expansion → basis grows → plans reconstructed → next query uses the unit
```

- Unit: `(def107 ID VARS PATTERN BODY)`; `BODY` may call an earlier unit.
- Support: distinct records (one observation = one record); retraction lowers it
  and the unit becomes inactive without being deleted.
- Revision replaces a unit's pattern (same arity) and re-validates dependents;
  those that no longer expand correctly are dropped.
- Conservation is tested: answers and witness sets are identical before and
  after learning, and the observation list is byte-identical.
- Measured effect: plan steps 3 → 2; executed joins are unchanged, so this is a
  change of inference unit, **not** a speedup.

`(dlm 'rules ...)` remains a configuration command that resets the session; the
learning operator is `(dlm 'learn)` or the `learn` agenda item used by `step`.

## 5. M2+ (not implemented)

1. **Definitions**: conjunctive views with `call`, conservative expansion check,
   support ≥ 2 distinct records, then rewrite of query plans. Needed before
   "learning" can be claimed.
2. **Negation with record scope**: closed-world only over a declared domain;
   certified absence (N9) with witnesses.
3. **Lemma mining** from repeated proof fragments, with reuse accounting.
4. **N4–N9** reading: composition order, architecture, causal, purpose, analogy,
   certified absence.
5. **Native reduction**: a Maru subset parser whose output hash equals the
   adapter's, with a differential test as the gate.
6. **Cooperative idle**: `start/pause` on the original REPL idle hook.

Each of 1–5 has a falsifier that must fail before the feature is claimed: forged
proof, scope leak, record-mixing join, stale summary, and adapter/native hash
mismatch respectively.
