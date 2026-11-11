import torch, torch.nn as nn, random
torch.manual_seed(17); random.seed(17)
def sample():
    order=list(range(5)); random.shuffle(order)
    x=[[1 if order[i]==0 else 0,1 if order[i]==1 else 0,1 if order[i] in (1,4) else 0,1 if order[i] in (2,3,4) else 0,0] for i in range(5)]
    y=[1 if order[i] in (0,1) else 0 for i in range(5)]
    return torch.tensor(x,dtype=torch.float),torch.tensor(y,dtype=torch.float)
tr=[sample() for _ in range(5000)]; te=[sample() for _ in range(1000)]
X=torch.stack([x for x,_ in tr]); Y=torch.stack([y for _,y in tr]); TX=torch.stack([x for x,_ in te]); TY=torch.stack([y for _,y in te])
class M(nn.Module):
 def __init__(self): super().__init__(); self.f=nn.Linear(5,64); self.tr=nn.TransformerEncoder(nn.TransformerEncoderLayer(64,4,128,batch_first=True),2); self.o=nn.Linear(64,1)
 def forward(self,x): return self.o(self.tr(self.f(x))).squeeze(-1)
m=M(); opt=torch.optim.Adam(m.parameters(),1e-3); base=0.0
for ep in range(20):
 for i in range(0,len(X),64):
  xb=X[i:i+64]; yb=Y[i:i+64]; logits=m(xb); dist=torch.distributions.Bernoulli(logits=logits); s=dist.sample(); logp=dist.log_prob(s).sum(1)
  exact=(s==yb).all(1).float(); cov=(s*yb).sum(1); r=3*exact+cov-0.5*s.sum(1)
  loss=-(logp*(r-base)).mean(); opt.zero_grad(); loss.backward(); opt.step(); base=0.95*base+0.05*r.mean().item()
 with torch.no_grad():
  p=(m(TX)>0).float(); exact=(p==TY).all(1).float().mean().item(); bits=(p==TY).float().mean().item()
 print(ep,round(exact,3),round(bits,3),round(base,3))
