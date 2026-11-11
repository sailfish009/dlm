import torch, torch.nn as nn, random
torch.manual_seed(13); random.seed(13)
N=12
def sample(maxlen,pos):
    while True:
        n=random.randint(2,maxlen); nodes=random.sample(range(N),n)
        edges=list(zip(nodes,nodes[1:]))
        if pos: x,y=nodes[0],nodes[-1]
        else:
            x,y=random.sample(nodes,2)
            if nodes.index(x)<nodes.index(y): continue
        return edges,x,y,int(pos)
train=[sample(4,i%2==0) for i in range(12000)]
test=[sample(8,i%2==0) for i in range(3000)]
class Block(nn.Module):
 def __init__(self): super().__init__(); self.f=nn.Sequential(nn.Linear(64,128),nn.ReLU(),nn.Linear(128,64))
 def forward(self,h,a): return h + self.f(torch.bmm(a,h))
class Model(nn.Module):
 def __init__(self,loops):
  super().__init__(); self.emb=nn.Embedding(N,64); self.block=Block(); self.loops=loops; self.q=nn.Embedding(3,64); self.out=nn.Sequential(nn.Linear(128,64),nn.ReLU(),nn.Linear(64,2))
 def forward(self,edges,x,y):
  B=len(edges); h=self.emb(torch.arange(N)).unsqueeze(0).repeat(B,1,1)
  qm=self.q(torch.zeros(N,dtype=torch.long)).unsqueeze(0).repeat(B,1,1)
  for b in range(B): qm[b,x[b]]=self.q(torch.tensor(1)); qm[b,y[b]]=self.q(torch.tensor(2))
  h=h+qm
  a=torch.eye(N).unsqueeze(0).repeat(B,1,1)
  for b,es in enumerate(edges):
   for u,v in es: a[b,u,v]=1
  a=a/(a.sum(2,keepdim=True).clamp(min=1))
  for _ in range(self.loops): h=self.block(h,a)
  return self.out(torch.cat([h[torch.arange(B),x],h[torch.arange(B),y]],1))
def batch(d):
 return [z[0] for z in d],torch.tensor([z[1] for z in d]),torch.tensor([z[2] for z in d]),torch.tensor([z[3] for z in d])
def run(loops):
 m=Model(loops); opt=torch.optim.Adam(m.parameters(),1e-3); lf=nn.CrossEntropyLoss()
 for ep in range(12):
  for i in range(0,len(train),64):
   e,x,y,l=batch(train[i:i+64]); opt.zero_grad(); loss=lf(m(e,x,y),l); loss.backward(); opt.step()
 e,x,y,l=batch(test); acc=(m(e,x,y).argmax(1)==l).float().mean().item()
 print('loops',loops,'depth_acc',round(acc,3))
run(1); run(6)
