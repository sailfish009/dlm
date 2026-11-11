# basis_repl — accumulated basis axioms (0.0185)

Run:

```bash
./scripts/basis.sh
```

Two learned programs are accumulated as basis axioms A and B. Both active rules
prove their targets. Deactivating B leaves A usable and makes the B target fail.
Rollback restores B.

This demonstrates data → learned rules → basis axiom → proof separation.
