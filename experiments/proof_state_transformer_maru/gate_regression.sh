#!/usr/bin/env bash
# Regression suite for the 0.0244 F2/F3 gate defects: every mutation below must
# be rejected by tools/gate_check, and the unmodified log must pass.
set -euo pipefail
cd "$(dirname "$0")"
LOG="${1:-out/hard_base.txt}"
SEEDS="${2:-5}"
D=out/gate_probes
rm -rf "$D"; mkdir -p "$D"

./bin/gate_check "$LOG" hard "$SEEDS" 11 > /dev/null || { echo "GATE-REGRESSION-FAIL baseline does not pass"; exit 1; }

probe () { # name, must-fail(0) or pass(1), mutator
  local name="$1" want="$2"; shift 2
  "$@" > "$D/$name.txt"
  set +e
  ./bin/gate_check "$D/$name.txt" hard "$SEEDS" 11 > "$D/$name.out" 2>&1
  local rc=$?
  set -e
  if [ "$want" = fail ] && [ $rc -eq 0 ]; then echo "GATE-REGRESSION-FAIL $name was accepted"; exit 1; fi
  if [ "$want" = pass ] && [ $rc -ne 0 ]; then echo "GATE-REGRESSION-FAIL $name was rejected"; cat "$D/$name.out"; exit 1; fi
  printf '  %-22s want=%s got=exit%d\n' "$name" "$want" "$rc"
}

probe empty          fail bash -c ': > /dev/null; cat /dev/null'
probe no_seed_rows   fail grep -v '^SEED ' "$LOG"
probe one_seed_only  fail grep -v '^SEED 1[2-5] ' "$LOG"
probe model_below_prior fail sed -E 's/proof_model=([0-9.]+)/proof_model=0.0500/g' "$LOG"
probe support_stronger_is_data pass sed -E 's/proof_support=([0-9.]+)/proof_support=0.9000/g' "$LOG"
probe missing_shuffled    fail sed -E 's/ proof_shuffled=[0-9.]+//' "$LOG"
probe shuffled_099        fail sed -E 's/proof_shuffled=([0-9.]+)/proof_shuffled=0.9900/g' "$LOG"
probe mean_tampered       fail sed -E 's/(^MEAN .* proof_model=)[0-9.]+/\10.9900/' "$LOG"
probe beam_prior_high     fail sed -E 's/beam_prior=([0-9.]+)/beam_prior=0.9000/g' "$LOG"
probe duplicate_seed      fail sed -E 's/^SEED 12 /SEED 11 /' "$LOG"
probe perm_not_invariant  fail sed -E 's/perm_maxdiff=[0-9.e+-]+/perm_maxdiff=1.000e-03/g' "$LOG"
# R245-1 probes: ratio > 1, schema/aggregation holes, non-finite, metadata,
# suffix garbage and duplicate fields must all be rejected.
probe proof_rate_101     fail sed -E 's/proof_model=([0-9.]+)/proof_model=1.0100/g' "$LOG"
probe mean_beam_full_tamper fail sed -E 's/(^MEAN .*beam_full_support=)[0-9.]+/\10.9900/' "$LOG"
probe seed_budget_zero   fail awk '{ if ($1=="SEED"){ for(i=1;i<=NF;i++) if ($i ~ /^search_states=/) $i="search_states=0" } print }' "$LOG"
probe mean_budget_inf    fail sed -E 's/(^MEAN .*search_states=)[0-9]+/\1inf/' "$LOG"
probe mean_seeds_mismatch fail sed -E 's/(^MEAN .*seeds=)[0-9]+/\1999/' "$LOG"
probe token_garbage      fail sed -E 's/(proof_model=[0-9.]+)/\1garbage/' "$LOG"
probe duplicate_field    fail sed -E 's/(^SEED 11 .*proof_model=[0-9.]+ )/\1proof_model=0.5000 /' "$LOG"
echo "GATE-REGRESSION-PASS $D (17 mutations rejected, baseline accepted)"
