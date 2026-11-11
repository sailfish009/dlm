# graph_cse_repl — duplicate node CSE (0.0182)

Run:

```bash
./scripts/graph_cse.sh
```

Two identical fragments and two identical templates are merged. Program
references and value edges are rewritten to the canonical IDs. The graph checks
and the run summary is unchanged.

CSE is limited to fragment/template nodes.
