import torch, torch.nn as nn, random
torch.manual_seed(39); random.seed(39)
MAX=12
def sample(n,depth):
    order=list(range(n)); random.shuffle(order); seed_i,step_i=order[0],order[1]
    x=[]; y=[]
    for i in range(MAX):
        if i<n:
            orig=order[i]
            bind=[1,1,1] if orig in (seed_i,step_i) else [random.randint(0,1),random.randint(0,1),random.randint(0,1)]
            x.append([1 if i==seed_i else 0,1 if i==step_i else 0,1 if i==step_i else 0]+bind+[depth/8.0,0])
            y.append(1 if i in (seed_i,step_i) else 0)
        else:
            x.append([0,0,0,0,0,0,0,1]); y.append(0)
    return torch.tensor(x,dtype=torch.float),torch.tensor(y,dtype=torch.float)
tr=[sample(random.randint(5,9),random.randint(2,4)) for _ in range(8000)]
te=[sample(12,8) for _ in range(1000)]
class M(nn.Module):
 def __init__(self,loops): super().__init__(); self.f=nn.Linear(8,64); self.block=nn.TransformerEncoderLayer(64,4,128,batch_first=True); self.loops=loops; self.o=nn.Linear(64,1)
 def forward(self,x):
  h=self.f(x)
  for _ in range(self.loops): h=self.block(h)
  return torch.sigmoid(self.o(h).squeeze(-1))
X=torch.stack([a for a,_ in tr]); Y=torch.stack([b for _,b in tr]); TX=torch.stack([a for a,_ in te]); TY=torch.stack([b for _,b in te])
for loops in [1,3]:
 m=M(loops); opt=torch.optim.Adam(m.parameters(),1e-3); lf=nn.BCELoss()
 for ep in range(8):
  for i in range(0,len(X),64):
   xb=X[i:i+64]; yb=Y[i:i+64]; opt.zero_grad(); loss=lf(m(xb),yb); loss.backward(); opt.step()
 with torch.no_grad():
  p=(m(TX)>0.5).float(); print('loops',loops,'pool12_depth8_exact',round((p==TY).all(1).float().mean().item(),3))
