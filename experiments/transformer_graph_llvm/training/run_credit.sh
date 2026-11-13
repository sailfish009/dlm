#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
for n in 0 1 2; do
  clang -O3 -I. -DINT_CREDIT=$n dt_train_c.c -o dt_credit_$n -lm
  ./dt_credit_$n > credit_$n.out
done
