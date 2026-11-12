#!/usr/bin/env python3
"""Configurable DT-1 training/inference variant lab.
Generates a variant-specific C trainer from the fixed v0.0218 baseline.
Supported structural config: D, F, layers, heads, epochs, lr, posw,
prior/weight decay/dropout/scheduler. No MLIR, no PyTorch training.
"""
from __future__ import annotations
import json, subprocess, sys, shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / 'dt_full_port_no_mlir'
HERE = Path(__file__).resolve().parent
TEMPLATE = (BASE/'dt_train_c.c').read_text()
REF = json.loads((BASE/'expected_all.json').read_text())
REF_PICKS = [x['pick'] for x in REF]

def layout(d:int, f:int):
    sizes = [
        ('IMG_W', d*196), ('IMG_B', d), ('RULE_W', d*16), ('RULE_B', d),
        ('IN_W', 3*d*d), ('IN_B', 3*d), ('OUT_W', d*d), ('OUT_B', d),
        ('L1_W', f*d), ('L1_B', f), ('L2_W', d*f), ('L2_B', d),
        ('N1G', d), ('N1B', d), ('N2G', d), ('N2B', d), ('FW', d), ('FB', 1),
    ]
    off = 0; lines = ['#ifndef VARIANT_LAYOUT_H', '#define VARIANT_LAYOUT_H']
    for name, size in sizes:
        lines.append(f'#define {name} {off}')
        off += size
    lines += [f'#define V_PSIZE {off}', '#endif', '']
    return '\n'.join(lines)

def make_source(cfg):
    d=int(cfg.get('D',32)); f=int(cfg.get('F',64)); layers=int(cfg.get('layers',6))
    heads=int(cfg.get('heads',1))
    if heads < 1 or heads > 8 or d % heads != 0:
        raise SystemExit('heads must divide D and be <= 8')
    prior=float(cfg.get('prior_weight',4.0))
    s=TEMPLATE
    s=s.replace('#define D 32', f'#define D {d}')
    s=s.replace('#define H 1', f'#define H {heads}')
    s=s.replace('static int fold_seed = 61;', f'static int fold_seed = {int(cfg.get("seed",61))};')
    s=s.replace('#define F 64', f'#define F {f}')
    s=s.replace('#define NLAYER 6', f'#define NLAYER {layers}')
    s=s.replace('#define NEPOCH 50', f'#define NEPOCH {int(cfg.get("epochs",50))}')
    s=s.replace('#define LR 0.001', f'#define LR {float(cfg.get("lr",0.001))}')
    s=s.replace('#define WD 0.0', f'#define WD {float(cfg.get("weight_decay",0.0))}')
    s=s.replace('#define DROP 0.0', f'#define DROP {float(cfg.get("dropout",0.0))}')
    s=s.replace('#define SCHED 0', f'#define SCHED {int(cfg.get("scheduler",0))}')
    s=s.replace('#define SCHED_STEPS 450', f'#define SCHED_STEPS {int(cfg.get("epochs",50))*10}')
    s=s.replace('#define POSW 30.0', f'#define POSW {float(cfg.get("posw",30.0))}')
    s=s.replace('#define PSIZE 15425', '#define PSIZE V_PSIZE')
    s=s.replace('4.0*(prior_log', f'{prior}*(prior_log')
    s=s.replace('#include "fixture_all.h"', '#include "fixture_all.h"\n#include "variant_layout.h"')
    # remove fixed enum
    import re
    s=re.sub(r'/\* offsets must match fixture_all\.h \*/\nenum \{.*?\};\n', '', s, flags=re.S)
    # init sizes
    reps = {
      'for(int i=0;i<32*196;i++)': 'for(int i=0;i<D*196;i++)',
      'for(int r=0;r<32;r++)P[IMG_B+r]=0;': 'for(int r=0;r<D;r++)P[IMG_B+r]=0;',
      'for(int i=0;i<32*16;i++)': 'for(int i=0;i<D*16;i++)',
      'for(int r=0;r<32;r++)P[RULE_B+r]=0;': 'for(int r=0;r<D;r++)P[RULE_B+r]=0;',
      'for(int i=0;i<96*32;i++)': 'for(int i=0;i<3*D*D;i++)',
      'for(int i=0;i<96;i++)': 'for(int i=0;i<3*D;i++)',
      'for(int i=0;i<32*32;i++)': 'for(int i=0;i<D*D;i++)',
      'for(int i=0;i<32;i++)P[OUT_B+i]=0;': 'for(int i=0;i<D;i++)P[OUT_B+i]=0;',
      'for(int i=0;i<64*32;i++)': 'for(int i=0;i<F*D;i++)',
      'for(int i=0;i<64;i++)P[L1_B+i]=0;': 'for(int i=0;i<F;i++)P[L1_B+i]=0;',
      'for(int i=0;i<32*F;i++)': 'for(int i=0;i<D*F;i++)',
      'for(int i=0;i<32;i++)P[L2_B+i]=0;': 'for(int i=0;i<D;i++)P[L2_B+i]=0;',
      'for(int i=0;i<32;i++){P[N1G+i]=1;P[N1B+i]=0;P[N2G+i]=1;P[N2B+i]=0;}': 'for(int i=0;i<D;i++){P[N1G+i]=1;P[N1B+i]=0;P[N2G+i]=1;P[N2B+i]=0;}',
      'for(int i=0;i<32;i++)P[FW+i]=(urand()*2-1)/sqrt(32.0);': 'for(int i=0;i<D;i++)P[FW+i]=(urand()*2-1)/sqrt((double)D);',
      'mvd(P+L1_W,64,D,c->x1[t],P+L1_B,': 'mvd(P+L1_W,F,D,c->x1[t],P+L1_B,',
    }
    for a,b in reps.items():
        if a not in s: raise SystemExit(f'template pattern missing: {a}')
        s=s.replace(a,b)
    s=s.replace('sqrt(32.0)', 'sqrt((double)D)')
    s=s.replace('G[IN_B+32+r]', 'G[IN_B+D+r]')
    s=s.replace('G[IN_B+64+r]', 'G[IN_B+2*D+r]')
    s=s.replace('G[IN_W+(32+r)*D+c1]', 'G[IN_W+(D+r)*D+c1]')
    s=s.replace('G[IN_W+(64+r)*D+c1]', 'G[IN_W+(2*D+r)*D+c1]')
    s=s.replace('P[IN_W+(32+r)*D+c1]', 'P[IN_W+(D+r)*D+c1]')
    s=s.replace('P[IN_W+(64+r)*D+c1]', 'P[IN_W+(2*D+r)*D+c1]')
    # fail closed if a template substitution was missed
    forbidden=['#define PSIZE 15425','sqrt(32.0)','32*196','32*16','96*32','32*32','64*32']
    bad=[x for x in forbidden if x in s]
    if bad: raise SystemExit('unsubstituted template fragments: '+repr(bad))
    return s

def run(cfg_path):
    cfg=json.loads(Path(cfg_path).read_text())
    name=cfg.get('name', Path(cfg_path).stem)
    d=int(cfg.get('D',32)); f=int(cfg.get('F',64))
    out=HERE/'variants'/name; out.mkdir(parents=True, exist_ok=True)
    (out/'variant_layout.h').write_text(layout(d,f))
    (out/'dt_train.c').write_text(make_source(cfg))
    exe=out/'dt_train'
    cmd=['clang','-O3','-I',str(out),'-I',str(BASE),str(out/'dt_train.c'),'-o',str(exe),'-lm']
    subprocess.run(cmd,check=True)
    res=subprocess.run([str(exe)],capture_output=True,text=True,check=True)
    (out/'train.out').write_text(res.stdout)
    picks=[int(l.split()[-1]) for l in res.stdout.splitlines() if l.startswith('FOLD ') and 'PICK' in l]
    n=sum(a==b for a,b in zip(picks,REF_PICKS))
    by_rule={x['pick']:x.get('correct',0) for x in REF}
    acc=sum(by_rule.get(p,0) for p in picks)
    row={'name':name,'config':cfg,'picks':picks,'reference':REF_PICKS,'matches':n,'accuracy':acc}
    (out/'result.json').write_text(json.dumps(row,indent=2)+'\n')
    print(f'{name:20s} matches={n}/10 picks={picks}')
    return row

if __name__=='__main__':
    cfg=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'configs/baseline.json'
    run(cfg)
