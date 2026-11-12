from parse_probe import parse
import re
from pathlib import Path

def strip(x):
    if isinstance(x,list) and x and x[0]=='list':
        return [strip(y) for y in x[1:]]
    return x

def getdefs(path):
    ast=parse(path)
    out={}
    for e in ast:
        if isinstance(e,list) and len(e)>=3 and e[0]=='define':
            out[e[1]]=strip(e[2])
    return out
if __name__=='__main__':
    m=getdefs('/research/dlm_v0.0204/experiments/deductive_transformer_maru/src/models.l')
    d=getdefs('/research/dlm_v0.0204/experiments/deductive_transformer_maru/src/data.l')
    print('model folds',len(m['models']))
    for i,t in enumerate(m['models'][0]):
        # tensor may be flat list or matrix list
        print(i, type(t).__name__, len(t) if isinstance(t,list) else t, (len(t[0]) if isinstance(t,list) and t and isinstance(t[0],list) else ''))
    for k in ['case-bits','pool-bits','pool-labels','rule-heads','rule-bodies']:
        print(k,len(d[k]), d[k][0] if k!='case-bits' else len(d[k][0]))
