"""Module: IO -- the untrusted data boundary between the world and the logic.

Web data is heterogeneous: natural-language text, tabular datasets, binary
media (images, audio, video).  DLM processes *logic*.  This module is the one
place where those worlds meet, in both directions:

    world bytes/str  --decode-->  Block  --(caller)-->  atoms / frames / KB
    DLM result       --encode-->  bytes/str, incl. natural-language sentences

It is deliberately UNTRUSTED.  It only *proposes* atoms and *renders* results;
the kernel gate in the core still decides truth.  Nothing here may assert.

The representation is a :class:`Block`: a frozen, ordered, JSON-serialisable
record that carries sentences, IR frames, logic atoms, table rows, media
metadata, and (optionally) the raw bytes.  Codecs are registered per media
type, so a real vision/speech model can be plugged in later without touching
this file's callers.  Stdlib only, deterministic; imports the core one-way and
``dlm.ssl`` for the language layer.
"""
from __future__ import annotations

import csv as _csv
import hashlib as _hashlib
import json as _json
import re as _re
import struct as _struct
from dataclasses import dataclass, replace as _replace
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple, Union

from . import (Atom, Const, Rule, SexpError, Sym, atom_to_form, dump,
               form_to_atom, form_to_rule, parse, rule_to_form)
from .ssl import (FRAMES, Frame, frame_from_form, frame_to_form, frame_sexp,
                 render)

__all__ = [
    "Block", "detect_media", "register_reader", "register_writer",
    "decode", "encode", "read_file", "write_file",
    "readers", "writers",
    "split_sentences", "frames_from_sentences", "atoms_from_rows", "media_atoms",
    "default_frame", "atom_sentence", "atoms_to_sentences",
    "atoms_to_sexp", "atoms_to_json", "result_to_text",
]

Payload = Union[str, bytes]


@dataclass(frozen=True)
class Block:
    """One normalised payload crossing the IO boundary.

    ``kind`` is one of ``text|table|atoms|image|audio|video|binary``.  Only the
    fields relevant to that kind are filled; the rest stay empty.  Order is
    preserved and every field is hashable so blocks compare and serialise
    deterministically.
    """

    media: str = "application/octet-stream"
    kind: str = "binary"
    name: str = ""
    sentences: Tuple[str, ...] = ()
    frames: Tuple[Frame, ...] = ()
    atoms: Tuple[Atom, ...] = ()
    rules: Tuple[Rule, ...] = ()
    columns: Tuple[str, ...] = ()
    rows: Tuple[Tuple[str, ...], ...] = ()
    meta: Tuple[Tuple[str, str], ...] = ()
    data: bytes = b""

    def meta_dict(self) -> Dict[str, str]:
        return dict(self.meta)

    def json(self) -> dict:
        """JSON-serialisable view (atoms/frames as their one-form strings)."""
        return {
            "media": self.media,
            "kind": self.kind,
            "name": self.name,
            "sentences": list(self.sentences),
            "frames": [frame_sexp(f) for f in self.frames],
            "atoms": [dump(atom_to_form(a)) for a in self.atoms],
            "rules": [dump(rule_to_form(r)) for r in self.rules],
            "columns": list(self.columns),
            "rows": [list(r) for r in self.rows],
            "meta": self.meta_dict(),
            "nbytes": len(self.data),
        }


# --- §1 helpers -----------------------------------------------------------
_SENT_SPLIT = _re.compile(r"(?<=[.!?])\s+|\n{2,}")


def split_sentences(text: str) -> Tuple[str, ...]:
    """Deterministic sentence split: end punctuation / blank line."""
    out = [s.strip() for s in _SENT_SPLIT.split(text) if s and s.strip()]
    return tuple(out)


def _as_text(payload: Payload, encoding: str = "utf-8") -> str:
    if isinstance(payload, bytes):
        return payload.decode(encoding, "replace")
    return payload


def _as_bytes(payload: Payload, encoding: str = "utf-8") -> bytes:
    if isinstance(payload, bytes):
        return payload
    return payload.encode(encoding)


_ROLE_ALIASES = (
    (("pred", "predicate", "p", "relation", "rel"), "pred"),
    (("subj", "subject", "s", "head", "arg1", "a1"), "subj"),
    (("obj", "object", "o", "tail", "arg2", "a2"), "obj"),
)


def _role_indices(columns: Sequence[str], roles: Dict[str, int]) -> Dict[str, int]:
    """Map {pred,subj,obj} -> column index, from a header or explicit roles."""
    if roles:
        out = dict(roles)
    else:
        low = [c.strip().lower() for c in columns]
        out = {}
        for names, role in _ROLE_ALIASES:
            for i, c in enumerate(low):
                if c in names:
                    out[role] = i
                    break
    missing = [r for r in ("pred", "subj", "obj") if r not in out]
    if missing:
        raise ValueError("cannot locate role column(s) %s in %r" % (missing, tuple(columns)))
    return out


def atoms_from_rows(columns: Sequence[str], rows: Iterable[Sequence[str]],
                    roles: Dict[str, int] | None = None) -> Tuple[Atom, ...]:
    """Turn table rows into ground atoms via the role columns."""
    idx = _role_indices(columns, roles or {})
    atoms: List[Atom] = []
    for r in rows:
        if len(r) <= max(idx.values()):
            continue
        pred = str(r[idx["pred"]]).strip()
        subj = str(r[idx["subj"]]).strip()
        obj = str(r[idx["obj"]]).strip()
        if not pred:
            continue
        atoms.append(Atom(Const(pred), (Const(subj), Const(obj))))
    return tuple(atoms)


# --- §2 registry + boundary -----------------------------------------------
_READERS: Dict[str, Callable[..., Block]] = {}
_WRITERS: Dict[str, Callable[..., Union[str, bytes]]] = {}

_EXT = {
    ".txt": "text/plain", ".md": "text/plain", ".text": "text/plain",
    ".csv": "text/csv", ".tsv": "text/tab-separated-values",
    ".tab": "text/tab-separated-values",
    ".json": "application/json", ".jsonl": "application/x-ndjson",
    ".ndjson": "application/x-ndjson",
    ".sx": "application/x-dlm", ".dlm": "application/x-dlm",
    ".lisp": "application/x-dlm",
    ".png": "image/png", ".gif": "image/gif", ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg", ".wav": "audio/wav", ".mp4": "video/mp4",
}


def readers() -> Tuple[str, ...]:
    return tuple(sorted(_READERS))


def writers() -> Tuple[str, ...]:
    return tuple(sorted(_WRITERS))


def register_reader(media: str, fn: Callable[..., Block], *, replace: bool = False) -> None:
    if media in _READERS and not replace:
        raise KeyError("reader for %r already registered" % media)
    _READERS[media] = fn


def register_writer(media: str, fn: Callable[..., Union[str, bytes]], *, replace: bool = False) -> None:
    if media in _WRITERS and not replace:
        raise KeyError("writer for %r already registered" % media)
    _WRITERS[media] = fn


def detect_media(name: str = "", data: Payload = b"") -> str:
    """Sniff a media type from magic bytes, then filename extension."""
    b = _as_bytes(data)[:16] if data else b""
    if b.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if b[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if b[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if b[:4] == b"RIFF" and b[8:12] == b"WAVE":
        return "audio/wav"
    if len(b) >= 12 and b[4:8] == b"ftyp":
        return "video/mp4"
    ext = Path(name).suffix.lower() if name else ""
    return _EXT.get(ext, "application/octet-stream")


def decode(payload: Payload, media: str | None = None, *, name: str = "", **options) -> Block:
    """Bytes/str -> Block, auto-detecting the media type when not given."""
    if isinstance(payload, Block):
        return payload
    media = media or detect_media(name, payload)
    reader = _READERS.get(media)
    if reader is None:
        raise KeyError("no reader for %r; known: %s" % (media, ", ".join(readers())))
    block = reader(payload, **options)
    if name and not block.name:
        block = _with(block, name=name)
    return block


def encode(value, media: str, *, name: str = "", **options) -> Union[str, bytes]:
    """A DLM result (atoms/Block/str) -> output payload, incl. NL sentences."""
    writer = _WRITERS.get(media)
    if writer is None:
        raise KeyError("no writer for %r; known: %s" % (media, ", ".join(writers())))
    return writer(value, name=name, **options)


def read_file(path: Union[str, Path], media: str | None = None, **options) -> Block:
    p = Path(path)
    return decode(p.read_bytes(), media, name=p.name, **options)


def write_file(path: Union[str, Path], value, media: str | None = None, **options) -> None:
    p = Path(path)
    media = media or detect_media(p.name, b"")
    out = encode(value, media, name=p.name, **options)
    if isinstance(out, bytes):
        p.write_bytes(out)
    else:
        p.write_text(out, encoding="utf-8")


def _with(block: Block, **kw) -> Block:
    return _replace(block, **kw)


# --- §3 text / dataset readers --------------------------------------------
def _read_text(payload: Payload, **kw) -> Block:
    text = _as_text(payload)
    return Block(media="text/plain", kind="text", sentences=split_sentences(text),
                 meta=(("chars", str(len(text))),), data=_as_bytes(payload))


def _read_csv(payload: Payload, *, delimiter: str = ",", header: bool = True,
              roles: Dict[str, int] | None = None, **kw) -> Block:
    text = _as_text(payload)
    table = [r for r in _csv.reader(text.splitlines(), delimiter=delimiter) if r]
    if not table:
        return Block(media="text/csv", kind="table")
    columns = tuple(table[0]) if header else tuple("c%d" % i for i in range(len(table[0])))
    body = table[1:] if header else table
    rows = tuple(tuple(str(c) for c in r) for r in body)
    media = "text/tab-separated-values" if delimiter == "\t" else "text/csv"
    try:
        atoms = atoms_from_rows(columns, rows, roles)
    except ValueError:
        atoms = ()
    return Block(media=media, kind="table", columns=columns, rows=rows, atoms=atoms,
                 meta=(("nrows", str(len(rows))),))


def _read_json(payload: Payload, **kw) -> Block:
    obj = _json.loads(_as_text(payload))
    if isinstance(obj, dict) and "atoms" in obj:
        obj = obj["atoms"]
    if isinstance(obj, list) and obj and all(isinstance(x, dict) for x in obj):
        cols = ("pred", "subj", "obj")
        rows = tuple(tuple(str(x.get(c, "")) for c in cols) for x in obj)
        try:
            atoms = atoms_from_rows(cols, rows)
        except ValueError:
            atoms = ()
        return Block(media="application/json", kind="table", columns=cols, rows=rows, atoms=atoms)
    if isinstance(obj, list) and all(isinstance(x, str) for x in obj):
        return Block(media="application/json", kind="text", sentences=tuple(obj))
    return Block(media="application/json", kind="binary", meta=(("json", _json.dumps(obj)),),
                 data=_as_bytes(payload))


def _read_ndjson(payload: Payload, **kw) -> Block:
    lines = [l for l in _as_text(payload).splitlines() if l.strip()]
    objs = [_json.loads(l) for l in lines]
    cols = ("pred", "subj", "obj")
    rows = tuple(tuple(str(o.get(c, "")) if isinstance(o, dict) else "" for c in cols) for o in objs)
    try:
        atoms = atoms_from_rows(cols, rows)
    except ValueError:
        atoms = ()
    return Block(media="application/x-ndjson", kind="table", columns=cols, rows=rows, atoms=atoms)


def _read_dlm(payload: Payload, **kw) -> Block:
    forms = parse(_as_text(payload))
    atoms: List[Atom] = []
    rules: List[Rule] = []
    frames: List[Frame] = []
    for f in forms:
        if f and str(f[0]) == "ir":
            frames.append(frame_from_form(f))
        elif f and str(f[0]) == "rule":
            rules.append(form_to_rule(f))
        else:
            atoms.append(form_to_atom(f))
    return Block(media="application/x-dlm", kind="atoms", atoms=tuple(atoms),
                 rules=tuple(rules), frames=tuple(frames),
                 meta=(("nrules", str(len(rules))),))


# --- §4 binary media readers (stdlib metadata + pluggable seam) ------------
def _read_png(payload: Payload, **kw) -> Block:
    b = _as_bytes(payload)
    if len(b) < 24 or b[:8] != b"\x89PNG\r\n\x1a\n":
        raise SexpError("not a PNG")
    w, h = _struct.unpack(">II", b[16:24])
    return Block(media="image/png", kind="image", data=b,
                 meta=(("width", str(w)), ("height", str(h)), ("nbytes", str(len(b)))),
                 atoms=())


def _read_gif(payload: Payload, **kw) -> Block:
    b = _as_bytes(payload)
    if b[:6] not in (b"GIF87a", b"GIF89a"):
        raise SexpError("not a GIF")
    w, h = _struct.unpack("<HH", b[6:10])
    return Block(media="image/gif", kind="image", data=b,
                 meta=(("width", str(w)), ("height", str(h)), ("nbytes", str(len(b)))),
                 atoms=())


def _read_jpeg(payload: Payload, **kw) -> Block:
    b = _as_bytes(payload)
    if b[:3] != b"\xff\xd8\xff":
        raise SexpError("not a JPEG")
    i, w, h = 2, 0, 0
    while i + 9 < len(b):
        if b[i] != 0xFF:
            i += 1
            continue
        marker = b[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = _struct.unpack(">HH", b[i + 5:i + 9])
            break
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        seg = _struct.unpack(">H", b[i + 2:i + 4])[0]
        i += 2 + seg
    return Block(media="image/jpeg", kind="image", data=b,
                 meta=(("width", str(w)), ("height", str(h)), ("nbytes", str(len(b)))),
                 atoms=())


def _read_wav(payload: Payload, **kw) -> Block:
    b = _as_bytes(payload)
    if b[:4] != b"RIFF" or b[8:12] != b"WAVE":
        raise SexpError("not a WAV")
    channels = rate = bits = 0
    i = 12
    while i + 8 <= len(b):
        cid, size = b[i:i + 4], _struct.unpack("<I", b[i + 4:i + 8])[0]
        if cid == b"fmt ":
            _fmt, channels, rate = _struct.unpack("<HHI", b[i + 8:i + 16])
            bits = _struct.unpack("<H", b[i + 22:i + 24])[0]
        i += 8 + size + (size & 1)
    return Block(media="audio/wav", kind="audio", data=b,
                 meta=(("channels", str(channels)), ("sample_rate", str(rate)),
                       ("bits", str(bits)), ("nbytes", str(len(b)))), atoms=())


def _read_mp4(payload: Payload, **kw) -> Block:
    b = _as_bytes(payload)
    if len(b) < 12 or b[4:8] != b"ftyp":
        raise SexpError("not an MP4")
    brand = b[8:12].decode("ascii", "replace")
    return Block(media="video/mp4", kind="video", data=b,
                 meta=(("brand", brand), ("nbytes", str(len(b)))), atoms=())


def _read_octet(payload: Payload, **kw) -> Block:
    b = _as_bytes(payload)
    return Block(media="application/octet-stream", kind="binary", data=b,
                 meta=(("nbytes", str(len(b))), ("sha1", _hashlib.sha1(b).hexdigest())))


def media_atoms(block: Block) -> Tuple[Atom, ...]:
    """Descriptor atoms for a media block, so metadata can enter the KB."""
    if not block.name:
        return ()
    out = [Atom(Const("media_kind"), (Const(block.name), Const(block.kind)))]
    for k, v in block.meta:
        out.append(Atom(Const(k), (Const(block.name), Const(v))))
    return tuple(out)


# --- §5 natural-language egress (atoms -> sentences) ----------------------
def frames_from_sentences(sentences: Iterable[str]) -> Tuple[Frame, ...]:
    from .ssl import frame_of
    return tuple(frame_of(s) for s in sentences)


def default_frame(atom: Atom, frames: Sequence[Frame] = FRAMES) -> Frame:
    """Pick a surface frame by predicate name, then cue-token overlap.

    Unknown predicates fall back to a frame built from the predicate's own
    words, so every atom renders (``tom`` + ``is a`` + ``cat``).
    """
    for f in frames:
        if f.name == atom.pred:
            return f
    ptoks = set(str(atom.pred).split("_"))
    best = max(frames, key=lambda f: (len(set(f.rel) & ptoks), f.name))
    if set(best.rel) & ptoks:
        return best
    from .ssl import MASK
    return Frame(rel=tuple(str(atom.pred).split("_")) or ("relates", "to"),
                 subject=(MASK,), obj=(MASK,), name=str(atom.pred))


def atom_sentence(atom: Atom, frame: Frame | None = None) -> str:
    """Render one atom as a natural-language sentence."""
    return render(frame or default_frame(atom), atom)


def atoms_to_sentences(atoms: Iterable[Atom], *,
                       frames: Sequence[Frame] = FRAMES) -> Tuple[str, ...]:
    return tuple(atom_sentence(a, default_frame(a, frames)) for a in atoms)


def atoms_to_sexp(atoms: Iterable[Atom], sep: str = "\n") -> str:
    return sep.join(dump(atom_to_form(a)) for a in atoms)


def atoms_to_json(atoms: Iterable[Atom], *, indent: int = 2) -> str:
    return _json.dumps([_atom_dict(a) for a in atoms], ensure_ascii=False, indent=indent)


def _atom_dict(a: Atom) -> dict:
    return {"pred": str(a.pred), "args": [str(x) for x in a.args],
            "sexp": dump(atom_to_form(a))}


def result_to_text(value, *, frames: Sequence[Frame] = FRAMES, sep: str = "\n") -> str:
    """Render any DLM result as text; atoms become NL sentences."""
    if isinstance(value, Block):
        if value.atoms:
            return sep.join(atoms_to_sentences(value.atoms, frames=frames))
        if value.sentences:
            return sep.join(value.sentences)
        return _json.dumps(value.json(), ensure_ascii=False, indent=2)
    if isinstance(value, Atom):
        return atom_sentence(value)
    if isinstance(value, str):
        return value
    if isinstance(value, Frame):
        return frame_sexp(value)
    try:
        items = list(value)
    except TypeError:
        return str(value)
    if items and all(isinstance(x, Atom) for x in items):
        return sep.join(atoms_to_sentences(items, frames=frames))
    return sep.join(str(x) for x in items)


# --- §6 writers ------------------------------------------------------------
def _write_text(value, *, frames=FRAMES, **kw) -> str:
    if isinstance(value, Block) and value.atoms:
        return result_to_text(value.atoms, frames=frames)
    if isinstance(value, Block):
        return result_to_text(value, frames=frames)
    return result_to_text(value, frames=frames)


def _write_json(value, *, indent: int = 2, **kw) -> str:
    if isinstance(value, Block):
        return _json.dumps(value.json(), ensure_ascii=False, indent=indent)
    if isinstance(value, Atom):
        return _json.dumps(_atom_dict(value), ensure_ascii=False, indent=indent)
    try:
        items = list(value)
    except TypeError:
        return _json.dumps(value, ensure_ascii=False, indent=indent, default=str)
    if all(isinstance(x, Atom) for x in items):
        return atoms_to_json(items, indent=indent)
    return _json.dumps(items, ensure_ascii=False, indent=indent, default=str)


class _Buf(list):
    def write(self, s):
        self.append(s)


def _write_csv(value, *, delimiter: str = ",", **kw) -> str:
    rows: List[Sequence[str]] = []
    if isinstance(value, Block) and value.rows:
        rows = [value.columns] + [list(r) for r in value.rows]
    else:
        if isinstance(value, Atom):
            items = [value]
        else:
            try:
                items = list(value)
            except TypeError:
                items = [value]
        atoms = [a for a in items if isinstance(a, Atom)]
        if atoms:
            rows = [("pred", "subj", "obj")] + [[str(a.pred)] + [str(x) for x in a.args] for a in atoms]
    buf = _Buf()
    w = _csv.writer(buf, delimiter=delimiter, lineterminator="\n")
    for r in rows:
        w.writerow(list(r))
    return "".join(buf)


def _write_dlm(value, **kw) -> str:
    lines: List[str] = []
    if isinstance(value, Block):
        lines += [frame_sexp(f) for f in value.frames]
        lines += [dump(rule_to_form(r)) for r in value.rules]
        lines += [dump(atom_to_form(a)) for a in value.atoms]
    elif isinstance(value, Frame):
        lines.append(frame_sexp(value))
    else:
        items = value if isinstance(value, (list, tuple)) else [value]
        for x in items:
            if isinstance(x, Frame):
                lines.append(frame_sexp(x))
            elif isinstance(x, Rule):
                lines.append(dump(rule_to_form(x)))
            elif isinstance(x, Atom):
                lines.append(dump(atom_to_form(x)))
    return "\n".join(lines)


def _write_ndjson(value, **kw) -> str:
    items = value if isinstance(value, (list, tuple)) else [value]
    if isinstance(value, Block) and value.atoms:
        items = list(value.atoms)
    return "\n".join(_json.dumps(_atom_dict(x) if isinstance(x, Atom) else x,
                                 ensure_ascii=False, default=str) for x in items)


def _write_octet(value, **kw) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, Block):
        return value.data or _as_bytes(_write_text(value))
    return _as_bytes(str(value))


# --- §7 default registration ----------------------------------------------
register_reader("text/plain", _read_text)
register_reader("text/csv", _read_csv)
register_reader("text/tab-separated-values", lambda p, **kw: _read_csv(p, delimiter="\t", **kw))
register_reader("application/json", _read_json)
register_reader("application/x-ndjson", _read_ndjson)
register_reader("application/x-dlm", _read_dlm)
register_reader("image/png", _read_png)
register_reader("image/gif", _read_gif)
register_reader("image/jpeg", _read_jpeg)
register_reader("audio/wav", _read_wav)
register_reader("video/mp4", _read_mp4)
register_reader("application/octet-stream", _read_octet)

register_writer("text/plain", _write_text)
register_writer("application/json", _write_json)
register_writer("text/csv", _write_csv)
register_writer("text/tab-separated-values", lambda v, **kw: _write_csv(v, delimiter="\t", **kw))
register_writer("application/x-dlm", _write_dlm)
register_writer("application/x-ndjson", _write_ndjson)
register_writer("application/octet-stream", _write_octet)
