#!/usr/bin/env python3
"""Verify the Q16 Maru port against the PyTorch reference."""
import json, os, re, subprocess, sys
from pathlib import Path
import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
MARU = Path(os.environ.get("MARU", "/research/dlm_v0.0204/maru-compiler"))
BOOT = Path("/research/dlm_v0.0204/src/maru/boot.l")
LOGIC = Path("/research/dlm_v0.0204/src/dlm/logic.l")
BASE = [str(MARU), str(BOOT), str(LOGIC), str(ROOT/'src/exp_table.l'), str(ROOT/'src/fx.l')]
WEIGHTS = [str(ROOT/'src/weights.l'), str(ROOT/'src/cases.l'), str(ROOT/'src/transformer.l')]
Q = 65536

def run(files, timeout=240, weights=False):
    files = BASE + (WEIGHTS if weights else []) + [str(f) for f in files]
    r = subprocess.run(files, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        print(r.stdout); print(r.stderr, file=sys.stderr)
        raise SystemExit(f"maru failed rc={r.returncode} files={files}")
    return r.stdout

def main():
    results = []
    def ck(name, ok, detail=""):
        results.append({"name": name, "pass": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + name + (" " + str(detail) if detail else ""))

    # 1. fixed-point unit tests
    fx = run([ROOT/'src/fxtest.l'])
    ck("Q16 kernel tests", fx.count("PASS ") == 7 and "FAIL" not in fx and "FX-TEST-DONE" in fx,
       f"{fx.count('PASS ')} pass")

    # 2. encoder + first-step logits vs PyTorch
    import reference as R
    model = R.load_checkpoint(ROOT / 'checkpoint.pt')
    src_text = R.EN_CN_PAIRS[0][0]
    src = torch.tensor([R.SOURCE_IDS[w] for w in src_text.split()])
    with torch.no_grad():
        src_t = torch.tensor([R.SOURCE_IDS[w] for w in src_text.split()], dtype=torch.long)
        enc_t = model.encode(src_t)
        bos_t = torch.tensor([R.BOS], dtype=torch.long)
        dec_t = model.target_embedding(bos_t)
        enc_ref = enc_t.numpy()
        lg_ref = model.output_projection(model.decoder(dec_t, enc_t))[-1].numpy()

    dump1 = run([ROOT/'src/dump.l'], weights=True)
    dump2 = run([ROOT/'src/dump.l'], weights=True)
    ck("Maru dump deterministic", dump1 == dump2)
    encs, logits_by_case, mode, cur = {}, {}, None, None
    for line in dump1.splitlines():
        m = re.match(r"(ENC|LOGITS) (\d+)", line)
        if m:
            mode, cur = m.group(1), int(m.group(2)); continue
        if not line.strip(): continue
        vals = [int(x) for x in line.split()]
        if mode == "ENC": encs.setdefault(cur, []).append(vals)
        elif mode == "LOGITS": logits_by_case[cur] = vals
    ck("dump has 8 encoders and 8 logit rows", len(encs) == 8 and len(logits_by_case) == 8,
       f"{len(encs)}/{len(logits_by_case)}")

    max_enc_err, max_lg_err, argmax_ok = 0.0, 0.0, True
    with torch.no_grad():
        for c, (en, _cn) in enumerate(R.EN_CN_PAIRS):
            s_ids = torch.tensor([R.SOURCE_IDS[w] for w in en.split()], dtype=torch.long)
            e_t = model.encode(s_ids)
            e_ref = e_t.numpy()
            l_ref = model.output_projection(model.decoder(
                model.target_embedding(torch.tensor([R.BOS], dtype=torch.long)), e_t))[-1].numpy()
            rows = np.array(encs[c]).reshape(e_ref.shape) / Q
            lg = np.array(logits_by_case[c]) / Q
            max_enc_err = max(max_enc_err, float(np.abs(rows - e_ref).max()))
            max_lg_err = max(max_lg_err, float(np.abs(lg - l_ref).max()))
            if int(lg.argmax()) != int(l_ref.argmax()): argmax_ok = False
    ck("encoder row counts match source lengths", all(
        len(encs[c]) == len(R.EN_CN_PAIRS[c][0].split()) for c in range(8)),
       [len(encs[c]) for c in range(8)])
    ck("encoder max abs error < 0.01 (8 cases)", max_enc_err < 0.01, f"{max_enc_err:.6f}")
    ck("logits max abs error < 0.05 (8 cases)", max_lg_err < 0.05, f"{max_lg_err:.6f}")
    ck("first-step argmax matches (8 cases)", argmax_ok)

    # 3. full translations
    out = run([ROOT/'src/main.l'], timeout=300, weights=True)
    blocks = re.findall(r"CASE (\d+)\nSRC (.*)\nMARU (.*)\nREF (.*)\nMATCH (\d)", out)
    ref = json.loads((ROOT/'reference_out.json').read_text())
    ck("8 cases emitted", len(blocks) == 8, len(blocks))
    matched = sum(int(b[4]) for b in blocks)
    ck("greedy translations 8/8", matched == 8 and len(blocks) == 8, f"{matched}/8")
    texts_ok = all(b[2] == ref[int(b[0])]['translation'] for b in blocks)
    ck("Maru text equals exported reference", texts_ok)

    ok = all(r["pass"] for r in results)
    (ROOT/'verification.json').write_text(json.dumps({
        "pass": ok, "results": results,
        "encoder_max_abs_error": max_enc_err,
        "logits_max_abs_error": max_lg_err,
        "greedy_matched": matched,
        "sentences": [{"case": int(b[0]), "source": b[1], "maru": b[2], "ref": b[3], "match": int(b[4])} for b in blocks],
    }, ensure_ascii=False, indent=2) + "\n")
    print("MARU-PORT-VERIFY-PASS" if ok else "MARU-PORT-VERIFY-FAIL")
    return 0 if ok else 1

if __name__ == '__main__':
    raise SystemExit(main())
