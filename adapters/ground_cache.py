#!/usr/bin/env python3
"""Emit a native ground store from cached real-web snapshots + extractions.

The adapter is untrusted extraction tooling. It validates that every recorded
quote is exactly the UTF-8 byte span in the source text. Maru then independently
checks the same span again in p107-gclaim-ok?. No claim is ever treated as an
axiom: it still needs corroboration/projection and the Horn checker.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path


def quote(x):
    return json.dumps(str(x), ensure_ascii=False)


def atom(pred, args):
    return "'(atom " + pred + " (" + " ".join(quote(a) for a in args) + "))"


def form_atom(a):
    if not isinstance(a, list) or len(a) != 2:
        raise ValueError(f"bad atom: {a!r}")
    return atom(a[0], a[1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--scramble', action='store_true')
    ns = ap.parse_args()
    data = json.loads(Path(ns.input).read_text(encoding='utf-8'))
    base = Path(ns.input).resolve().parent
    sources = {s['id']: s for s in data['sources']}
    texts = {}
    for sid, s in sources.items():
        text = (base / 'snapshots' / s['text_file']).read_text(encoding='utf-8')
        actual = hashlib.sha256(text.encode('utf-8')).hexdigest()
        if actual != s['sha256']:
            raise ValueError(f"sha256 mismatch for {sid}")
        texts[sid] = text
    forms = []
    for c in data['claims']:
        if ns.scramble:
            if c['pred'] == 'country':
                c = dict(c); c['args'] = [c['args'][0], 'Japan']
            elif c['pred'] == 'subfield_of':
                c = dict(c); c['args'] = [c['args'][0], 'biology']
        sid = c['source']
        text = texts[sid]
        q = c['quote']
        start = len(text[:text.index(q)].encode('utf-8')) if text.count(q) == 1 else c['start']
        # Prefer the recorded span, but verify it exactly.
        got = text.encode('utf-8')[c['start']:c['end']].decode('utf-8', errors='strict')
        if got != q:
            raise ValueError(f"span mismatch for {c['id']}: {got!r} != {q!r}")
        pol = c.get('polarity', 'positive')
        conds = c.get('conditions') or []
        condform = '(list ' + ' '.join(form_atom(a) for a in conds) + ')' if conds else '()'
        fr = c.get('from')
        to = c.get('to')
        fr = "'none" if fr is None else str(int(fr))
        to = "'none" if to is None else str(int(to))
        forms.append(
            f"(p107-gclaim (p107-claim {quote(c['id'])} {atom(c['pred'], c['args'])} "
            f"{quote(sid)} {quote(c['version'])} 'web '{c.get('trust','hypothesis')} "
            f"{quote(c.get('extractor','manual-v1'))}) '{pol} {condform} {fr} {to} "
            f"{quote(sid)} {quote(c['version'])} {int(c['start'])} {int(c['end'])} "
            f"{quote(q)} {quote(c.get('extractor','manual-v1'))})")
    srcforms = []
    for sid, s in sources.items():
        srcforms.append(
            f"(p107-source {quote(sid)} {quote(s['url'])} {quote(s['revision'])} "
            f"{quote(s['fetched'])} {quote(s['sha256'])} {quote(texts[sid])})")
    out = ("(define all-sources (list\n  " + "\n  ".join(srcforms) + "))\n"
           "(define all-gclaims (list\n  " + "\n  ".join(forms) + "))\n")
    Path(ns.out).write_text(out, encoding='utf-8')
    print(f"sources={len(srcforms)} claims={len(forms)}")


if __name__ == '__main__':
    main()
