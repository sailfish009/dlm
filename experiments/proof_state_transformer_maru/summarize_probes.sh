#!/usr/bin/env bash
# Summarise a probe prefix: average the per-seed MEAN/REGRET lines per config.
set -euo pipefail
cd "$(dirname "$0")"
P="${1:?prefix e.g. probes/bal}"
echo "# prefix=$P"
for cfg in 2_4 3_4 4_4 2_6 4_6; do
  f="$P/cfg_$cfg.txt"
  [ -f "$f" ] || continue
  awk -v tag="$cfg" '
    /^MEAN /{n++; for(i=1;i<=NF;i++){split($i,kv,"="); m[kv[1]]+=kv[2]}}
    END{ if(n) printf "ladder %s goal=%.4f full=%.4f beam=%.4f beam_full=%.4f support_beam=%.4f\n",
         tag, m["proof_model"]/n, m["full_model"]/n, m["proof_beam"]/n, m["full_beam"]/n, m["beam_support"]/n }
  ' "$f"
  awk -v tag="$cfg" '
    /^REGRET-MEAN /{n++; for(i=1;i<=NF;i++){split($i,kv,"="); r[kv[1]]+=kv[2]}}
    END{ if(n) printf "regret %s model=%.4f model_opt=%.4f support=%.4f ug=%.4f\n",
         tag, r["model_regret"]/n, r["model_opt"]/n, r["support_regret"]/n, r["ug_regret"]/n }
  ' "$f"
done
