#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOL="$ROOT/src/maru/tools-for-build/build-compiler-image.sh"
MODE="${1:-}"; shift || true
case "$MODE" in
 rebuild|reproduce)
  ID="$(date -u +%Y%m%dT%H%M%SZ)-$RANDOM"
  DIR="$ROOT/runtime/releases/$ID"; mkdir -p "$DIR"
  PARENT="$(sha256sum "$ROOT/maru-compiler" | cut -d' ' -f1)"
  (cd "$ROOT"; find src -type f -print0 | sort -z | xargs -0 sha256sum) > "$DIR/sources.sha256"
  if [[ "$MODE" == rebuild ]]; then
   "$TOOL" "$ROOT/bootstrap/maru-seed" "$DIR/maru" > "$DIR/build.log" 2>&1
  else
   "$TOOL" --self "$ROOT/maru-compiler" "$DIR/maru" > "$DIR/build.log" 2>&1
  fi
  printf 'mode=%s\nparent_sha256=%s\n' "$MODE" "$PARENT" > "$DIR/record"
  (cd "$DIR"; sha256sum maru maru.ll sources.sha256 record) > "$DIR/artifacts.sha256"
  echo "$ID" ;;
 verify)
  ID="${1:?release ID required}"
  [[ "$ID" =~ ^[A-Za-z0-9_-]+$ ]] || exit 2
  DIR="$ROOT/runtime/releases/$ID"
  (cd "$DIR"; sha256sum -c artifacts.sha256) > "$DIR/verify.log" 2>&1
  MARU="$DIR/maru" "$ROOT/scripts/run.sh" test >> "$DIR/verify.log" 2>&1
  MLIR_LOG="$DIR/mlir.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/mlir.sh" </dev/null > "$MLIR_LOG" 2>&1; then
    cat "$MLIR_LOG" >> "$DIR/verify.log"
    echo 'MLIR experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$MLIR_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-mlir' "$MLIR_LOG" || ! grep -q 'tasks 4 solved 4' "$MLIR_LOG"; then
    echo 'MLIR experiment did not produce expected 4/4 result' >> "$DIR/verify.log"
    exit 1
  fi
  TYPED_LOG="$DIR/typed.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/typed.sh" </dev/null > "$TYPED_LOG" 2>&1; then
    cat "$TYPED_LOG" >> "$DIR/verify.log"
    echo 'typed experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$TYPED_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-typed' "$TYPED_LOG" || ! grep -q 'tasks 4 solved 4' "$TYPED_LOG"; then
    echo 'typed experiment did not produce expected 4/4 result' >> "$DIR/verify.log"
    exit 1
  fi
  PROOF_LOG="$DIR/proof.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/proof.sh" > "$PROOF_LOG" 2>&1; then
    cat "$PROOF_LOG" >> "$DIR/verify.log"
    echo 'proof experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$PROOF_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-proof' "$PROOF_LOG" || ! grep -q 'essential=(0 1)' "$PROOF_LOG"; then
    echo 'proof experiment did not produce expected credit/frontier result' >> "$DIR/verify.log"
    exit 1
  fi
  SYNTH_LOG="$DIR/synth.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/synth.sh" </dev/null > "$SYNTH_LOG" 2>&1; then
    cat "$SYNTH_LOG" >> "$DIR/verify.log"
    echo 'synth experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$SYNTH_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-synth' "$SYNTH_LOG" || ! grep -q 'SYNTH synth107' "$SYNTH_LOG"; then
    echo 'synth experiment did not synthesize the composition rule' >> "$DIR/verify.log"
    exit 1
  fi
  RANK_LOG="$DIR/synth-rank.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/synth_rank.sh" > "$RANK_LOG" 2>&1; then
    cat "$RANK_LOG" >> "$DIR/verify.log"
    echo 'ranked synthesis exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$RANK_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-rank' "$RANK_LOG" || ! grep -q 'RANKED COVERAGE 2/2' "$RANK_LOG"; then
    echo 'ranked synthesis did not produce expected coverage' >> "$DIR/verify.log"
    exit 1
  fi
  CHAIN_LOG="$DIR/synth-chain.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/synth_chain.sh" > "$CHAIN_LOG" 2>&1; then
    cat "$CHAIN_LOG" >> "$DIR/verify.log"
    echo 'chain synthesis exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$CHAIN_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-chain' "$CHAIN_LOG" || ! grep -q 'COVERAGE 2/2' "$CHAIN_LOG"; then
    echo 'chain synthesis did not produce expected coverage' >> "$DIR/verify.log"
    exit 1
  fi
  LONG_LOG="$DIR/synth-long.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/synth_long.sh" > "$LONG_LOG" 2>&1; then
    cat "$LONG_LOG" >> "$DIR/verify.log"
    echo 'long chain synthesis exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$LONG_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-long' "$LONG_LOG" || ! grep -q 'COVERAGE 2/2' "$LONG_LOG"; then
    echo 'long chain synthesis did not produce expected coverage' >> "$DIR/verify.log"
    exit 1
  fi
  REC_LOG="$DIR/synth-recursive.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/synth_recursive.sh" > "$REC_LOG" 2>&1; then
    cat "$REC_LOG" >> "$DIR/verify.log"
    echo 'recursive synthesis exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$REC_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-recursive' "$REC_LOG" || ! grep -q 'PROGRAM recursive rules=2' "$REC_LOG" || ! grep -q 'COVERAGE 2/2' "$REC_LOG" || ! grep -q 'HELD proof' "$REC_LOG"; then
    echo 'recursive synthesis did not produce expected program/coverage' >> "$DIR/verify.log"
    exit 1
  fi
  TMPL_LOG="$DIR/synth-template.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/synth_template.sh" > "$TMPL_LOG" 2>&1; then
    cat "$TMPL_LOG" >> "$DIR/verify.log"
    echo 'template synthesis exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$TMPL_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-template' "$TMPL_LOG" || ! grep -q 'PROGRAM template rules=2' "$TMPL_LOG" || ! grep -q 'COVERAGE 1/1' "$TMPL_LOG" || ! grep -q 'HELD proof' "$TMPL_LOG"; then
    echo 'template synthesis did not produce expected program/coverage' >> "$DIR/verify.log"
    exit 1
  fi
  REV_LOG="$DIR/synth-revise.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/synth_revise.sh" > "$REV_LOG" 2>&1; then
    cat "$REV_LOG" >> "$DIR/verify.log"
    echo 'revision synthesis exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$REV_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-revise' "$REV_LOG" || ! grep -q 'PROGRAM stride2 rules=2' "$REV_LOG" || ! grep -q 'NEGATIVE clean' "$REV_LOG" || ! grep -q 'HELD NEG fail' "$REV_LOG"; then
    echo 'revision synthesis did not reject the negative' >> "$DIR/verify.log"
    exit 1
  fi
  STRIDE_LOG="$DIR/synth-stride.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/synth_stride.sh" > "$STRIDE_LOG" 2>&1; then
    cat "$STRIDE_LOG" >> "$DIR/verify.log"
    echo 'stride synthesis exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$STRIDE_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-stride' "$STRIDE_LOG" || ! grep -q 'PROGRAM stride=3' "$STRIDE_LOG" || ! grep -q 'COVERAGE 1/1' "$STRIDE_LOG" || ! grep -q 'HELD NEG fail' "$STRIDE_LOG"; then
    echo 'stride synthesis did not infer stride three' >> "$DIR/verify.log"
    exit 1
  fi
  PAIR_LOG="$DIR/synth-pair.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/synth_pair.sh" > "$PAIR_LOG" 2>&1; then
    cat "$PAIR_LOG" >> "$DIR/verify.log"
    echo 'pair synthesis exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$PAIR_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-pair' "$PAIR_LOG" || ! grep -q 'PROGRAM pair rules=2' "$PAIR_LOG" || ! grep -q 'SINGLE coverage=0' "$PAIR_LOG" || ! grep -q 'HELD NEG fail' "$PAIR_LOG"; then
    echo 'pair synthesis did not beat single-predicate search' >> "$DIR/verify.log"
    exit 1
  fi
  SMLIR_LOG="$DIR/synth-mlir.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/synth_mlir.sh" > "$SMLIR_LOG" 2>&1; then
    cat "$SMLIR_LOG" >> "$DIR/verify.log"
    echo 'MLIR synthesis experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$SMLIR_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-mlir-synth' "$SMLIR_LOG" || ! grep -q 'SAME stride yes' "$SMLIR_LOG" || ! grep -q 'SAME pair yes' "$SMLIR_LOG"; then
    echo 'MLIR synthesis lowering did not match direct synthesis' >> "$DIR/verify.log"
    exit 1
  fi
  SMLIRP_LOG="$DIR/synth-mlir-pipeline.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/synth_mlir_pipeline.sh" > "$SMLIRP_LOG" 2>&1; then
    cat "$SMLIRP_LOG" >> "$DIR/verify.log"
    echo 'MLIR synthesis pipeline exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$SMLIRP_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-mlir-pipeline' "$SMLIRP_LOG" || ! grep -q 'SAME stride yes' "$SMLIRP_LOG" || ! grep -q 'SAME pair yes' "$SMLIRP_LOG" || ! grep -q 'PROOF stride pos=proof neg=fail' "$SMLIRP_LOG" || ! grep -q 'PROOF pair pos=proof neg=fail' "$SMLIRP_LOG"; then
    echo 'MLIR search/proof pipeline did not match expected results' >> "$DIR/verify.log"
    exit 1
  fi
  SMLIRA_LOG="$DIR/synth-mlir-auto.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/synth_mlir_auto.sh" > "$SMLIRA_LOG" 2>&1; then
    cat "$SMLIRA_LOG" >> "$DIR/verify.log"
    echo 'MLIR auto selection exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$SMLIRA_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-mlir-auto' "$SMLIRA_LOG" || ! grep -q 'AUTO parent mode=stride' "$SMLIRA_LOG" || ! grep -q 'AUTO alt mode=pair' "$SMLIRA_LOG"; then
    echo 'MLIR auto selection did not choose expected modes' >> "$DIR/verify.log"
    exit 1
  fi
  GOAL_LOG="$DIR/goal-proof.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/goal_proof.sh" > "$GOAL_LOG" 2>&1; then
    cat "$GOAL_LOG" >> "$DIR/verify.log"
    echo 'goal proof experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$GOAL_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-goal-proof' "$GOAL_LOG" || ! grep -q 'N=20 .*prove=13 .*status=proof' "$GOAL_LOG" || ! grep -q 'CHECK20 ok' "$GOAL_LOG"; then
    echo 'goal-directed proof did not produce expected bounded probes/proof' >> "$DIR/verify.log"
    exit 1
  fi
  PCACHE_LOG="$DIR/proof-cache.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/proof_cache.sh" > "$PCACHE_LOG" 2>&1; then
    cat "$PCACHE_LOG" >> "$DIR/verify.log"
    echo 'proof cache experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$PCACHE_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-proof-cache' "$PCACHE_LOG" || ! grep -q 'CACHED status=proof probes=0' "$PCACHE_LOG" || ! grep -q 'UNRELATED status=proof probes=0' "$PCACHE_LOG" || ! grep -q 'REMOVED status=fail' "$PCACHE_LOG"; then
    echo 'proof cache did not reuse/invalidate as expected' >> "$DIR/verify.log"
    exit 1
  fi
  GRAPH_LOG="$DIR/graph-ir.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/graph_ir.sh" > "$GRAPH_LOG" 2>&1; then
    cat "$GRAPH_LOG" >> "$DIR/verify.log"
    echo 'graph IR experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$GRAPH_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-graph-ir' "$GRAPH_LOG" || ! grep -q 'GRAPH check=ok' "$GRAPH_LOG" || ! grep -q 'same=yes' "$GRAPH_LOG" || ! grep -q 'DUP (rejected107 mg-node-id)' "$GRAPH_LOG" || ! grep -q 'BADEDGE (rejected107 mg-edge-input)' "$GRAPH_LOG"; then
    echo 'graph IR verifier/lowering did not match expectations' >> "$DIR/verify.log"
    exit 1
  fi
  CGRAPH_LOG="$DIR/constraint-graph.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/constraint_graph.sh" > "$CGRAPH_LOG" 2>&1; then
    cat "$CGRAPH_LOG" >> "$DIR/verify.log"
    echo 'constraint graph experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$CGRAPH_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-constraints' "$CGRAPH_LOG" || ! grep -q 'HARD ok' "$CGRAPH_LOG" || ! grep -q 'c-soft soft active false' "$CGRAPH_LOG" || ! grep -q 'BAD (rejected107 mg-constraint c-missing)' "$CGRAPH_LOG" || ! grep -q 'BADEXPR (rejected107 mg-constraint-expr c-expr)' "$CGRAPH_LOG"; then
    echo 'graph constraints did not classify hard/soft as expected' >> "$DIR/verify.log"
    exit 1
  fi
  EMBED_LOG="$DIR/graph-embed.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/graph_embed.sh" > "$EMBED_LOG" 2>&1; then
    cat "$EMBED_LOG" >> "$DIR/verify.log"
    echo 'graph embedding experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$EMBED_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-embed' "$EMBED_LOG" || ! grep -q 'EMBED ok' "$EMBED_LOG" || ! grep -q 'RANK ' "$EMBED_LOG" || ! grep -q 'BADDIM (rejected107 mg-embedding-dim)' "$EMBED_LOG" || ! grep -q 'BADNODE (rejected107 mg-embedding-node)' "$EMBED_LOG"; then
    echo 'graph embedding checks did not match expectations' >> "$DIR/verify.log"
    exit 1
  fi
  SCHED_LOG="$DIR/graph-schedule.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/graph_schedule.sh" > "$SCHED_LOG" 2>&1; then
    cat "$SCHED_LOG" >> "$DIR/verify.log"
    echo 'graph schedule experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$SCHED_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-schedule' "$SCHED_LOG" || ! grep -q 'RANKED ' "$SCHED_LOG" || ! grep -q 'SAME yes' "$SCHED_LOG"; then
    echo 'embedding schedule did not preserve run results' >> "$DIR/verify.log"
    exit 1
  fi
  DCE_LOG="$DIR/graph-dce.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/graph_dce.sh" > "$DCE_LOG" 2>&1; then
    cat "$DCE_LOG" >> "$DIR/verify.log"
    echo 'graph DCE experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$DCE_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-dce' "$DCE_LOG" || ! grep -q 'AFTER nodes=3 edges=1' "$DCE_LOG" || ! grep -q 'SAME yes' "$DCE_LOG"; then
    echo 'graph DCE did not preserve the run result' >> "$DIR/verify.log"
    exit 1
  fi
  SELECT_LOG="$DIR/graph-select.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/graph_select.sh" > "$SELECT_LOG" 2>&1; then
    cat "$SELECT_LOG" >> "$DIR/verify.log"
    echo 'graph candidate selection exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$SELECT_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-select' "$SELECT_LOG" || ! grep -q 'SOFT base=0 extra=1' "$SELECT_LOG" || ! grep -q 'SELECTED extra' "$SELECT_LOG"; then
    echo 'soft-constraint candidate selection did not choose expected graph' >> "$DIR/verify.log"
    exit 1
  fi
  CSE_LOG="$DIR/graph-cse.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/graph_cse.sh" > "$CSE_LOG" 2>&1; then
    cat "$CSE_LOG" >> "$DIR/verify.log"
    echo 'graph CSE experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$CSE_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-cse' "$CSE_LOG" || ! grep -q 'BEFORE nodes=6' "$CSE_LOG" || ! grep -q 'AFTER nodes=4 values=4 check=ok' "$CSE_LOG" || ! grep -q 'SAME yes' "$CSE_LOG"; then
    echo 'graph CSE did not merge duplicates or preserve run' >> "$DIR/verify.log"
    exit 1
  fi
  NL_LOG="$DIR/nl.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/nl.sh" > "$NL_LOG" 2>&1; then
    cat "$NL_LOG" >> "$DIR/verify.log"
    echo 'NL experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$NL_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-nl' "$NL_LOG" || ! grep -q 'BASIS RULES 2' "$NL_LOG" || ! grep -q 'STATUS1 proved' "$NL_LOG" || ! grep -q 'ANSWER1 Yes, a cat is a living thing.' "$NL_LOG" || ! grep -q 'STATUS2 unknown' "$NL_LOG"; then
    echo 'NL proof/answer did not match expectations' >> "$DIR/verify.log"
    exit 1
  fi
  BASIS_LOG="$DIR/basis.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/basis.sh" > "$BASIS_LOG" 2>&1; then
    cat "$BASIS_LOG" >> "$DIR/verify.log"
    echo 'basis experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$BASIS_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-basis' "$BASIS_LOG" || ! grep -q 'A proof=proof' "$BASIS_LOG" || ! grep -q 'B proof=proof' "$BASIS_LOG" || ! grep -q 'B OFF path=fail reach=proof' "$BASIS_LOG" || ! grep -q 'B ROLLBACK status=active path=proof' "$BASIS_LOG"; then
    echo 'basis lifecycle did not produce expected proof results' >> "$DIR/verify.log"
    exit 1
  fi
  TEACH_LOG="$DIR/teacher.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/teacher.sh" > "$TEACH_LOG" 2>&1; then
    cat "$TEACH_LOG" >> "$DIR/verify.log"
    echo 'teacher distillation experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$TEACH_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-teacher' "$TEACH_LOG" || ! grep -q 'HELD sparrow=proof' "$TEACH_LOG" || ! grep -q 'NL1 Yes, a sparrow is a living thing.' "$TEACH_LOG" || ! grep -q 'NL2 I cannot prove that a living thing is a sparrow.' "$TEACH_LOG"; then
    echo 'teacher distillation/NL boundary did not match expectations' >> "$DIR/verify.log"
    exit 1
  fi
  WEB_LOG="$DIR/web-nl.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/web_nl.sh" > "$WEB_LOG" 2>&1; then
    cat "$WEB_LOG" >> "$DIR/verify.log"
    echo 'web NL experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$WEB_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-web' "$WEB_LOG" || ! grep -q 'WEB1 proved Yes, a dog is a mammal.' "$WEB_LOG" || ! grep -q 'WEB2 unknown' "$WEB_LOG"; then
    echo 'web observation/NL answer did not match expectations' >> "$DIR/verify.log"
    exit 1
  fi
  WEBM_LOG="$DIR/web-multi.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/web_multi.sh" > "$WEBM_LOG" 2>&1; then
    cat "$WEBM_LOG" >> "$DIR/verify.log"
    echo 'multi-page web experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$WEBM_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-web-multi' "$WEBM_LOG" || ! grep -q 'DOG proved Yes, a dog is a mammal.' "$WEBM_LOG" || ! grep -q 'CAT proved Yes, a cat is a mammal.' "$WEBM_LOG"; then
    echo 'multi-page web observations did not answer both queries' >> "$DIR/verify.log"
    exit 1
  fi
  WEBR_LOG="$DIR/web-rule.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/web_rule.sh" > "$WEBR_LOG" 2>&1; then
    cat "$WEBR_LOG" >> "$DIR/verify.log"
    echo 'web universal rule experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$WEBR_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-web-rule' "$WEBR_LOG" || ! grep -q 'BASIS 2 rules' "$WEBR_LOG" || ! grep -q 'Q1 proved Yes, a dog is a living thing.' "$WEBR_LOG" || ! grep -q 'Q2 unknown' "$WEBR_LOG"; then
    echo 'web universal rule/basis answer did not match expectations' >> "$DIR/verify.log"
    exit 1
  fi
  WSTORE_LOG="$DIR/web-store.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/web_store.sh" > "$WSTORE_LOG" 2>&1; then
    cat "$WSTORE_LOG" >> "$DIR/verify.log"
    echo 'web store experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$WSTORE_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-store' "$WSTORE_LOG" || ! grep -q 'STORE1 obs=3 rules=2 Q1=proved' "$WSTORE_LOG" || ! grep -q 'STORE2 obs=4 rules=2 Q2=proved Q3=proved' "$WSTORE_LOG"; then
    echo 'incremental web store did not accumulate expected state' >> "$DIR/verify.log"
    exit 1
  fi
  WINV_LOG="$DIR/web-inverse.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/web_inverse.sh" > "$WINV_LOG" 2>&1; then
    cat "$WINV_LOG" >> "$DIR/verify.log"
    echo 'web inverse experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$WINV_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-web-inverse' "$WINV_LOG" || ! grep -q 'OBS 5 FACTS 5 RULES 2' "$WINV_LOG" || ! grep -q 'Q1 proved Yes, a cat is a living thing.' "$WINV_LOG" || ! grep -q 'Q2 unknown' "$WINV_LOG"; then
    echo 'web inverse deduction did not match expectations' >> "$DIR/verify.log"
    exit 1
  fi
  WREC_LOG="$DIR/web-recursive.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/web_recursive.sh" > "$WREC_LOG" 2>&1; then
    cat "$WREC_LOG" >> "$DIR/verify.log"
    echo 'web recursive experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$WREC_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-web-recursive' "$WREC_LOG" || ! grep -q 'WEB pages=7 edges=7 train=5' "$WREC_LOG" || ! grep -q 'POS 3 SELF 8' "$WREC_LOG" || ! grep -q 'RULES1 2 RULES2 2' "$WREC_LOG" || ! grep -q 'HELD 3/3 NEG fail' "$WREC_LOG"; then
    echo 'web recursive self-supervision did not match expectations' >> "$DIR/verify.log"
    exit 1
  fi
  WPERS_LOG="$DIR/web-persist.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/web_persist.sh" > "$WPERS_LOG" 2>&1; then
    cat "$WPERS_LOG" >> "$DIR/verify.log"
    echo 'web persistence experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$WPERS_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-persist-p1' "$WPERS_LOG" || ! grep -q 'SAVE /tmp/dlm-web-store.l obs=3 rules=2' "$WPERS_LOG" || ! grep -q 'LOAD (3 2)' "$WPERS_LOG" || ! grep -q 'P2 proved' "$WPERS_LOG" || ! grep -q 'P3 unknown' "$WPERS_LOG"; then
    echo 'persistent web store did not round-trip correctly' >> "$DIR/verify.log"
    exit 1
  fi
  WRECP_LOG="$DIR/web-recursive-persist.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/web_recursive_persist.sh" > "$WRECP_LOG" 2>&1; then
    cat "$WRECP_LOG" >> "$DIR/verify.log"
    echo 'web recursive persistence exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$WRECP_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-rec-persist-p1' "$WRECP_LOG" || ! grep -q 'SAVE /tmp/dlm-web-recursive-basis.l rules=2' "$WRECP_LOG" || ! grep -q 'LOAD (0 2)' "$WRECP_LOG" || ! grep -q 'HELD 3/3 NEG fail RULES 2' "$WRECP_LOG"; then
    echo 'persistent web recursive basis did not round-trip correctly' >> "$DIR/verify.log"
    exit 1
  fi
  AX_LOG="$DIR/axiom.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/axiom.sh" > "$AX_LOG" 2>&1; then
    cat "$AX_LOG" >> "$DIR/verify.log"
    echo 'atomic axiom experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$AX_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-axiom' "$AX_LOG" || ! grep -q 'AX 2 SUBSETS 4 CLOSED 3' "$AX_LOG" || ! grep -q 'SEL (A-0 A-1) COV 3' "$AX_LOG" || ! grep -q 'HELD 3/3' "$AX_LOG"; then
    echo 'atomic axiom subset search did not match expectations' >> "$DIR/verify.log"
    exit 1
  fi
  AG_LOG="$DIR/axiom-graph.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/axiom_graph.sh" > "$AG_LOG" 2>&1; then
    cat "$AG_LOG" >> "$DIR/verify.log"
    echo 'axiom graph experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$AG_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-axiom-graph' "$AG_LOG" || ! grep -q 'AG nodes=2 check=ok deps=ok' "$AG_LOG" || ! grep -q 'AG SEL (A-0 A-1) COV 3' "$AG_LOG" || ! grep -q 'A SEL (A-0 A-1) SAME yes' "$AG_LOG" || ! grep -q 'HELD 3/3' "$AG_LOG"; then
    echo 'axiom graph selection did not match list selection' >> "$DIR/verify.log"
    exit 1
  fi
  AGD_LOG="$DIR/axiom-dce.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/axiom_dce.sh" > "$AGD_LOG" 2>&1; then
    cat "$AGD_LOG" >> "$DIR/verify.log"
    echo 'axiom DCE experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$AGD_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-axiom-dce' "$AGD_LOG" || ! grep -q 'BEFORE 3 AFTER 2 check=ok' "$AGD_LOG" || ! grep -q 'AG SEL (A-0 A-1)' "$AGD_LOG"; then
    echo 'axiom graph DCE did not drop the unrelated axiom' >> "$DIR/verify.log"
    exit 1
  fi
  AGC_LOG="$DIR/axiom-cse.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/axiom_cse.sh" > "$AGC_LOG" 2>&1; then
    cat "$AGC_LOG" >> "$DIR/verify.log"
    echo 'axiom CSE experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$AGC_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-axiom-cse' "$AGC_LOG" || ! grep -q 'BEFORE 3 AFTER 2 check=ok deps=(A-0)' "$AGC_LOG" || ! grep -q 'SEL (A-0 A-1)' "$AGC_LOG"; then
    echo 'axiom graph CSE did not merge duplicates correctly' >> "$DIR/verify.log"
    exit 1
  fi
  SSL_LOG="$DIR/selfssl.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/selfssl.sh" > "$SSL_LOG" 2>&1; then
    cat "$SSL_LOG" >> "$DIR/verify.log"
    echo 'self-supervision loop exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$SSL_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-selfssl' "$SSL_LOG" || ! grep -q 'ROUND 1 pos=8 new=5 rules=2' "$SSL_LOG" || ! grep -q 'ROUND 2 pos=8 new=0 rules=2' "$SSL_LOG" || ! grep -q 'HELD 3/3 NEG fail' "$SSL_LOG"; then
    echo 'self-supervision loop did not reach expected saturation' >> "$DIR/verify.log"
    exit 1
  fi
  DT_LOG="$DIR/dtir.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/dtir.sh" > "$DT_LOG" 2>&1; then
    cat "$DT_LOG" >> "$DIR/verify.log"
    echo 'DTIR experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$DT_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-dtir' "$DT_LOG" || ! grep -q 'DT name=dt1 selected=(A-0 A-1) cov=3 proof=proof' "$DT_LOG" || ! grep -q 'BAD (rejected107 dt-verifier-missing)' "$DT_LOG"; then
    echo 'DT proof-state dialect did not select/verify as expected' >> "$DIR/verify.log"
    exit 1
  fi
  TTR_LOG="$DIR/teacher-transformer.log"
  if ! MARU="$DIR/maru" "$ROOT/scripts/teacher_transformer.sh" > "$TTR_LOG" 2>&1; then
    cat "$TTR_LOG" >> "$DIR/verify.log"
    echo 'transformer behavior experiment exited non-zero' >> "$DIR/verify.log"
    exit 1
  fi
  cat "$TTR_LOG" >> "$DIR/verify.log"
  if ! grep -q 'done-teacher-transformer' "$TTR_LOG" || ! grep -q 'teacher_train_acc=' "$TTR_LOG" || ! grep -q 'TRAIN pos=3 neg=3 RULES 1' "$TTR_LOG" || ! grep -q 'HELD 2/2 NEGPROOFS 0' "$TTR_LOG"; then
    echo 'transformer behavior/inverse deduction did not match expectations' >> "$DIR/verify.log"
    exit 1
  fi
  "$TOOL" --self "$DIR/maru" "$DIR/next" >> "$DIR/verify.log" 2>&1
  cmp "$DIR/maru.ll" "$DIR/next.ll" >> "$DIR/verify.log" 2>&1
  cp "$DIR/maru" "$DIR/maru.stripped"; cp "$DIR/next" "$DIR/next.stripped"
  strip "$DIR/maru.stripped" "$DIR/next.stripped"
  cmp "$DIR/maru.stripped" "$DIR/next.stripped" >> "$DIR/verify.log" 2>&1
  "$TOOL" --self "$DIR/next" "$DIR/third" >> "$DIR/verify.log" 2>&1
  cmp "$DIR/next.ll" "$DIR/third.ll" >> "$DIR/verify.log" 2>&1
  cp "$DIR/third" "$DIR/third.stripped"; strip "$DIR/third.stripped"
  cmp "$DIR/next.stripped" "$DIR/third.stripped" >> "$DIR/verify.log" 2>&1
  (cd "$ROOT"; { find src/dlm tests adapters scripts experiments -type f \( -name '*.l' -o -name '*.sh' -o -name '*.py' -o -name '*.sexp' \); printf '%s\n' VERSION; } | sort -u | xargs sha256sum) > "$DIR/tests.sha256"
  (cd "$DIR"; sha256sum artifacts.sha256 tests.sha256 verify.log) > "$DIR/verified"
  echo "Verified: $ID" ;;
 promote)
  ID="${1:?release ID required}"
  [[ "$ID" =~ ^[A-Za-z0-9_-]+$ ]] || exit 2
  DIR="$ROOT/runtime/releases/$ID"
  (cd "$DIR"; sha256sum -c verified; sha256sum -c artifacts.sha256) >/dev/null
  (cd "$ROOT"; sha256sum -c "$DIR/tests.sha256") >/dev/null
  if grep -qx 'mode=rebuild' "$DIR/record"; then
   CURRENT="$(mktemp)"
   (cd "$ROOT"; find src -type f -print0 | sort -z | xargs -0 sha256sum) > "$CURRENT"
   if ! cmp -s "$CURRENT" "$DIR/sources.sha256"; then
    rm -f "$CURRENT"; echo 'Source changed since candidate build' >&2; exit 1
   fi
   rm -f "$CURRENT"
  fi
  [[ -L "$ROOT/maru-compiler" ]] || { echo 'Active runtime must be a symlink' >&2; exit 1; }
  OLD="$(readlink "$ROOT/maru-compiler")"
  ln -s "$OLD" "$ROOT/runtime/previous.new"; mv -Tf "$ROOT/runtime/previous.new" "$ROOT/runtime/previous"
  ln -s "runtime/releases/$ID/maru" "$ROOT/maru-compiler.new"
  mv -Tf "$ROOT/maru-compiler.new" "$ROOT/maru-compiler"
  echo "Promoted: $ID" ;;
 rollback)
  OLD="$(readlink "$ROOT/runtime/previous")"
  [[ -x "$ROOT/$OLD" ]] || exit 1
  ln -s "$OLD" "$ROOT/maru-compiler.new"; mv -Tf "$ROOT/maru-compiler.new" "$ROOT/maru-compiler"
  echo 'Rolled back to previous runtime' ;;
 *) echo 'usage: compiler.sh rebuild|reproduce|verify ID|promote ID|rollback' >&2; exit 2 ;;
esac
