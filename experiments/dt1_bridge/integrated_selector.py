import json, torch, torch.nn as nn
from pathlib import Path
rows=json.load(open('experiments/dt1_bridge_batch/../dt1_bridge/rewards_all.json'))['rows']
reward={frozenset(r['ids']):(1.0 if r['proof']=='proof' else -0.2) for r in rows}
# two axiom descriptors: seed, step, canonical-unifier, dependency
X=torch.tensor([[[1,0,1,0],[0,1,1,1]]],dtype=torch.float)
Y=torch.tensor([[1,1]],dtype=torch.float)
class M(nn.Module):
 def __init__(self): super().__init__(); self.f=nn.Linear(4,32); self.o=nn.Linear(32,1)
 def forward(self,x): return torch.sigmoid(self.o(torch.relu(self.f(x))).squeeze(-1))
m=M(); opt=torch.optim.Adam(m.parameters(),0.05); lf=nn.BCELoss()
for _ in range(80):
 opt.zero_grad(); loss=lf(m(X),Y); loss.backward(); opt.step()
with torch.no_grad():
 p=(m(X)>0.5).long().tolist()[0]
ids=[f'A-{i}' for i,v in enumerate(p) if v]
print('selected',ids,'reward',reward.get(frozenset(ids),-0.2))
