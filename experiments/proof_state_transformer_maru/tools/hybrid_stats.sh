#!/usr/bin/env bash
# Hybrid-layer statistics: schema validation, per-seed table, paired contrasts.
#   table <seeds>                 recompute out/hybrid.txt from probes_h/*/cfg_4_4.txt
#   verify <table> <seeds>        validate every arm log and require table == recomputation
#   contrast <A> <B> <field>      paired-by-seed mean, SE, |mean|>2*SE verdict
# 0.0259 review F2: every printed number is a per-seed mean over DISTINCT seed rows;
# duplicate rows (multiple MEAN lines per seed) are rejected instead of averaged.
set -euo pipefail
cd "$(dirname "$0")/.."
ARMS=(pure topk pc soft focus cert lemma hybrid)
mode="${1:?mode}"

recompute () { # arm seeds -> one ARM row
  awk -v a="$1" -v n="$2" -v f="probes_h/$1/cfg_4_4.txt" '
  function num(line,key,  i,f2,kv){ split(line,f2," "); for(i=1;i<=NF;i++){ split(f2[i],kv,"="); if(kv[1]==key) return kv[2]+"" } return "" }
  BEGIN{ bad=0; ns=0; nd=0; nh=0 }
  /^SEED /{ s=$2+0;
    if (s in seen) { printf "HYBRID-AGG-FAIL %s duplicate SEED row %d\n", a, s; bad=1 }
    seen[s]=1; ns++; g[s]=num($0,"proof_model")+0; b[s]=num($0,"proof_beam")+0 }
  /^DFS seed=/{ s=num($0,"seed")+0;
    if (s in dseen) { printf "HYBRID-AGG-FAIL %s duplicate DFS row %d\n", a, s; bad=1 }
    dseen[s]=1; nd++;
    dg[s]=num($0,"goal")+0; df[s]=num($0,"full")+0; dn[s]=num($0,"nodes")+0; dc[s]=num($0,"cands")+0 }
  /^HYBRID seed=/{ s=num($0,"seed")+0;
    if (s in hseen) { printf "HYBRID-AGG-FAIL %s duplicate HYBRID row %d\n", a, s; bad=1 }
    hseen[s]=1; nh++;
    gv[s]=num($0,"gate_viol")+0; cd[s]=num($0,"pc_dropped")+0; cf[s]=num($0,"pc_fallback")+0;
    co[s]=num($0,"cert_ok")+0; cX[s]=num($0,"cert_fail")+0; cc[s]=num($0,"cert_checked")+0;
    lu[s]=num($0,"lemma_uses")+0; fs[s]=num($0,"focus_states")+0; fr[s]=num($0,"focus_removed")+0 }
  { if (length($0) > 0 && $0 !~ /^(SEED |DFS seed=|HYBRID seed=|LEMMA-MINE|MEAN |BOOT |BOUND-ASSERT|SEARCH-BUDGET|PARAMS |DATASET|CENSUS|EXPORT|TRAJ |REGRET)/){
      printf "HYBRID-AGG-FAIL %s stray line: %s\n", a, $0; bad=1 } }
  END{
    if (ns!=n || nd!=n || nh!=n){ printf "HYBRID-AGG-FAIL %s rows seedy=%d dfs=%d hybrid=%d need %d\n", a, ns, nd, nh, n; exit 1 }
    d=0; for (k in seen) d++; if (d!=n){ printf "HYBRID-AGG-FAIL %s distinct=%d need %d\n", a, d, n; exit 1 }
    sg=sb=sd=sf=sn=sc=0; sgv=scd=scf=sco=scX=scc=slu=sfs=sfr=0
    for (k in seen){
      if (!(k in dg) || !(k in gv)){ printf "HYBRID-AGG-FAIL %s seed %d missing metric row\n", a, k; bad=1; continue }
      if (g[k]<0 || g[k]>1 || b[k]<0 || b[k]>1 || dg[k]<0 || dg[k]>1 || df[k]<0 || df[k]>1){
        printf "HYBRID-AGG-FAIL %s seed %d out-of-range metric\n", a, k; bad=1 }
      if (co[k]+cX[k] > cc[k]) { printf "HYBRID-AGG-FAIL %s seed %d certificate counts inconsistent\n", a, k; bad=1 }
      sg+=g[k]; sb+=b[k]; sd+=dg[k]; sf+=df[k]; sn+=dn[k]; sc+=dc[k]
      sgv+=gv[k]; scd+=cd[k]; scf+=cf[k]; sco+=co[k]; scX+=cX[k]; scc+=cc[k]; slu+=lu[k]; sfs+=fs[k]; sfr+=fr[k]
    }
    if (bad) exit 1
    printf "ARM %-7s greedy=%.4f beam=%.4f dfs=%.4f dfs_full=%.4f nodes=%.0f cands=%.0f gate_viol=%.0f pc_dropped=%.0f pc_fallback=%.0f cert_ok=%.0f cert_fail=%.0f cert_checked=%.0f lemma_uses=%.0f focus_states=%.0f focus_removed=%.0f n=%d\n",
      a, sg/n, sb/n, sd/n, sf/n, sn/n, sc/n, sgv/n, scd/n, scf/n, sco/n, scX/n, scc/n, slu/n, sfs/n, sfr/n, n
  }' "probes_h/$1/cfg_4_4.txt" || exit 1
}

if [ "$mode" = table ]; then
  N="${2:?seeds}"
  for a in "${ARMS[@]}"; do recompute "$a" "$N"; done
  exit 0
fi

if [ "$mode" = verify ]; then
  T="${2:?table}"; N="${3:?seeds}"
  tmp=$(mktemp); trap 'rm -f "$tmp"' EXIT
  for a in "${ARMS[@]}"; do recompute "$a" "$N"; done > "$tmp"
  # compare every field of every arm row (integers allowed a 0.5 rounding)
  awk 'NR==FNR{ for(i=1;i<=NF;i++){ split($i,kv,"="); key[FNR"/"kv[1]]=kv[2] } na=FNR; next }
       { for(i=1;i<=NF;i++){ split($i,kv,"="); k=FNR"/"kv[1];
           if (!(k in key)) { printf "HYBRID-TABLE-FAIL missing field arm=%s field=%s\n", $2, kv[1]; bad=1; continue }
           x=key[k]+0; y=kv[2]+0; if (x-y>1e-6 || y-x>1e-6){ printf "HYBRID-TABLE-FAIL arm=%s field=%s table=%.6f recomputed=%.6f\n", $2, kv[1], y, x; bad=1 } } }
       END{ exit bad }' "$tmp" "$T" || exit 1
  echo "HYBRID-TABLE-PASS table equals per-seed recomputation (all arms, $N seeds)"
  exit 0
fi

if [ "$mode" = contrast ]; then
  A="${2:?A}"; B="${3:?B}"; F="${4:?field}"
  fa="probes_h/$A/cfg_4_4.txt"; fb="probes_h/$B/cfg_4_4.txt"
  for f in "$fa" "$fb"; do [ -f "$f" ] || { echo "HYBRID-CONTRAST-FAIL missing $f"; exit 1; }; done
  pa=$(mktemp); pb=$(mktemp)
  for pair in "$fa:$pa" "$fb:$pb"; do
    file="${pair%%:*}"; out="${pair##*:}"
    awk -v f="$F" '
      function num(line,key,  i,f2,kv){ split(line,f2," "); for(i=1;i<=NF;i++){ split(f2[i],kv,"="); if(kv[1]==key) return kv[2]+"" } return "" }
      /^SEED /{ v=num($0,f); if (v!="") print $2, v }
      /^DFS seed=|^HYBRID seed=/{ v=num($0,f); if (v!="") print num($0,"seed"), v }
    ' "$file" | sort -u > "$out"
  done
  join "$pa" "$pb" | awk -v a="$A" -v b="$B" -v f="$F" '
    { n++; d=$2-$3; s+=d; ss+=d*d }
    END{ if (n<2){ printf "HYBRID-CONTRAST %s-%s %s INSUFFICIENT n=%d\n", a, b, f, n; exit 1 }
      m=s/n; v=(ss-n*m*m)/(n-1); se=sqrt(v/n);
      verdict=(se>0 && (m>2*se || m<-2*se)) ? "SIGNIFICANT(2SE)" : "INCONCLUSIVE(2SE)";
      printf "HYBRID-CONTRAST %s-%s %s mean=%+.4f se=%.4f n=%d %s\n", a, b, f, m, se, n, verdict }'
  rm -f "$pa" "$pb"
  exit 0
fi

echo "unknown mode $mode"; exit 2