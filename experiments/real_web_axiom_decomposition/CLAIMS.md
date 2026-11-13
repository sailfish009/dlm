# v0.0233 Claims and Limits

## Supported

```text
- gold/extracted are schema-aligned to (id kind pred subj obj)
- gold-vs-gold positive control: 22/22
- wrong/empty controls: 0
- nl-fact-parse no longer fabricates an empty-object fact
- leakage flag is computed from input shape
- parser-representable isa-only gold cap: 6/22
- current parser real-web extraction: TP0 FP3 FN22
- independent oracle agrees with eval
- stub-only output is rejected
- adversarial controls pass
- repeated run is byte-identical
- experiment source is in the release manifest
```

## Not supported

```text
- "current model can decompose real web text into axioms"
  -> measured TP0/22; no such claim.
- "recall is 0%" as a general parser property
  -> only this 15-passage sample and parser.
- transformer extraction
  -> rule-based nl-parse only.
- per-passage provenance
  -> oldid/checksum is page-level only.
- multi-annotator gold
  -> author-decomposed single annotation.
```

## Commands

```bash
cd /research/dlm_v0.0233/experiments/real_web_axiom_decomposition
./run_all.sh
./final_review.sh
```

```bash
cd /research/dlm_v0.0233
env PATH=/opt/miniconda3/envs/py314/bin:$PATH ./scripts/verify_release.sh
```
