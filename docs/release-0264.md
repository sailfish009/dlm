# DLM 0.0264 — capacity scaling of the native transformer (width / depth / untied phases)

**Corrections after review (2026-11-16).** An independent falsification pass found
six defects in the first version of this note; all six are confirmed and fixed
here:

- F1 the `±` column was the **1 SE** standard error while the text called it a
  2 SE interval (2× error). The table now prints both `se1` and `ci95` (=2 SE),
  and `tools/hybrid_stats.sh` prints `se1=`/`ci95=` so the two can never be
  confused again.
- F2 the table mixed a 15-seed block (base/w48/untied) with a 5-seed block
  (d3/w48d3) — comparisons across those rows were invalid. All five arms are
  now 15 seeds (51–65).
- F3 "19,939 parameters saturate the fixture" is **false as stated**: the same
  19,939-parameter model reaches 0.654 goal / 0.608 full under the `dplem` regime
  (DP value label + verified contracts, +14.5 pp, `docs/release-0262.md`). The
  capacity result below is conditioned on the single-step utility label.
- F4 three rows of the map ("top-k −6 pp", "residual gate −3 pp", "path
  condition −3 pp") are n=3 inconclusive results; they are relabelled
  **not detected at n=3**, not "negative".
- F5 the `focus` vacuity census (10,312 consultations, 0 removed) holds at d4/b4
  only; at d3/b6 the same binary removes 70 % of candidates
  (`out/hb_id_O0.txt`: focus_states=6609, focus_removed=4599). "Only a relational
  fixture can discriminate" was overstated.
- F6 this note's sibling `docs/release-0262.md` carried shell-heredoc residue
  (a pasted command block after the final paragraph) that the token-only gate did
  not catch. The residue is removed and `verify_value.sh`/`verify_scale.sh` now
  run `tools/doc_check.sh`, which rejects residue lines and requires the verdict
  token in prose.

## Design

Same data, epochs, search, protocol and seed base; only model size / parameter
tying differ.

```text
arm      structure                                        params
base     D=32, L=2                                         19,939
w48      D=48, L=2                                         35,987
d3       D=32, L=3                                         28,484
w48d3    D=48, L=3                                         51,844
untied   D=32, L=2, two passes with independent block
         parameters (Rocq tactic phases, PHASEUNTIE)       37,029
```

## Result — 15 seeds (base 51–65), d4/b4, single-step utility label

```text
arm      dfs     sd      dfs_full   params
base     0.4836  0.0920  0.4140     19,939
w48      0.5011  0.0984  0.4320     35,987
untied   0.4937  0.0684  0.4167     37,029
d3       0.4598  0.0861  0.3813     28,484
w48d3    0.5021  0.0658  0.4280     51,844
```

Paired by seed (`mean`, `se1`, `ci95` = 2 SE):

```text
contrast          mean      se1     ci95     verdict
w48   − base     +0.0175   0.0396  0.0792   inconclusive (2 SE)
d3    − base     −0.0238   0.0272  0.0544   inconclusive
w48d3 − base     +0.0185   0.0295  0.0590   inconclusive
untied− base     +0.0100   0.0275  0.0550   inconclusive
w48d3 − w48      +0.0010   0.0347  0.0694   inconclusive
```

### Verdict: SCALE-NOT-DEMONSTRATED (under the util label)

No capacity contrast reaches 2 SE. The earlier 5-seed width gain (+11.4 pp) was
seed variance: the largest single-seed jump is **seed 53** (0.294 → 0.730). The
5-seed w48d3 row (+7.8 pp) is likewise inside 2 SE once measured at 15 seeds
(+1.85 ± 5.90).

### Detection limit, correctly stated

Per-seed sd is 0.066–0.098 (not 0.20). With 15 seeds paired, 2 SE resolves
5.4–7.9 pp; **with 5 seeds the same contrasts resolve 3.6–11.2 pp depending on the
arm** — the paired variance, not the marginal sd, sets the limit. This is why the
5-seed tables in 0.0260–0.0263 can only support claims of large effects.

## What this does and does not establish

| claim | status |
|---|---|
| width/depth/untied phases give no **detectable** gain at 19.9k–51.8k params under the util label | established at 15 seeds (null, ±5.4–7.9 pp) |
| the model is saturated | **withdrawn**: `dplem` at 19,939 params reaches +14.5 pp |
| capacity × label interaction is null | **untested** (0.0264c measures w48 and b2max under `dplem`, 15 seeds) |
| the transformer has no internal headroom left | **withdrawn**: branching tokens + sequence value head (C1/C2) are untested here |

## Gates (`verify_scale.sh` → `V0264-SCALE-PASS`)

```text
SCALE-GRADCHECK  five capacity configurations incl. untied phase blocks
SCALE-OFF        PHASEUNTIE with tied passes is bit-identical to base
SCALE-PARAMS     base = 19,939
SCALE-CLAIM      verdict token required in this note
DOC              no shell residue in the release notes (tools/doc_check.sh)
AGG              table == per-seed recomputation; 10 mutations rejected
WHDR             width/depth/phase tags in the header; cross-capacity load refused
LLVM             O0/O2/O3 identical; ASan+UBSan clean (untied)
V0264-SCALE-PASS
```

## Next measurements, in discriminating order

1. **0.0264c — capacity under the `dplem` regime** (15 seeds): does width or
   multi-register help once the label carries composition? A null here is a much
   stronger statement than the util-label null.
2. Relational fixture (entity binding non-trivial): `focus`, `bind`, contract
   coverage and capacity are all degenerate or saturated on the unary world.
3. Branching tokens + sequence value head (C1/C2) — still untested internal axes.
## Appendix — corrected uncertainty labels for 0.0260–0.0263

The earlier notes printed `±` values that are **1 SE** standard errors while the
text called them 2 SE intervals. The tool now prints `se1` and `ci95`, and the
intervals below are the corrected 2 SE values (2 × the old `±`). Verdicts marked
"significant" were already judged against 2 SE, so the direction of every
conclusion is unchanged; only the printed widths were wrong.

```text
note   contrast                 mean      old ±(1SE)  corrected 2SE   verdict
0260   hybrid − pure goal      +15.08 pp    7.20        14.41        significant (n=3)
0260   lemma  − pure goal      +12.96 pp    1.15         2.29        significant
0261   learn  − rand goal       −0.64 pp    0.68         1.36        inconclusive (n=5)
0261   learn  − mined goal      +4.76 pp    1.44         2.88        significant
0261   mined  − pure goal      +16.19 pp    1.90         3.80        significant
0262   dp     − util goal       +2.22 pp    2.82         5.64        inconclusive (n=5)
0262   dplem  − dp   goal      +12.22 pp    1.05         2.10        significant
0262   dp     − dpshuf goal    +35.72 pp    4.82         9.64        significant
0263   b2max  − base goal       +1.27 pp    3.02         6.04        inconclusive (n=5)
0263   b3max  − base goal       −2.38 pp    5.97        11.94        inconclusive
0264   w48    − base goal       +1.75 pp    3.96         7.92        inconclusive (n=15)
0264   d3     − base goal       −2.38 pp    2.72         5.44        inconclusive (n=15)
0264   w48d3  − base goal       +1.85 pp    2.95         5.90        inconclusive (n=15)
```

Consequence for the map: "top-k attention −6 pp", "residual gate −3 pp" and
"path condition −3 pp" are **not detected at n=3**, not established negatives.
The only tight nulls are `d3` (n=15, ±5.44) and `b2shuf − b2` (n=5, ±5.44).
