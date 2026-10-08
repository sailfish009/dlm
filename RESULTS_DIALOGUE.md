# DLM v0.0003 — Grounded dialogue results (W4)

Governed by `PRE_REGISTRATION.md` (section A) and `/research/GUIDELINES.md`.
Claim tier: **Tier 2** for the grounding exact-match numbers, **Tier 1** for the
retrieval/abstention behaviour. No Tier 3. No "advantage" language. 6GB is a
constraint, not a claim.

## What was added

`dlm/dialogue.py` assembles parts that already existed into an actual loop:

```
utterance -- Grounder --> Grounding(kind=query|assert)
    assert -> contradiction check -> kb.add_fact (user provenance)
    query  -> DecisionEngine.noul(atom) -> proof -> template verbalizer
    ungrounded / non-ground atom -> ABSTAIN;  negated contradiction -> REJECT
```

* **No generation.** A reply is one of a fixed set of templates; the only
  dynamic part is a rendering of the proof tree (`Proof.render()`).
* `ask()` / `tell()` force the intent, which resolves the ambiguity of a surface
  form that could be either a question or a statement; `say()` trusts the
  grounder's `kind`.
* `provenance` labels a conclusion `user` if **any** proof leaf was asserted by
  the user, and `process` if it rests only on seed facts/rules.

Files: `dlm/dialogue.py`, `tests/test_dialogue.py` (17 tests),
`examples/dialogue_demo.py`, `run_dialogue_eval.py`, `tests/test_dialogue_eval.py`.

## Measurement (matched arms)

Single variable = the **grounder**. Everything else is identical (KB, scripted
turns, forced intent, deterministic verbalizer).

| arm | coverage | exact-atom | verdict | confident-wrong | abstain | verdict-when-grounded |
|---|---|---|---|---|---|---|
| `t1_only` (grammar, train phrasing) | 0.545 | 0.600 | 0.500 | 0 | 0.455 | 1.000 |
| `chain` (T1 + lexical T2)           | 0.727 | 0.800 | 0.750 | 0 | 0.273 | 1.000 |

* `verdict_accuracy` counts an **abstention as an incorrect verdict** (end-to-end
  usefulness); `verdict_accuracy_when_grounded` excludes abstentions.
* By phrasing (`chain`): train coverage 1.000 / exact 1.000; unseen coverage
  0.500 / exact 0.500; out-of-domain coverage 0.000 (abstains, as required).
* **Judgment: `fallback_helps`** — here the lexical fallback adds coverage
  **without** adding any confident-wrong verdict.
* **SMALL-N CAVEAT**: n = 11 turns (4 unseen). This is a scripted smoke test of
  the loop, **not** a general dialogue claim.

### Why this is not in tension with NL-6

`NEGATIVE_LEDGER.md` NL-6 compared the lexical grounder against the *learned*
grounder (`control_favored`: lexical 0.547 > learned 0.352). Here the
alternative to the lexical fallback is **abstention**, so the fallback can only
add answers. Both statements are true at once and are about different contrasts.

## Honest limits

1. **The dialogue ceiling is the grounder's.** Unseen phrasing falls to the
   lexical T2, which is imperfect. `examples/dialogue_demo.py` shows a
   mis-grounding live: *"is alice the mother of bob"* retrieves
   `ancestor(alice,bob)` with `conf=0.63`, so DLM answers **yes** with a sound
   proof **of the wrong atom**.
2. **Closed-world negation** ("not derivable" = false) is an assumption, not a
   theorem; a negative assertion is "consistent" iff the positive is not
   derivable, and is never stored.
3. **No web ingestion yet.** W1–W3 (`web.py` / `extract.py` / `ingest.py`) are
   unimplemented, so the KB still grows only from the user, not the internet.
4. **Rule induction is unchanged** and can be over-general (in the demo it
   induces `grandparent :- ancestor`).

## Reproduce

```bash
python3 -m pytest -q                       # 83 tests
python3 run_dialogue_eval.py               # writes artifacts/dialogue_eval.json
PYTHONPATH=. python3 examples/dialogue_demo.py
PYTHONPATH=. python3 examples/grounding_demo.py
```

## Reopen conditions

* A harder split (entity-held-out) or more supervision that lets the **learned**
  T2 beat the lexical one (reopen NL-6).
* Any turn where `confident_wrong > 0` — that would be a new, more serious
  negative than NL-6 and should be added to `NEGATIVE_LEDGER.md`.
* Once W1–W3 land, re-run this eval with fetched facts to check provenance and
  contradiction handling end to end.