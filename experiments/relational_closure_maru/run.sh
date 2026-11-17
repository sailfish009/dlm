#!/usr/bin/env bash
# 0.0253 relational closure lab: kernel soundness, closure-primitive gates,
# gradchecks, and the closure-vs-attention length-extrapolation discrimination.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p bin out
EPOCHS="${EPOCHS:-200}"

clang -O2 -Iinclude src/rc.c       -o bin/rc       -lm
clang -O2 -Iinclude src/rc_model.c -o bin/rc_model -lm
clang -O2 -Iinclude src/rc_chain.c -o bin/rc_chain -lm
clang -O2 -Iinclude src/rc_attn.c  -o bin/rc_attn  -lm

./bin/rc --self-check | tee out/self_check.txt
./bin/rc_model --worlds 100 | tee out/primitive_gates.txt
./bin/rc_model --gradcheck | tee out/model_gradcheck.txt
./bin/rc_chain --worlds 30 | tee out/primitive_scaling.txt
./bin/rc_attn --gradcheck | tee out/attn_gradcheck.txt

# discrimination: attention length-extrapolation at 3 branching levels (primitive=1.0 constructive)
for dec in 0 20 40; do
  ./bin/rc_attn --extrap --epochs "$EPOCHS" --decoy "$dec" > out/extrap_decoy$dec.txt 2>&1
  grep '^ATTN-EXTRAP-DONE' out/extrap_decoy$dec.txt
done
./bin/rc_chain --mlp > out/mlp_extrap.txt 2>&1
grep '^MLP-EXTRAP-DONE' out/mlp_extrap.txt

# O0/O2/O3 identity (apparatus determinism)
for O in 0 2 3; do
  clang -O$O -Iinclude src/rc_attn.c -o bin/attn_O$O -lm
  { ./bin/attn_O$O --gradcheck; ./bin/attn_O$O --extrap --epochs 30 --decoy 20; } > out/id_attn_O$O.txt 2>/dev/null
  clang -O$O -Iinclude src/rc_model.c -o bin/rcm_O$O -lm
  { ./bin/rcm_O$O --worlds 50; ./bin/rcm_O$O --gradcheck; } > out/id_rcm_O$O.txt 2>/dev/null
done
diff -q out/id_attn_O0.txt out/id_attn_O2.txt
diff -q out/id_attn_O0.txt out/id_attn_O3.txt
diff -q out/id_rcm_O0.txt out/id_rcm_O2.txt
diff -q out/id_rcm_O0.txt out/id_rcm_O3.txt
echo "LLVM-MATRIX PASS O0/O2/O3 (attn + rc_model)"

clang -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer -Iinclude src/rc_attn.c -o bin/attn_asan -lm
./bin/attn_asan --gradcheck > out/asan.txt 2> out/asan.err
./bin/attn_asan --extrap --epochs 5 --decoy 20 >> out/asan.txt 2>> out/asan.err
grep -q 'Sanitizer' out/asan.err && { echo ASAN-FAIL; cat out/asan.err; exit 1; }
echo "ASAN+UBSAN clean (rc_attn)"
echo "RC-RUN-DONE"