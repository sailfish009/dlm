# DLM 0.0260 — hybrid reasoning layer: Rocq, Silicon and Screamer elements in the native proof-state transformer

> **Correction (review F1, 2026-11-16):** the `±` values in this note are
> 1 SE standard errors, not 2 SE intervals. The corrected 2 SE widths and the
> unchanged verdicts are tabulated in `docs/release-0264.md` (Appendix).

0.0260 continues the 0.0259 layer-substitution experiment on the same native
(C/LLVM IR + Maru Q16) proof-state transformer. 0.0259 ablated two transformer
readouts (sparse top-k attention, symbolic residual gate). 0.0260 keeps those and
adds three *reasoning* layers borrowed from proof engineering, each ablatable,
all under one training protocol and one evaluation protocol:

| Source | Element | Implementation | Compile flag |
|---|---|---|---|
| Rocq | independent proof certificate | parent-map re-derivation of every proved goal from base facts; the checker never trusts the search's closure | `-DCERT=1` |
| Rocq | obligation focus | relevance fixpoint from unproved goal predicates over the candidate ruleset; candidates whose head cannot reach a goal leave the action set | `-DFOCUS=1` |
| Silicon | kernel path condition | a candidate whose body is unsupported violates the path condition: removed from the action set (hard) instead of merely damped in the attention residual (soft) | `-DSYMGATE=2` (`1` = soft) |
| Silicon | verified contracts | 2-rule chains admitted only when the kernel confirms `body(r2) = head(r1)`; applied as one action slot | `-DLEMMA=1` |
| Screamer | branching attention | sparse top-k attention layer | `-DATTMODE=2` |
| Screamer | nondeterministic search | branch + backtrack + propagation + subsumption (unchanged baseline search) | runtime `--branch/--subsume/--prop` |

The transformer is untouched in size: every arm trains 19,939 parameters with the
same data, the same 40 epochs and the same optimizer settings (180/60/100 worlds,
`--collect full --sample sub --goal-scan --balance-reward`, hard fixture, seeds
11–13). 0.0260 changes only what happens *around* the score: which candidates
exist, which proofs are accepted, and which action is taken.

## Result (3 seeds, per-seed means; d4/b4 evaluation)

```text
arm     greedy   beam    dfs     dfs_full  nodes  cands   gate_viol cert_ok/fail  lemma_uses
pure     0.3281  0.4180  0.5529  0.4767   3437   24625   0         –             0
topk     0.2461  0.3228  0.4921  0.4133   3735   26723   0         –             0
pc       0.3095  0.3730  0.5238  0.4433   3592   23333   0         –             0
soft     0.2910  0.3651  0.5212  0.4467   3491   25002   57        –             0
focus    0.3281  0.4180  0.5529  0.4767   3437   24625   0         –             0
cert     0.3281  0.4180  0.5529  0.4767   3437   24625   0         70 / 0        0
lemma    0.3281  0.4180  0.6825  0.6367   3422   24142   0         –             465
hybrid   0.2672  0.3968  0.7037  0.6567   3592   23117   0         89 / 0        480
```

Paired by seed (n=3, underpowered; 2 SE verdict):

```text
hybrid − pure   goal +15.1 pp ± 7.2   SIGNIFICANT   full +18.0 pp ± 7.6   SIGNIFICANT
lemma  − pure   goal +13.0 pp ± 1.2   SIGNIFICANT   full +16.0 pp ± 1.0   SIGNIFICANT
pc     − pure   goal  −2.9 pp ± 3.0   inconclusive  beam  −4.5 pp
soft   − pure   goal  −3.2 pp ± 7.4   inconclusive
topk   − pure   goal  −6.1 pp ± 7.1   inconclusive
cert   − pure   goal  ±0             exact identity (conservation)
```

What each element contributes:

- **Verified contracts (Silicon) are the effect.** `lemma` alone moves DFS goal
  coverage +13.0 pp and full-world success +16.0 pp, with node count unchanged
  (3437 → 3422) and 465 lemma actions applied. A 2-step composition becomes one
  action slot, which is exactly the capability that single-step utility labels
  could not learn (0.0246 "Limits").
- **Path condition (Silicon) is a neutral-to-negative filter on this fixture.**
  Hard admissibility removes 24,173 candidates but costs −2.9 pp goal; the soft
  residual gate removes 14,011 tokens and selects inadmissible candidates 57
  times (0.0260 census) — the 0.0259 "admissibility" claim was a damped residual,
  not an enforced condition. Both are inside 2 SE.
- **Obligation focus (Rocq) is vacuous on this fixture.** The relevance fixpoint
  over 6 unary predicates and 24 candidate rules saturates: every candidate head
  reaches a goal, so the filter removes 0 candidates in 10,312 consultations.
  Reported as a negative result; no gain is claimed. Completeness is still gated
  (exhaustive branch=POOL answer identical with and without the filter).
- **Certificates (Rocq) are conservation, not gain.** 70 (cert arm) and 89
  (hybrid) proved goals carry a parent-map certificate that is re-derived
  independently; answer identity with `pure` is exact. A mutated parent map is
  rejected 81/81, so the checker is not vacuous.
- **Branching attention (Screamer) does not transfer to this fixture.**
  Sparse top-k attention costs −6.1 pp goal and −9.5 pp beam; the search
  baseline (branch/backtrack/propagation/subsumption) remains the dominant
  component. Consistent with 0.0259.
- **Greedy (1-step) gets worse in `hybrid`** (−6.1 pp): the hard path condition
  and top-k readout shrink the candidate set the one-step policy relies on, while
  the DFS profits from contract actions. Scoring and search are separable
  effects, and the headline is a search effect.

## Gates (`verify_hybrid.sh` → `V0260-HYBRID-PASS`)

```text
GRADCHECK          8 arms, finite differences vs analytic, rel_to_max_grad ~3e-10
PC-PATH            hard arms gate_viol=0; soft arm gate_viol>0 (control non-vacuous);
                   pure arm drops nothing; hard arms actually drop candidates
CERT               valid certificate accepted (cert_ok == cert_checked);
                   corrupted parent map rejected (81/81); answer conserved
FOCUS              census: consulted 10,312 times, removed 0 -> FOCUS-VACUOUS-SATURATED
FOCUS-COMPLETENESS exhaustive branch=POOL answer unchanged (0.8492)
LEMMA              contracts applied (465 / 480); node count not increased
AGG                table == per-seed recomputation; 11 mutations rejected
WHDR               cross-variant weight loads refused (exit 4), own weights accepted
LLVM               O0/O2/O3 byte-identical; ASan+UBSan clean at depth 4
V0260-HYBRID-PASS
```

## Repairs carried from the 0.0259 review

| Finding | Repair in 0.0260 |
|---|---|
| F1 release gate failed in the committed tree (stale manifests, missing lemma token) | manifests regenerated (new lab files included), wrapper token matches the emitted token, `run_hybrid.sh`/`verify_hybrid.sh` are inside the release gate |
| F2 `run_layer.sh` printed the seed-13 row as an "average" | `tools/hybrid_stats.sh` refuses duplicate/missing seed rows, recomputes every printed mean from `SEED`/`DFS`/`HYBRID` rows, and `gate_regression_hybrid.sh` keeps 11 rejected mutations; `run_hybrid.sh` no longer averages `MEAN` lines |
| F3 new capabilities had no gate path | `topk_attention_layer`, `symbolic_residual_gate`, `proof_certificate_check`, `kernel_path_condition`, `verified_contract_actions` all point at `verify_hybrid.sh`, which runs gradcheck/LLVM/ASan/schema per arm |
| F4 weight header omitted the variant tag | header now carries `attmode, symgate, cert, focus, lemma`; cross-load is refused and gated |
| F5 inflated capability wording | residuals and readouts are named after what they do (`sparse top-k attention`, `feature-conditioned residual gate`); "admissibility" is only claimed for `SYMGATE=2`, where the census shows 0 inadmissible selections |
| F7 `run.sh` missing newline swallowed `RUN-DONE` | `run.sh` last line restored |

## New finding (found by the 0.0260 ASan gate)

The verified-lemma action writes **two** rules into a sequence array sized
`SEED_RULES + MAXBUDGET`. With `--eval-budget 4` the DFS wrote past the end:
`stack-buffer-overflow` in `dfs_world` (train.inc:595), reproduced on seeds 11 and
13 under ASan and a hard segfault without it. The same sizing exists in 0.0257
(the lemma experiment that introduced the action) and in 0.0259 (where lemmas are
compiled out, so the overflow is unreachable). 0.0260 sizes rule sequences at
`SEED_RULES + 2*MAXBUDGET` and adds a capacity guard before the lemma recursion.
This is a soundness-relevant repair, not cosmetic: the release gate now runs ASan
on the arm that can reach the path.

## Scope and limits

- 3 seeds, one fixture family (6 unary predicates, 24 candidate rules, 3 goals),
  hard fixture = goals that need ≥2 candidate steps. Seeds share train/val/test
  worlds; seeds vary init and order.
- The transformer is unchanged in size; 0.0260 measures which symbolic layer
  pays, not a new architecture.
- Maru is used for Q16 inference parity on the initial-state scoring path
  (0.0246 artifact). The new layers are inside the C/LLVM IR search, not in Maru
  Lisp; no Maru parity claim is made for them in this version.
- `focus` saturates here. A relational or wider-predicate fixture is the next
  test for it, and the census fields (`focus_states`, `focus_removed`) are the
  measurement to watch.
- n=3 with a 2 SE rule: `hybrid − pure` is at 2.09 SE. Treat it as a directional
  result that needs 5 seeds on a fresh seed base before promotion.
## Release-gate repairs and findings (2026-11-15 continuation)

Running `scripts/verify_release.sh` end to end in this tree (SEEDS=5 for the
legacy labs, which are pinned at 5 seeds) exposed three gate defects inherited
from 0.0259. All three are repairs of the *gate*, not of the measurements; the
headline numbers above are unchanged.

1. **Stale manifests (review 0259 F1).** `docs/release.sources.sha256` had 9
   mismatched entries and no entry for any new lab file; `release.tests.sha256`
   pinned the previous `VERSION`. Regenerated over 265 source paths (new hybrid
   scripts included) and re-pinned `VERSION`/`tests/core-tests.l`. Both manifests
   now verify clean.
2. **Wrapper token mismatch (review 0259 F1b).** `scripts/verify_release.sh`
   required `V0256-VERIFIED-LEMMA-PASS`, which the 0.0258/0.0259 `verify.sh` no
   longer prints. The wrapper now requires the token the lab actually emits
   (`V0256-SOUNDNESS-PASS`) and additionally runs `run_hybrid.sh` +
   `verify_hybrid.sh` with `V0260-HYBRID-PASS`.
3. **False trajectory gate.** 0.0259 `verify.sh` asserted
   `d4 step1 < step3 < step4` optimality. The model produces
   `0.898 / 0.732 / 0.972` at 5 seeds — identically in the 0.0259 tree and here
   (measured by re-running the 0.0259 source on its own protocol), so the claim is
   false for this model and the gate could never pass. The strict monotonicity
   claim is withdrawn; the full profile is still printed and two stable
   invariants are gated (harder fixture lowers first-step optimality; the d4
   profile recovers by the last step).
4. **Broken failure diagnostics.** `tail -20 fileA fileB` is rejected by GNU
   coreutils 9.12 (`option used in invalid context`), so a failing lab gate
   printed only `PST-LAB-GATE-FAIL` without the log tail. Now `tail -n 20`.
5. **Seed-count dependence of the 0.0251 harness pin.** `verify.sh` compared
   `bal 2_4 goal` with a 5-seed pin (0.7832 ± 0.01) regardless of `SEEDS`; at
   SEEDS=3 it reported a spurious regression (0.7998). The legacy labs are now
   invoked with an explicit `LEGACY_SEEDS=5`, and the pin is skipped with a
   printed reason when another seed count is requested.
6. **`run.sh` swallowed its own completion marker (review 0259 F7).**
   `tee out/port_summary.txtecho "RUN-DONE"` wrote a file instead of echoing; the
   last line is restored, and the gate log now shows `RUN-DONE`.

Verification logs: `docs/verification-0260.log` (release gate),
`docs/verification-0260-lab.log` (proof-state lab gate),
`docs/verification-0260-hybrid.log` (hybrid gate).
