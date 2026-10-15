# selfssl — recursive self-supervised learning, the one loop (v0.0058)

This is the **single** recursive self-supervised learning runner. The other
`experiments/*` recursive-learning scripts were unified into this one: it wires
the model's own capabilities into a single **closed loop** and then refuses to
stop on its own — after every round of learning + evaluation the model
summarises the round in natural language, and **you** decide when training ends
(Ctrl-C).

```
              +-----------------------------------------------------+
              |                                                      |
  PERCEIVE --> LEARN --> EVALUATE --> SUMMARIZE --> ADMIT ----------+
  (new prog)  (concepts (proof on      (one NL      (fold into
              over old  held-out +     sentence)     own corpus)
              corpus)   reify calls)
```

## The round

| step | what happens | where |
|------|--------------|-------|
| PERCEIVE | one new program from the deterministic stream | `reduce_program` |
| LEARN | induce concepts over the corpus the model **already had** (its own past output) | `dlm.generalize.induce_concepts` |
| EVALUATE | re-derive those concepts on the **held-out** new program by proof, reify the model's own `calls` relation one level, self-assess from the kernel closure | `dlm.generalize.transfer`, `dlm.recursive`, `dlm.ability` |
| SUMMARIZE | one natural-language sentence built from those derived numbers | `_summarize` |
| ADMIT | only now fold the program into the corpus, so the next round learns from strictly more of the model's own conclusions | — |

The order matters: the program is always tested **before** it is absorbed, so
`concepts_transferred` is a genuine out-of-sample read, not memorisation.

### The source stream

`northstar` (the real `main.py`) → the 12-program corpus (`p0`…`p11`) → an
unbounded, deterministic stream of generated variants (`g1`, `g2`, …). Offline,
the whole thing replays byte-for-byte; the bounded check is reproducible.

## Termination is manual

The loop runs **forever**. Watch the round summaries and press **Ctrl-C** when
you have seen enough:

* first Ctrl-C — sets a flag; the round in flight is allowed to finish, then the
  report is written and the process exits cleanly;
* second Ctrl-C — forces an immediate exit.

**No arguments are needed.** `--rounds N` is available only to bound the loop in
tests / the harness; `run(...)` itself never self-terminates.

## Natural language is built from the model's own output

The sentence is not free text. Every clause is a count or a concept body the
kernel actually derived:

```
Round 7 read p6 and reduced it to 14 new facts; from the 109 facts it already had
it induced 8 concepts, and 4 of them re-derive on this held-out program by proof
(5 instances, e.g. a subject that backpropagates the loss and updates parameters);
in-sample it derives 468 atoms and proves 22/23 of its own promises; its reified
calls relation reaches depth 2 (282 pairs); its open promise 'recognizes' is
blocked only on acquired knowledge (dataset_of).
```

The separate `reading` field is the model's own **certified** N1–N9 sentence
(`dlm.narrative`); the round sentence is a *report* over derived quantities,
never a certification. The JSON keeps `summary` and `reading` distinct.

## Usage

```bash
./experiments/selfssl/selfssl.sh                 # run until you Ctrl-C
./experiments/selfssl/selfssl.sh --rounds 5      # bounded (CI / a quick look)
./experiments/selfssl/selfssl.sh --no-reading    # skip the per-program reading
./experiments/selfssl/selfssl.sh --online        # allow live acquisition
OUTDIR=reports/selfssl/mine ./experiments/selfssl/selfssl.sh
```

Report: `reports/selfssl/<stamp>/result.json` (or `--json PATH`). Every round
record carries `concepts`, `concepts_transferred`, `transfer_instances`,
`derived_atoms`, `open` / `actionable` promises, `reach_depth` / `reach_pairs`,
the `reading`, and the `summary`.

## What to watch

* `corpus` and `reach_pairs` grow every round — the model's own output is the
  input it learns from.
* `concepts` appears once the corpus is big enough to make a conjunction
  non-degenerate (measured: round 5), then `concepts_transferred` on later
  programs is the deductive-transfer signal.
* `open` stays `recognizes`, blocked on the acquirable premise `dataset_of` —
  the model's honest self-assessment that it still lacks domain knowledge.