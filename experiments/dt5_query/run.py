#!/usr/bin/env python3
"""E29: query-conditioned set transformer over the five-axiom actual verifier.

Two queries share one axiom pool but have different proof-minimal subsets:
  dog/living-thing     -> A-0,A-1,A-2
  sparrow/living-thing -> A-2,A-3
"""
import json
from pathlib import Path
import torch, torch.nn as nn

data = json.loads(Path('experiments/dt3_pool5/rewards_multi.json').read_text())
ids = ['A-0', 'A-1', 'A-2', 'A-3', 'A-4']
target = {'dog': ['A-0','A-1','A-2'], 'sparrow': ['A-2','A-3']}
reward = {}
for q, t in data.items():
    reward[q] = {tuple(r['ids']): (1.0 if r['proof'] == 'proof' else -0.2) for r in t['rows']}

sem = {
 'A-0': [1,1,0,1,0,0,0,0,0],
 'A-1': [1,0,1,0,0,0,0,1/3,1],
 'A-2': [1,0,1,0,0,0,0,2/3,1],
 'A-3': [1,1,0,0,1,0,0,0,0],
 'A-4': [1,1,0,0,0,1,0,0,0],
}
qvec = {'dog': [1,0,0], 'sparrow': [0,1,0], 'blind': [0,0,0]}

class QSet(nn.Module):
    def __init__(self, dim, loops=1):
        super().__init__(); self.inp = nn.Linear(dim, 32)
        self.block = nn.TransformerEncoderLayer(32, 2, 64, batch_first=True)
        self.out = nn.Linear(32, 1); self.loops = loops
    def forward(self, x):
        h = self.inp(x)
        for _ in range(self.loops): h = self.block(h)
        return self.out(h).squeeze(-1)

def features(query):
    q = qvec[query]
    return [sem[i] + q for i in ids]

def train(use_query, loops=1, seed=0, epochs=500):
    torch.manual_seed(seed)
    m = QSet(12, loops); opt = torch.optim.Adam(m.parameters(), lr=0.02)
    lf = nn.BCEWithLogitsLoss()
    xs, ys = [], []
    for q in ('dog','sparrow'):
        xs.append(features(q) if use_query else features('blind'))
        ys.append([1 if i in target[q] else 0 for i in ids])
    X = torch.tensor(xs, dtype=torch.float); Y = torch.tensor(ys, dtype=torch.float)
    for _ in range(epochs):
        opt.zero_grad(); loss = lf(m(X), Y); loss.backward(); opt.step()
    return m

def infer(m, use_query, q):
    with torch.no_grad():
        x = torch.tensor([features(q) if use_query else features('blind')], dtype=torch.float)
        mask = (m(x)[0] > 0).long().tolist()
    return [ids[i] for i, v in enumerate(mask) if v]

for use_query in (True, False):
    for loops in (1, 3):
        m = train(use_query, loops=loops)
        tag = 'query' if use_query else 'blind'
        for q in ('dog','sparrow'):
            sel = infer(m, use_query, q)
            print(tag, 'loops', loops, q, 'selected', sel,
                  'exact', sel == target[q], 'reward', reward[q].get(tuple(sel), -0.2))
