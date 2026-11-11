# graph_dce_repl — dead-node elimination (0.0180)

Run:

```bash
./scripts/graph_dce.sh
```

An extra unused fragment is present in the graph. Backward reachability from
`p` and `t` keeps the live template/program/task, drops the unused fragment, and
retains the `seed → p` edge. The graph run summary is unchanged.

This is root-relative DCE, not full graph optimization.
