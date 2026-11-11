# proof_cache_repl — dependency-aware proof cache (0.0175)

Run:

```bash
./scripts/proof_cache.sh
```

A repeated goal is served from cache with 0 probes. Adding an unrelated fact
still preserves the cached proof. Removing a fact used by the proof invalidates
the cache and the query fails. The cached proof is rechecked.

This is an in-memory positive-proof cache, not a persistent cache service.
