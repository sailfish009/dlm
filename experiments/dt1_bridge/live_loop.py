import re, subprocess, tempfile, torch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=(ROOT/'experiments/dt1_bridge/start.l').read_text()
def verify(ids):
    text=re.sub(r'\(eval-set[^\n]*\)\n', '', BASE)
    text=text.replace('(print "done-dt1-bridge\\n")', f'(eval-set "cand" (list {" ".join(chr(34)+x+chr(34) for x in ids)}))\n(print "done-dt1-bridge\\n")')
    with tempfile.NamedTemporaryFile('w',suffix='.l',delete=False) as f:
        f.write(text); path=f.name
    p=subprocess.run([str(ROOT/'scripts/run.sh'),'proof-extra',str(ROOT/'experiments/web_recursive_repl/web_data.l'),path],cwd=ROOT,text=True,capture_output=True,timeout=180)
    Path(path).unlink()
    m=re.search(r'CAND cand .*?proof=(\w+)',p.stdout)
    return (m.group(1) if m else 'fail')
torch.manual_seed(60); logits=torch.zeros(2,requires_grad=True); opt=torch.optim.Adam([logits],0.2); base=0
for step in range(4):
    d=torch.distributions.Bernoulli(logits=logits); s=d.sample(); ids=[f'A-{i}' for i,v in enumerate(s.tolist()) if v]
    status=verify(ids); r=1.0 if status=='proof' else -0.2
    loss=-(d.log_prob(s).sum()*(r-base)); opt.zero_grad(); loss.backward(); opt.step(); base=.9*base+.1*r
    print('step',step,'ids',ids,'proof',status,'reward',r)
with torch.no_grad():
    s=(logits>0).long().tolist(); print('FINAL',[f'A-{i}' for i,v in enumerate(s) if v])
