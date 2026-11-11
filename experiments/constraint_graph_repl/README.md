# constraint_graph_repl — graph constraints (0.0177)

Run:

```bash
./scripts/constraint_graph.sh
```

Hard constraints are checked before the graph is accepted. A false soft
constraint is reported but does not reject the graph. A false hard constraint
and a malformed expression are rejected.

This is a finite constraint evaluator; hard constraints still do not replace
the proof checker.
