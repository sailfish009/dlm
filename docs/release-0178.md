# Release 0.0178 — NumPy graph embedding sidecar (candidate)

- Date: 2026-11-08
- Predecessor: 0.0177. Candidate, not promoted.
- Scope: attach a small deterministic NumPy embedding to explicit graph nodes;
  verify dimension/node/hash; use it for ranking only.
- Analysis: `/research/analysis-graph-embedding-0178.md`.

## Changes

`src/dlm/graph-ir.l`:

```text
mg-embedding ID DIM VEC HASH
mg-embedding-graph
mg-check-embeddings
mg-embedding-score
mg-rank-query
```

`adapters/graph_embed.py`:

```text
node features
+ normalized adjacency
+ fixed seeded NumPy projection
→ 8-dim embedding
→ Maru mg-embedding records
```

`scripts/run.sh` gains `proof-extra` to load the generated embeddings file.

`experiments/graph_embed_repl/` + `scripts/graph_embed.sh`.

## Experiment

```text
GRAPH ok
EMBED ok
EMBEDDINGS 4
RANK ((p 1000000729790) (t 371270909353)
      (seed 344082641939) (fseed 298811334744))
BADDIM (rejected107 mg-embedding-dim)
BADNODE (rejected107 mg-embedding-node)
MATCH t active=1 covered=1/1 conflict=0 result=selected
RUN (summary tasks 1 solved 1 active (p))
done-embed
```

The graph runs normally with and without embeddings. Bad dimension and a
missing graph node are rejected.

## Fixed-point encoding

Maru's reader does not accept `.396747` as a float literal; it tokenizes the dot
separately. NumPy floats are therefore rounded to fixed-point integers
(`scale = 1,000,000`) before emitting the Maru `mg-embedding` file. Dot-product
order is preserved; scores are large integers and are advisory only.

## Self-host

```text
compiler.sh reproduce
→ 20261109T113717Z-12722
compiler.sh verify 20261109T113717Z-12722
→ Verified
```

## Measured

```text
native normal   48 checks / 0 FAIL
native safety-2 48 checks / 0 FAIL
self-host       verified
```

## Still not

- Embedding is offline and graph-fixture based; no live Maru export/import.
- No co-input/spectral features yet.
- Embedding is not used to select a proof or admit a rule.
- Fixed-point quantization is deliberate; no float literals in Maru.
- Truth remains with the proof checker.
