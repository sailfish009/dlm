# synth_rank_repl — ranked synthesis (0.0163)

Run:

```bash
./scripts/synth_rank.sh
```

Two candidates both explain the triggering path goal. First-fit picks an
alternative that covers only 1/2 training positives. Coverage ranking selects the
hop1/hop2 rule, which covers 2/2 and transfers to a held path.

This is a fixed-candidate composition ranking experiment, not general ILP.
