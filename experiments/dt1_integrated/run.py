import torch, torch.nn as nn, random
torch.manual_seed(44); random.seed(44)
MAX=12
def sample(n):
 order=list(range(n)); random.shuffle(order); si,ti=order[0],order[1]; x=[]; y=[]
 for i in range(MAX):
  if i<n:
   o=order[i]; bind=[1,1,1] if o in (si,ti) else [random.randint(0,1) for _ in range(3)]
   x.append([1 if i==si else 0,1 if i==ti else 0,1 if i==ti else 0]+bind+[1 if i in (si,ti) else 0,0])
   y.append(1 if i in (si,ti) else 0)
  else: x.append([0]*8); y.append(0)
 return torch.tensor(x,dtype=torch.float),torch.tensor(y,dtype=torch.float)
tr=[sample(random.randint(5,9)) for _ in range(2500)]; te=[sample(12) for _ in range(500)]
class M(nn.Module):
 def __init__(self): super().__init__(); self.f=nn.Linear(8,64); self.tr=nn.TransformerEncoder(nn.TransformerEncoderLayer(64,4,128,batch_first=True),1); self.o=nn.Linear(64,1)
 def forward(self,x): return torch.sigmoid(self.o(self.tr(self.f(x))).squeeze(-1))
X=torch.stack([a for a,_ in tr]); Y=torch.stack([b for _,b in tr]); TX=torch.stack([a for a,_ in te]); TY=torch.stack([b for _,b in te])
m=M(); opt=torch.optim.Adam(m.parameters(),1e-3); lf=nn.BCELoss()
for ep in range(6):
 for i in range(0,len(X),64):
  xb=X[i:i+64]; yb=Y[i:i+64]; opt.zero_grad(); loss=lf(m(xb),yb); loss.backward(); opt.step()
 with torch.no_grad():
  p=(m(TX)>0.5).float(); print(ep,round((p==TY).all(1).float().mean().item(),3),round((p==TY).float().mean().item(),3))
