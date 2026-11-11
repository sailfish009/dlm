import torch, torch.nn as nn, random
torch.manual_seed(16); random.seed(16)
N=12
def sample(maxlen,pos):
    while True:
        n=random.randint(2,maxlen); nodes=random.sample(range(N),n)
        edges=list(zip(nodes,nodes[1:]))
        i,j=sorted(random.sample(range(n),2))
        ok=(j-i)>=1
        if pos and ok: x,y=nodes[i],nodes[j]; return edges,x,y,1
        if not pos:
            # choose non-reachable pair: reversed
            x,y=nodes[j],nodes[i]; return edges,x,y,0
train=[sample(4,i%2==0) for i in range(20000)]
test=[sample(8,i%2==0) for i in range(4000)]
class Model(nn.Module):
 def __init__(self,loops):
  super().__init__(); self.emb=nn.Embedding(N,96); self.block=nn.Sequential(nn.Linear(96,192),nn.ReLU(),nn.Linear(192,96)); self.loops=loops; self.out=nn.Sequential(nn.Linear(192,96),nn.ReLU(),nn.Linear(96,2))
 def forward(self,edges,x,y):
  B=len(edges); h=self.emb(torch.arange(N)).unsqueeze(0).repeat(B,1,1); a=torch.eye(N).unsqueeze(0).repeat(B,1,1)
  for b,es in enumerate(edges):
   for u,v in es: a[b,u,v]=1
  a=a/(a.sum(2,keepdim=True).clamp(min=1))
  for _ in range(self.loops): h=h+self.block(torch.bmm(a,h))
  return self.out(torch.cat([h[torch.arange(B),x],h[torch.arange(B),y]],1))
def batch(d): return [z[0] for z in d],torch.tensor([z[1] for z in d]),torch.tensor([z[2] for z in d]),torch.tensor([z[3] for z in d])
def run(loops):
 m=Model(loops); opt=torch.optim.Adam(m.parameters(),1e-3); lf=nn.CrossEntropyLoss()
 for ep in range(18):
  for i in range(0,len(train),64):
   e,x,y,l=batch(train[i:i+64]); opt.zero_grad(); loss=lf(m(e,x,y),l); loss.backward(); opt.step()
 e,x,y,l=batch(test); print('loops',loops,'depth_acc',round((m(e,x,y).argmax(1)==l).float().mean().item(),3))
run(1); run(8)
