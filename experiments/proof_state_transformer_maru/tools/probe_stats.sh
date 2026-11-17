#!/usr/bin/env bash
# Probe-log validator and paired statistics (R250-4/R250-5).
#  check <prefix> <seeds>          validate per-seed schema, print mean +- SE
#  contrast <prefixA> <prefixB> <cfg> <field>
#     paired-by-seed mean, SE and |mean| > 2*SE verdict
set -euo pipefail
cd "$(dirname "$0")/.."
mode="${1:?mode}"

if [ "$mode" = check ]; then
  P="${2:?prefix}"; N="${3:?seeds}"
  [ -d "$P" ] || { echo "PROBECHECK-FAIL missing $P"; exit 1; }
  awk -v n="$N" -v dir="$P" '
  function num(line, key,   i, f, kv, v){ split(line, f, " "); for (i=1;i<=length(f);i++){ split(f[i],kv,"="); if(kv[1]==key) return kv[2]+0 } return "" }
  BEGIN{
    bad = 0; cfgs[1]="2_4"; cfgs[2]="3_4"; cfgs[3]="4_4"; cfgs[4]="2_6"; cfgs[5]="4_6"
    for (c = 1; c <= 5; c++){
      cfg = cfgs[c]; f = dir "/cfg_" cfg ".txt"; ns = 0; nm = 0; delete seen
      while ((getline line < f) > 0){
        if (line ~ /^SEED /){ ns++; s = substr(line, 6)+0; seen[s]++; 
          for (k in FIELDS) {}
          v1 = num(line,"proof_model"); v2 = num(line,"full_model"); v3 = num(line,"proof_beam"); v4 = num(line,"full_beam")
          if (v1 == "" || v1 < 0 || v1 > 1 || v2 < 0 || v2 > 1 || v3 < 0 || v3 > 1 || v4 < 0 || v4 > 1){
            printf "PROBECHECK-FAIL %s bad field in SEED line: %s\n", cfg, line; bad = 1 }
        } else if (line ~ /^MEAN /){ nm++ }
        else if (line ~ /^REGRET/) { }
        else if (line ~ /^(BOOT|BOUND-ASSERT|SEARCH-BUDGET|PARAMS|DATASET|CENSUS|EXPORT|TRAJ)/) { }
        else if (line !~ /^#/ && length(line) > 0){ printf "PROBECHECK-FAIL %s stray line: %s\n", cfg, line; bad = 1 }
      }
      close(f)
      if (ns != n){ printf "PROBECHECK-FAIL %s seed rows=%d need %d\n", cfg, ns, n; bad = 1 }
      if (nm != n){ printf "PROBECHECK-FAIL %s mean rows=%d need %d\n", cfg, nm, n; bad = 1 }
      d = 0; for (s in seen) d++
      if (d != n){ printf "PROBECHECK-FAIL %s distinct seeds=%d need %d\n", cfg, d, n; bad = 1 }
    }
    if (bad) exit 1
    print "PROBECHECK-PASS " dir " seeds=" n
  }' || exit 1
  # mean +- SE per config, computed from the same files
  for cfg in 2_4 3_4 4_4 2_6 4_6; do
    awk -v cfg="$cfg" '
    function num(line, key,   i, f, kv){ split(line, f, " "); for (i=1;i<=NF;i++){ split(f[i],kv,"="); if(kv[1]==key) return kv[2]+0 } return -1 }
    /^SEED /{ n++; g[n]=num($0,"proof_model"); f[n]=num($0,"full_model"); b[n]=num($0,"proof_beam") }
    END{ if(!n){ printf "PROBESTAT %s INSUFFICIENT\n", cfg; exit }
      sg=sf=sb=0; for(i=1;i<=n;i++){ sg+=g[i]; sf+=f[i]; sb+=b[i] }
      mg=sg/n; mf=sf/n; mb=sb/n
      vg=vf=vb=0; for(i=1;i<=n;i++){ vg+=(g[i]-mg)^2; vf+=(f[i]-mf)^2; vb+=(b[i]-mb)^2 }
      eg=sqrt(vg/(n-1)/n); ef=sqrt(vf/(n-1)/n); eb=sqrt(vb/(n-1)/n)
      printf "PROBESTAT %s n=%d goal=%.4f+-%.4f full=%.4f+-%.4f beam=%.4f+-%.4f\n", cfg, n, mg, eg, mf, ef, mb, eb }
    ' "probes/$(basename "$P")/cfg_$cfg.txt" 2>/dev/null || true
  done
  exit 0
fi

if [ "$mode" = contrast ]; then
  A="${2:?prefixA}"; B="${3:?prefixB}"; CFG="${4:?cfg}"; FIELD="${5:?field}"
  fa="probes/$A/cfg_$CFG.txt"; fb="probes/$B/cfg_$CFG.txt"
  [ -f "$fa" ] && [ -f "$fb" ] || { echo "PROBECONTRAST-FAIL missing $fa or $fb"; exit 1; }
  pa=$(mktemp); pb=$(mktemp)
  grep '^SEED ' "$fa" | awk -v f="$FIELD" '{v=""; for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]==f) v=kv[2]} if(v!="") print $2, v}' | sort > "$pa"
  grep '^SEED ' "$fb" | awk -v f="$FIELD" '{v=""; for(i=1;i<=NF;i++){split($i,kv,"="); if(kv[1]==f) v=kv[2]} if(v!="") print $2, v}' | sort > "$pb"
  join "$pa" "$pb" | awk -v tag="$A-$B@$CFG:$FIELD" '
    { n++; d = $2 - $3; s += d; ss += d*d; if (n==1 || d < lo) lo = d; if (n==1 || d > hi) hi = d }
    END{
      if (n < 2){ printf "PROBECONTRAST %s n=%d INSUFFICIENT\n", tag, n; exit 1 }
      m = s/n; v = (ss - n*m*m)/(n-1); se = sqrt(v/n)
      verdict = (se > 0 && (m > 2*se || m < -2*se)) ? "SIGNIFICANT(2SE)" : "INCONCLUSIVE(2SE)"
      printf "PROBECONTRAST %s mean=%+.4f se=%.4f n=%d range=[%+.4f,%+.4f] %s\n", tag, m, se, n, lo, hi, verdict
    }'
  rm -f "$pa" "$pb"
  exit 0
fi

echo "usage: probe_stats.sh check <prefix> <seeds> | contrast <A> <B> <cfg> <field>" >&2
exit 2
