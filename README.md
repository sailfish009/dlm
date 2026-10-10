# DLM v0.0006

Rebuilt from the first principle. v0.0005 is kept frozen as a reference for the
overall skeleton; v0.0006 starts from nothing and implements only the core idea:

> **Recognize the general logic a natural-language sentence instantiates, make
> it explicit as a function-free Horn atom, and abstain when it cannot.**

"Decomposition" is only the surface trace of that recognition.

## Why a fresh start

The v0.0005 front-end converts language to atoms by *template lookup* over a
closed vocabulary: the predicate name is hard-coded in the phrase pattern, so
the same logical form cannot be recognized under a different vocabulary. The
target normal form, the role/schema convention, and state -> facts grounding are
absent. v0.0006 rebuilds those from the ground up.

## Module 1 — `dlm/logic.py` (semantic normal form)

The **target** of the conversion:

- `Const`, `Var`, `Term` — function-free terms.
- `Atom` — a predicate applied to ordered terms.
- `Literal` — an atom with a sign (negation is metadata, never a predicate).
- `Schema` — a predicate's arity and **role order**: the general, transferable part.
- `Frame` — the surface `role -> filler` read from a sentence (unordered).
- `SchemaRegistry.normalize(frame) -> Literal | None` — order fillers by schema,
  or **abstain** (unknown predicate / role mismatch).

```
sentence --(reader, module 3)--> Frame --(normalize)--> Literal
```

## Module 2 — `dlm/sexp.py` (canonical concrete syntax)

S-expr is the **surface notation** for every logic unit (atom / literal / rule /
proof all share it). It is *not* a semantic engine: the logic stays function-free
Horn, and "abstain, never guess" still applies.

- `parse(text)` — general, read-only S-expr reader; **never `eval`** (trust boundary).
- `dump` / `dump_all` — the matching writer.
- `atom_to_form` / `form_to_atom` / `literal_to_form` / `form_to_literal` — the
  bridge to module 1.
- The parser accepts nesting; the function-free core still **rejects** it at
  `Atom` construction. Syntax is general, semantics abstains.

`logic.py.__str__` now also emits canonical S-expr, e.g. `(parent alice bob)`,
`(not (charges c1 c2))`.

## Module 3 — `dlm/reader.py` (sentence -> Frame, seam B)

The **conversion** itself, as an untrusted proposer (protocol `Reader`). A
learned reader (CLM action head / seq2seq) can replace `LexicalReader` behind
the same method.

- Closed, role-labelled subset, **full match only**: `E V` -> `V(agent=E)`;
  `E V E` -> `V(agent=E, patient=E)`; `E COP P E` -> `P(figure=E, ground=E)`;
  `E COP V` -> `V(subject=E)`.
- Deterministic preprocessing: lowercase, expand `n't`, drop possessives /
  determiners / punctuation / auxiliaries; a negation word sets the frame sign.
- `read(sentence) -> tuple[Frame, ...]`: **all** distinct readings are returned
  (ambiguity preserved, not resolved); `()` means **abstain**. An unknown
  predicate word or an unconsumed token makes the sentence unreadable.

```
"Alice calls Bob"        -> calls(agent=alice, patient=bob)
"The cat is on the mat"  -> on(figure=cat, ground=mat)
"Alice flies to Rome"    -> ()   # 'flies' not in the lexicon -> abstain
```

## Module 4-6 — `kb.py`, `engine.py`, `kernel.py` (kernel C)

The trusted deduction core that logic self-supervision (B) uses as its
correctness criterion.

- `KnowledgeBase` (`kb.py`) — ground facts + definite Horn `Rule`s (now in
  `logic.py`) + a negation side table. Facts are indexed by predicate. It also
  hosts **seam A**: `StateGrounder` (protocol) + `StateBinding` +
  `DictStateGrounder`, which ground a structured `state` dict into role-labelled
  `Frame`s (see Module 7); `add_facts` bulk-loads the result.
- `engine.py` — `closure` (forward chaining to the least fixpoint = derivation
  set), `prove` (rebuilds a re-checkable `Proof` from the closure's support, so
  it is **complete by construction** and never disagrees with `entails`),
  `holds` (positive by closure, negative only by the side table).
- `kernel.py` — `Proof` + `verify`: re-check a certificate against the KB with
  **no search**; it must bottom out only in known facts and known rules.
- `unify.py` — function-free unification shared by engine and kernel.

```
(rule (ancestor ?x ?y) (parent ?x ?y))
(rule (ancestor ?x ?z) (parent ?x ?y) (ancestor ?y ?z))

closure(ancestor) = (ancestor a b) (ancestor a c) (ancestor a d) ...
prove(ancestor a d) -> (proof ...)      verify(proof, kb) == True
```

## Module 7 — `dlm/convert.py` (input ingress, the firewall)

Standing decision (NOTE.md §27): natural language exists **only at the input
boundary**. User input and external data are all text, so text is converted to
logic **immediately at ingress** and no sentence is retained inside the model.
After this module the only strings are *symbols* (predicate / role / constant
names), never phrases.

- `Ingestor(reader, registry)` — the single entry point. `literals(sentence)`
  returns every normalized reading; `literal(sentence)` is the strict gate that
  **abstains on 0 or >1** readings. `logic(text)` / `form(form)` accept
  already-symbolic S-expr and skip the reader.
- `sentence_to_literals` / `sentence_to_literal` / `form_to_logic` — the pieces.
- Two paths: (a) text → reader (untrusted) → normalize (trust boundary) →
  `Literal | abstain`; (b) symbolic form → function-free check →
  `Atom | Literal | Rule`. A third path grounds structured state:
  (c) `state` dict → `StateGrounder` (seam A) → normalize → facts,
  via `Ingestor.facts(state)` / `state_to_facts`.
- **Nothing textual leaves this module.** Downstream (judge, engine) receives
  logic only.

```
Ingestor.literal("Alice calls Bob")  -> (calls alice bob)
Ingestor.literal("Alice flies")      -> None            # abstain
Ingestor.logic("(rule (r ?x) (calls ?x bob))") -> Rule
Ingestor.facts({"edge": ["alice", "bob"]}) -> (parent alice bob)    # seam A
```

## Module 8 — `dlm/judge.py` (judgment, seam D)

The first-class judgment protocol. It keeps the two kinds of signal structurally
separate:

- **trusted verdict** — a re-checkable proof (seam C) that a ground `Literal` is
  entailed, or an explicit negative in the side table. **Only this asserts.**
- **untrusted score** — a number a `Proposer` attaches to a candidate (CLM
  cosine, strands logit, a learned reader, retrieval). It may only *choose what
  to try* or *annotate confidence*.

- `Verdict` — `ASSERTED` / `REFUTED` / `ABSTAIN`.
- `Judgement` — `literal`, `verdict`, `proof`, `score`, `confidence`, `source`.
- `Proposal` — an untrusted candidate `literal` + `score`.
- `Judge` protocol (trusted) and `Proposer` protocol (untrusted).
- `ProofJudge` — asserts iff `prove -> verify` succeeds; a ground negative is
  refuted only by the side table; non-ground literals abstain.
- `StaticProposer` / `KbProposer` — untrusted arms (fixed fixtures / KB facts).
- `Adjudicator` — fuses a `Judge` with proposals under `Policy.GATE` (P1) or
  `Policy.TWO_AXIS` (P3).

```python
adj = Adjudicator()
lie = Proposal(Literal(Atom("steals", (Const("alice"),))), score=1.0, source="evil")
adj.decide(kb, query=lie.literal, proposals=[lie])   # -> ABSTAIN (never asserted)
adj.decide(kb, query=legal_literal)                  # -> ASSERTED if provable
```

The invariant is structural: the `Adjudicator` never reads a proposer's verdict,
only its `Literal` and `score`, so a high score cannot manufacture an assertion.
`GATE` drops the learned signal when the proof abstains; `TWO_AXIS` keeps it as
display-only confidence (the verdict is still `ABSTAIN`).

## Module 9 — `dlm/wire.py` (System-One boundary)

DLM behind the **same JSON interface** as CLM / strands-decider / TypeSafe:
`{state, questions} -> {model, answers, usage}` with `noul` / `choice` / `score`
questions. Anything with `answer(request) -> response` satisfies `WireService`,
so the services are interchangeable by construction.

- **NL only at the boundary**: `state` is grounded to facts (seam A) and every
  question text becomes a `Literal` (seam B) immediately.
- **Egress is template-only**: a DLM answer *renders* a proof-backed verdict; it
  never generates prose. Where the schema has no way to say "I cannot", DLM adds
  honest fields (`abstain`, `literal`, `proof`, `verdict`, `reason`). Consumers
  must check `abstain` — DLM never guesses to fill a slot.
- **DLM extension**: an optional `theory` list of S-expr strings (rules / facts /
  explicit negatives) makes deduction possible. `state` gives the situation,
  `theory` the laws; each request runs on a copy of the base KB.

Honest answers per type: a `noul` is true iff proved, false iff its **opposite**
is on record, otherwise it abstains (absence is not refutation). A `choice`
picks its key only when exactly one option is provable; 0 or >1 provable options
abstain. A `score` question is outside the Horn fragment and always abstains.

```python
svc = DlmService(Ingestor(reader, registry, grounder))
svc.answer({
    "state": {"edge": ["alice", "bob"]},
    "theory": ["(rule (knows ?x ?y) (calls ?x ?y))"],
    "questions": {"q": {"type": "noul", "instructions": "Alice knows Bob"}},
})
# -> answers.q = {noul: 1.0, abstain: False, verdict: "asserted",
#                 proof: "(proof (knows alice bob) rule (calls alice bob))"}
```

## Module 10 — `dlm/selfsup.py` (DLM-native self-supervision)

Not surface pretexts. The unlabeled resource is the **theory itself**, and the
**trusted kernel (C) is the correctness criterion**; the target of every pretext
is the *evaluation result*, so what is learned is logic, not form (decision B).

Kernel-labeled pretexts: `closure_mask_examples` (derive-or-not),
`minimal_pairs` (schema-violating permutation / sign flip — logical edits that
change entailment), `rule_removal_examples` (redundancy delta),
`compose_rules` / `rule_composition_examples` (a composed rule must not extend
the closure), `proof_holes` (reconstruct a hidden premise). `ssl_l_examples`
bundles the **SSL-L** (logic-side) ledger.

The learned object is an **untrusted proposer** (seam B'/D): a dependency-free
`FeatureScorer` over structural + symbol-identity features, wrapped as a
`ScorerRetriever` (`Retriever` protocol). It only *ranks*; the kernel still
decides.

Evaluation is the fixed protocol: `soundness` first, then `recall_at_k`
(held-out derivation completeness), then `proof_cost`; controls are `flip_labels`
(surface-SSL) and `scramble_constants` (shuffled-KB).

```
recall@k  no-SSL=0.57   trained=1.00   surface(flip)=0.00   shuffled-KB=0.71
soundness = True
```

The **SSL-NL** ledger is separate: `RejectionSelfTrainer` accepts a
`(sentence, Literal)` pair only if the kernel already proves it, so it can only
reinforce what the KB entails and cannot invent vocabulary grounding (the
NL↔logic problem stays open).

## Run the tests (without disturbing the editable v0.0005 install)

```bash
cd /research/dlm_v0.0006
PYTHONPATH=. python -m pytest -q
```

See `work.txt` for the module plan and resume point.