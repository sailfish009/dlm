import torch, torch.nn as nn, random
torch.manual_seed(24); random.seed(24)
MAX=12
# features: seed, step, dep, binding pattern 3 bits, decoy, pad
def sample(n):
    order=list(range(n)); random.shuffle(order); seed_i,step_i=order[0],order[1]
    x=[]; y=[]
    for i in range(MAX):
        if i<n:
            orig=order[i]
            bind=[1,1,1] if orig in (seed_i,step_i) else [random.randint(0,1),random.randint(0,1),random.randint(0,1)]
            x.append([1 if i==seed_i else 0,1 if i==step_i else 0,1 if i==step_i else 0]+bind+[1 if i not in (seed_i,step_i) else 0,0])
            y.append(1 if i in (seed_i,step_i) else 0)
        else:
            x.append([0,0,0,0,0,0,0,1]); y.append(0)
    return torch.tensor(x,dtype=torch.float),torch.tensor(y,dtype=torch.float)
tr=[sample(random.randint(5,9)) for _ in range(8000)]
te=[sample(11) for _ in range(1000)]; te2=[sample(12) for _ in range(1000)]
class M(nn.Module):
 def __init__(self): super().__init__(); self.f=nn.Linear(8,64); self.tr=nn.TransformerEncoder(nn.TransformerEncoderLayer(64,4,128,batch_first=True),2); self.o=nn.Linear(64,1)
 def forward(self,x): return torch.sigmoid(self.o(self.tr(self.f(x))).squeeze(-1))
X=torch.stack([a for a,_ in tr]); Y=torch.stack([b for _,b in tr]); TX=torch.stack([a for a,_ in te]); TY=torch.stack([b for _,b in te]); T2=torch.stack([a for a,_ in te2]); Y2=torch.stack([b for _,b in te2])
m=M(); opt=torch.optim.Adam(m.parameters(),1e-3); lf=nn.BCELoss()
for ep in range(12):
 for i in range(0,len(X),64):
  xb=X[i:i+64]; yb=Y[i:i+64]; opt.zero_grad(); loss=lf(m(xb),yb); loss.backward(); opt.step()
 with torch.no_grad():
  p=(m(TX)>0.5).float(); e1=(p==TY).all(1).float().mean().item()
  p2=(m(T2)>0.5).float(); e2=(p2==Y2).all(1).float().mean().item()
 print(ep,round(e1,3),round(e2,3))
