# Release 0.0160 — typed ports, provenance and self-hosted typed curriculum (candidate)

- Date: 2026-11-08
- Predecessor: 0.0159. Candidate, not promoted.
- Scope: add typed fragment ports and provenance, reject invalid composition before
  proving, and verify the typed experiment through a self-host compiler rebuild.
- Analysis: `/research/analysis-typed-selfhost-0160.md`.

## Typed layer

New `src/dlm/typed.l`:

```text
pt-fragment ID HEAD BODY PORTS PROVENANCE
pt-template ID HEAD BODY PORTS PROVENANCE
pt-combine ID LEFT RIGHT
pt-program ID TEMPLATES
pt-run MODULE
```

Port roles:

```text
in / out / link
```

Verification:

- fragment provenance non-empty
- ports non-empty and variables range over body
- same-variable same-role conflict rejected
- combined body must cover head variables
- provenance is merged across fragments/templates/programs

## Experiment

`experiments/typed_repl/start.l` via `./scripts/typed.sh`:

- 5 typed fragments
- 4 templates
- 2 programs (`p-rec`, `p-comp`)
- 4 fixed tasks

Results:

```text
TYPED fragments ok=5
BADPORT rejected107
tasks solved: 4/4
active: p-rec, p-comp
p-comp provenance: (claim:left claim:q)
p-rec  provenance: (claim:seed claim:left claim:right)
```

`p-rec` is reused for ancestor/reaches/inside; `p-comp` handles path.

## Self-host verification

```text
compiler.sh reproduce
  → 20261109T074007Z-16161
compiler.sh verify 20261109T074007Z-16161
  → Verified
```

The verify gate now runs the typed experiment and asserts:

- `done-typed`
- `tasks 4 solved 4`
- typed provenance output

Self-host results:

```text
native normal   9 checks / 0 FAIL
native safety-2 9 checks / 0 FAIL
next/third LLVM and stripped equality: PASS
```

Only benign clang `-Woverride-module` warnings remain.

## Still not

- Fixed tasks and alignments; no new rule invention.
- Provenance is an ID list, not a full claim/span/quote chain in this layer.
- Port semantics are minimal in/out/link, not full type/qualifier matching.
- No general assembly search or automatic web extraction.
- The experiment is a sequential typed curriculum, not pure label-free
  self-supervision.
