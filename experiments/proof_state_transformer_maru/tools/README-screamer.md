# Screamer × native transformer (integration experiment, 2026-11-16)

Toolchain (no root): SBCL 2.6.9 installed from conda-forge by direct package
download into `/research/toolchain/sbcl` (see memory entry). Screamer 4.0.0 is
used in place from `/research/screamer` (no deps, no build).

Integration:

```text
C  bin/serve --serve <weights>      reads  "<world> <nrules> <r1> ... <rn>"
                                    writes "<nlive> <id> <score> ..."
CL tools/screamer_search.lisp       DFS with backtracking (Screamer either/local/
                                    all-values), children ordered by the C scores
```

Run:

```sh
export PATH=/research/toolchain/sbcl/bin:$PATH
./bin/pst_hard_relob --dump-test out/hard_worlds_d4.txt --test-n 100 --seed 11 \
    --goaldepth 4 --goal-scan
sbcl --noinform --disable-debugger --script tools/screamer_search.lisp \
     bin/serve out/hard_worlds_d4.txt probes/w_11.bin <branch> 100
```

Observed (5 seeds, 100 worlds, genuine depth 4, branch = children kept per node):

```text
branch M   CL best_frac   C beam goal   C greedy
1          0.0905         W=1 0.2365    0.1159
3          0.2095         W=3 0.3587
5          0.2318         W=10 0.4651
exhaustive 0.9333 (10 worlds)
bound      0.849 (C, 0253)
```

Findings from the cross-check (not yet resolved):

1. C `policy_world` (greedy) and C `policy_world_beam` with W=1 disagree on
   **100/100** worlds, so one of the two policy paths is wrong; the W=1 anchor of
   the 0254 width curve is therefore suspect (the monotone trend is not).
2. CL top-1 and C greedy differ (0.0905 vs 0.1159) on the same dump/weights.
3. Latent fixture defect: `NATOMS=40` is used for noise-fact atom ids while facts
   are 6-bit × 6 entities (36); `1u << randbelow(40)` truncated into uint8 masks,
   so noise facts are partly dropped/aliased.

Not yet started (blocked on toolchains): Rocq (needs ocaml/dune/coqc) and
Silicon (needs java/sbt/z3 + the silver submodule). Install recipe is the same
direct conda-forge download used for SBCL.
