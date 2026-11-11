import json, random, torch, torch.nn as nn
from pathlib import Path
rows=json.load(open('experiments/dt1_bridge/rewards_all.json'))['rows']
reward={frozenset(r['ids']):(1.0 if r['proof']=='proof' else -0.2) for r in rows}
class M(nn.Module):
 def __init__(self): super().__init__(); self.logit=nn.Parameter(torch.zeros(2))
 def forward(self): return self.logit
m=M(); opt=torch.optim.Adam(m.parameters(),0.1); base=0
for step in range(100):
 logits=m(); d=torch.distributions.Bernoulli(logits=logits); s=d.sample(); key=frozenset([f'A-{i}' for i,v in enumerate(s.tolist()) if v]); r=reward.get(key,-0.2)
 loss=-(d.log_prob(s).sum()*(r-base)); opt.zero_grad(); loss.backward(); opt.step(); base=.9*base+.1*r
with torch.no_grad():
 p=(m()>0).long().tolist(); key=frozenset([f'A-{i}' for i,v in enumerate(p) if v])
print('selected',sorted(key),'proof_reward',reward.get(key,-0.2),'params',[round(x,2) for x in m().tolist()])
