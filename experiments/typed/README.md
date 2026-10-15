# experiments/typed -- D6: typed/moded signatures

Run: `./experiments/typed/typed.sh --offline`

## The question

The learner (v0.0038+) admits a candidate rule only when the kernel derives no
negative with it.  That gate is *sound* but *blind to shape*: it never asks
whether the clause is even a well-formed sentence over a typed, moded
vocabulary.  D6 adds a static check in front of every derivation.

## What the kernel now does

`dlm.Signature` gives each predicate position a **type** and a **mode**
(`in` / `out` / `any`); `dlm.type_errors(rule, sig)` returns every reason a rule
is inadmissible, and `closure(kb, sig)` rejects an ill-typed theory with
`TypeError` *before* any fact is derived.  Four independent checks:

| check | rejects |
| --- | --- |
| predicate/arity | a call to an undeclared predicate, or the wrong arity |
| type soundness | one variable at two incompatible types; a constant outside its slot's type |
| range restriction | a head or negated variable bound by no **positive** body literal |
| mode anability | an `in` position that no head input or positive literal produces |

Types are a small acyclic lattice (`module <: fn <: callable`, `layer <: symbol`,
`dataset <: symbol`, ...): two types unify only when one is a subtype of the
other, so `module` and `symbol` **clash** even though both sit under `callable`.

## Why this is a level raise (not presentation)

The D5 closed-world rule

```
absent(?m, ?l) :- is_module(?m), candidate_layer(?l), not has_layer(?m, ?l)
```

is now checkable *statically*: `?l` is a `layer`, it is produced by
`candidate_layer`, and the negated literal's variables are range-restricted.  A
seed-3-style unsound clause (a module where a symbol is required; a head variable
bound by no body literal; an unbound negated literal; an input that is never
produced) is **inexpressible** -- it never enters the candidate set.

## Honesty

Typing only **forbids**.  For the honest theory the signature is a no-op on
truth: `closure(kb, sig) == closure(kb)`, and the same gist
(`recognizes(main, handwritten_digit)`) and the same six closed-world absences
are derived.  The signature cannot assert anything by itself.

## Result (real `mnist/main.py`, offline)

* 16 honest rules (bridge + gist + learned `calls` law + `absent`) -- all type-safe
* 7 adversarial clauses -- each rejected with its expected reason
* typing prunes **105,330 / 127,584** head-bound candidates (82%) on type/mode
  grounds before the kernel is asked; of 189,216 arity-valid clauses only 22,254
  survive
* vendored report: `reports/typed/<stamp>/result.json`