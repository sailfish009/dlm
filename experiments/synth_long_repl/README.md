# synth_long_repl — bounded four-fact chain synthesis (0.0165)

Run:

```bash
./scripts/synth_long.sh
```

The target needs four hops. Two- and three-fact candidate spaces are empty; the
bounded walker finds a four-fact rule, which covers both training positives and
transfers to a held chain.

This is bounded chain synthesis, not general ILP.
