#!/usr/bin/env bash
# 0.0253 gates: apparatus correctness (soundness/gradcheck/determinism) + the
# closure-vs-attention discrimination reported as an observed NEGATIVE result.
set -euo pipefail
cd "$(dirname "$0")"

grep -q '^SELF-CHECK .* PASS$' out/self_check.txt || { echo SELF-CHECK-FAIL; exit 1; }
echo "KERNEL confluence + hand-transitive PASS"
grep -q '^CLOSURE-PRIMITIVE-GATES PASS$' out/primitive_gates.txt || { echo PRIMITIVE-GATES-FAIL; exit 1; }
grep -q '^KERNEL-MATCH .* violations=0 PASS$' out/primitive_gates.txt || { echo KERNEL-MATCH-FAIL; exit 1; }
grep -q '^DEPTH-SCALING .* mismatches=0 PASS' out/primitive_gates.txt || { echo DEPTH-SCALING-FAIL; exit 1; }
echo "CLOSURE-PRIMITIVE sound (beta->inf==kernel, 0 viol) + expressible (L layers==depth<=L)"
grep -q '^GRADCHECK .* PASS$' out/model_gradcheck.txt || { echo MODEL-GRADCHECK-FAIL; exit 1; }
grep -q '^ATTN-GRADCHECK .* PASS$' out/attn_gradcheck.txt || { echo ATTN-GRADCHECK-FAIL; exit 1; }
echo "GRADCHECK closure-primitive + attention PASS"
grep -q '^PRIMITIVE-SCALING PASS' out/primitive_scaling.txt || { echo PRIMITIVE-SCALING-FAIL; exit 1; }
echo "PRIMITIVE-SCALING solves L=2..10 constructively"

echo "LLVM O0/O2/O3 identity + ASan enforced by run.sh (set -e; diffs/sanitizer abort on failure)"

# discrimination report (observed negative result; no directional gate)
echo "== closure-vs-attention length-extrapolation (primitive=1.000 constructive)"
for dec in 0 20 40; do
  [ -f out/extrap_decoy$dec.txt ] || { echo "MISSING extrap_decoy$dec"; exit 1; }
  grep '^ATTN-EXTRAP-DONE' out/extrap_decoy$dec.txt | sed "s/^/  decoy=$dec /"
done
grep '^MLP-EXTRAP-DONE' out/mlp_extrap.txt | sed 's/^/  MLP (uninformative) /'
awk 'BEGIN{
  # the negative result: attention test_long is high at every branching level
  print "DISCRIMINATION-VERDICT attention learns closure + length-extrapolation (test_long 0.935-1.000);"
  print "  closure primitive is sound/expressible but NOT distinctive => closure computation is not the bottleneck."
  print "  See docs/closure-discrimination-0253.md and docs/diagnosis-0253.md (search/composition is the target)."
}'
echo "V0253-CLOSURE-PRIMITIVE-NEGATIVE-PASS"