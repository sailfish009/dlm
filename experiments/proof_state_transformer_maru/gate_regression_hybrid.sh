#!/usr/bin/env bash
# Mutation regression for the 0.0260 aggregation gate (review 0259 F2 pattern).
# Every mutation MUST be rejected by tools/hybrid_stats.sh verify; the unmutated
# table MUST be accepted. An accepted mutation is a gate failure.
set -euo pipefail
cd "$(dirname "$0")"
T="${1:?table}"; P="${2:?probe dir}"; N="${3:?seeds}"
PROBES_DIR="$(basename "$P")"
export PROBES="$PROBES_DIR"
export ARMS="${ARMS:-pure topk pc soft focus cert lemma hybrid}"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/tools" "$tmp/pristine"
cp -a "$P" "$tmp/$PROBES_DIR" 2>/dev/null || cp -a "$P" "$tmp/$PROBES_DIR"
mkdir -p "$tmp/pristine"; cp -a "$tmp/$PROBES_DIR" "$tmp/pristine/$PROBES_DIR"
cp tools/hybrid_stats.sh "$tmp/tools/hybrid_stats.sh"
cp "$T" "$tmp/hybrid.txt"
cases=0; fail=0
run_verify () { ( cd "$tmp" && PROBES="$PROBES_DIR" ARMS="$ARMS" bash tools/hybrid_stats.sh verify hybrid.txt "$N" ) ; }
mutate () { ( cd "$tmp" && eval "$1" ) ; }

# baseline must pass
if ! run_verify > "$tmp/baseline.log" 2>&1; then
  echo "GATE-REGRESSION-FAIL baseline table/table-recomputation mismatch"; cat "$tmp/baseline.log"; exit 1
fi

expect_fail () { # name command (run with cwd=$tmp)
  local name="$1"; shift
  rm -rf "$tmp/$PROBES_DIR"; cp -a "$tmp/pristine/$PROBES_DIR" "$tmp/$PROBES_DIR"
  cp "$T" "$tmp/hybrid.txt"
  mutate "$1"
  cases=$((cases+1))
  if run_verify > "$tmp/$name.log" 2>&1; then
    echo "GATE-REGRESSION-FAIL accepted mutation: $name"; cat "$tmp/$name.log"; fail=$((fail+1))
  fi
}

A1=$(echo $ARMS | awk '{print $1}'); A2=$(echo $ARMS | awk '{print $2}')
expect_fail missing-seed       "grep -v -m1 '^SEED ' \"\$PROBES_DIR\"/$A2/cfg_4_4.txt > x && mv x \"\$PROBES_DIR\"/$A2/cfg_4_4.txt"
expect_fail duplicate-seed-row "grep -m1 '^SEED ' \"\$PROBES_DIR\"/$A2/cfg_4_4.txt >> \"\$PROBES_DIR\"/$A2/cfg_4_4.txt"
expect_fail duplicate-dfs-row  "grep -m1 '^DFS ' \"\$PROBES_DIR\"/$A2/cfg_4_4.txt >> \"\$PROBES_DIR\"/$A2/cfg_4_4.txt"
expect_fail nan-metric         "sed -i '0,/proof_model=/s|proof_model=[0-9.]*|proof_model=nan|' \"\$PROBES_DIR\"/$A2/cfg_4_4.txt"
expect_fail out-of-range       "sed -i '0,/proof_model=/s|proof_model=[0-9.]*|proof_model=1.7|' \"\$PROBES_DIR\"/$A1/cfg_4_4.txt"
expect_fail stray-line         "echo 'SEED 99 variant=x proof_model=0.5' >> \"\$PROBES_DIR\"/$A1/cfg_4_4.txt"
expect_fail empty-log          ": > \"\$PROBES_DIR\"/$A2/cfg_4_4.txt"
expect_fail degraded-table     "sed -i 's|^ARM $A1 .*|ARM $A1 greedy=0.9000 beam=0.9000 dfs=0.9000 dfs_full=0.9000 nodes=3437 cands=24625 gate_viol=0 pc_dropped=0 pc_fallback=0 cert_ok=0 cert_fail=0 cert_checked=0 lemma_uses=0 focus_states=0 focus_removed=0 pair_uses=0 pair_viol=0 n=5|' hybrid.txt"
expect_fail duplicated-row     'head -1 hybrid.txt >> hybrid.txt'
expect_fail dropped-arm        "grep -v '^ARM $A2 ' hybrid.txt > x && mv x hybrid.txt"

if [ "$fail" -ne 0 ]; then echo "GATE-REGRESSION-FAIL $fail accepted mutation(s)"; exit 1; fi
echo "GATE-REGRESSION-PASS $cases mutations rejected, baseline accepted"