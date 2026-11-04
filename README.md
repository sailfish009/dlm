# DLM 0.0095 — Cumulative Relational, Numeric, and Composite Basis Formation

## What Changed

The owner remains `basis-state91` / `execution-core91`. The same library, global prefix IDs, interpretation, execution, admission, audit, replay, checkpoint, and locking lifecycle now connect the following steps:

```text
Apply an existing relational basis R
 → Use original relation witnesses to pair object measurements and assign roles
 → Search for an EML numeric program N from those observations
 → Admit N and a composite basis C together in one event
 → Apply C to new objects and measurements to compute actual outputs
 → Form a subsequent composite basis D using those outputs as inputs
```

An external oracle interprets the structures formed in the main experiment as follows. The exp/log/difference labels describe **observed computational behavior**, not program names supplied to the learner.

```text
R1(a,b,c) = r(a,b) ∧ s(b,c)
N2(x)    ≈ exp(x)
N3(x)    ≈ log(x)
N4(u,v)  ≈ u-v                        # Formed from observations paired by R
C5(a,b,c)= N4(measure(a),measure(c))     # Admitted jointly with N4
D6(a,b,c)= N2(output(C5(a,b,c)))         # Formed using actual C outputs
```

The implementation distinguishes object roles from numeric scalars, raw observations from derived outputs, and computational definitions from empirical correspondences. Intermediate object roles remain visible even when they are not used numerically. Withdrawing C's applicability assumptions also affects D when D applies C. Raw observations are not rewritten to match model predictions, and derived outputs are not counted as fresh raw support.

Relational bodies retain support for both the existing logical representation and EML94 encoding. **Not every basis must be converted to EML:** the direct-logical arm forms the same composite structure. Existing relational formation also continues in the same library after typed learning.

## Validation Results

- **26 new integration tests passed; 264 offline tests passed.** Native, store, runtime, and graph-store checks also passed.
- Sequential 40-process experiment: **288 complete queries / 2,592 complete result rows**, with **zero numeric, binding, or original-witness mismatches**.
- The **192 unknown queries** in controls with required bases removed were not counted as correct answers.
- Disabling composite-output reuse allowed recovery through an additional numeric definition: that arm required seven definitions instead of the main arm's six.
- The direct-logical arm formed the same cross-family graph and was smaller and faster than the EML relational arm. No EML-specific advantage is claimed.

## Running

```sh
cd /research/dlm_v0.0095
./scripts/run.sh compose95
./scripts/run.sh compose95-input < experiments/composition95/input-example.sexp
./scripts/run.sh proof experiments/composition95/interventions.l

python3 -B -m unittest discover -s tests -p 'test_composition95.py' -v
python3 -B tests/run_offline.py
./scripts/run.sh test
bash tests/store-tests.sh
bash tests/runtime-tests.sh
bash tests/graph-store-tests.sh

# 40 sequential runs: 2 seeds × 2 branches × 5 arms × 2 repeats
python3 -B adapters/composition95_experiment.py \
  --seeds 2 --queries 6 --repeats 2 --output /tmp/composition95.json
python3 -B docs/composition95-evidence/final_check.py
```

`compose95-input` validates one structured datum and EOF; it does not evaluate input as Maru code. The Python adapter only generates synthetic data and supplies an independent oracle. Product-side numeric expression search, learning, and execution run through the native CPU path. No GPU, external LLM/API, or gradient training is used.

## Checking Contracts

- Numeric and composite results are labeled `empirical95`, not unconditional logical theorems.
- Logical structural expansion, numeric partial-function evaluation, and applicability assumptions inferred from finite observations remain distinct.
- Checks preserve roles, types, prefix dependencies, original witnesses, source/version references, and sign cells.
- Numeric and composite admission use separate primitive-expansion and primitive-relation-join checking paths.
- Incorrect values, omissions, and forged evidence are **rejected**, never filled with reference answers.
- Missing measurements, unsupported scopes, numeric domain failures, and exhausted budgets remain `unknown`. Partial rows from unfinished queries are not published as complete results.
- Application can use new inputs and an execution core without training targets, training facts/history, learners, or a live model owner.
- Frozen query models remain immutable. Source revisions produce a new active model. The definition-count epoch alone does not identify an exact model revision.

## Documentation

- [0095 implementation contracts and design](docs/composition95-design.md)
- [0095 validation, experiments, limitations, and reproduction](docs/release-0095.md)
- [Original 0094 README](README-0094.md)
- [0094 design](docs/integration94-design.md)
- [0093 standalone numeric experiment](docs/eml93-design.md) — a separate historical path, not the model owner in 0095.

The experiment uses small, structured synthetic datasets and a bounded grammar. It does not provide free-text/web semantic extraction, physical-unit understanding, general condition invention, noisy large-scale long-term learning, a universal numeric error theorem, or a proof of a latent-axiom theory. It demonstrates formation of role wiring, function structures, and hierarchical compositions, but **does not establish an EML-specific learning-power, speed, or compression advantage**. Observation schemas, sign cells, search/admission rules, and the reuse-first policy are fixed foundations.

`README-0094.md` and predecessor directories were preserved in their actual copy-time state. The compiler/runtime was not changed. Preservation records are in `docs/composition95-evidence/`. Existing subsystems and unresolved native source-integrity/HTTP issues remain; this version does not complete the entire DLM or end-to-end autonomous web learning.
