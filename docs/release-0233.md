# Release 0.0233 — Schema-Aligned Real Web Axiom Decomposition

- Date: 2026-11-13
- Predecessor: 0.0232
- Type: candidate research release
- Runtime: `20261113T083631Z-25576`

## Fixes

- gold/extracted schema is now 5 fields: `(id kind pred subj obj)`.
- positive control: gold-vs-gold TP=22/22.
- negative control: wrong tuple TP=0.
- `nl-fact-parse` no longer emits an empty-object fact.
- leakage flag is computed from input shape.
- parser-representable isa-only gold is reported as 6/22.
- independent oracle agrees with eval.
- stub-only output is rejected by the gate.
- source revision/checksum metadata added for six pages.

## Result

```text
GOLD-EXPRESSIBLE 6/22 (isa-only parser cap)
TEXT 15 EXTRACTED 3
TP 0 FP 3 FN 22
PRECISION 0/3 RECALL 0/22
GATE FACTS 3 RULES 0 PROOF fail
EMPTY-TEST nl-unknown
GOLD-FIELDS-IN-INPUT false
ORACLE TP 0 FP 3 FN 22
PERFECT-TP 22/22 WRONG-TP 0 EMPTY-TP 0
SOURCE-META 6
V0233-PHASE6-ADVERSARIAL-PASS
STUB-REJECTED
```

The current parser still extracts zero correct real-web axioms. The metric is
now schema-aligned and discriminative, so this is a measured negative result
rather than a column-shift artifact. Recall is also capped by the parser's
isa-only grammar (6/22 gold axioms).

## Verification

```bash
cd /research/dlm_v0.0233/experiments/real_web_axiom_decomposition
./run_all.sh
```

Release:

```bash
cd /research/dlm_v0.0233
env PATH=/opt/miniconda3/envs/py314/bin:$PATH ./scripts/verify_release.sh
```

## Limits

- 15 passages, 22 gold axioms; small and author-decomposed.
- Current extractor is rule-based `nl-parse`; no learned transformer.
- `oldid/checksum` is page-level, not per-passage.
- MLIR not used.
