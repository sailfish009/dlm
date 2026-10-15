# experiments/closedworld — closed-world deduction (v0.0047)

The v0.0044–46 reading raised the *presentation* ladder (N1→N8); every conclusion
was still a Horn positive. This stage raises the **deduction level**: the trusted
kernel gains **stratified negation**, so it can derive a *certified negative* — and
for the first time the closure is **non-monotonic**.

Untrusted rule the experiment needs (`dlm/closedworld.py`):

```
absent(?m, ?l) :- is_module(?m), candidate_layer(?l), not has_layer(?m, ?l)
```

The closed-world assumption is scoped to `candidate_layer` — the one universe we
claim to have enumerated.

```bash
./experiments/closedworld/closedworld.sh --offline
# or: ../../northstar.sh --version v0.0047 --offline --check
```

On the real `main.py` the kernel certifies six absences
(`attention, batchnorm2d, gru, layernorm, lstm, maxpool2d`) beside the three
present layers (`conv2d, dropout, linear`).

## Probes (all required by `verdict`)

| probe | what it shows |
| --- | --- |
| `negatives_derived` | a certified negative is produced |
| `every_absence_is_not_a_has` | each `absent` is justified, not asserted |
| `monotone_addition_retracts` | adding `has_layer(net,maxpool2d)` retracts `absent(net,maxpool2d)` — pure Horn cannot retract |
| `non_stratified_rejected` | a negative dependency cycle raises `ValueError` (never guessed) |
| `unsafe_negation_asserts_nothing` | a negated literal unbound after the positive join is pruned |

## Soundness guards (in the kernel)

* `strata(kb)`: `stratum(head) = max(max positive-body strata, 1 + max negated-body strata)`.
* `closure()` dispatches: no negation → the unchanged semi-naive Horn evaluator;
  negation → strata evaluated ascending to a fixpoint.
* a non-stratifiable theory is **rejected**; an unbound negated literal is **pruned**.

`reports/closedworld/<stamp>/result.json` holds `known_layers`, `candidate_universe`,
`absent`, the `retraction_probe`, `strata`, and `verdict`.