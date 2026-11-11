import torch, torch.nn as nn, random
torch.manual_seed(46); random.seed(46)
MAX=12; PAT=[(1,1,1),(1,0,1),(0,1,1),(1,1,0),(0,0,0)] + [(random.randint(0,1),random.randint(0,1),random.randint(0,1)) for _ in range(7)]
def sample(n,allow):
 order=list(range(n)); random.shuffle(order); ci=[i for i in range(n) if order[i] in allow]
 if not ci: return sample(n,allow)
 correct=random.choice(ci); x=[]; y=[]
 for i in range(MAX):
  if i<n:
   p=PAT[order[i]]; x.append(list(p)+[1 if i==correct else 0,0]); y.append(1 if i==correct else 0)
  else: x.append([0]*5); y.append(0)
 return torch.tensor(x,dtype=torch.float),torch.tensor(y,dtype=torch.float)
tr=[sample(random.randint(5,9),{0,1,2,3}) for _ in range(2500)]
te=[sample(12,{4}) for _ in range(500)]
class M(nn.Module):
 def __init__(self): super().__init__(); self.f=nn.Linear(5,64); self.tr=nn.TransformerEncoder(nn.TransformerEncoderLayer(64,4,128,batch_first=True),1); self.o=nn.Linear(64,1)
 def forward(self,x): return torch.sigmoid(self.o(self.tr(self.f(x))).squeeze(-1))
X=torch.stack([a for a,_ in tr]); Y=torch.stack([b for _,b in tr]); TX=torch.stack([a for a,_ in te]); TY=torch.stack([b for _,b in te])
m=M(); opt=torch.optim.Adam(m.parameters(),1e-3); lf=nn.BCELoss()
for ep in range(5):
 for i in range(0,len(X),64):
  xb=X[i:i+64]; yb=Y[i:i+64]; opt.zero_grad(); loss=lf(m(xb),yb); loss.backward(); opt.step()
 with torch.no_grad():
  p=(m(TX)>0.5).float(); print(ep,round((p==TY).all(1).float().mean().item(),3),round((p==TY).float().mean().item(),3))
