# Model semantics

- Atom: `(atom PRED (TERM ...))`; variable: `(var NAME)`.
- Rule: `(rule HEAD (BODY ...))`, nonempty body and range-restricted head.
- Episode: `(episode SOURCE FACTS CONFIRMED CONTRADICTED)`.
- Matching success is `(ok ENV)`; failure is `()`. Empty bindings are success.
- Closure is a least positive Horn fixpoint over finite ground constants.
- A proof is accepted only with actual fact/theory membership and a consistent
  shared substitution across all premises. No proof implies unknown, not false.
- State: `(model VERSION ROUND EPISODES GROUND EXPERIENCE HISTORY)`.
- Observe replaces episodes without altering theory. Learning revises Experience
  greedily in stored order against counterevidence, then admits at most one rule
  with new confirmed coverage and zero contradicted consequences.
- Ground is never learned or retracted. A Ground conflict produces an unchanged
  state. History retains admitted/retracted rule records.
- Proposal: `(proposal ACTION (transition BEFORE AFTER OUTCOME))`.
  Commit recomputes the full proposal. There is no persistent journal yet.

Differences from v0.0066: integer heuristic reward, no learned scorer, no explicit
unknown partition, no independent-source minimum, no tombstone exclusion from
future relearning. Sources are identifiers supplied by the caller, not verified
independence groups. These limits prohibit claims of full feature equivalence.
