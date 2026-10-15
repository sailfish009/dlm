# DLM v0.0039 abstract experiment — label-free abstraction

No labels. From a theory + facts alone, fold a recurring body conjunction into an
**invented predicate**, certify with the kernel that the closure is preserved, and
measure that the form-tree description length shrinks and that a fixed inference
budget covers more of the same closure.

```bash
./experiments/abstract/abstract.sh
./experiments/abstract/abstract.sh --rules 8 --core 4 --budget 60 \
    --json experiments/abstract/reports/abstract.json
```

## Falsifiable criteria

1. `closure_preserved` — kernel re-derives the identical closure (`dlm.abstract.closure_preserved`).
2. `dl_strictly_decreases` — form-tree DL of the theory shrinks (`dlm.abstract.theory_dl`).
3. `budget_coverage_gain` — at a fixed **join-work** budget the abstracted theory
   recovers more of the same closure than the un-abstracted one.

Conservative abstraction cannot derive *more* atoms; the only honest way coverage can
rise is under a fixed **inference budget** (the DreamCoder mechanism). Measured here
on *join work* (unification attempts): a baseline rule that joins four body literals is
one application, so a rule-application budget hides the win. There is a **seed cost** —
the definition must be derived before any folded rule fires — so the abstracted theory
lags at very small budgets and dominates once past the crossover (~budget 300 here).`