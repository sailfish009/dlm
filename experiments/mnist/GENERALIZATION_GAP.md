# The missing generalization/abstraction layer — diagnosis (v0.0040)

> **Resolved in v0.0041.** The gap diagnosed below is closed by
> `dlm/generalize.py` + `experiments/generalize/`: a corpus of programs makes the
> understanding predicates non-degenerate, an invented concept is certified
> definitional, and the kernel re-derives it on a held-out program (deductive
> transfer).  See [`../generalize/README.md`](../generalize/README.md) and
> `COMPOSITION.md` §19.  The measurement below is kept as the diagnosis that
> motivated the layer.

The north-star slice reaches natural language (`experiments/mnist`), but the
**deductive generalization/abstraction** of those detailed sentences is absent.
This note measures *why*, and what a fix must look like.

## 1. The abstraction stage does nothing: `gain 0, invented []`

`run.py` calls `dlm.abstract.abstract_theory(ground.rules + learned_rule, closed)`.
`abstract_theory` folds **recurring rule bodies shared by >= 2 rules**
(`common_body_patterns`) into an invented predicate.

* `ground.rules` = the 11 `BRIDGE_FORMS` (each with a *distinct* body)
* `learned` = 1 rule (transitivity)

No two rules share a body => no group => `invented = []`, `DL 161 -> 161`. The
operator looks *across rules*; the detailed knowledge lives in **facts**, which it
never touches.

## 2. Even a fact-level concept inventor finds nothing here

The understanding predicates are extensionally **degenerate** on one program:

| predicate | extension (owners) |
|---|---|
| `trains`, `backpropagates`, `optimizes` | `{main, train}` |
| `evaluates`, `uses_grad_free` | `{main, test}` |
| `loads_data`, `builds_model`, `orchestrates`, `saves_model` | `{main}` |
| `is_module` | `{net}` |

Every conjunction of them has the extension of one of them already:

```
extensionally equivalent groups:
  {backpropagates, optimizes, trains}      -> {main, train}
  {evaluates, uses_grad_free}              -> {main, test}
  {builds_model, loads_data, orchestrates, saves_model} -> {main}

conjunctive patterns whose extension differs from EVERY single predicate
(i.e. a genuinely new concept): 0
```

So `gain 0` is not a bug: on a **single small program** there is no non-trivial
concept to invent — every pattern is a rename of an existing predicate.

## 3. Consequence: the layer must be corpus-level and deduction-judged

This is the same shape as the `calls` law: single-file => unidentifiable, learned
**across repos** (`experiments/code`, held-out recovery 1.000). Generalization /
abstraction of the understanding vocabulary must likewise be induced over a
**corpus of programs**, and certified by:

* `closure_preserved` (kernel) — conservative extension over the original signature;
* **deductive transfer** — the kernel `prove`s the invented concept on a **held-out**
  program, which is what separates a real generalization from a re-description.

It is exactly the next layer COMPOSITION.md §15 already names:
> "the next layer would make the reduction itself tree-structured (recurring
> bodies / macros) and judge it by deductive transfer, which is a genuine IR-TREE
> reduction rather than this flat one."

## 4. What the fix produces

1. **generalized laws** over the understanding vocabulary (e.g. a `training_step`
   concept defined by a body that is *not* equivalent to a single predicate);
2. **invented concepts** (predicate + definitional rule), kernel-certified;
3. **abstracted sentences** — N detailed sentences collapse to M higher-level ones,
   each backed by a kernel *proof* of the invented predicate (not a template);
4. a **transfer report** on held-out programs (the falsification arm).