import torch, torch.nn as nn, random
torch.manual_seed(55); random.seed(55)
PAT=[(1,1,1),(1,0,1),(0,1,1),(1,1,0),(0,0,0)]
def sample(allow):
 order=list(range(5)); random.shuffle(order)
 ci=[i for i in range(5) if order[i] in allow]
 correct=random.choice(ci); x=[]; y=[]; deps=[]
 for i in range(5):
  p=PAT[order[i]]; x.append(list(p)+[1 if i==correct else 0,0]); y.append(1 if i==correct else 0); deps.append([])
 return torch.tensor(x,dtype=torch.float),torch.tensor(y,dtype=torch.float)
tr=[sample({0,1,2,3}) for _ in range(3000)]; te=[sample({4}) for _ in range(500)]
X=torch.stack([a for a,_ in tr]); Y=torch.stack([b for _,b in tr]); TX=torch.stack([a for a,_ in te]); TY=torch.stack([b for _,b in te])
class M(nn.Module):
 def __init__(self): super().__init__(); self.f=nn.Linear(5,64); self.tr=nn.TransformerEncoder(nn.TransformerEncoderLayer(64,4,128,batch_first=True),1); self.o=nn.Linear(64,1)
 def forward(self,x): return self.o(self.tr(self.f(x))).squeeze(-1)
m=M(); opt=torch.optim.Adam(m.parameters(),1e-3); base=0.0
for ep in range(15):
 for i in range(0,len(X),64):
  xb=X[i:i+64]; yb=Y[i:i+64]; logits=m(xb); dist=torch.distributions.Bernoulli(logits=logits); s=dist.sample(); lp=dist.log_prob(s).sum(1)
  exact=(s==yb).all(1).float(); cov=(s*yb).sum(1); decoy=(s*(1-yb)).sum(1); r=3*exact+cov-0.5*s.sum(1)-2*decoy
  loss=-(lp*(r-base)).mean(); opt.zero_grad(); loss.backward(); opt.step(); base=0.95*base+0.05*r.mean().item()
 with torch.no_grad():
  p=(m(TX)>0).float(); print(ep,round((p==TY).all(1).float().mean().item(),3),round((p==TY).float().mean().item(),3))
