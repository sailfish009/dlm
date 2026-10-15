# self-evaluation + weakness-targeted curriculum (v0.0056)

The model is **not told what to look for**. It reads its own ability off the
kernel closure, finds the deduction target it cannot yet conclude, asks the web
only for the premise it lacks, re-closes, re-assesses, and stops on a *named*
reason. This is the closed self-evaluation loop the earlier versions were missing:
web access, search, acquisition and the self-supervised loop live inside `dlm/`
(`dlm/ability.py`, `dlm/curriculum.py`, `dlm/agent.py`'s `Reader.self_improve`),
not in the experiment.

## The loop

```
ASSESS   ability_profile(rules, kernel_closure)      dlm/ability.py
PICK     weak_spots -> actionable external premise   dlm/ability.py
ASK      build a search request from the gap         dlm/curriculum.py
ACQUIRE  web search (abstain when evidence missing)  dlm/acquire.py
RE-CLOSE kernel closure of the enlarged knowledge    dlm/__init__.py
SCORE    which targets became provable               dlm/ability.py
REPEAT   to a named stop
```

The deduction targets are **unrestricted**: `target_predicates` returns every
predicate some rule can conclude (plus observed fact predicates). Whatever the
model's theory promises is the agenda.

## North-star slice

The reader proves `trains(<program>)` but cannot prove `recognizes(<program>, <what>)`,
because `dataset_of` (what the dataset contains) is neither in the code nor in a
symbol's definition. The model discovers that gap itself, searches for it, and one
acquisition makes the target provable:

```
actionable weak spots before: ['recognizes']
  * premise  recognizes  missing=['dataset_of'] external=['dataset_of']
  round 0: recognizes <- [what does dataset mnist contain]
           acquired=[dataset_of(mnist, handwritten_digit)]
           improved=True gained=['recognizes']
stop: saturated
```

## Multi-round

A synthetic theory with three independent weak spots proves the loop **iterates**:
three rounds, one target gained per round, then `saturated` because no weak spot is
left — the model was not told how many there were.

## Falsifiers

| verdict | meaning |
|---|---|
| `weakness_identified` | the model itself finds an open target with an acquirable gap |
| `improvement_from_web` | one self-directed acquisition proves the target |
| `web_target_resolved` | no actionable weak spot remains afterwards |
| `targets_unrestricted` | the target set is discovered from the theory, not a fixed list |
| `scramble_no_gain` | a scrambled acquisition improves nothing |
| `no_web_abstains` | with acquisition removed the loop abstains, invents nothing |
| `stop_named` | the loop halts on a named reason |
| `multi_round_self_improvement` | three weak spots resolved one per round |
| `deterministic` | two runs are byte-identical |

## Honest limits

- The **agenda** is predicate-level (`dataset_of` is missing *somewhere*); only the
  **kernel** is argument-level. A scrambled fact can therefore *silence* a weak
  spot without proving the target — the model stops asking, but it never asserts
  anything false. This is the conservative direction (abstain, don't invent).
- Acquisition abstains (no fact) when the cache/network has no evidence, so offline
  replay is byte-for-byte deterministic.

## Usage

```bash
./experiments/selfimprove/selfimprove.sh
OUTDIR=reports/selfimprove/mine ./experiments/selfimprove/selfimprove.sh
python3 -m pytest tests/test_ability.py tests/test_curriculum.py -q
```