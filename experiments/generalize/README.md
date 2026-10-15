# `experiments/generalize` — generalize the understanding across a corpus (v0.0041)

The north star reduces **one** program (`main.py`) to understanding facts and
glosses them as natural-language sentences. But on one program the understanding
predicates are *extensionally degenerate*: `trains`, `backpropagates`,
`optimizes` all hold of exactly `{main, train}`; `evaluates`, `uses_grad_free`
exactly `{main, test}`; and so on. Every conjunction you can form is equal to one
of its members, so there is **nothing to generalize** — measured, `0` new
concepts, `dl == dl`. That is the gap diagnosed in
[`../mnist/GENERALIZATION_GAP.md`](../mnist/GENERALIZATION_GAP.md).

This experiment closes it the way the `calls` law is learned in
`experiments/code`: **learn across a corpus, transfer by deduction.**

```
corpus of programs          (programs.py: deterministic PyTorch-like trainers)
   -- extract + acquire -->  understanding facts, subjects namespaced per program
   -- induce_concepts -->    conjunctions of subject-features that recur and are
                             irredundant + non-degenerate
   -- transfer -->           the kernel re-derives each concept on HELD-OUT programs
   --> abstracted sentences for the north star, each backed by a kernel proof
```

## Result (v0.0041)

`./generalize.sh`

```
corpus : 13 programs (11 train, 2 held out: ['northstar', 'p11'])
concepts (8):
   concept0: ['backpropagates(X)', 'optimizes(X)']            (support 18)
   concept1: ['backpropagates(X)', 'builds_model(X)']         (support 10)
   concept2: ['builds_model(X)', 'optimizes(X)']              (support 10)
   concept3: ['backpropagates(X)', 'builds_model(X)', 'optimizes(X)'] (support 9)
   concept4: ['backpropagates(X)', 'uses_grad_free(X)']       (support 7)
   concept5: ['evaluates(X)', 'optimizes(X)']                 (support 7)
   concept6: ['evaluates(X)', 'loads_data(X)']                (support 6)
   concept7: ['has_layer(X,conv2d)', 'has_layer(X,linear)']    (support 6)
transfer (kernel re-derives on held out):
   northstar (total 9) ...
   p11       (total 8) ...   # concept7 correctly does NOT transfer: p11 has no linear
abstracted sentences (north star):
   [ok] main  backpropagates (loss.backward) and updates parameters (optimizer.step).
   [ok] train backpropagates (loss.backward) and updates parameters (optimizer.step).
   [ok] net   has a conv2d layer and has a linear layer.
   ...
verdict: {concepts_found, concepts_non_degenerate, single_program_finds_nothing,
          concepts_definitionally_sound, deterministic, transfers_to_north_star,
          each_held_out_gets_a_concept, sentences_all_verified, sentence_compression}
```

`concept0` is the abstraction the user asked for: **"a training step"** —
*backpropagate then update* — learned from the corpus, not written by hand, and
re-derived by the kernel on the held-out `main.py` (`main` and `train` both).

## What is honest here

- **The invention is definitional.** Each concept rule is
  `concept_i(X) :- <feature>, <feature>, ...`; it adds a *name*, not truth. The
  control `concepts_definitionally_sound` closes the training corpus with and
  without the rules and checks the original-vocabulary atoms are unchanged.
- **The gap is real and shown.** `single_program_finds_nothing` runs the *same*
  miner on `main.py` alone and gets `0` concepts — reproducing the diagnosis.
- **Transfer is the falsification.** A concept that is a genuine generalization
  fires on programs it never saw; `p11` (a conv-only net) correctly rejects the
  `conv2d ∧ linear` concept (`concept7` hits `0`).
- **The gloss is untrusted.** Sentence phrasing is a fixed, human-readable
  template; the *support* is the kernel proof `concept_i(subject)`, verified by
  `dlm.proof.verify`.

## Files

| file | role |
|------|------|
| `programs.py` | deterministic corpus generator (real Python trainers) + `NORTH_STAR` |
| `run.py` | pipeline: reduce+acquire → induce → transfer → abstracted sentences + controls |
| `generalize.sh` | PYTHONPATH wrapper; writes `reports/generalize/<stamp>/result.json` |

## Run

```
./experiments/generalize/generalize.sh                       # from the version dir
# or, from /research, the shared harness runs it automatically:
./northstar.sh --offline --check
```