# Release 0.0242 — Native Integral-Credit Composition (Maru + LLVM IR)

- Date: 2026-11-14
- Predecessor: 0.0241 (0240 is a separate agent's worktree; untouched)
- Type: candidate research release
- Runtime: `20261113T120607Z-976` (reused; `src/` unchanged)

## What changed

- Added `experiments/native_integral/`: a **native** (C/LLVM IR + Maru oracle,
  no Python/PyTorch) implementation of the deductive-learning vision's core
  learning principle — accumulated axiom base + combinatorial composition +
  integral credit.
- VERSION 0.0242; lab sources in both manifests; generated artifacts gitignored.

## The hypothesis (from the 0241 discussion)

0241 found integral ≈ single for **exact** single-rule utility: exact credit is
a potential difference, so greedy ascent is already optimal and accumulation
adds nothing. The user's vision predicts that in the **combinatorial** regime —
where credit is **partial and noisy** (proof participation, not exact marginal
utility) — accumulation (the integral) should denoise and beat greedy. 0242
tests this natively.

## Native architecture

- Axiom base: 32 Horn rules (8 topics × 3-chain + 8 decoys), 40 atoms, bitset;
  rules shuffled so index order is uninformative.
- Composition: budget-limited (6 firings) forward closure, rule order guided by
  learned credit weights; goals require 3-rule chains (combinatorial).
- Credit: **partial participation** — a rule is credited iff it fired on the
  backward path to a reached goal, computed under a tight budget (noisy).
- Learning: accumulate credit over 400 train episodes; modes integral (running
  sum) / single (one episode) / random / uniform; evaluate on 400 held-out test.
- Exact oracle: Maru `p-close` on the same ground theory (parity gate).
- Integer Q16, deterministic xorshift PRNG, LLVM IR emitted, O0/O2/O3 identity.

## Result (3 seeds × 400 test episodes; goals reached within budget)

```text
seed  integral  single  random  uniform   integral−single
777   36.60%    25.62%  18.94%  20.05%    +10.98pp
778   37.88%    19.90%  18.54%  19.90%    +17.98pp
779   38.06%    20.81%  18.45%  20.81%    +17.25pp
```

**Integral beats single by +11–18 percentage points on every seed**, and beats
random/uniform by ~17–19pp. The learned weights recover the latent hot/cold
structure. With noisy partial participation credit, accumulation denoises and
guides combinatorial search substantially better than a single episode.

## Verdict — the refined thesis, validated natively

The integral earns its keep exactly where predicted: **when the credit signal
is partial/noisy** (the realistic regime for combinatorial composition),
accumulation over many episodes beats greedy/single. This contrasts 0241's
exact-credit null and confirms the division:

- exact, integrable credit → greedy ascent suffices (0241);
- partial, noisy credit → integral accumulation wins (0242).

The power of the deductive direction is the **kernel-certified credit signal**;
the integral is the right learning calculus when that signal is partial — which
is precisely the combinatorial axiom-matching setting of the user's vision.

## Verification

```bash
cd /research/dlm_v0.0242/experiments/native_integral
./run_all.sh        # LLVM matrix + 3 seeds + Maru parity + verify (V0242-NATIVE-INTEGRAL-PASS)
```

```bash
cd /research/dlm_v0.0242
env PATH=/opt/miniconda3/envs/py314/bin:$PATH ./scripts/verify_release.sh
```

Gates: C==Maru ground-closure parity (derived=6 reached=2); LLVM O0/O2/O3
byte-identical + IR/opt/llc; discriminative integral>single+3pp on all seeds;
determinism byte-identical. All computed (bash+awk), no decorative PASS lines.

## Limits

- Propositional ground Horn, 40 atoms / 32 rules (bitset ≤64). Synthetic
  hot/cold topics; the integral learns this stable latent core.
- Credit is binary backward-path participation, not full deep_credit
  (depth-weighted / failure-frontier blame) — richer credit is future work.
- The matcher is credit-weighted rule ordering, **not yet a learned transformer
  over a large axiom base**. 0242 validates the integral-learning principle
  natively; the transformer matcher at scale (the full vision) is the next step.
- 3 seeds; +3pp margin is a pre-registered heuristic, not a significance test.
- A `fired[]` buffer-overflow UB (NATOMS=40 vs NRULES=32) was caught by the
  O0/O2/O3 identity gate (O2 hung) and fixed — the gate earned its keep.