# Proof-state transformer — native (C/LLVM + Maru Q16), 0.0262

## 0.0262 budget-exact DP value labels (`run_value.sh`, `verify_value.sh`)

```text
arm      dfs     dfs_full  pair_uses(note)
util     0.5095  0.4340    single-step utility
dp       0.5318  0.4560    exact V(mask,rem) label
dpshuf   0.1746  0.1660    shuffled-label control
dplem    0.6540  0.6080    dp + mined contracts, 428
```

`dp − util = +2.2pp ± 2.8` → **DP-VALUE-NOT-DEMONSTRATED**; the label is used
(shuffled control collapses) but does not yield a better policy. Contracts stack
(+12.2pp over dp). Gate: `verify_value.sh` → `V0262-DPVALUE-PASS`.

## 0.0261 learned contract proposal (`run_pair.sh`, `verify_pair.sh`)

## 0.0261 learned contract proposal (`run_pair.sh`, `verify_pair.sh`)

Same transformer and protocols; only the contract proposer differs, at matched
count (16 offers/state). Seeds 21–25.

```text
arm     dfs     dfs_full  nodes  pair_uses  pair_viol
pure    0.4683  0.3900    3553   0          0
mined   0.6302  0.5880    3519   479        0
learn   0.6778  0.6400    3437   887        0
rand    0.6841  0.6480    3444   922        0
```

`learn − rand = −0.6pp ± 0.7` → **PAIR-LEARN-NOT-DEMONSTRATED**: a kernel-labelled
pointwise pair scorer does not beat a matched random proposer. The contract gain
is carried by the action space (kernel-verified 2-rule actions), and the mined
set was a coverage restriction. Verdict and gates: `docs/release-0261.md`,
`verify_pair.sh` → `V0261-PAIRLEARN-PASS`.

## 0.0260 hybrid reasoning layer (`run_hybrid.sh`, `verify_hybrid.sh`)

## 0.0260 hybrid reasoning layer (`run_hybrid.sh`, `verify_hybrid.sh`)

Same transformer, same 19,939 parameters, same data/epochs; only the symbolic
layers around the score change. 8 arms, 3 seeds, d4/b4:

```text
arm     greedy   beam    dfs     dfs_full  gate_viol cert_ok/fail lemma_uses
pure     0.3281  0.4180  0.5529  0.4767    0         –            0
topk     0.2461  0.3228  0.4921  0.4133    0         –            0
pc       0.3095  0.3730  0.5238  0.4433    0         –            0
soft     0.2910  0.3651  0.5212  0.4467    57        –            0
focus    0.3281  0.4180  0.5529  0.4767    0         –            0
cert     0.3281  0.4180  0.5529  0.4767    0         70 / 0       0
lemma    0.3281  0.4180  0.6825  0.6367    0         –            465
hybrid   0.2672  0.3968  0.7037  0.6567    0         89 / 0       480
```

Verified 2-rule contracts are the effect (+13.0 pp goal, +16.0 pp full, node
count unchanged). Path condition is neutral-to-negative; obligation focus is
vacuous on this fixture (relevance closure saturates, census reported);
certificates are conservation (answer identity, mutated map rejected 81/81);
sparse top-k attention stays negative. Full write-up: `docs/release-0260.md`.

```bash
./run_hybrid.sh     # 8 arms x 3 seeds, ~6 min
./verify_hybrid.sh  # gates, ~3 min -> V0260-HYBRID-PASS
```

## 0.0246 baseline (unchanged)

0.0246 applies the second review (R245-1..5). The decisive intervention
(teacher-state exposure × representation, 5 seeds, matched updates):

```text
arm                        proof   full    beam    beam_full
A root × aggregate         0.2958  0.1180  0.3774  0.1620
B full × aggregate         0.5147  0.3420  0.6294  0.4520
C root × relation          0.3147  0.1300  0.3955  0.1860
D full × relation          0.7653  0.5380  0.8498  0.6860
E full × relation (all)    0.7442  0.5280  0.8309  0.6420
utility_greedy 0.7774   support beam 0.6000/0.4100   exact bound 0.9434/0.8500
```

Teacher-state exposure is dominant (+21.9pp); relation features add +25.1pp on
top. D's beam beats the support beam by +25.0pp goal [+17.6,+32.4] at the same
search budget. The 0.0245 negative result was an exposure defect plus an
aggregate representation that aliases goal bindings (5,906 feature-equal legal
pairs, 1 with distinct optimal actions; relation features: 0 collisions).

## 0.0245 repairs (review F1–F7, superseded measurements)

Torch-free proof-state rule ranker: given the current theory, the goal set and
the candidate Horn rules, score the candidates by their kernel utility. The
closure decides what is proved; the ranker only orders candidates.

0.0245 applies the 0.0244 review (`/research/code-review-0244.md`, F1–F7) to a
new numbered version. 0.0244 is preserved unchanged.

## Repairs

| Finding | Repair |
|---|---|
| F1 goal generation ignored the per-entity body condition | `src/pst.c` now adds `(head,e)` only when the candidate body holds **at e**; `tools/world_audit.c` (independent set-of-atoms implementation) checks witness and reachability invariants |
| F2 MEAN omitted `proof_shuffled` (read as 0) | MEAN prints every control; `tools/gate_check.c` requires all fields and **recomputes MEAN from the SEED rows** |
| F3 metric gates accepted empty/zero-row/one-row inputs and model < support | strict validator: exactly one MEAN, N distinct expected SEED ids, finite required fields, recomputed means, control margins, declared direction; `gate_regression.sh` keeps 10 rejected mutations as a regression suite |
| F4 utility-greedy called an upper bound | renamed `utility_greedy`; the failing gate is gone; a **budget-exact bound** enumerates all rule subsets of size ≤4 (12,950/world) and asserts model ≤ bound on all 500 seed-world pairs |
| F5 Maru parity used a different checkpoint | `maru_check.sh` exports the **main protocol** (hard fixture, 180/60/100, seed 11, 40 epochs), prints `EXPORT-CONFIG ... weights_checksum`, and reproduces **100/100** initial-state picks (max Q16 error 271/65536 = 0.0041) |
| F6 no matched-search control | six beam arms (model raw, model log-prob, support, prior, random, untrained) share the controller and the exact budget (1000 states, 22,200 candidate queries, 300 final closures; support/prior/random use 0 forwards); a paired world bootstrap reports the CI |
| F7 mask gradcheck compared a different objective | training and the finite-difference checker now call one `loss_from_cache` (mask-aware); `verify.sh` runs `--gradcheck` for **all six variants** |

## Two fixtures

- **ref** (reference semantics, F1-correct): every goal has a per-entity witness,
  so a single candidate derives it. The 4-step budget then has a **100 % exact
  bound**: the fixture saturates and cannot discriminate rankers. Reported as a
  qualification result, not as evidence.
- **hard** (declared deviation, `-DHARD_GOALS=1`): goals are atoms in
  `closure(base + all candidates) \ closure(base + any one candidate)`, i.e. they
  require at least two candidate steps. Exact bound 95.57 % goal / 88.00 % full.

## Results (5 seeds, 180 train / 60 val / 100 entity-held-out worlds)

Reference fixture (saturated, bound 100 %):

```text
arm / control       proof   full
model (base)        0.9307  0.8220     utility_greedy comparator 1.0000
support heuristic   0.8600            prior 0.5200  random 0.4033
untrained           0.1600            shuffled features 0.3933
model beam          0.9473  0.8640     support beam 0.9400 / 0.8400
                                       model-beam minus support-beam +0.0073 [−0.018,+0.036]
```

Hard fixture (composition-requiring goals, bound 95.57 % / 88.00 %):

```text
arm / control       proof   full
model (base)        0.3247  0.1240     utility_greedy comparator 0.7565
support heuristic   0.3579            prior 0.1476  random 0.0664
untrained           0.0295            shuffled features 0.0694
model beam          0.4066  0.1680     model log-prob beam 0.4103
support beam        0.5535  0.3600     prior beam 0.1697  random beam 0.1107
```

Matched-search paired bootstrap (hard, 100 worlds × 5 seeds):
model-raw − support beam = **−14.7 pp goal** [−22.7, −5.9] and **−19.2 pp full**
[−28.0, −10.6].

Variants on the hard fixture (same budget, same data):

```text
variant   top1     hit     proof   full    beam    beam_support
base     -0.7871  0.4098  0.3247  0.1240  0.4066  0.5535
utilhead -0.7879  0.4373  0.3365  0.1240  0.4214  0.5535
mask     -0.8000  0.3843  0.3365  0.1300  0.4066  0.5535
goalx    -0.7762  0.4627  0.3528  0.1360  0.4310  0.5535
loop     -0.7897  0.4353  0.3358  0.1200  0.4096  0.5535
bind     -0.7903  0.3980  0.3365  0.1240  0.4030  0.5535
```

Reference-fixture variants stay at 0.9280–0.9407 proof (saturated).

## Verdict

- **The 0.0244 headline does not survive the repaired fixture.** With per-entity
  goals the reference distribution saturates (greedy comparator 100 %), and on
  the declared composition-requiring fixture the learned ranker (32.5 % greedy,
  40.7 % beam) loses to a symbolic support heuristic (35.8 % / 55.4 %) and to the
  utility-greedy comparator (75.7 %). The earlier model-minus-support advantage
  was a property of the broken goal distribution.
- **Matched search is what moves the number**, and it moves the support scorer
  more than the learned scorer on hard: +19.6 pp for support beam over support
  greedy vs +8.2 pp for the model.
- **Architecture variants remain within noise** (32.5–35.3 % proof on hard;
  92.8–94.1 % on ref). No variant changes the verdict.
- The remaining gap is a *learning-target* problem: single-step utility labels
  give a ranker that cannot plan a 2–3 step composition, while the comparator
  and support beam can. Multi-step targets (budget-aware value/DP labels) are the
  next experiment; they are not implemented here.

## Gates (`verify.sh`, bash/awk + two native checkers, no Python)

```text
PARITY            world/features/kernel-utility/rollout vs reference implementation
GRADCHECK         all six variants, shared masked objective (rel_to_max_grad ~1e-10)
LLVM-MATRIX       O0/O2/O3 byte-identical; training re-run byte-identical
F1-INVARIANTS     ref witness=0 unreachable=0 bound=100%; hard unreachable=0
F4-BOUND          lab bound == independent audit bound; model<=bound on 500 pairs
F2/F3-VALIDATION   gate_check ref/hard + 10-mutation regression suite
F6-MATCHED-SEARCH  six arms, identical budgets, paired bootstrap CI
F5-MARU            100/100 picks on the main-protocol checkpoint
V0245-PROOF-STATE-TRANSFORMER-PASS
```

## Files

```text
src/pst.c         world (per-entity goals; HARD_GOALS variant), oracle, features,
                  rollout, dump/dump-test, Maru export, main
src/model.inc     set transformer + backprop + shared masked loss
src/train.inc     data, training, greedy policies, matched-search beam,
                  budget-exact bound, bootstrap, reporting, gradcheck, export
tools/world_audit.c   independent audit (set-of-atoms): witness, reachability, bound
tools/gate_check.c    strict log validator (F2/F3)
tools/check_parity.py reference-implementation parity evidence
maru/*.l + maru_check.sh   Q16 inference on the main-protocol artifact
run.sh / verify.sh / run_variants.sh / gate_regression.sh
```

## Run

```bash
./run.sh            # build, parity, LLVM identity, ref + hard base runs (~3 min)
./verify.sh         # gates (~10 min, includes 100 Maru cases)
./run_variants.sh   # 12 arms (6 variants x 2 fixtures) x 5 seeds (~15 min)
./maru_check.sh     # Q16 parity on the main-protocol checkpoint
```

## Limits

- The unary world makes argument binding trivial; a relational world is still the
  next fixture for `bind`.
- The hard fixture is a declared deviation from the reference generator, not the
  reference distribution; both are reported separately.
- The ranker is trained on single-step utility; no plan/value target is learned.
- Maru covers inference of the initial-state scoring path only (100 states).
- 5 seeds share the same train/val/test worlds; seeds vary init and order.