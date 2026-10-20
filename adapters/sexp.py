"""Data-only S-expressions. No eval, reader macros, dotted pairs or code loading."""
import json
import re

class Symbol(str):
    pass

def dumps(x):
    if isinstance(x, Symbol):
        if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9-]*', x):
            raise ValueError('unsafe symbol')
        return str(x)
    if isinstance(x, str):
        # Maru supports the JSON escapes used here, not JSON's unicode escapes.
        return json.dumps(x, ensure_ascii=False)
    if isinstance(x, int):
        return str(x)
    if isinstance(x, (list, tuple)):
        return '(' + ' '.join(map(dumps, x)) + ')'
    raise TypeError(type(x))

def loads_many(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text)
    pos = 0
    def read():
        nonlocal pos
        if pos >= len(tokens):
            raise ValueError('truncated datum')
        t = tokens[pos]; pos += 1
        if t == '(':
            out = []
            while pos < len(tokens) and tokens[pos] != ')':
                out.append(read())
            if pos >= len(tokens):
                raise ValueError('unclosed list')
            pos += 1
            return out
        if t == ')':
            raise ValueError('unexpected close')
        if t.startswith('"'):
            return json.loads(t)
        if re.fullmatch(r'-?\d+', t):
            return int(t)
        return Symbol(t)
    out = []
    while pos < len(tokens):
        out.append(read())
    return out
