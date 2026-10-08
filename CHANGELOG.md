# Changelog

## 0.0.1

First release of the Deductive Logic Model. A local, non-generative reasoning
system: it induces rules, retrieves a knowledge base, and derives answers with
an auditable proof. No language model and no free-text generation are used.

- `dlm/terms.py`: terms, atoms, unification (Robinson + occurs-check). No
  function symbols, so the Herbrand base is finite and deduction terminates.
- `dlm/rules.py`: function-free Horn clauses (`Rule`), facts, alpha-renaming.
- `dlm/kb.py`: predicate-indexed knowledge base with a Datalog safety check
  (every head variable must appear in the body).
- `dlm/deduce.py`: forward least-fixpoint closure and SLD backward chaining,
  returning a `Proof` tree; the two agree on every ground atom.
- `dlm/generalize.py`: inductive rule learning by anti-unification (LGG) over
  positive and negative examples, bounded in body length; recovers
  `grandparent(?x,?z) :- edge(?x,?y), edge(?y,?z)` and never covers a negative.
- `dlm/retrieval.py`: predicate-indexed candidates and an 8-feature vector.
- `dlm/decider.py`: a 161-parameter NumPy MLP gate (plus a torch mirror), with
  temperature calibration. This is the only learned component.
- `dlm/pipeline.py`: orchestration with a recall-preserving System-2 fallback:
  if the gate yields no answer, deduction retries with the full candidate set.
- tests: 9 pytest cases (unification, safety, forward/backward soundness, proof
  trace, induction, feature contract, decider, fallback recall).
- examples: induction and deduction walkthroughs; a VRAM probe.

Honest scope: claim Tier 2 for the engine and induction, Tier 1 for the decider,
no Tier 3. The 6 GB GPU result is a feasibility constraint, not an advantage.
Registered null (P4): the 8 hand features cannot separate an instantiable,
same-shape, semantically wrong rule from a good one; false positives persist in
both matched arms. Recorded, not hidden, in `RESULTS.md`.