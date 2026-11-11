# graph_schedule_repl — embedding-prioritized scheduling (0.0179)

Run:

```bash
./scripts/graph_schedule.sh
```

Embedding similarity chooses among currently-ready graph nodes. The ranked order
differs from the base order, but `seed` still precedes `p`, and the graph run
summary is identical.

This is advisory scheduling, not proof selection.
