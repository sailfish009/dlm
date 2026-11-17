# Release 0.0256 — reviewer repair of the 0.0255 native search ports

- Date: 2026-11-16
- Predecessor: 0.0255 (preserved; builder-owned)
- Type: repair release (created by the reviewer session under the user's
  "직접 수정하거나 지시" authorization, 10:02 KST; pattern of 0.0243)
- Runtime: `20261114T001318Z-27176` (reused; compiler sources unchanged)
- Review: `/research/code-review-0255.md`, evidence `/research/review-0255-evidence/`

## Repairs (all confirmed by discriminative probes before fixing)

| finding | defect | fix |
|---|---|---|
| F1 | `cand_features` skipped unused goal slots (`pst.c` RELOB block), leaving stale values in the static eval buffers; training collection is calloc-zero → train/eval feature mismatch; greedy ≠ beam W1 | zero-fill skipped slots (`for z<CAND_GOAL_FEAT out[k++]=0.0`) |
| F2 | subsumption table reset once per split, shared across worlds | `subs_n = 0` per world in `policy_metrics_dfs` |
| F3 | preorder `subs_add` let an ancestor dominate its own descendants (unsound even exhaustive) | register after the child loop (postorder, closed-list) |
| F3b | `pack_facts_u64` returned `int`: 36-bit fact masks truncated to 32 bits and sign-extended; entity-5 predicates 2–5 corrupted in every dominance test | return type `uint64_t` |

F3b counterexample: seed 11 test world 11, goal=(e5,p2) — exactly the corrupted
bit region. Winning subsets {71,37,76,55}/{71,39,76,55}/{71,42,76,55} were all
pruned; exhaustive sub1 gave 0 goals vs bound 1. After the fix, exhaustive
DFS(sub1,prop0) and DFS(sub1,prop1) both equal the exact bound on 100 worlds
(0.8492/0.8200, seed 11).

## New gates (verify.sh, V0256-SOUNDNESS-PASS)

1. EXH-ORACLE: per seed, exhaustive DFS(branch=24, sub1, prop1) goal/full ==
   budget-exact bound goal/full (run_port.sh emits EXH-ORACLE lines).
2. GREEDY-W1: greedy == beam W1 aggregate on the test split (F1 regression).
3. ONECOMMIT: `--onecommit-audit` scan, 0 worlds where a single root commit
   proves 2+ goals (prop-bound assumption guard).

`scripts/verify_release.sh` additionally requires V0256-SOUNDNESS-PASS and uses
version-suffixed /tmp logs (no collision with concurrent 0255 runs).

## Results (SEEDS=5, clean features)

(pending — filled after ./run.sh && ./verify.sh completes; the 0255 table is
invalidated by F1 and must not be cited)

## Left to the builder (next version)

- R255-6: Maru Q16 side port of the search (user requirement) or explicit
  boundary documentation; `maru/*.l` is unchanged here.
- Re-derive the DFS-vs-beam ≥10pp gate threshold from clean data (the 0255
  threshold was calibrated on contaminated features).
- Branch-limited dominance remains a heuristic (review F4): disclose the
  residual sub1-vs-sub0 gap; the "cannot derive more" argument holds only for
  exhaustive closed-list search.
