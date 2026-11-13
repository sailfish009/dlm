#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
grep -q '^GRAPH ok NODES 14 EDGES 17$' graph.out || { echo 'graph shape changed'; exit 1; }
grep -q '^CSE 14 DCE 14$' graph.out || { echo 'graph rewrite changed'; exit 1; }
grep -q '^TOPO (input matmul-q' graph.out || { echo 'topo changed'; exit 1; }
n=$(grep -c 'PICKS-OK' llvm.out)
[ "$n" -eq 8 ] || { echo "LLVM pick parity $n/8"; exit 1; }
echo 'GRAPH ok NODES 14 EDGES 17'
echo 'CSE 14 DCE 14'
echo 'LLVM PICKS-OK 8/8'
[ "$(grep -c 'PICKS-OK' llvm_opt.out)" -eq 8 ] || { echo 'opt matrix pick parity failed'; exit 1; }
echo 'LLVM-OPT PICKS-OK 8/8'
grep -q '^TRAIN-GRAPH ok NODES 5 EDGES 6$' train_graph.out || { echo 'train graph changed'; exit 1; }
[ "$(grep -c 'PICKS-OK' training_llvm.out)" -eq 3 ] || { echo 'LLVM training parity failed'; exit 1; }
echo 'TRAIN-GRAPH ok NODES 5 EDGES 6'
echo 'LLVM-TRAIN PICKS-OK 3/3'
grep -q '^G-SHARED ok NODES 2 TOPO (sinput shared)$' graph_variants.out || { echo 'shared graph changed'; exit 1; }
grep -q '^G-GATED ok NODES 3 TOPO (ginput gate gout)$' graph_variants.out || { echo 'gated graph changed'; exit 1; }
grep -q '^G-PROOF ok NODES 4 TOPO (pinput candidate proof credit)$' graph_variants.out || { echo 'proof graph changed'; exit 1; }
echo 'G-SHARED/GATED/PROOF ok'
grep -q 'V0229-PROOF-PATH-INTEGRAL-REBUILD-PASS' ../proof_path_integral_rebuild/proof_path.verify || { echo 'proof-path credit failed'; exit 1; }
echo 'PROOF-PATH-INTEGRAL credit ok'
grep -q '^BAD-EDGE (rejected107 mg-edge-node)$' graph_control.out || { echo 'bad-edge control failed'; exit 1; }
grep -q '^CYCLE (rejected107 mg-cycle)$' graph_control.out || { echo 'cycle control failed'; exit 1; }
echo 'BAD-EDGE/CYCLE rejected'
echo 'V0236-GRAPH-LLVM-STAGE5-PASS'
grep -q '^TRAIN-GRAPH ok NODES 5 EDGES 6$' train_graph.out || { echo 'train graph changed'; exit 1; }
[ "$(grep -c 'PICKS-OK' training_llvm.out)" -eq 3 ] || { echo 'LLVM training parity failed'; exit 1; }
echo 'TRAIN-GRAPH ok NODES 5 EDGES 6'
echo 'LLVM-TRAIN PICKS-OK 3/3'
grep -q '^G-SHARED ok NODES 2 TOPO (sinput shared)$' graph_variants.out || { echo 'shared graph changed'; exit 1; }
grep -q '^G-GATED ok NODES 3 TOPO (ginput gate gout)$' graph_variants.out || { echo 'gated graph changed'; exit 1; }
grep -q '^G-PROOF ok NODES 4 TOPO (pinput candidate proof credit)$' graph_variants.out || { echo 'proof graph changed'; exit 1; }
echo 'G-SHARED/GATED/PROOF ok'
grep -q 'V0229-PROOF-PATH-INTEGRAL-REBUILD-PASS' ../proof_path_integral_rebuild/proof_path.verify || { echo 'proof-path credit failed'; exit 1; }
echo 'PROOF-PATH-INTEGRAL credit ok'
grep -q '^BAD-EDGE (rejected107 mg-edge-node)$' graph_control.out || { echo 'bad-edge control failed'; exit 1; }
grep -q '^CYCLE (rejected107 mg-cycle)$' graph_control.out || { echo 'cycle control failed'; exit 1; }
echo 'BAD-EDGE/CYCLE rejected'
echo 'V0236-GRAPH-LLVM-STAGE5-PASS'
