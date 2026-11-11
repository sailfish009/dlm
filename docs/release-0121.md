# Release 0.0121 — resident definition-learning loop in the Maru REPL

- Date: 2026-11-07
- Predecessor: 0.0120. This tree is a **candidate**, not promoted.
- Runtime: reuses the promoted 0.0116 release `20261107T064706Z-31624`.
- Exact name: **resident definition-learning loop**. It is not the completion of
  broad recursive self-supervision.

## What it does

One native Maru process opens a store, optionally seeds explicit demo
observations when the store is empty, starts a cooperative idle task, and hands
the terminal to the original `maru>` reader.

```text
(dlm 'start [ms])   start/resume the resident loop
(dlm 'pause)        user pause; unregister the idle task
(dlm 'stop)         pause, then save when a store is attached
(dlm 'status)       summary includes mode, round, interval, reason
```

The loop repeatedly runs the existing bounded agenda (`interpret` observations,
then `learn` one definition from the same data, then idle). When the agenda is
exhausted the idle task is **unregistered**; new evidence reactivates only a
loop that was `waiting`.

Launcher:

```sh
./scripts/selfssl.sh --demo /tmp/model121.sexp
```

The shell only execs `run.sh learn`; it does not restart Maru per round.

## Deliberately narrow scope

- **Grammar stays 2→3 atoms.** `p107-3-decomposition` reuses only an existing
  2-atom active definition. Repeated ticks therefore learn `b1` (2 atoms) and
  `b2` (3 atoms calling `b1`), then wait. Deeper chaining (`c0→c1→c2` like
  0.0077) is **not** produced; that needs a grammar extension and the inherited
  F2 (nested admitted-call execution) to be fixed first.
- **The idle interval is not a work-time bound.** A tick runs
  `p107-step-once` to completion. Long `p107-learn`/closure/proof work blocks
  the REPL reader; scheduling is cooperative, pending input has priority.
- **No self-generated observations or goals.** This release does not promote
  answers, readings or definitions into `obs107`. It does not need the full
  provenance tier yet because it does not feed its own conclusions back as
  observations.
- **F1 is still open.** The loop does not use `answer` as a self-supervision
  signal; `answer` still lacks the proof gate. No self-evaluation, weakness
  curriculum or goal frontier is added here.
- **Loop control state is not persisted.** `mode`, `round`, `interval` and
  `reason` are in-memory. `open`/`reset` start stopped at round 0. Only the
  semantic state (observations, interpretations, definitions, events) is saved
  and replayed.

## Failure and pause semantics

| event | result |
|---|---|
| agenda empty | mode `waiting`, idle task unregistered, no repeated search |
| new observation while `waiting` | mode `running`, task re-registered |
| new observation while `paused` / `stopped` / `halted` | mode unchanged |
| `unknown` status | mode `waiting`, reason `unknown` (reactivates on evidence) |
| `(rejected107 event-limit)` | mode `halted`, task unregistered |
| checkpoint/save failure | mode `halted`, task unregistered |

A halted loop requires an explicit `(dlm 'start ...)`; new evidence does not
silently clear a hard failure.

## Event-only output

- `interpreted` and `learned` are distinct events; learning is no longer printed
  as `interpreted`.
- `waiting` prints nothing; the task is unregistered at saturation.
- The Maru idle hook itself still emits a newline and `maru> ` after each task
  execution. That is one line per executed tick, not a per-interval waiting
  spam. Output can interleave with typed input.

## Measured

```text
start -> running; pause -> paused
observe while paused -> still paused
observe while running -> running
tick interpret x2, learn b1, learn b2, then waiting (round stays 4)
waiting + new observation -> running
pause + new observation -> still paused
tick while paused -> (p107-paused)
stop -> paused; reset -> (stopped 0 1000)
```

Launcher transcript (5 s wait before input):

```text
[dlm] interpreted demo-a
[dlm] interpreted demo-b
[dlm] learned b1
[dlm] learned b2
status ... mode running round 4 ... definitions 2
```

```text
native normal      223 ok / 0 FAIL
native safety-2    223 ok / 0 FAIL
Python             16 tests OK
review contract oracle (seed 116)  256/256 PASS
```

## Reproduce

```sh
./scripts/run.sh test
MARU="$PWD/runtime/safety2/maru" ./scripts/run.sh test
python3 -m unittest discover -s tests -p 'test_d107.py' -v
./scripts/selfssl.sh --demo /tmp/model121.sexp
```
