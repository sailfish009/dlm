# Release 0.0093 — native EML-foundational basis experiment

## Goal and outcome

Implement an EML-based basis-formation experiment incorporating the previous
working latent-axiom goals: data-led internal structure, active use, later
formation, explicit conditions, human-usable partial results and laptop-scale
CPU operation. Do not substitute a routing optimization or an optional math
plug-in for that experiment.

The implemented path uses only EML/1/variables as primitive program vocabulary.
Numeric observations select B1, then B2 using B1, then B3 using B1/B2, then B4
using B3. Queries execute the resulting organization without stored answers.
Data updates extend/withdraw scoped applications. The basis notion remains
exploratory, not a theorem that these definitions are novel/minimal world axioms.

## Delivered

- 5 native modules: numeric VM, IR, execution/checking, formation, sessions.
- Native `eml93`, `eml93-input`, data-only example and intervention driver.
- Python-only observation generator/independent cmath oracle; no Python learner.
- 27 new regression/adversarial/integration tests.
- [Design](eml93-design.md), [experiment](eml93-experiment.json),
  [demo](eml93-demo.sexp), [input demo](eml93-input-demo.sexp),
  [interventions](eml93-interventions.sexp), [evidence](eml93-evidence/).

## Demonstrated formation

| Step | Learned EML-based definition | Initial observations |
|---|---|---:|
|1 | B1(x)=E(x,1) |7 |
|2 | B2(x)=E(1,B1(E(1,x))) |5 |
|3 | B3(x,y)=E(B2(x),B1(y)) |8 |
|4 | B4(x,y)=B1(B3(x,y)) |8 |

Input relation names are opaque u1..u4 and are rename-tested. Expected program
bodies and reference function names are not supplied to native discovery.
The oracle interprets these as exp, log, subtraction and exp(x-y) on the tested
scopes. Bodies are not asserted equivalent to those functions on all inputs.

The same cost≤3 primitive-only search gives `no-fit` on subtraction; learned
B1/B2 enable a fitting B3. This is a representation/reuse intervention, not a
speed claim or evidence of an unrestricted advantage over all symbolic learners.
B4 executes a nested dependency chain; recorded query IDs are reverse encounter
order `(1 1 1 2 3 4)`, six actual basis calls,27 worker node visits.

## Branch and source updates

Both branch conventions learn four bases from the initial28 observations and
have seven active source/sign-cell bindings. Adding three negative-log rows:

- lower93: log's negative cell becomes active; total bindings seven→eight.
- principal93: negative cell remains unresolved; a cost≤3 re-search gives bounded
  `no-fit` (not global impossibility). Positive log and other sources remain usable.

At x=-1 the nested log tree yields approximately -i*pi or+i*pi respectively.
This behavior is explicit and is not hidden by answer normalization.
A counterexample to an active mapping removes that cell; an additional/corrected
source version can restore it. Definitions remain descriptions of their own
partial EML functions. Old explicit cores remain historical, not revoked.

## Final validation

- **213 offline Python tests passed in671.930s**, including27 new EML tests.
  Six inherited local-HTTP tests are excluded. The runner's socket guard is not
  an OS-wide network sandbox.
- Separate27-case EML run passed in55.933s.
- `./scripts/run.sh test`, `tests/store-tests.sh`, `tests/runtime-tests.sh` and
  `tests/graph-store-tests.sh` passed.
- 400 malformed external trees; bad variable roles, forward calls, forged
  expansions/snapshots, mixed source versions, omitted/wrong worker results,
  insufficient observations, counterexample withdrawal, retraction, budget,
  fresh-process restoration, two-process exclusion and failed-close retention.
- 206 primitive comparisons against independent Python cmath passed at0.002.
- The four-stage fixture and stdin data-only demo produce identical output.
- Final295 product-file hashes and16 artifact hashes verify;13 local links,
  Python AST, launcher shell syntax, new-product whitespace and git diff checks pass.

### Heldout formation experiment

12 sequential fresh native processes:3 observation-order/query seeds ×2 branch
conventions ×with/without additional negative-log experience. Each has64 heldout
queries, never fed back as training data.

| Condition, over three seeds | Completed | Unknown | Errors above0.002 |
|---|---:|---:|---:|
| principal93, initial observations |192 |0 |0 |
| principal93, negative-log observations added |168 |24 |0 |
| lower93, initial observations |192 |0 |0 |
| lower93, negative-log observations added |192 |0 |0 |
| **Total** |**744** |**24** |**0** |

Maximum complex absolute error:0.00013319425208990765. The24 unknowns are expected
unsupported negative-log applications under principal93, not wrong completed
answers. Unknown counts are checked explicitly in tests.

Recorded whole-process times were2.1773–2.2974s. An additional fresh default demo
measurement was1.8819s and20,176KiB child peak RSS, including startup/inherited
module loading and all four learning stages. One core's compact JSON encoding
was1,125 bytes. RSS is not model/heap size; JSON size is not parameter count.
These small synthetic cases establish local feasibility only, not general
scalability or superiority to LLMs. Speed is not the research success criterion.

## Bounds and unresolved work

- Bounded complex fixed-point arithmetic, scale10^-6; not exact math or a global
  error-bound proof. exp real parts outside[-6,6] and log-zero are undefined.
- Cost≤3 per candidate, raw expansion≤96 EML nodes,8 bases,6 sources,12 rows per
  source,1–2 inputs,32 events,200000 worker node visits.
- Five sign-cell predicates are supplied, not invented by the learner.
- Finite agreement is empirical; an alternative-law/counterexample test makes
  the ambiguity explicit. No noise model or universal identifiability guarantee.
- No free-text/web meaning extraction. Observations are synthetic outputs of
  author-selected reference functions. This is **not** an end-to-end web-to-
  knowledge claim, and no manually prepared semantic input is attributed to
  automatic extraction.
- Branch convention is supplied by a person/experiment, not inferred.
- No authentication, fsync guarantee or full CPU-work metering. Replay admission
  can repeat search. Snapshot restore does not repair old corruption.

## Preservation

0093 was copied before implementation; `version-boundary.json` records that
initial stage. The predecessor's499 recorded nonignored files, Git state and
compiler are rechecked in `preservation.json`. Only inherited `README.md`,
`VERSION` and `scripts/run.sh` change in the successor. `README-0092.md` preserves
the previous README. Basis90/Basis91/Attention92 code and Maru/compiler/runtime
remain unchanged; their APIs remain separate.

Compiler SHA256:
`2cbe804829509f5386933d832cbba2fef1bad367b7510a543b5d3f5818136fc9`.

## Reproduce

```sh
cd /research/dlm_v0.0093
./scripts/run.sh eml93
./scripts/run.sh eml93-input < experiments/eml93/input-example.sexp
./scripts/run.sh proof experiments/eml93/interventions.l
python3 -B -m unittest discover -s tests -p 'test_eml93.py' -v
python3 -B tests/run_offline.py
./scripts/run.sh test
bash tests/store-tests.sh
bash tests/runtime-tests.sh
bash tests/graph-store-tests.sh
python3 -B adapters/eml93_experiment.py --output /tmp/eml93.json
sha256sum -c docs/eml93-evidence/source.sha256
sha256sum -c docs/eml93-evidence/SHA256SUMS
```

The mathematical reference is arXiv2603.21852v2. This implementation uses a
separate discrete/native search, not the paper's Adam training, CUDA search,
complete calculator compiler or full proof/reproduction package.
