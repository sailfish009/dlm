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

- [x] `python -m pytest -q` → 89 passed.
- [x] `PYTHONPATH=. python examples/grounding_demo.py` runs (T1 hit, T2 hit, abstain).
- [x] `PYTHONPATH=. python examples/dialogue_demo.py` runs (induction, KB growth,
      deduction over the new fact, lexical fallback, abstention).
- [x] `python run_grounding_eval.py --epochs 150` → `artifacts/grounding_eval.json`
      (reproducible: lexical 0.547, t2_trained 0.352, t2_frozen 0.195).
- [x] `python run_dialogue_eval.py` → `artifacts/dialogue_eval.json`
      (t1_only 0.545/0.500, chain 0.727/0.750, 0 confident-wrong).
- [x] `dlm-chat` runs interactively (ask/tell/deny, `:kb`, `:quit`) and abstains
      on out-of-domain input.
- [x] v0.0002 decision eval still reproducible: `python run_eval.py`.

## Dialogue loop (W4)

- [x] Single variable = the grounder; intent forced with `ask`/`tell` so the
      measurement is the loop + grounder, not a question/statement heuristic.
- [x] Gold atoms/verdicts are explicit (not a self-consistent oracle), so wrong
      grounding is visible as `confident_wrong`.
- [x] Small-n caveat stated (n = 11 turns; a scripted smoke test, not a claim).
- [x] No generation; the only dynamic text is a `Proof.render()` rendering.
- [x] Ungrounded input abstains; a contradicting negated assertion is rejected.
- [x] Cross-referenced with NL-6 in `NEGATIVE_LEDGER.md` so the two contrasts
      (lexical vs learned; lexical vs abstention) are not confused.

## Artifact

- [x] `python tools/build_upload.py` → bundle + zip, folder == zip, sha256 printed.
- [ ] Verify the extracted bundle outside the checkout (pytest + examples + manifest).
- [ ] GitHub web upload (not performed; needs a remote URL/repo name).