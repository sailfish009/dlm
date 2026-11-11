import torch, torch.nn as nn, random
torch.manual_seed(11); random.seed(11)
# 5 axioms: features [head_pred, body1_pred, body2_pred, recursive, seed]
# predicates: 0=R,1=P,2=Q
AX=[
 [0,1,-1,0,1], # R:-P (seed)
 [0,1,0,1,0],  # R:-P,R (step)
 [0,2,-1,0,1], # R:-Q
 [0,1,2,0,0],  # R:-P,Q
 [0,2,0,1,0],  # R:-Q,R
]
def perm():
    idx=list(range(5)); random.shuffle(idx)
    return idx
def feat(i,idx):
    f=AX[idx[i]][:]
    # structural extras: body count, head/body relation
    f += [1 if f[2]>=0 else 0, 1 if f[2]==0 else 0]
    return f
def make(n):
    X=[];Y=[]
    for _ in range(n):
        idx=perm(); f=[]
        for i in range(5): f.append(feat(i,idx))
        # observation: P chain length 3, positives R(a,c), neg R(c,a)
        obs=[1,1,1,0,3,1,0]  # P exists, chain, len, pos, neg
        X.append((torch.tensor(f,dtype=torch.float),torch.tensor(obs,dtype=torch.float)))
        y=[1 if idx[i] in (0,1) else 0 for i in range(5)]
        Y.append(torch.tensor(y,dtype=torch.float))
    return X,Y
class SetSel(nn.Module):
 def __init__(self):
  super().__init__(); self.af=nn.Linear(7,64); self.of=nn.Linear(7,64); self.tr=nn.TransformerEncoder(nn.TransformerEncoderLayer(64,4,128,batch_first=True),2); self.out=nn.Linear(64,1)
 def forward(self,ax,obs):
  B=ax.shape[0]; tok=self.af(ax); q=self.of(obs).unsqueeze(1); h=torch.cat([q,tok],1); h=self.tr(h); return torch.sigmoid(self.out(h[:,1:]).squeeze(-1))
trX,trY=make(5000); teX,teY=make(1000)
def stack(X):
 return torch.stack([x[0] for x in X]), torch.stack([x[1] for x in X])
m=SetSel(); opt=torch.optim.Adam(m.parameters(),1e-3); lf=nn.BCELoss()
TX,TO=stack(trX); VX,VO=stack(teX); TY=torch.stack(trY); VY=torch.stack(teY)
for ep in range(15):
 for i in range(0,len(TX),64):
  xb=TX[i:i+64]; ob=TO[i:i+64]; yb=TY[i:i+64]; opt.zero_grad(); loss=lf(m(xb,ob),yb); loss.backward(); opt.step()
 with torch.no_grad():
  p=(m(VX,VO)>0.5).float(); exact=(p==VY).all(1).float().mean().item(); bit=(p==VY).float().mean().item()
 print(ep,round(exact,3),round(bit,3))
