# Heterogeneous source ingestion

This runner acquires or reads external text and commits its complete typed
`(source-document ...)` representation to the same model-state Store used by
self-SSL.

```bash
# Deterministic local/offline input
./experiments/ingest/ingest.sh --file README.md \
  --store /tmp/dlm65-store --fresh --offline

# Fresh external acquisition
./experiments/ingest/ingest.sh --query 'deductive logic model' \
  --providers wikipedia,github,web-search --limit 3 \
  --store /tmp/dlm65-store

# Continue recursive self-study from the same model state
./experiments/selfssl/selfssl.sh --store /tmp/dlm65-store
```

The transport is untrusted and cached. The candidate-blind extractor records raw
content, normalized text, a sentence or Python-AST tree, claims, content hash,
URI, revision, trust, and source-group. Only non-uncertain claims above the
confidence threshold enter an evidence episode. They remain facts, never learned
Ground rules. Network/cache misses produce an abstention rather than invented
content.
