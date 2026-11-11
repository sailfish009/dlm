# graph_embed_repl — NumPy embedding sidecar (0.0178)

Run:

```bash
./scripts/graph_embed.sh
```

The shell script runs the NumPy sidecar, writes `embeddings.l`, loads it into
Maru, checks the embedding records, and ranks graph nodes by dot product. The
graph and run summary are unchanged. Bad dimension and missing-node records are
rejected.

Embeddings are advisory only; they do not admit proofs.
