# experiments/irlearn — the IR-TREE is the one medium (v0.0058)

v0.0057 made real progress on deduction, but it did so on a **flat**
`Atom`/`Rule` substrate while Lisp read a **different** form tree. The model was
improving deduction on one representation and reasoning about itself on another.
v0.0058 removes the split: the **IR-TREE is the one medium** — the object the
recursion grows and the object Lisp evaluates are the *same* canonical set of
forms.

## What one run does

| stage | what happens | where |
|---|---|---|
| perceive | own `dlm` source → IR-TREE: a canonical frozen set of head/arg forms (`calls`, `defined`, `documented`, `dunder`, `method`, `private`) | `dlm.irlearn.perceive_ir` |
| induce | search candidate shapes (compose/swap/reverse/identity) **on the tree**, scored on self-generated positives vs sampled negatives | `dlm.irlearn.induce_law` |
| recurse | reify the kernel-certified extension round by round; **the medium itself grows**; fixpoint is the round that adds nothing | `dlm.irlearn.recurse` |
| lisp | build a Lisp `Env` from the *same* tree, derive the levels through Lisp's own `eval_form`/`findall`, and compare against the kernel | `dlm.irlearn.lisp_env` / `lisp_recurse` / `lisp_kernel_agreement` |
| roundtrip | `parse(dump(f)) == f`, `atom_ir(ir_atom(f)) == f`, `pattern_key` alpha-invariant; a Lisp macro writes a new form back into the same tree | `dlm.irlearn.roundtrip` / `lisp_writes_ir` |

## Measured on the model itself (deterministic, offline)

```
medium     : IR-TREE 1272 forms over 350 nodes / 578 call edges
induction  : law(form)=compose  tp=400 fp=0     (identity/reverse/swap lose)
deduction  : one_shot recall=0.306  recursive recall=1.000  fixed=True
             medium 2538 -> 5075 -> 7813 -> 10551 forms; false=0 each round
lisp       : reads IR-TREE; one_shot_match=True, final_match=True, kernel_match=True
             (2738 pairs, 4 levels)
roundtrip  : read/dump exact=True, atom/rule projection exact=True
macro      : wrote (r1 probe_a probe_b) into the same tree (in_env=True)
```

The deduction gain is exactly the v0.0057 one — but it now happens **on the
IR-TREE**, and Lisp proves the **same** levels through its own `findall`. That
agreement (Lisp == kernel at every level) is the point of the version.

## The unification, precisely

`dlm/ir.py` named the form tree but nothing *learned* on it; `dlm/lisp.py`
evaluated forms but the deduction ran elsewhere. v0.0058 makes a single
`IRTree` the medium for both:

- the same object is what the recursion grows (`medium.forms` climbs each round)
  and what `lisp_env` loads;
- the induced law is a **form** (`(rule (reach ?x ?z) (calls ?x ?y) (calls ?y ?z))`)
  and the same definitional level rules are executed through Lisp;
- the round-trip and projection are exact, so nothing is lost translating between
  the deduction view and the representation view;
- a Lisp macro can *write* into the medium, and the written form is visible to the
  kernel (`written_in_env`).

## Honest boundary

- The deduction medium and the Lisp medium are literally the same object; both
  the round-trip and the Lisp/kernel agreement are demonstrated on the model's own
  `dlm` source (bounded, deterministic, network-free).
- The **law is still induced** in a small generic rule space; v0.0058 fixes the
  *representation*, not the reach of the induction. It does not yet rival the
  open-ended induction of an LLM.

## Run

> The single recursive-SSL entry point is `experiments/selfssl/selfssl.sh`; this
> bounded experiment remains as an internal validation module (no shell).

```bash
python3 experiments/irlearn/run.py
python3 experiments/irlearn/run.py --rounds 8
```

Verdicts (`all_ok`): `ir_tree_is_the_medium`, `law_induced_on_the_tree`,
`induction_discriminates`, `recursion_improves_deduction`,
`recursive_reaches_closure`, `no_false_derivations`, `medium_grows`,
`lisp_reads_ir_tree`, `lisp_evaluates_induced_law`, `lisp_findall_matches_kernel`,
`lisp_writes_ir`, `ir_roundtrip_exact`, `pattern_key_invariant`, `deterministic`.