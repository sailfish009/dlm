import json, torch, torch.nn as nn
rows=json.load(open('experiments/dt1_bridge/rewards_all.json'))['rows']
reward={frozenset(r['ids']):(1.0 if r['proof']=='proof' else -0.2) for r in rows}
X=torch.tensor([[[1,0,1,0],[0,1,1,1]]],dtype=torch.float); Y=torch.tensor([[1,1]],dtype=torch.float)
class M(nn.Module):
 def __init__(self,loops): super().__init__(); self.f=nn.Linear(4,32); self.b=nn.TransformerEncoderLayer(32,2,64,batch_first=True); self.loops=loops; self.o=nn.Linear(32,1)
 def forward(self,x):
  h=self.f(x)
  for _ in range(self.loops): h=self.b(h)
  return torch.sigmoid(self.o(h).squeeze(-1))
for loops in [1,3]:
 m=M(loops); opt=torch.optim.Adam(m.parameters(),0.05); lf=nn.BCELoss()
 for _ in range(80):
  opt.zero_grad(); loss=lf(m(X),Y); loss.backward(); opt.step()
 with torch.no_grad():
  p=(m(X)>0.5).long().tolist()[0]; ids=[f'A-{i}' for i,v in enumerate(p) if v]
  print('loops',loops,'selected',ids,'reward',reward.get(frozenset(ids),-0.2))
