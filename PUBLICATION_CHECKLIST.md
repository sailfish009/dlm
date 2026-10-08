# Publication checklist — dlm v0.0003

## Claims

- [x] Claim tiers declared (Tier 2 grounding/engine, Tier 1 calibration/retrieval, no Tier 3).
- [x] Single core variable per comparison (the grounder); arms differ only there.
- [x] Registered negative recorded, not tuned around: `NEGATIVE_LEDGER.md` NL-6
      (`control_favored`: lexical 0.547 > learned 0.352).
- [x] Limitations stated: no pretrained encoder; 128 training pairs; grounding is
      Tier 2 and imperfect; 6GB is a constraint, not an advantage.

## Grounding method (pre-registered before numbers)

- [x] Threshold tuned on VAL only, frozen for TEST.
- [x] Arms share one candidate atom set; test atoms ⊆ train atoms.
- [x] T1 uses train phrases only, so its held-out coverage is 0 by construction.
- [x] `by_phrase` breakdown reported, not just the aggregate.
- [x] No free-text generation in the answer path (retrieval + abstain + template).

## Evidence

- [x] `python -m pytest -q` → 59 passed.
- [x] `PYTHONPATH=. python examples/grounding_demo.py` runs (T1 hit, T2 hit, abstain).
- [x] `python run_grounding_eval.py --epochs 150` → `artifacts/grounding_eval.json`
      (reproducible: lexical 0.547, t2_trained 0.352, t2_frozen 0.195).
- [x] v0.0002 decision eval still reproducible: `python run_eval.py`.

## Artifact

- [x] `python tools/build_upload.py` → bundle + zip, folder == zip, sha256 printed.
- [ ] Verify the extracted bundle outside the checkout (pytest + examples + manifest).
- [ ] GitHub web upload (not performed; needs a remote URL/repo name).