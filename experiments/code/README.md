# `experiments/code` — learning the dependency law from real GitHub repos

v0.0039 widens the learning scope from **web facts** (`experiments/web`) to
**source code**: download small random Python repos from GitHub, turn each repo
into a module import graph, hold out **whole repos**, and let the kernel induce
the transitivity law on the train repos. No human labels, no weak supervision —
the repo is the oracle.

## Pipeline

```
GitHub  search/repositories        seeded page of small Python repos (fork:false, size<1500 KB)
codeload.github.com  tar.gz        the repo's *.py sources
experiments/code/extract.py        stdlib ast -> (imports M N) Horn facts
experiments/code/run.py            hold out whole repos -> dlm.ground.learn -> closure
```

* **Node** = repo-relative dotted module (`pkg.sub.mod`; `__init__` folds into its
  package). Imports that resolve outside the repo (stdlib/third-party) are dropped.
* **Fact** = `(imports M N)` when module `M` imports repo module `N` — function-free
  binary Horn facts, single-token constants (namespaced by repo slug).
* **Target** = the transitive dependency closure. `identity` (direct edges only) is
  the baseline; the *learned* law is the induced transitivity rule.
* **Honest split** = whole repos. Held-out repos never appear in induction, so this
  is a cross-distribution test, not the same-distribution effect of §5.4.

Everything is cached under `cache/`, so `--offline` replays a run byte-for-byte and
never touches the network. Unauthenticated GitHub API allows ~10 search
requests/minute; tarballs come from codeload and are cached by repo.

## Run

```bash
./experiments/code/code_learn.sh                 # 6 repos, seed 1 -> reports/code/<stamp>/
./experiments/code/code_learn.sh --synthetic     # network-free smoke test
./experiments/code/code_learn.sh --repos 6 --seed 2
./experiments/code/code_learn.sh --offline       # replay from cache
```

The record (`reports/code/<stamp>/result.json`) has `corpus`, `graph`, `arms`
(identity / learned / scrambled), `learned_rules`, and `verdict`.

## Measured (real GitHub, 6 repos, ~2 held out)

| seed | repos | held pairs | identity | learned | scrambled | false |
|---|---|---|---|---|---|---|
| 1 | nano-vllm, awesome-aws, gixy, diff-match-patch, DAIN, bert | 309 | 0.346 | **1.000** | 0.346 | 0 |
| 2 | nano-vllm, termtosvg, swarm, hashsigs-py, agentskills, google-images-download | 115 | 0.313 | **1.000** | 0.313 | 0 |

The kernel induces exactly the transitivity law

```
imports(G0, G1) :- imports(G0, E0), imports(E0, G1)
```

on 4 train repos, and it recovers the **full** transitive import closure of 2
*unseen* repos (identity keeps only the direct edges), deriving **zero** false
pairs. The scrambled control (constants permuted) learns nothing and stays at
identity. Verdict: `found_transitivity`, `learned_beats_identity`, `learned_sound`,
`scrambled_not_better` — all true.

## Honest limits

* This is a **dependency-closure** experiment: the learned law is transitivity on
  one relation. It demonstrates that code facts feed the same kernel pipeline and
  that the law transfers across repos; it is not yet a code *understanding* claim.
* Extraction covers the import graph only. A call graph or symbol table needs a
  name resolver (scope-aware), which is a larger untrusted extractor.
* Soundness here is structural for this task (transitivity is a law of the
  relation), **not** a general answer to the §5.4 gate problem. Negatives are still
  sampled within train repos; the cross-repo transfer is what makes the result
  stronger than §5.4's same-distribution recovery.
* Repo selection is seeded-but-not-uniform (GitHub search page + shuffle), and a
  repo missing a default branch or too few edges is skipped.