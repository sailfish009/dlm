# DLM v0.0003 — PRE-REGISTRATION

Governed in spirit by `/research/GUIDELINES.md`. No quantum resource is claimed.

This version ships two evaluated systems: the v0.0002 **decision engine**
(`run_eval.py`) and the v0.0003 **grounding front-end** (`run_grounding_eval.py`).

---

## A. Grounding front-end (v0.0003)

### Identity

The NL front-end maps a user sentence to a predicate atom, or abstains. It is the
SAME bottleneck as web-text extraction, so it is the primary risk.

- **No generation in the answer path.** T2 is retrieval: nearest candidate atom
  over a fixed atom index, or abstain below a threshold.
- **Tiers** behind one `Grounder` protocol: T1 deterministic grammar
  (`GrammarGrounder`), T2 learned (`LearnedGrounder`) or lexical
  (`CharNgramGrounder`), chained by `ChainGrounder`.
- **Borrowed structure** (not code): a projection head trained with a
  bidirectional in-batch InfoNCE and a learnable `logit_scale` (CLM
  `_clm_loss` shape), with group masking. pyssl-style SSL is future work.
- No pretrained encoder exists on this host (no `transformers`; MeowLLM ships no
  weights), so the ~3.1M encoder is trained from scratch on 6GB.

### Claim tiers

| Component | Tier | Why |
|---|---|---|
| Grounding exact-match on a fixed test set | **Tier 2** | deterministic metric |
| Threshold / retrieval effects | **Tier 1** | calibration knob |
| Whole system | **no Tier 3** | no hardware/quantum claim |

**R2.3 compliance**: no "advantage" language. 6GB is a constraint.

### Single core variable / matched arms

The only variable is the grounder. All arms see the same sentences and the same
candidate atom set (64 atoms = 4 relations x 16 ordered entity pairs).

| Arm | Grounding source |
|---|---|
| `t1_train` | deterministic grammar over TRAIN phrases only |
| `lexical` | char-3gram cosine nearest prototype (no learning) |
| `t2_trained` | encoder + head trained end to end |
| `t2_frozen` | same head, encoder frozen at random init |

### Splits and threshold policy (fixed before the run)

- Phrases per relation are split into **train / val / test**; the test phrasing is
  unseen, so `t1_train` abstains on all of it by construction.
- The retrieval threshold is chosen on **VAL only**, then frozen for TEST.
- Test atoms are a subset of the train atom index (no unwinnable items).

### Postulates

- **G1 (abstain over guess)**: a grounder that cannot map the sentence returns
  `ok=False`; it never fabricates an atom.
- **G2 (learning is real)**: `t2_trained` beats `t2_frozen` and chance.
- **G3 (registered null)**: if the learned grounder does not beat the lexical
  baseline on the same split, that is recorded as `control_favored` and the
  lexical grounder stays the default. Ties are ties.

### Judgement / stop rules

- **Survival**: `t2_trained` ≥ `lexical` on exact-atom accuracy, with G1 intact.
- **Null**: register it (done: `NEGATIVE_LEDGER.md` NL-6) and do not claim a win.
- Every number carries (n, split, path). No best-of-sweep.

---

## B. Decision engine (v0.0002, still shipped)

DLM v0.0002 is a **System-One decision engine** for CLM / strands-decider style
pipelines. The LLM **torso and learned head are replaced by DLM deduction** on a
closed, groundable view:

- **Input**: a `state` and `questions` in the strands-decider wire shape
  (`noul`, `choice`, `score`).
- **Decision**: each option is interpreted to a logical atom, the KB is queried,
  and the answer distribution comes from **derivability + proof features**,
  calibrated on a small feature set. No embeddings, no tokenizer, no LoRA, no
  LM head, no vision tower in the decision path.
- **Output**: the same wire types (`NoulAnswer`, `ChoiceAnswer`, `ScoreAnswer`)
  with the same confidence formulas.

Franca / pyssl are **not** part of the decision path. They are the perception
encoders behind an optional `Grounding` hook (image → predicates), considered
separately.

## Claim tiers

| Component | Tier | Why |
|---|---|---|
| DLM decision (enumerate → prove) | **Tier 2** | exact symbolic semantics; auditable proof |
| Calibration over discrete features | **Tier 1** | learned bias |
| Whole system | **no Tier 3** | no hardware/quantum advantage claimed |

**R2.3 compliance**: no "advantage" language. 6 GB is a constraint, not a gain.

## Single core variable / matched arms

The only variable is the **decision source**. All arms share the same KB, the
same interpreter, and the same candidate options.

| Arm | Decision source |
|---|---|
| **B (DLM)** | exact proof: derivable / refuted / partial features |
| **A (matched)** | learned head on the *same discrete features* (no proof) |
| **C (prior)** | retrieval-only base rate (no proof, no head) |

Arm A isolates the *proof* from the *features*: same inputs, learned readout.

## Postulates (written before the run)

- **P1 (soundness)**: for `noul`, whenever DLM returns P(true) above the act
  threshold, the statement is entailed; a refuted statement never gets P(true) > 0.5.
- **P2 (exact preference)**: on a task where the KB alone is sufficient and only
  one option is derivable, `choice` accuracy is 1.0 and confidence ≥ 0.9 (a
  forced answer is certain).
- **P3 (abstention)**: options that cannot be interpreted to an atom yield
  abstention, never a fabricated probability.
- **P4 (registered null, carried from v0.0001)**: on a task where options are
  groundable but the *features cannot separate* an instantiable-but-wrong option
  from a good one, arm A and arm B are tied, and both exceed chance only via the
  base rate. Expected; recorded, not tuned.

## Judgement / stop rules

- **Survival**: B ≥ A on groundable decision tasks with exactness (P1) intact,
  and B is not worse than A where P4 does not apply.
- **Null**: if B ≈ A everywhere, report that proofs add nothing over features on
  these tasks and register it; do not claim a win.
- Ties are ties. Every number carries (n, split, path). No best-of-sweep.

## Scale and limits

- Closed domains only. If the KB does not ground an option, the engine abstains.
- The learned components (rule induction, calibration) are bounded as in v0.0001.
- Retrieval recall upper-bounds decision quality.

## Next decision this run informs

If B survives, keep the engine and invest in the **interpreter/grounding** layer
(so more real questions become groundable). If B ≈ A, pivot to grounding rather
than decision tuning.
---

## C. Dialogue loop (v0.0003, W4)

Registered for completeness: the arms, metric definitions, and the judgement rule
below were fixed in `run_dialogue_eval.py` **before** the numbers were read
(`judge()` is a pure function of the two arms' metrics).

### Identity

`DialogueSession` is not a new capability; it is the loop that assembles the
existing parts:

    utterance -- Grounder --> Grounding(kind=query|assert)
        assert -> contradiction check -> kb.add_fact (user provenance)
        query  -> DecisionEngine.noul(atom) -> proof -> template verbalizer
        ungrounded / non-ground atom -> ABSTAIN;  negated contradiction -> REJECT

No generation. The only dynamic reply text is a `Proof.render()` rendering.

### Single core variable / matched arms

The only variable is the grounder; everything else (KB, scripted turns, forced
intent with `ask`/`tell`, verbalizer) is identical.

| Arm | Grounding source |
|---|---|
| `t1_only` | grammar over TRAIN phrasing only (abstains on unseen) |
| `chain`   | `t1_only` + lexical char-3gram T2 (the adopted default fallback) |

### Metric definitions (fixed before reading)

- `coverage` = fraction of turns the grounder grounded.
- `exact_atom_accuracy` = over turns with a gold atom; wrong atom counts wrong.
- `verdict_accuracy` = over turns with a gold verdict; **abstention counts as an
  incorrect verdict** (end-to-end usefulness).
- `verdict_accuracy_when_grounded` = same, excluding abstentions.
- `confident_wrong` = grounded turns whose verdict disagrees with gold (a sound
  proof of the wrong atom). This is the failure mode that dominates a bad
  grounding, so it is reported separately and never averaged away.

Gold atoms/verdicts are explicit, not re-derived from the KB, so a wrong
grounding cannot hide behind a self-consistent oracle.

### Judgment rule (fixed before reading)

- `control_favored` if `chain.confident_wrong > t1_only.confident_wrong`.
- `fallback_helps` if `chain.coverage > t1_only.coverage` **and**
  `chain.verdict_accuracy >= t1_only.verdict_accuracy`.
- `tie` otherwise.

### Postulates

- **D1**: the loop never generates text and never invents an atom.
- **D2**: ungrounded input abstains; a negated assertion contradicting the KB is
  rejected; a non-ground atom is never asserted.
- **D3 (small-n)**: n is 11 (4 unseen), so any judgement here is a smoke test of
  the loop, **not** a claim about general dialogue. This is stated in the payload.

### Result

Judgement `fallback_helps` (recorded in `RESULTS_DIALOGUE.md`,
`artifacts/dialogue_eval.json`). This concerns a **different contrast** from NL-6
(lexical vs *learned*); here the alternative to lexical is *abstention*.
