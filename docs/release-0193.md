# Release 0.0193 — actual web data + recursive self-supervision (candidate)

- Date: 2026-11-10
- Predecessor: 0.0192. Candidate, not promoted.
- Scope: fetch seven actual Simple Wikipedia pages, extract subclass edges,
  generate path labels from training edges, induce recursive rules, self-label
  with the induced closure, re-induce, and prove held-out paths.
- Analysis: `/research/analysis-web-recursive-0193.md`.

## Data

Pages:

```text
Dog Cat Bird Sparrow Mammal Animal Plant
```

Extracted edges (7):

```text
dog -> mammal
cat -> mammal
bird -> animal
sparrow -> bird
mammal -> animal
animal -> living-thing
plant -> living-thing
```

Held out from training:

```text
animal -> living-thing
plant -> living-thing
```

Training edges: 5. Self-supervised path positives: 3.

## Loop

```text
train edges
→ path positives (cat/dog/sparrow -> animal)
→ s-template-synthesize
→ recursive rule program + basis R1
→ p-close generates self-labeled isa positives (8)
→ s-template-synthesize with augmented positives
→ basis R2
→ held-out proof on full web edges
```

## Result

```text
WEB pages=7 edges=7 train=5
POS 3 SELF 8
RULES1 2 RULES2 2
HELD 3/3 NEG fail
done-web-recursive
```

Held-out:

```text
dog -> living-thing
sparrow -> living-thing
plant -> living-thing
```

Negative `living-thing -> dog` fails.

## Self-host

```text
compiler.sh reproduce
→ 20261110T093509Z-1578
compiler.sh verify 20261110T093509Z-1578
→ Verified
```

## Measured

```text
native normal   61 checks / 0 FAIL
native safety-2 61 checks / 0 FAIL
self-host       verified
```

## Still not

- extraction is heuristic and small (7 pages)
- held-out edge split is manual
- self-labeling is closure on the training graph, not a transformer teacher
- no persistent observation/basis store
- no open-web general parser
