#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
# Re-run the lab and all gates.
./run_all.sh > /tmp/final_lab.out
# Source manifest must include the experiment and exclude generated *.out.
cd ../..
if ! grep -q 'experiments/real_web_axiom_decomposition/src/extract.l' docs/release.sources.sha256; then echo 'experiment missing from manifest'; exit 1; fi
if grep -q 'experiments/real_web_axiom_decomposition/.*\.out' docs/release.sources.sha256; then echo 'generated output in manifest'; exit 1; fi
sha256sum -c docs/release.sources.sha256 >/dev/null
sha256sum -c docs/release.tests.sha256 >/dev/null
echo 'LAB-REPRODUCED'
echo 'MANIFEST-EXPERIMENT-INCLUDED'
echo 'MANIFEST-NO-GENERATED-OUT'
echo 'MANIFEST-SHA256-OK'
echo 'V0234-FINAL-REVIEW-PASS'
