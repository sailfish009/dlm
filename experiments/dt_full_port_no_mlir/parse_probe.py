from pathlib import Path
import re, json

def parse(path):
    s=Path(path).read_text()
    s=re.sub(r';[^\n]*','',s)
    toks=s.replace('(',' ( ').replace(')',' ) ').split()
    def rd(i):
        t=toks[i]
        if t=='(':
            out=[]; i+=1
            while toks[i]!=')':
                x,i=rd(i); out.append(x)
            return out,i+1
        if t==')': raise ValueError('unexpected )')
        try: return int(t),i+1
        except: return t,i+1
    out=[]; i=0
    while i<len(toks):
        x,i=rd(i); out.append(x)
    return out
for path in ['/research/dlm_v0.0204/experiments/deductive_transformer_maru/src/models.l','/research/dlm_v0.0204/experiments/deductive_transformer_maru/src/data.l']:
    ast=parse(path)
    print(path, 'top', len(ast))
    for e in ast[:2]:
        print(' ', e[0] if isinstance(e,list) else e, type(e))
    # find define models
    for e in ast:
        if isinstance(e,list) and len(e)>=3 and e[1]=='models':
            m=e[2]
            print('models folds',len(m),'tensors',len(m[0]))
            print('tensor lens',[len(x) if isinstance(x,list) else None for x in m[0]])
    for e in ast:
        if isinstance(e,list) and len(e)>=3 and e[1] in ('case-bits','pool-bits','pool-labels','rule-heads','rule-bodies'):
            print(e[1], 'len', len(e[2]), 'firstlen', len(e[2][0]) if e[2] and isinstance(e[2][0],list) else None)
