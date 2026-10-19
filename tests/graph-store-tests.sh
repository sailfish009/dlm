#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
export STORE="$WORK/store"
"$ROOT/scripts/graph.sh" > "$WORK/first.log"
grep -q '(active-claims 9)' "$WORK/first.log"
cp "$STORE/state.sexp" "$WORK/original.sexp"
printf '()\n' > "$WORK/no-actions.sexp"
"$ROOT/scripts/graph.sh" "$WORK/no-actions.sexp" > "$WORK/resume.log"
cmp "$WORK/original.sexp" "$STORE/state.sexp"
printf '((retract-observation ab))\n' > "$WORK/retract.sexp"
"$ROOT/scripts/graph.sh" "$WORK/retract.sexp" > "$WORK/retract.log"
grep -q '(active-claims 7)' "$WORK/retract.log"
printf '((observe (observation bad positive (atom edge (x)) (provenance fixture () observed))))\n' > "$WORK/invalid.sexp"
cp "$STORE/state.sexp" "$WORK/before-invalid.sexp"
if "$ROOT/scripts/graph.sh" "$WORK/invalid.sexp" > "$WORK/invalid.log" 2>&1; then
  echo 'FAIL invalid signature committed' >&2; exit 1
fi
cmp "$WORK/before-invalid.sexp" "$STORE/state.sexp"
# State remains verifiable after a rejected update.
"$ROOT/scripts/run.sh" graph-report < "$STORE/state.sexp" > /dev/null
# Corrupt only the derived snapshot tag; replay must reject it.
{ printf '(graph 76'; tail -c +10 "$STORE/state.sexp"; } > "$WORK/forged.sexp"
if "$ROOT/scripts/run.sh" graph-report < "$WORK/forged.sexp" > "$WORK/forged.log" 2>&1; then
  echo 'FAIL forged graph accepted' >&2; exit 1
fi
awk '{sub(/metrics 3/, "metrics 999"); print}' "$STORE/state.sexp" > "$WORK/forged-metrics.sexp"
if "$ROOT/scripts/run.sh" graph-report < "$WORK/forged-metrics.sexp" > "$WORK/metrics.log" 2>&1; then
  echo 'FAIL forged derived metrics accepted' >&2; exit 1
fi
printf '%s\n' '((observe (observation strings positive (atom label ("Hello world" "quote: \\\"")) (provenance fixture () observed))))' > "$WORK/strings.sexp"
STORE="$WORK/strings" "$ROOT/scripts/graph.sh" "$WORK/strings.sexp" > "$WORK/strings.log"
STORE="$WORK/strings" "$ROOT/scripts/graph.sh" "$WORK/no-actions.sexp" > "$WORK/strings-resume.log"
echo 'PASS graph process restart, retraction replay, string roundtrip and atomic rejection'
