# Recursive86 — generated branch programs as the learning execution path

## Scope

This release integrates the DLM77 relation-definition generator and Search84/85
control with the existing space79 nondeterministic program machine. It is not a
new LLM, Common Lisp Screamer import, neural policy, MCTS implementation or
arbitrary natural-language/code generator. The bounded grammar composes binary
relations and prior learned definitions into paths of primitive length<=4.

The integration is real runtime delegation: new nd modes no longer call the
old sequential trial loop. They construct data programs with multiple `choose`
alternatives and execute them with `s79-program-job`/`s79-run` before admission.
The engine is single-threaded/cooperative; logical alternatives are not workers.

## One shared loop

1. Start from the current native model, never from the model's own output as new
   observations. Generate indexed, deduplicated `(word, composition)` candidates.
2. Use FIFO (`nd-cache`) or integer family UCB (`nd-ucb`) to select a batch of at
   most `min(requested budget,16)` candidate decisions. A previous-generation
   complete negative hit consumes a decision without creating a branch.
3. Generate a data-only program:

```
(choose
 (((certify86 (MODEL DEFINITION-1)) (accept DEFINITION-1))
  ((certify86 (MODEL DEFINITION-2)) (accept DEFINITION-2)) ...))
```

4. Execute in the real space79 machine. Each branch sees its immutable model and
   isolated context. `certify86` invokes the native `a77-certify` gate; it stores
   a branch-local checked ticket and actual inspected-proof-entry work count.
   Rejected candidates fail that branch, not the whole model.
5. Collect checked outcomes from ALL executed branches, including those not
   ultimately selected. Update family trial/reward/work statistics. This is
   self-supervision from formal checking, not externally supplied answer labels.
6. `accept` yields only a provisional result. A matching checked ticket and a
   generated proposal must exist. The chosen definition is checked independently
   AGAIN before authoritative admission. One definition at most is committed.
7. Existing `d77-commit` checkpoints first, then publishes model/controller state.
   Next-round generation uses learned operators, not only primitive relations.

## Why multiple branch checks occur

Every alternative has a `certify86` action followed by `accept`. The FIFO ready
queue executes those first actions before the first accept is delivered. Thus
multiple candidates are checked even if an earlier one can succeed. Remaining
accept continuations become alternatives after the job is done; their tickets
are still collected as valid policy labels.

This is deliberately bounded breadth-style branch evaluation, not efficient
short-circuit DFS. Batch proposal priorities are frozen until the batch outcomes
return. New statistics affect subsequent batches/rounds. One scalar per-kind UCB
score is not a neural policy or a guarantee of improved exploration performance.

Candidates use the same fresh name in separate hypothetical branches. Only one
is committed; others are not simultaneously entered under that name. Nonchosen
verified candidates provide statistics, not new world facts or automatic lemmas.
The next model revision regenerates with the new library and fresh naming.

## Trust and failure semantics

- `n86-action?` validates model and definition shape; the native checker validates
  definition semantics, source instances, rule proofs and independent primitive
  path reference results.
- There is no `eval` of generated program data or external code execution. The
  new opcode is explicitly named/versioned `certify86` and calls one fixed gate.
- `assume` or local branch bindings do not become inputs to native certification;
  only the immutable authoritative model is used.
- A forged/bare accept without a matching checked ticket remains incomplete and
  cannot publish a definition. The final gate is independent of provisional accept.
- Verification/unknown failures are deferred for retry. Complete insufficient-reuse
  outcomes can be cached by exact model and primitive word; this is not logical
  unprovability. Space-job exhaustion does not imply semantic refutation.
- Positive branch costs and the extra final recheck are counted. The final recheck
  is cost, not a duplicated supervision label.

Tests explicitly exercise a failed and a successful generated branch, bare-accept
bypass attempts, unknown failure retry, recursive proof checking and source-free
new-store behavior inherited from the native learner.

## State and persistence

`control84` now has an additional final diagnostic field containing a compact
`nd86` trace: branch count, engine event count, admitted flag and per-candidate
checked outcomes/work. Full engine stacks and hypothetical next models are NOT
serialized into the authoritative checkpoint. The frame is replay-reconstructed.
Historical trace records are diagnostics, never evidence for current claims.

New public configurations log `(search86 MODE)` and use `dlm-session86`. Search
steps retain the established `(search84-run BUDGET)` event form. Old77/83/84/85
sessions remain accepted; new86 events cannot hide under old tags. Existing
space-session79 data can contain the explicit new opcode on this runtime; older
runtimes reject that unknown opcode rather than silently execute it differently.

Fresh-process tests compare the full controller (including branch trace), next
step and subsequent controller. Capacity/saturation reasons and resource preflight
pause from85 are preserved. Original observations retain episode provenance;
learned definitions are conservative language extensions, not empirical axioms.

## Experimental shell

```
./scripts/recursive-selfssl.sh --demo /tmp/recursive86.sexp
./scripts/recursive-selfssl.sh --demo --rounds 4 --budget 4 /tmp/recursive86.sexp
./scripts/recursive-selfssl.sh --rounds 1 /tmp/recursive86.sexp
```

Default: one original interactive Maru reader, native idle task interval1000ms,
budget8. `--interval 20..60000`, `--budget 1..16`, `--rounds 1..1000` are optional.
The shell execs Maru directly; there is no Python transport/learner process.
Without `--rounds`, Ctrl-C ends the process and only completed checkpoints are
durable. Finite runs assert successful final close and return nonzero on admission,
resource or checkpoint failure. Invalid CLI values and malformed stores fail closed.
Relative store paths refer to the caller's working directory.

Demo sources are explicitly requested and only added if no source episodes remain.
Existing observations are not overwritten. A restored nd mode is preserved rather
than reconfigured on every launch, preserving frontier/stop replay. Runtime budget
and interval are launcher settings; use the same budget to compare the same next
step. Choosing this launcher on an older compatible store explicitly enables nd
mode and writes a new-tag checkpoint with the old checkpoint retained as previous.
Copy stores before experiments if the old-format file must remain untouched.

Saturation does not create new progress: the native REPL remains available for
new observations and prints waiting. The grammar, definitions12, candidate pool512,
unit limits, events256 and cumulative request budget100000 still bound learning.
This is not an unbounded autonomous curriculum or automatic web learning.

## Results

The explicit chain experiment learns primitive path lengths2 ->3 ->4, with each
later definition using an earlier learned definition. Branch counts are1/3/3,
with7 checked branch labels and10 certification calls (including3 final rechecks).
A fourth round saturates; reopening returns waiting without new learning events.
Native depth-four queries carry recursively checked proofs.

`python3 adapters/recursive86_experiment.py` compares36 fresh processes: three
structurally varied seeds, direct UCB versus nd-cache/nd-ucb, two repeats, randomized
arm order and two protocols. It reuses the Search85 parent-observed marker timing
and independent cold-graph/primitive-path oracle. Data:
`docs/recursive86-experiment.json`.

| Protocol/mode | Definitions by seed | Median live certify calls | Search s | Workflow s |
|---|---|---|---|---|
| Mixed, six rounds, memory / UCB | 3,3,6 | 8 | 0.3204 | 0.4968 |
| Mixed / nd-cache | 3,3,6 | 19 | 0.4166 | 0.5799 |
| Mixed / nd-ucb | 3,3,6 | 19 | 0.4652 | 0.6328 |
| Distractors, target2, attached / UCB | 2,2,2 | 2 | 0.2412 | 0.7229 |
| Distractors / nd-cache | 2,2,2 | 6 | 0.5360 | 1.2348 |
| Distractors / nd-ucb | 2,2,2 | 6 | 0.5193 | 1.2608 |

All modes had the same cold-probe instance coverage (mixed seeds5/2/4). Attached
median certification calls including checkpoint/close replay were15 direct versus
42 in each nd mode. Generated branches provide more checked labels, but batching,
validation and rechecking cost more. Negative-cache reuse within the same frozen
batch is not realized until its outcomes return, another cost of this design.

**Conclusion:** integrated generation/execution/verification/self-supervision works;
speedup and improved task coverage are NOT demonstrated. The new launcher is an
explicit experiment, not a claim that nd-ucb should replace all earlier defaults.
Future work should evaluate smaller/adaptive batches, validated short-circuit
search and incremental checkpointing before adding richer MCTS machinery.

## Boundaries and final verification

This does not yet solve arbitrary human questions, extract web axioms, synthesize
general programs or generate unrestricted natural-language answers. Those need
separate grounded input/goal semantics and a larger verified action grammar.

Eight new tests cover real branch execution, recursive supervision, gate safety,
retry semantics, exact fresh-process reconstruction, finite/interactive shell,
CLI validation and corrupt-store refusal. The public-command snapshot expectation
is updated to86; legacy codecs are still tested. Full suite:89 tests. Final
source/test manifests and Maru three-generation reproduction are recorded in
`docs/release-0086.md` after verification. Compiler/platform sources are unchanged.
