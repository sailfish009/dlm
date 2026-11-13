#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
OUT="${OUT:-out.txt}"
./run.sh > /tmp/v0234_verify_recompute.out
cmp -s "$OUT" /tmp/v0234_verify_recompute.out || { echo "output is not a fresh re-execution"; exit 1; }
grep -q '^TEXT 15 EXTRACTED 3$' "$OUT" || { echo 'extraction count changed'; exit 1; }
grep -q '^POS-TP 22/22 NEG-TP 0/1$' "$OUT" || { echo 'metric controls failed'; exit 1; }
grep -q '^GOLD-EXPRESSIBLE 6/22 (isa-only parser cap)$' "$OUT" || { echo 'recall cap missing'; exit 1; }
grep -q '^TP 0 FP 3 FN 22$' "$OUT" || { echo 'metrics changed'; exit 1; }
grep -q '^PRECISION 0/3 RECALL 0/22$' "$OUT" || { echo 'precision/recall changed'; exit 1; }
grep -q '^GATE FACTS 3 RULES 0 PROOF fail$' "$OUT" || { echo 'gate changed'; exit 1; }
grep -q '^GATE-POS proof GATE-NEG fail$' "$OUT" || { echo 'gate controls failed'; exit 1; }
grep -q '^EMPTY-TEST nl-unknown (want nl-unknown)$' "$OUT" || { echo 'empty-object bug returned'; exit 1; }
grep -q '^GOLD-FIELDS-IN-INPUT false$' "$OUT" || { echo 'leakage claim missing'; exit 1; }
# Leakage is checked by the computed GOLD-FIELDS-IN-INPUT output.
echo 'POS-TP 22/22 NEG-TP 0/1'
echo 'GOLD-EXPRESSIBLE 6/22'
echo 'TEXT 15 EXTRACTED 3'
echo 'TP 0 FP 3 FN 22'
echo 'PRECISION 0/3 RECALL 0/22'
echo 'GATE PROOF fail'
echo 'GATE-POS proof GATE-NEG fail'
echo 'EMPTY-TEST nl-unknown'
echo 'GOLD-FIELDS-IN-INPUT false'
grep -q '^ORACLE TP 0 FP 3 FN 22$' oracle.out || { echo 'oracle mismatch'; exit 1; }
grep -q '^PERFECT-TP 22/22 WRONG-TP 0 EMPTY-TP 0$' adversarial.out || { echo 'adversarial controls failed'; exit 1; }
grep -q '^SOURCE-META 6 CHECKSUM-TARGET full-extract-utf8 UNVERIFIED$' adversarial.out || { echo 'source metadata/checksum target missing'; exit 1; }
echo 'ORACLE TP 0 FP 3 FN 22'
echo 'PERFECT-TP 22/22 WRONG-TP 0 EMPTY-TP 0'
echo 'SOURCE-META 6 CHECKSUM-TARGET full-extract-utf8 UNVERIFIED'
grep -q '^SYNTH-FACT nl-fact zorblax flimflam$' probe.out || { echo 'text channel broken'; exit 1; }
grep -q '^SYNTH-RULE nl-rule zorblaxe flimflam$' probe.out || { echo 'rule channel broken'; exit 1; }
grep -q '^NEGATION nl-unknown a dataset is not a collection () (known limitation)$' probe.out || { echo 'negation probe changed'; exit 1; }
grep -q '^DETERMINISTIC yes$' repeat.out || { echo 'nondeterministic'; exit 1; }
echo 'SYNTH-FACT/RULE ok'
echo 'NEGATION nl-unknown'
echo 'DETERMINISTIC yes'
echo 'RUN-REEXECUTED'
echo 'V0234-PHASE5-COMPUTED-LEAKAGE-PASS'
