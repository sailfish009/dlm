# synth_template_repl — recursive program from one long positive (0.0167)

Run:

```bash
./scripts/synth_template.sh
```

Only one positive `ancestor(a,e)` and parent edges are given. The synthesizer
proposes a seed plus recursive step, covers the positive, rejects the negative,
and transfers to a held chain. Seed-only and frozen controls fail.

This removes the need for direct `ancestor(a,b)` examples, but the recursive
rule shape is still fixed.
