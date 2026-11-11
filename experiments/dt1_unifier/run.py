import torch, torch.nn as nn, random
torch.manual_seed(42); random.seed(42)
PAT=[(1,1,1),(1,0,1),(0,1,1),(1,1,0),(0,0,0)]
def sample(allow):
    order=list(range(5)); random.shuffle(order)
    ci=[i for i in range(5) if order[i] in allow]
    correct=random.choice(ci); x=[]; y=[]
    for i in range(5):
        p=PAT[order[i]]
        x.append(list(p)+[1 if i==correct else 0]); y.append(1 if i==correct else 0)
    return torch.tensor(x,dtype=torch.float),torch.tensor(y,dtype=torch.float)
tr=[sample({0,1,2,3}) for _ in range(1500)]
te=[sample({4}) for _ in range(300)]
class M(nn.Module):
 def __init__(self): super().__init__(); self.f=nn.Linear(4,48); self.tr=nn.TransformerEncoder(nn.TransformerEncoderLayer(48,4,96,batch_first=True),1); self.o=nn.Linear(48,1)
 def forward(self,x): return torch.sigmoid(self.o(self.tr(self.f(x))).squeeze(-1))
X=torch.stack([a for a,_ in tr]); Y=torch.stack([b for _,b in tr]); TX=torch.stack([a for a,_ in te]); TY=torch.stack([b for _,b in te])
m=M(); opt=torch.optim.Adam(m.parameters(),1e-3); lf=nn.BCELoss()
for ep in range(3):
 for i in range(0,len(X),64):
  xb=X[i:i+64]; yb=Y[i:i+64]; opt.zero_grad(); loss=lf(m(xb),yb); loss.backward(); opt.step()
 with torch.no_grad():
  p=(m(TX)>0.5).float(); print(ep,round((p==TY).all(1).float().mean().item(),3),round((p==TY).float().mean().item(),3))
