# DLM v0.0217 — DT-1 selector on an array-view C backend: feasibility probe

## Question

Can the deductive-learning transformer (DT-1) be transplanted into the v0.0216
Maru array-view + C/LLVM fast backend, or is it structurally incompatible?

## Short answer

**Inference hot path: yes, with caveats.**
**Training: no.**

The DT-1 selector is already Q16 integer arithmetic on dense vectors and
matrices. It maps naturally to contiguous C arrays. This probe ports the
complete selector for one LOCO fold/case to standalone C and checks it against
both the PyTorch reference and the Maru Q16 runtime.

## Probe scope

Ported in `dt_selector_c.c`:

```text
valid-rule mask (body match)
rule features (n/on/off/index/saturation)
image projection
rule-token projection
6 compact masked attention blocks
  matvec / Q16 dot
  Q16 exp softmax
  Q16 layernorm
  residual + ReLU FFN
final selector readout
k-NN head prior
score + argmax
```

Not ported:

```text
proof (p-prove / p-proof-check)      remains Maru
Maru fault/safety/type admission     remains Maru
training / autograd                  remains external PyTorch
```

## Fixture

Source:

```text
/research/dlm_v0.0204/experiments/deductive_transformer_maru
```

Generated C fixture:

```text
fixture.py → fixture.h
```

Model fold 0: **15,425 Q16 ints = ~123 KB**.
All 10 folds: ~1.23 MB. This fits comfortably in persistent C arrays or
array-view buffers.

Case 0 valid rules: `102 211`.

## Parity result

```text
CASE 0 VALID      102 211
C-SELECTOR        3.379913330 3.380187988
PY_SELECTOR       3.379095793 3.379302502
MARU_SELECTOR     3.378845215 3.379074097
C-PICK            211
```

Errors:

```text
C vs PyTorch max abs error   8.85e-4
C vs Maru Q16 max abs error  1.11e-3
```

The selected rule matches:

```text
C-PICK = MARU PICK = PYTORCH PICK = 211
CASE 0 HEAD = 7
```

This is **parity of the decision**, not bit-exact fixed-point equality.
The remaining difference is expected from Q16 rounding/softmax/layernorm
ordering; exact alignment is a separate task.

## Performance

Standalone C, one case including process startup:

```text
~1 ms / invocation
```

The Maru v0.0204 DT run (`run.sh`, 10 cases including proof) took ~84 s.
This is not an apples-to-apples comparison: the C probe does selector scoring
only, while Maru also runs the proof gate. It establishes that the selector
compute itself is small enough that data export/transport and proof, not
attention arithmetic, are the likely bottlenecks.

## Array-view fit

| DT component | Array-view fit | Notes |
|---|---|---|
| image bits | direct | 196 × 1-byte or 8-byte vector |
| rule bodies | direct | flat int32/int64 + lengths |
| model tensors | direct | 1.23 MB Q16 for all folds |
| valid-rule mask | direct | byte/bit scanned in C |
| matvec/dot | direct | dense contiguous Q16 |
| softmax/layernorm | direct but numerical | Q16 exp table + rounding must match |
| k-NN prior | direct | pool 190×196 bytes |
| selector argmax | direct | scalar + small valid set |
| proof/admission | **not portable** | must stay in Maru |
| training | **not portable** | PyTorch/autograd |

## Why this is promising

- DT-1 is already integer-only at inference.
- Tokens are tiny: image + ~2 valid rules; attention is O(3²), not O(219²).
- The expensive-looking part is dense matvec over 196/32/64 dimensions.
- Weights fit in ~1.2 MB; no dynamic graph, no gradient tape, no float
  tensors are required.
- The C implementation reproduces the selected rule and stays within ~1e-3
  of both references.

## Blockers / conditions

1. **Export format**
   S-expression `models.l` must become a flat binary/array-view buffer.
   `fixture.py` proves the conversion; a production exporter would write a
   persistent Q16 block once.

2. **Exact fixed-point conventions**
   C vs Maru is ~1.1e-3, not bit-exact. Align:
   - negative `fx-mul` shift
   - `fx-div` rounding
   - `v-softmax` division order
   - layernorm variance/mean ordering
   before claiming full numeric equivalence.

3. **Array-view element size**
   The v0.0216 indexed-join kernel uses 1-byte keys. DT needs Q16/int32/int64
   views; the ABI supports `elem_size` 1/2/4/8, but a DT-specific kernel must
   read the corresponding width.

4. **Proof stays outside**
   A C selector can accelerate candidate scoring, but it cannot replace
   `p-prove`/`p-proof-check` as the truth gate.

5. **Training is out of scope**
   The probe does not attempt autograd/Adam/softmax training in C or Maru.

## Decision

```text
Feasibility: POSITIVE for DT-1 inference selector
Recommended next step: binary export + one wrapped C selector primitive
Not recommended: move proof or training into C
```

## Reproduce

```bash
cd /research/dlm_v0.0216/experiments/dt_array_backend_probe
./run_probe.sh
```

Expected final line:

```text
DT-ARRAY-BACKEND-PARITY-PASS
```
