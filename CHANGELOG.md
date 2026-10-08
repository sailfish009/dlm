# Changelog

## 0.0.3 — grounding front-end (branch L1–L4)

Added the natural-language front-end and measured it.

### Added
- `dlm/byte_tokenizer.py` — dependency-free byte tokenizer (vocab 260); `tokenizers`
  is not installed, so MeowLLM's BPE file is not used.
- `dlm/tiny_encoder.py` — ~3.08M encoder vendored from MeowLLM blocks (MIT); RoPE,
  RMSNorm, SwiGLU, SDPA with an additive key-padding mask; `freeze()`/`unfreeze()`.
- `dlm/grounder_learn.py` — `ProjectionHead` (CLM-style linear + L2 + `logit_scale`),
  `LearnedGrounder` (bidirectional InfoNCE with group masking; retrieve-or-abstain),
  `CharNgramGrounder` (untrained lexical control), `AtomIndex`, `synthesize_pairs`,
  `pattern_split`.
- `run_grounding_eval.py` — matched-arm evaluation with a val-only threshold;
  writes `artifacts/grounding_eval.json` (incl. per-phrase breakdown).
- `examples/grounding_demo.py` — `ChainGrounder([T1, lexical])` + DLM proof.
- `RESULTS_GROUNDING.md`, this version's publication checklist, bundle tool.

### Result (registered negative)
- Test exact atom: lexical **0.547** > `t2_trained` 0.352 > `t2_frozen` 0.195 >
  `t1_train` coverage 0.000 (chance 0.016). Judgment `control_favored`;
  registered as `NEGATIVE_LEDGER.md` NL-6.
- Adopted: lexical T2 is the default fallback; the learned grounder is promoted
  only if it beats lexical on the same split.

### Notes
- 59 tests pass (`pytest`); `by_phrase` shows the lexical arm wins mainly by
  entity-pair matching; both arms fail when relation words change.
- Bugs fixed while building: SDPA bool-mask polarity (now additive float mask →
  padding-invariant features); `AtomIndex` key normalisation (spacing);
  `LearnedGrounder.save/load` did not persist `proj_dim`/`default_threshold`.

## 0.0.2 — decision engine (LLM torso replacement)

See `dlm_v0.0002/CHANGELOG.md`. DLM answers the `strands-decider` wire
(`noul`/`choice`/`score`) from proof; matched arms B=1.000, A=0.467, C=0.467;
P4 registered null (2 false positives).

## 0.0.1 — deductive core

Horn engine, LGG rule induction, KB, retrieve/decide pipeline, demo + VRAM probe.