# Learning-result analysis — North-Star `main.py` (v0.0040)

Everything below is measured offline on the cached PyTorch MNIST `main.py`
(5,392 B → 222 structural facts, 87 positive `calls`). Reproduce with
`PYTHONPATH=. python3` and the helpers in `experiments/mnist/run.py`.
The **only** learner is `dlm.ground.learn` (`max_body=2, extra_vars=2,
max_rules=4`); the kernel alone judges truth.

## 1. What was learned

Exactly **one law**:

```prolog
calls(G0, G1) :- calls(G0, E0), calls(E0, G1)      # transitivity of calls
```

Instance form: `(calls main G0) :- (calls E0 G0), (calls E1 E0)`.
Description length = **3**. It is the *general* transitive-closure law, not a
`main`-specific rule (the head's first argument is a variable).

## 2. Search trace (how the one law was found)

The greedy coverer evaluates candidate bodies shortest-first against the full
kernel `closure`:

| outcome | count |
|---|---|
| candidates evaluated | **712** |
| rejected — derives a declared negative (unsound) | 27 |
| rejected — sound but covers no uncovered positive | 684 |
| **admitted** | **1** |

So ~96 % of the search is elimination of useless candidates; only 28 of 712
were even sound, and only one of those generalised over the uncovered set.

## 3. Soundness (the kernel verdict)

* `false_assert` (declared negative set): **0**
* `false_final` = `derived_calls − positives` over the **whole complement**
  (67+20 = 87 pairs): **0**

`false_final` is the honest, stricter check and it is 0, so the law emits no
`calls` pair outside the true closure.

> Caveat found while stress-testing: `negatives()` drops reflexive pairs
> (`x == z`), so the *declared* negative set has a self-loop blind spot. On 300
> random tiny graphs the greedy coverer occasionally overfits a non-general
> rule (`calls(X,Z) :- calls(Z,X)`, `calls(X,Z) :- calls(X,E)` …) that emits a
> self-loop the declared gate doesn't punish. `false_final` (full complement)
> closes this hole and is 0 here. The overfit never happens on the North-Star
> instance because the uncovered positives force the `main` head and the only
> 2-body sound-covering body is transitivity.

## 4. Coverage

| | |
|---|---|
| direct `calls` facts in the file | 67 |
| positives reachable **only** with the law | 20 |
| transitive `calls` closure | 87 |

Removing the law (ablation) drops the narrative from **32 → 24 sentences**;
8 sentences exist *only* because of it (`Main performs a training step.`,
`Main calls backpropagation.`, `Main updates the parameters…`, …).

## 5. Generalization

* **Same file (`law_transfer`)**: `general_law_identifiable_from_one_file = False`.
  Every owner except `main` has zero multi-hop positives, so holding one owner
  out leaves no train example to generalise from. The law is *applied*, not
  *identified*, from one file — stated honestly in the report.
* **Across repos (`experiments/code`, real GitHub, seed 1, offline)**:

  | arm | held-out recovery | false |
  |---|---|---|
  | identity (raw edges) | 0.346 | 0 |
  | **learned transitivity** | **1.000** | **0** |
  | scrambled constants | 0.346 | 0 |

  The law, induced on train repos, recovers the **full** import closure of
  unseen repos with zero false pairs. This is the cross-distribution evidence
  the single file cannot provide.

## 6. Compression

The law (DL = 3) replaces 20 implied facts ⇒ net description-length saving 17.

## 7. Determinism

Two offline runs are byte-identical (rules and full result, minus `ir`/
`narrative` formatting) — the learner is deterministic given the cached facts.

## 8. v0.0039 → v0.0040 (why the rule count changed)

| version | learned rules |
|---|---|
| v0.0039 | `(calls main G0) :- (backpropagates E0), (calls E0 G0)` **(coincidental)** + transitivity |
| v0.0040 | transitivity only |

v0.0039 allowed the **meaning/understanding** predicate `backpropagates` in the
body; on this one file that produced an in-sample-coincidental rule.
v0.0040 restricts the body search to the `STRUCTURAL` vocabulary, so only the
transferable law survives. (The meaning predicate is still used by the bridge,
just not as a *learned* body literal.)

## 9. Honest limits

1. The North-Star slice learns **one** law by design; per-predicate/domain laws
   are out of scope here and are measured in `experiments/code` / `train`.
2. Each run **refits**; the cache holds the source and web knowledge, never the
   learned rules.
3. `learn` is greedy covering: sound w.r.t. the declared negatives, but not
   guaranteed to find the general law on small/thin instances (§3 caveat).
4. Runtime is short (≈0.5 s) because the problem is small (222 facts), not
   because learning is skipped — it is ~95 % of the run and scales ≈O(N²)
   (0.5 s for `main.py` vs ≈19 s for `dlm/lisp.py`).