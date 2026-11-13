#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./run_graph.sh > graph.out
./run_llvm.sh > llvm.out
./run_llvm_opt.sh > llvm_opt.out
./run_train_graph.sh > train_graph.out
./training/run_llvm_train.sh > training_llvm.out
./run_graph_variants.sh > graph_variants.out
(cd ../proof_path_integral_rebuild && ./run.sh > out.txt && ./verify.sh > proof_path.verify)
./run_graph_control.sh > graph_control.out
./verify.sh
