#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for c in baseline baseline_seed62 baseline_seed63 d16_f32_l3 d32_h2_l6 d16_h2_l3 d32_h4_l6 d32_adamw_cos d32_dropout d32_f64_l6_noprior d32_f64_l3; do
  python3 variant_lab.py "configs/$c.json"
done
clang -O3 -I ../dt_full_port_no_mlir prior_only.c -o prior_only
./prior_only > prior_only.out
python3 verify_lab.py
