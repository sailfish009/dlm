#!/usr/bin/env python3
"""E28: set transformer selects a proof-checked 5-axiom subset.

The reward/label comes from the actual Maru p-prove table produced by E27.
Compare semantic axiom descriptors against raw positional descriptors.
"""
import json, random
from pathlib import Path
import torch, torch.nn as nn

T = Path('experiments/dt3_pool5/rewards_pool5.json')
data = json.loads(T.read_text())
rows = data['rows']
reward = {tuple(r['ids']): (1.0 if r['proof'] == 'proof' else -0.2) for r in rows}
target = tuple(data['minimal_proof']['ids'])
ids = ['A-0', 'A-1', 'A-2', 'A-3', 'A-4']

# Semantic, order-independent descriptors.
sem = {
 'A-0': [1,1,0,1,0,0,0,0,0],   # head isa, body subclass, mammal, depth 0, dep 0
 'A-1': [1,0,1,0,0,0,0,1/3,1], # body isa, depth 1, dep 1
 'A-2': [1,0,1,0,0,0,0,2/3,1], # body isa, depth 2, dep 1
 'A-3': [1,1,0,0,1,0,0,0,0],   # body subclass,bird
 'A-4': [1,1,0,0,0,1,0,0,0],   # body subclass,cat
}
raw = [[1 if i == j else 0 for j in range(5)] for i in range(5)]

class SetTransformer(nn.Module):
    def __init__(self, dim, loops=1):
        super().__init__()
        self.inp = nn.Linear(dim, 32)
        self.block = nn.TransformerEncoderLayer(32, 2, 64, batch_first=True)
        self.out = nn.Linear(32, 1)
        self.loops = loops
    def forward(self, x):
        h = self.inp(x)
        for _ in range(self.loops):
            h = self.block(h)
        return self.out(h).squeeze(-1)

def train(feats, labels, loops=1, seed=0, epochs=300):
    torch.manual_seed(seed)
    m = SetTransformer(len(feats[0]), loops)
    opt = torch.optim.Adam(m.parameters(), lr=0.02)
    x = torch.tensor([feats], dtype=torch.float)
    y = torch.tensor([labels], dtype=torch.float)
    lf = nn.BCEWithLogitsLoss()
    for _ in range(epochs):
        opt.zero_grad(); loss = lf(m(x), y); loss.backward(); opt.step()
    return m

def infer(m, feats):
    with torch.no_grad():
        x = torch.tensor([feats], dtype=torch.float)
        return (m(x)[0] > 0).long().tolist()

def selected_ids(mask, order): return [order[i] for i, v in enumerate(mask) if v]

# Original pool.
y = [1 if i in target else 0 for i in ids]
models = {}
for name, feats in [('semantic', [sem[i] for i in ids]), ('rawpos', raw)]:
    for loops in (1, 3):
        model = train(feats, y, loops=loops)
        models[name] = (loops, model)
        sel = selected_ids(infer(model, feats), ids)
        print(name, 'loops', loops, 'selected', sel,
              'exact', tuple(sel) == target,
              'reward', reward.get(tuple(sel), -0.2))

# Unseen permutation: same axioms, reordered. Semantic model must track the
# descriptors; raw positional model keeps positions 0..2.
order = ['A-3', 'A-0', 'A-4', 'A-1', 'A-2']
perm_target = tuple(x for x in order if x in target)
perm_sem = [sem[i] for i in order]
perm_raw = [[1 if i == j else 0 for j in range(5)] for i in range(5)]
perm_y = [1 if i in perm_target else 0 for i in order]
for name, feats in [('semantic', perm_sem), ('rawpos', perm_raw)]:
    # zero-shot: reuse the model trained on the original pool, no retraining
    model = train(perm_sem if name == 'semantic' else perm_raw, perm_y, loops=1) if False else None
    # models dict from the original loop
    model = models[name][1]
    sel = selected_ids(infer(model, feats), order)
    print('PERMUTED', name, 'selected', sel,
          'exact', tuple(sel) == perm_target)
