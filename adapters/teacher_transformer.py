#!/usr/bin/env python3
"""Train a tiny CPU transformer on two-hop behavior, then emit DLM observations."""
import itertools, random
from pathlib import Path
import torch, torch.nn as nn

torch.manual_seed(4); random.seed(4)
N=6; V=N+3; PAD=0; SEP=N+1; CLS=N+2; L=8

def sample(pos):
    while True:
        a,b,c,d=[random.randrange(N) for _ in range(4)]
        if pos:
            x,y=a,d
            if b==c: break
        else:
            x,y=random.randrange(N),random.randrange(N)
            if not (b==c and x==a and y==d): break
    return [CLS,x,y,SEP,a,b,c,d], int(pos)

class M(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb=nn.Embedding(V,64,padding_idx=0)
        self.pos=nn.Embedding(L,64)
        self.tr=nn.TransformerEncoder(nn.TransformerEncoderLayer(64,4,128,batch_first=True),2)
        self.fc=nn.Linear(64,2)
    def forward(self,x):
        h=self.tr(self.emb(x)+self.pos(torch.arange(x.shape[1]).unsqueeze(0)))
        return self.fc(h[:,0])

D=[sample(i%2==0) for i in range(24000)]
X=torch.tensor([d[0] for d in D]); Y=torch.tensor([d[1] for d in D])
m=M(); opt=torch.optim.Adam(m.parameters(),1e-3); lf=nn.CrossEntropyLoss()
for ep in range(12):
    for i in range(0,len(X),64):
        xb=X[i:i+64]; yb=Y[i:i+64]
        opt.zero_grad(); loss=lf(m(xb),yb); loss.backward(); opt.step()
acc=((m(X).argmax(1)==Y).float().mean().item())
print(f"teacher_train_acc={acc:.4f}")

def pred(a,b,c,d,x,y):
    toks=torch.tensor([[CLS,x,y,SEP,a,b,c,d]])
    with torch.no_grad(): return int(m(toks).argmax(1).item())

chains=[('a','b','c'),('d','e','f'),('g','h','i')]
held=[('j','k','l'),('m','n','o')]
# map constants to first 6 ids for teacher input; use chain pattern ids 0,1,2
# Use distinct ids only for tokenization; behavior is shape-based.
def ids(ch): return (0,1,2)
rows=[]
for idx,ch in enumerate(chains):
    a,b,c=ids(ch)
    rows.append((ch, pred(a,b,b,c,a,c), pred(a,b,b,c,c,a)))
# facts for train + held
facts=[]
for i,ch in enumerate(chains+held):
    facts += [f'(l-fact "e{i}a" (l-atom \'edge1 (list \'{ch[0]} \'{ch[1]})))',
              f'(l-fact "e{i}b" (l-atom \'edge2 (list \'{ch[1]} \'{ch[2]})))']
pos=[f"(l-atom 'path (list '{ch[0]} '{ch[2]}))" for ch,t,_ in rows if t==1]
neg=[f"(l-atom 'path (list '{ch[2]} '{ch[0]}))" for ch,_,f in rows if f==0]
out=Path(__file__).resolve().parents[1]/"experiments/teacher_transformer_repl/teacher_data.l"
out.write_text("\n".join([
 "(define *teacher-facts*", "  (list", "    "+"\n    ".join(facts), "  ))",
 "(define *teacher-pos*", "  (list", "    "+"\n    ".join(pos), "  ))",
 "(define *teacher-neg*", "  (list", "    "+"\n    ".join(neg), "  ))",
 "(define *held-pos*", "  (list", "    (l-atom 'path (list 'j 'l))", "    (l-atom 'path (list 'm 'o))", "  ))",
 "(define *held-neg*", "  (list", "    (l-atom 'path (list 'l 'j))", "    (l-atom 'path (list 'o 'm))", "  ))",
 ""
]), encoding="utf-8")
print(f"wrote {out} train_pos={len(pos)} train_neg={len(neg)}")
