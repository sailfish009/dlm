#!/usr/bin/env python3
"""Train 10 LOCO masked-attention DT selectors and export Q16 data for Maru."""
import json, math, re, sys
from pathlib import Path
import numpy as np, torch, torch.nn as nn

ROOT = Path(__file__).resolve().parent
PRL = ROOT.parent / 'proof_rl_dlm'
DED = ROOT.parent / 'mnist_deduce'
sys.path.insert(0, str(PRL))
import iter_runner as ir

Q = 1 << 16
ONE = Q
def q16(x):
    if isinstance(x, list): return [q16(v) for v in x]
    return int(round(float(x) * Q))

# ---------- data ----------
allc = []
for line in (DED/'cases.l').read_text().splitlines():
    m = re.match(r'\s*\(list "(\d)" \(list (.*)\)\)$', line)
    if m:
        v = [0]*196
        for p, i in re.findall(r"l-atom '(on|off) \(list \"(\d+)\"\)", m.group(2)):
            v[int(i)] = 1 if p == 'on' else 0
        allc.append((int(m.group(1)), v))
cases = allc[:10]
pool = allc[10:]
P = np.array([v for _, v in pool]); PY = np.array([y for y, _ in pool])

rules = []
for line in (DED/'rules.l').read_text().splitlines():
    m = re.search(r"\(l-rule \(l-atom 'digit \(list \"(\d)\"\)\) \(list (.*)\)\)", line)
    if m:
        rules.append((int(m.group(1)), re.findall(r"l-atom '(on|off) \(list \"(\d+)\"\)", m.group(2))))
for d, b in list(rules):
    rules.append(((d + 5) % 10, b))
assert len(rules) == 218

actual, proof = {}, {}
for line in (PRL/'p1.out').read_text().splitlines():
    m = re.match(r'SINGLE case=(\d+) rule=(\d+) label=(\S+) pred=(\S+) status=(\w+) correct=(\d)', line)
    if m and int(m.group(1)) < 10:
        c, k = int(m.group(1)), int(m.group(2))
        actual[(c, k)] = int(m.group(6))
        proof[(c, k)] = 1 if m.group(5) == 'proof' else 0

# ---------- selector ----------
class SelM(nn.Module):
    def __init__(self, loops=6, w=32, h=1):
        super().__init__()
        self.img = nn.Linear(196, w)
        self.rule = nn.Linear(16, w)
        self.blk = nn.TransformerEncoderLayer(w, h, w * 2, batch_first=True)
        self.out = nn.Linear(w, 1)
        self.loops = loops

    def forward(self, img, r, pad):
        x = torch.cat([self.img(img).unsqueeze(1), self.rule(r)], 1)
        for _ in range(self.loops):
            x = self.blk(x, src_key_padding_mask=pad)
        return self.out(x[:, 1:]).squeeze(-1)

def train(cids, seed=61, epochs=20):
    torch.manual_seed(seed)
    X, R, M, Y = ir.data(cids, 'full')
    m = SelM()
    opt = torch.optim.Adam(m.parameters(), lr=0.01)
    pad = torch.cat([torch.zeros(X.shape[0], 1, dtype=torch.bool), M == 0], 1)
    for _ in range(epochs):
        logits = m(X, R, pad).masked_fill(M == 0, -1e9)
        loss = nn.functional.binary_cross_entropy_with_logits(logits, Y, pos_weight=torch.tensor(30.0))
        opt.zero_grad(); loss.backward(); opt.step()
    m.eval()
    return m

def compact_logits(m, c):
    img = torch.tensor(cases[c][1], dtype=torch.float)
    valid = [k for k in range(len(rules)) if ir.mask(c)[k].item() > 0]
    feats = torch.tensor([ir.rv(cases[c][1], rules[k][0], rules[k][1], 'full') for k in valid], dtype=torch.float)
    x = torch.cat([m.img(img).unsqueeze(0), m.rule(feats)], 0)
    with torch.no_grad():
        for _ in range(m.loops):
            x = m.blk(x)
        return valid, m.out(x[1:]).squeeze(-1).numpy()

def kNN(c, k=5):
    d = ((P - np.array(cases[c][1])) ** 2).sum(1)
    idx = np.argsort(d)[:k]
    return np.bincount(PY[idx], minlength=10), idx

# ---------- train/export ----------
def fmt_arr(a): return '(list ' + ' '.join(str(int(v)) for v in a) + ')'
def fmt_any(x):
    if isinstance(x, list): return '(list ' + ' '.join(fmt_any(v) for v in x) + ')'
    return str(int(x))
def fmt_mat(a): return '(list ' + ' '.join(fmt_arr(row) for row in a) + ')'
def names():
    return ['img-w','img-b','rule-w','rule-b','in-w','in-b','attn-out-w','attn-out-b',
            'lin1-w','lin1-b','lin2-w','lin2-b','n1-g','n1-b','n2-g','n2-b','out-w','out-b']

models, ref = [], []
for c in range(10):
    tr = [x for x in range(10) if x != c]
    m = train(tr)
    sd = m.state_dict()
    vals = [
        sd['img.weight'].numpy(), sd['img.bias'].numpy(),
        sd['rule.weight'].numpy(), sd['rule.bias'].numpy(),
        sd['blk.self_attn.in_proj_weight'].numpy(), sd['blk.self_attn.in_proj_bias'].numpy(),
        sd['blk.self_attn.out_proj.weight'].numpy(), sd['blk.self_attn.out_proj.bias'].numpy(),
        sd['blk.linear1.weight'].numpy(), sd['blk.linear1.bias'].numpy(),
        sd['blk.linear2.weight'].numpy(), sd['blk.linear2.bias'].numpy(),
        sd['blk.norm1.weight'].numpy(), sd['blk.norm1.bias'].numpy(),
        sd['blk.norm2.weight'].numpy(), sd['blk.norm2.bias'].numpy(),
        sd['out.weight'].numpy()[0], sd['out.bias'].numpy()[0],
    ]
    models.append([q16(np.asarray(a).tolist()) for a in vals])
    valid, s = compact_logits(m, c)
    counts, idx = kNN(c)
    prob = (counts + 1) / (5 + 10)
    scores = []
    for k, sk in zip(valid, s):
        scores.append((float(sk) + 4.0 * math.log(prob[rules[k][0]]), k))
    scores.sort(reverse=True)
    pick = scores[0][1]
    ref.append({'case': c, 'valid': valid, 'selector': [float(x) for x in s],
                'pick': pick, 'head': rules[pick][0], 'correct': actual.get((c, pick), 0),
                'label': cases[c][0], 'proof': proof.get((c, pick), 0),
                'scores': [[float(a), int(b)] for a, b in scores]})
    print(c, 'valid', valid, 'pick', pick, 'head', rules[pick][0], 'correct', ref[-1]['correct'], flush=True)

# ---------- write S-expressions ----------
L = [';;; auto-generated by export_dt.py — Q16']
L.append(f'(define q-scale {Q})')
L.append('(define models (list')
for vals in models:
    L.append('  (list ' + ' '.join(fmt_any(x) for x in vals) + ')')
L.append('))')
(ROOT/'src/models.l').write_text('\n'.join(L) + '\n')

L = [';;; auto-generated data']
L.append('(define case-bits (list ' + ' '.join(fmt_arr(v) for _, v in cases) + '))')
L.append('(define pool-bits (list ' + ' '.join(fmt_arr(v) for _, v in pool) + '))')
L.append('(define pool-labels (list ' + ' '.join(str(y) for y, _ in pool) + '))')
L.append('(define rule-heads (list ' + ' '.join(str(d) for d, _ in rules) + '))')
def code_body(b):
    out = []
    for p, i in b:
        n = int(i) + 1
        out.append(n if p == 'on' else -n)
    return out
L.append('(define rule-bodies (list ' +
         ' '.join(fmt_arr(code_body(b)) for _, b in rules) + '))')
(ROOT/'src/data.l').write_text('\n'.join(L) + '\n')

# all 218 rules for the Maru proof gate
R = [';;; auto-generated rules (real + same-body decoys)']
R.append('(define rules218 (list')
for d, b in rules:
    atoms = ' '.join(f"(l-atom '{p} (list \"{i}\"))" for p, i in b)
    R.append(f'  (l-rule (l-atom \'digit (list "{d}")) (list {atoms}))')
R.append('))')
(ROOT/'src/rules218.l').write_text('\n'.join(R) + '\n')

# prior log table count 0..5
vals = [int(round(math.log((c + 1) / 15.0) * Q)) for c in range(6)]
(ROOT/'src/prior_table.l').write_text('(define prior-log (list ' + ' '.join(map(str, vals)) + '))\n')

(ROOT/'reference_folds.json').write_text(json.dumps(ref, indent=2) + '\n')
print('TOTAL', sum(r['correct'] for r in ref), '/10')
print('wrote models.l, data.l, rules218.l, prior_table.l, reference_folds.json')
