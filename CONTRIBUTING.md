# Contributing

DLM is a deductive system. It must not smuggle generation, language modelling,
or attention into the reasoning path.

1. Start from a concrete entailment the system must decide, and the KB that
   supports it. State variables, arity, and whether the Herbrand base is finite.
2. Keep the parts separate: terms/unification, knowledge base, deduction,
   induction, retrieval, decider, pipeline. Do not hide a decision inside a
   predicate name.
3. Keep facts ground and keep rules safe (every head variable appears in the
   body). Reject unsafe rules instead of running them.
4. No function symbols in v0.0001. This is what makes the fixpoint finite and
   SLD terminating; adding them is a separate, declared design change.
5. Return a proof, not just a truth value. An answer without a trace is not an
   answer here.
6. The decider is a gate, never an oracle. It may not reduce recall: the
   pipeline must fall back to the full candidate set when the gate yields
   nothing. Report fast-path candidate reduction, fallback rate, and recall
   separately.
7. Induced rules must never cover a declared negative. Check this explicitly.
8. Record negative results and registered nulls. Do not tune around an
   unlearnable feature conflict; name it and schedule it.
9. No "advantage" language, no quantum or physical resource claim. The 6 GB
   result is a constraint that was measured, not assumed.
10. Keep examples self-contained. No machine-specific paths, credentials, or
    proprietary data.

```bash
python -m pip install -e .
python -m pytest tests -q
python examples/induction_demo.py
python examples/deduction_demo.py
python run_demo.py
python probe_vram.py   # requires CUDA for the GPU section
```

See `PRE_REGISTRATION.md` for the claim tiers and `RESULTS.md` for provenance.