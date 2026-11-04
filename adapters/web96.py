#!/usr/bin/env python3
"""Bounded real-web acquisition and declared-schema worker, never the learner.

Stdlib csv is the extraction worker. Native byte CSV/SHA/projection checks reject
wrong or omitted output. Raw mixed-license upstream data stays in a local cache,
not in the product tree. There is no target program or desired basis in packets.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import urllib.request

from sexp import Symbol as S, dumps
from web import CachedWeb, Redirects, atomic_write

COMMIT = '2d84034a0cae19ea5444b78c2131304a5c7f4bb9'
URL = f'https://raw.githubusercontent.com/datasets/country-codes/{COMMIT}/data/country-codes.csv'
ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(os.environ.get('DLM_WEB96_CACHE', Path.home() / '.cache/dlm-web96'))
FIELDS = ('M49', 'Sub-region Code', 'Region Code', 'Global Code')
PREDS = tuple(map(S, ('country-subregion96', 'subregion-region96', 'region-global96')))
NAMESPACES = ('country:', 'subregion:', 'region:', 'global:')
TOKEN = re.compile(rb'(?:"(?:[^"]|"")*"|[^,\r\n"]*)(?:,|\r?\n|$)')
URL_RE = re.compile(r'https://raw\.githubusercontent\.com/datasets/country-codes/[a-f0-9]{40}/data/country-codes\.csv\Z')


def allowed_url(url):
    return isinstance(url, str) and bool(URL_RE.fullmatch(url))


class RestrictedRedirects(Redirects):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed_url(newurl):
            raise ValueError('web96 redirect outside pinned repository path')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def acquire(cache=CACHE, *, online=False, refresh=False, url=URL):
    if not allowed_url(url):
        raise ValueError('unsupported web96 URL')
    web = CachedWeb(cache, offline=not online, refresh=refresh, max_bytes=262144)
    web.opener = urllib.request.build_opener(RestrictedRedirects())
    record, error = web.get_record(url)
    if error:
        raise ValueError('acquisition: ' + error)
    if record['final_url'] != url:
        raise ValueError('unexpected final URL')
    return record


def spans(raw):
    """Regex byte token boundaries; csv.reader independently supplies cell values."""
    result, cells, pos, start = [], [], 0, 0
    while pos < len(raw):
        match = TOKEN.match(raw, pos)
        if match is None or match.end() == pos:
            raise ValueError('CSV byte boundary')
        token = match.group()
        delim = 2 if token.endswith(b'\r\n') else int(token.endswith((b',', b'\n')))
        cells.append([pos, match.end() - delim])
        pos = match.end()
        if token.endswith(b'\n') or (pos == len(raw) and not token.endswith(b',')):
            result.append((start, pos, cells))
            start, cells = pos, []
    if cells:
        # RFC CSV permits a last empty field after a terminal comma.
        cells.append([len(raw), len(raw)])
        result.append((start, len(raw), cells))
    return result


def code(value):
    return value.zfill(3) if re.fullmatch(r'[0-9]{1,3}', value) and int(value) > 0 else None


def view(identifier, level, rows):
    numbers, facts, proofs = [], [], []
    for no, start, end, codes, locations in rows:
        numbers.append(no)
        for i in range(level):
            facts.append([S('atom'), PREDS[i], [NAMESPACES[i] + codes[i], NAMESPACES[i + 1] + codes[i + 1]]])
            proofs.append([S('edge96'), len(facts) - 1, no, start, end, FIELDS[i], *locations[i], FIELDS[i + 1], *locations[i + 1]])
    return [S('view96'), identifier, level, numbers, facts, proofs]


def extract(raw):
    if not raw or len(raw) > 262144:
        raise ValueError('byte limit')
    values = list(csv.reader(io.StringIO(raw.decode('utf-8'), newline=''), strict=True))
    locations = spans(raw)
    if not values or len(values) != len(locations) or len(values) > 512 or any(len(r) > 80 for r in values):
        raise ValueError('CSV bounds')
    header = values[0]
    if len(header) != len(set(header)) or not all(f in header for f in FIELDS):
        raise ValueError('CSV schema')
    indexes = [header.index(f) for f in FIELDS]
    rows, unresolved, seen = [], [], set()
    for no, (values_row, (start, end, cell_spans)) in enumerate(zip(values[1:], locations[1:]), 1):
        if len(values_row) != len(header) or len(cell_spans) != len(header) or any(b - a > 8192 for a, b in cell_spans):
            raise ValueError('CSV record shape')
        codes = [code(values_row[i]) for i in indexes]
        missing = [f for f, c in zip(FIELDS, codes) if c is None]
        if missing:
            unresolved.append([S('unresolved96'), no, start, end, missing])
            continue
        if codes[0] in seen:
            raise ValueError('duplicate M49')
        seen.add(codes[0])
        rows.append((no, start, end, codes, [cell_spans[i] for i in indexes]))
    rows.sort(key=lambda r: r[3][0])

    def select(excluded):
        selected, regions = [], set()
        for row in rows:
            if len(selected) < 2 and row[3][0] not in excluded and row[3][2] not in regions:
                selected.append(row)
                regions.add(row[3][2])
        return selected

    train = select(set())
    next_rows = select({r[3][0] for r in train})
    if len(train) != 2 or len(next_rows) != 2:
        raise ValueError('insufficient distinct-region records')
    used = {r[3][0] for r in train + next_rows}
    held = [view('web-row96:' + r[3][0], 3, [r]) for r in rows if r[3][0] not in used]
    return [S('extraction96'), S('m49-csv96'), view('web-train96', 2, train), view('web-next96', 3, next_rows), held, unresolved, len(values) - 1]


def packet(record):
    raw = base64.b64decode(record['raw_base64'], validate=True)
    if hashlib.sha256(raw).hexdigest() != record['sha256'] or not allowed_url(record['url']):
        raise ValueError('source integrity')
    # Normalized UTC ingress timestamp. Acquisition cache preserves original.
    fetched = record['fetched_at'][:19] + 'Z'
    return [S('web-document96'), 'country-codes96', record['url'], fetched,
            record['sha256'], S('m49-csv96'), raw.hex(), extract(raw)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=CACHE)
    parser.add_argument('--online', action='store_true', help='explicitly permit acquisition; default cache-only')
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--output', type=Path, required=True, help='private data packet, not executable Lisp')
    args = parser.parse_args()
    record = acquire(args.cache, online=args.online, refresh=args.refresh)
    p = packet(record)
    atomic_write(args.output, (dumps(p) + '\n').encode('ascii'))
    print(json.dumps(dict(sha256=p[4], rows=p[7][6], heldout=len(p[7][4]), unresolved=len(p[7][5]), output=str(args.output))))


if __name__ == '__main__':
    main()
