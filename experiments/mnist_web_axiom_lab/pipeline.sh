#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./run.sh > mnist_web.out
(cd ../dt_full_port_no_mlir && ./run_full.sh > /tmp/mnist_web_dt_infer.out)
(cd ../dt_full_port_no_mlir && ./run_train.sh > /tmp/mnist_web_dt_train.out)
cp /tmp/mnist_web_dt_infer.out dt_infer.out
cp /tmp/mnist_web_dt_train.out dt_train.out
python3 verify_pipeline.py
