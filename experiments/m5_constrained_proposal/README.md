# M5 — constrained rule proposal with kernel reward

M5 is the conditional generative-proposal step.  It starts only after M1–M3
and the M4 recall gate passed.

## Generator

Finite Horn-rule grammar:

```text
head <- body1
head <- body1 & body2
head ∉ body, body predicates distinct, arity fixed
```

The generator proposes a small top-k set.  It compares:

```text
random_unconstrained  malformed triples, no grammar
random_valid          random valid grammar rules
prior                 training rule/component frequency only
kernel                symbolic utility reward only
constrained           grammar + prior + kernel reward
```

The held-out split is over whole rules: 70 train rules, 20 held-out rules.
Recovery means the top-k proposal contains the highest-utility held-out rule
for a test world.

## Result

```text
M5-SEED-31 constrained=0.792 kernel=0.819 prior=0.125 random_valid=0.069 false_constrained=0.000 false_unconstrained=0.544
M5-SEED-32 constrained=0.875 kernel=0.938 prior=0.188 random_valid=0.047 false_constrained=0.000 false_unconstrained=0.547
M5-SEED-33 constrained=0.342 kernel=0.408 prior=0.000 random_valid=0.079 false_constrained=0.000 false_unconstrained=0.529
M5-MEAN constrained=0.670 prior=0.104
M5-CONSTRAINED-DECODE-PASS
M5-KERNEL-REWARD-PASS
M5-FALSE-RULE-RATE-PASS
M5-HELD-OUT-RULE-PASS
M5-PASS
```

## Run

```bash
cd /research/dlm_v0.0238/experiments/m5_constrained_proposal
./run_m5.sh
```

## Limits

- The current generator enumerates the 90-rule finite grammar; this is a
  constrained search, not an autoregressive neural decoder.
- The kernel utility is an oracle reward in this synthetic world.
- The held-out split is rule-held-out, not real-web text.
