import torch, torch.nn as nn, random
torch.manual_seed(12); random.seed(12)
# five axiom variable-role patterns for R(h0,h1) :- P(b0,b1), Q(b2,b3)
# pattern: equality indicators h0=b0, h1=b3, b1=b2; correct target pattern 0
PAT=[
 (1,1,1), # correct: R(x,z):-P(x,y),Q(y,z)
 (1,0,1),
 (0,1,1),
 (1,1,0),
 (0,0,0),
]
def sample(n):
 Xf=[];Xs=[];Y=[]
 for _ in range(n):
  order=list(range(5)); random.shuffle(order)
  f=[]; s=[]
  for i in range(5):
   p=PAT[order[i]]
   f.append([0,1,2,2,0,0]) # generic pred/arity features, no binding
   s.append(list(p)+[0,0,0]) # binding slots
  Xf.append(torch.tensor(f,dtype=torch.float)); Xs.append(torch.tensor(s,dtype=torch.float))
  y=[1 if order[i]==0 else 0 for i in range(5)]
  Y.append(torch.tensor(y,dtype=torch.float))
 return Xf,Xs,Y
tr= sample(5000); te=sample(1000)
class SetM(nn.Module):
 def __init__(self,d):
  super().__init__(); self.f=nn.Linear(d,64); self.tr=nn.TransformerEncoder(nn.TransformerEncoderLayer(64,4,128,batch_first=True),2); self.o=nn.Linear(64,1)
 def forward(self,x):
  h=self.tr(self.f(x)); return torch.sigmoid(self.o(h).squeeze(-1))
def run(mode):
 m=SetM(6 if mode=='flat' else 6); opt=torch.optim.Adam(m.parameters(),1e-3); lf=nn.BCELoss()
 TX=torch.stack(tr[0] if mode=='flat' else tr[1]); TY=torch.stack(tr[2]); VX=torch.stack(te[0] if mode=='flat' else te[1]); VY=torch.stack(te[2])
 for ep in range(15):
  for i in range(0,len(TX),64):
   xb=TX[i:i+64]; yb=TY[i:i+64]; opt.zero_grad(); loss=lf(m(xb),yb); loss.backward(); opt.step()
 with torch.no_grad():
  p=(m(VX)>0.5).float(); exact=(p==VY).all(1).float().mean().item(); bits=(p==VY).float().mean().item()
 print(mode,'exact',round(exact,3),'bits',round(bits,3))
run('flat'); run('slot')
