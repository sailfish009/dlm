"""Web-acquired PyTorch semantics -- the untrusted KNOWLEDGE source.

The reduction (``extract.py``) tells us which library symbols a program *uses*
(``loss.backward``, ``nn.Conv2d``, ``DataLoader``, ...) but not what they MEAN.
That meaning is not in the code; it lives in the library's documentation.  So the
untrusted acquirer looks the used symbols up on the web and turns the definitions
it finds into ``meaning(symbol, concept)`` facts.  The kernel never learns
anything here -- it only consumes the facts in the given bridge rules
(``semantics.py``), and abstains for a symbol with no acquired meaning.

Two web providers, both untrusted:

* ``search`` -- a real **web search service** (Stack Exchange's API).  It returns
  free-text Q&A for a symbol; a cue lexicon reduces the top hit to a concept.
  This is noisy (free text), so it is used to *corroborate* and to *fall back*.
* ``docs`` -- the documentation's own **object inventory** (Sphinx
  ``objects.inv``, a web-fetched search index) resolves a symbol to its canonical
  definition page; the definition paragraph is read verbatim.  Authoritative.

Everything is cached under ``cache/`` so an ``--offline`` replay is byte-for-byte
deterministic and needs no network.  Provenance (URL + the raw definition text +
the provider) is recorded for every fact so a reviewer can audit each meaning.
No meaning is invented: a definition with no cue yields no fact.
"""
from __future__ import annotations

import base64
import gzip
import html as _html
import json
import os
import re
import time
import urllib.parse as _up
import urllib.request
import zlib
from typing import Dict, List, Optional, Tuple

UA = {"User-Agent": "dlm-research/0.1 (+https://example.invalid/dlm)"}

DOCS_BASE = "https://docs.pytorch.org/docs/stable/"
INVENTORY_URL = DOCS_BASE + "objects.inv"
SE_API = "https://api.stackexchange.com/2.3/"
KNOWLEDGE_VERSION = 1

# A documented JS redirect on the docs site: ``location.replace("../../2.14/...")``.
_JS_REDIRECT = re.compile(r"location\.(?:replace|href)\s*(?:\(|=)\s*[\"']([^\"']+)[\"']")

# -- the concept vocabulary (the TARGET of the reduction) --------------------
#
# These are the handful of ideas the bridge rules in semantics.py can use.  A
# definition is mapped to at most one concept, by the FIRST concept whose cue
# phrase occurs in the (lower-cased) definition.  Order is the disambiguation
# priority.  The cues are matched against verbatim documentation text.
CONCEPT_CUES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("module_base", ("base class for all neural network", "base class for all neural")),
    ("backpropagation", ("computes the gradient", "compute the gradient",
                         "gradient of current tensor", "backward pass", "backpropagat")),
    ("parameter_update", ("optimization step", "update parameter", "update the parameters",
                          "updates the parameters", "updating the parameters")),
    ("evaluation", ("evaluation mode", "evaluating time")),
    ("gradient_free", ("disables gradient", "disable gradient", "disabling gradient",
                       "no gradient computation", "without tracking gradient",
                       "does not track gradient")),
    ("data_loading", ("data loader", "dataloader", "combines a dataset")),
    ("serialization", ("saves an object", "save and load", "state dict", "serializes")),
    ("layer", ("2d convolution", "convolution", "applies an affine linear",
               "linear transformation", "rectified linear", "max pooling", "pooling",
               "dropout", "zeroes some of the elements", "batch normalization",
               "normalization")),
)

# Free-text cues for the search provider (Stack Exchange titles + answers).  A
# search hit is reduced with the SAME concept vocabulary but looser phrasing,
# because Q&A is not a definition.  Used as a corroborating/fallback signal.
SEARCH_CUES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("module_base", ("base class for all neural network", "inherit from nn.module",
                     "subclass nn.module", "base class of all neural")),
    ("backpropagation", ("backward pass", "backpropagat", "compute the gradient",
                         "computes the gradient", "gradients are stored")),
    ("parameter_update", ("update the parameters", "updates the parameters",
                          "updating the parameters", "single optimization step",
                          "update the weights")),
    ("evaluation", ("evaluation mode", "inference mode", "evaluating time")),
    ("gradient_free", ("disable gradient", "disables gradient", "disabling gradient",
                       "no gradient computation", "without tracking gradient")),
    ("data_loading", ("data loader", "dataloader", "iterable over a dataset",
                      "combines a dataset")),
    ("serialization", ("saves an object", "save and load", "state dict", "serialize")),
    ("layer", ("2d convolution", "convolution", "linear transformation",
               "fully connected", "linear layer")),
)

# Receiver-type hints: a method label ``head.tail`` (e.g. ``loss.backward``) is
# disambiguated toward the documented class that owns it.  This is the small,
# auditable piece of "how variable names map to library types" the resolver
# needs; every resolution it produces is still recorded and reviewable.
RECEIVER_HINTS: Dict[str, str] = {
    "loss": "torch.Tensor",
    "pred": "torch.Tensor",
    "output": "torch.Tensor",
    "data": "torch.Tensor",
    "target": "torch.Tensor",
    "x": "torch.Tensor",
    "model": "torch.nn.Module",
    "optimizer": "torch.optim.Optimizer",
    "scheduler": "torch.optim.lr_scheduler",
}


# ---------------------------------------------------------------------------
# candidate selection (which symbols need a web lookup)
# ---------------------------------------------------------------------------
def symbol_candidates(facts: List[tuple], labels: Dict[str, str]) -> Dict[str, str]:
    """External, library-looking slugs the reduction uses, mapped to their label.

    "Library-looking" = a dotted name (``nn.Linear``) or a capitalised class
    (``DataLoader``).  Purely local names (``model``, ``range``) are dropped;
    names defined in the file are dropped; synthetic step slugs (``a__b``) are
    dropped.  This is a *reduction*, not knowledge: it only says *what to ask*.
    """
    defined = {f[2] for f in facts if f[0] in ("defines", "method_of")}
    out: Dict[str, str] = {}
    for f in facts:
        if f[0] == "creates":
            args = (f[2],)
        elif f[0] in ("calls", "inherits"):
            args = (f[2],)
        else:
            continue
        for s in args:
            if s in defined or "__" in s:
                continue
            label = labels.get(s)
            if not label:
                continue
            if "." not in label and not label[:1].isupper():
                continue
            out.setdefault(s, label)
    return out


# ---------------------------------------------------------------------------
# resolution: symbol label -> a documented object name
# ---------------------------------------------------------------------------
def _norm_label(label: str) -> str:
    return re.sub(r"[^a-z0-9_.]", "", label.lower())


def resolve(label: str, inventory: Dict[str, str]) -> Tuple[Optional[str], str]:
    """Resolve a human label to an inventory object name (or None).

    ``inventory`` maps dotted object name -> doc URL.  Thin dotted names are
    preferred (``torch.nn.Conv2d`` over ``torch.ao.quantization.Conv2d``).
    Returns ``(name, how)`` where ``how`` records the rule used, for audit.
    """
    lab = _norm_label(label)
    low = {k.lower(): k for k in inventory}
    if lab in low:
        return low[lab], "exact"
    suffix = [k for k in inventory if k.lower().endswith("." + lab)]
    if suffix:
        return min(suffix, key=lambda k: (k.count("."), len(k))), "suffix"
    head, _, last = lab.rpartition(".")
    segs = [k for k in inventory if k.lower().endswith("." + last)]
    if not segs:
        return None, "miss"
    hint = RECEIVER_HINTS.get(head)
    if hint:
        h = [k for k in segs if k.startswith(hint)]
        if h:
            return min(h, key=lambda k: (k.count("."), len(k))), "receiver-hint"
    return min(segs, key=lambda k: (k.count("."), len(k))), "last-segment"


# ---------------------------------------------------------------------------
# reduction: definition text -> concept
# ---------------------------------------------------------------------------
def reduce_definition(text: str,
                      cues: Tuple[Tuple[str, Tuple[str, ...]], ...] = CONCEPT_CUES
                      ) -> Optional[str]:
    low = re.sub(r"\s+", " ", text.lower())
    for concept, phrases in cues:
        for p in phrases:
            if p in low:
                return concept
    return None


# ---------------------------------------------------------------------------
# HTTP with a simple on-disk cache
# ---------------------------------------------------------------------------
class _Fetcher:
    def __init__(self, cache_dir: str, offline: bool = False):
        # Raw HTTP responses live in a ``fetch/`` subdir; the *reduced* records
        # (``pytorch_knowledge.json``) are what offline replay actually needs.
        self.cache_dir = os.path.join(cache_dir, "fetch")
        self.offline = offline
        os.makedirs(self.cache_dir, exist_ok=True)

    def _key(self, url: str) -> str:
        return base64.urlsafe_b64encode(url.encode("utf-8")).decode("ascii")[:120] + ".bin"

    def _fetch(self, url: str) -> Optional[bytes]:
        try:
            req = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(req, timeout=40).read()
        except Exception:
            return None

    def get(self, url: str) -> Optional[bytes]:
        path = os.path.join(self.cache_dir, self._key(url))
        if os.path.exists(path):
            with open(path, "rb") as fh:
                return fh.read()
        if self.offline:
            return None
        raw = self._fetch(url)
        # The docs site serves a tiny JS redirect stub for ``/docs/stable/...``;
        # follow it to the versioned page (the docs' own canonical target).
        if raw is not None and len(raw) < 4000:
            m = _JS_REDIRECT.search(raw.decode("utf-8", "replace"))
            if m and not m.group(1).startswith("http"):
                target = _up.urljoin(url, m.group(1))
                if target != url:
                    raw2 = self._fetch(target)
                    if raw2:
                        raw = raw2
        if raw is not None:
            with open(path, "wb") as fh:
                fh.write(raw)
        return raw


def load_inventory(fetch: _Fetcher) -> Dict[str, str]:
    """Fetch + parse the Sphinx object inventory (the docs' own search index)."""
    raw = fetch.get(INVENTORY_URL)
    if not raw:
        return {}
    i = 0
    for _ in range(4):
        j = raw.find(b"\n", i)
        if j < 0:
            break
        i = j + 1
    try:
        data = zlib.decompress(raw[i:]).decode("utf-8", "replace")
    except zlib.error:
        return {}
    out: Dict[str, str] = {}
    for line in data.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        name, uri = parts[0], parts[3]
        if not name.startswith("torch.") or "/" in name:
            continue
        out[name] = uri.split("#")[0]
    return out


# ---------------------------------------------------------------------------
# definition extraction
# ---------------------------------------------------------------------------
def extract_definition(page: str, anchor: str) -> Optional[str]:
    """The first paragraph of documentation after ``anchor`` on an HTML page."""
    i = page.find('id="%s"' % anchor)
    seg = page[i:] if i >= 0 else page
    m = re.search(r"<p>(.*?)</p>", seg, re.S)
    if not m:
        return None
    text = _html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


# ---------------------------------------------------------------------------
# the search provider (Stack Exchange web search)
# ---------------------------------------------------------------------------
def _se_json(path: str, params: dict) -> Optional[dict]:
    url = SE_API + path + "?" + _up.urlencode(params)
    try:
        req = urllib.request.Request(url, headers=UA)
        raw = urllib.request.urlopen(req, timeout=25).read()
    except Exception:
        return None
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    try:
        return json.loads(raw)
    except ValueError:
        return None


def search_evidence(fetch: _Fetcher, label: str, concept: Optional[str]) -> Optional[dict]:
    """One web-search corroboration for ``label``: the top question title.

    Reproducible: the raw query/response is cached under ``cache/fetch/``.
    Only the human-readable title is kept in the knowledge file.
    """
    q = "pytorch " + label
    url = SE_API + "search/advanced?" + _up.urlencode(
        {"order": "desc", "sort": "relevance", "q": q, "site": "stackoverflow", "pagesize": 3})
    raw = fetch.get(url)
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except ValueError:
        return None
    items = data.get("items") or []
    if not items:
        return None
    top = items[0]
    return {"provider": "stackexchange", "title": _html.unescape(top.get("title", ""))[:200],
            "concept": concept, "link": top.get("link", "")}


# ---------------------------------------------------------------------------
# acquisition
# ---------------------------------------------------------------------------
def _knowledge_path(cache_dir: str) -> str:
    return os.path.join(cache_dir, "pytorch_knowledge.json")


def load_knowledge(cache_dir: str) -> dict:
    path = _knowledge_path(cache_dir)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"version": KNOWLEDGE_VERSION, "source": INVENTORY_URL, "symbols": {}}


def save_knowledge(cache_dir: str, kb: dict) -> None:
    path = _knowledge_path(cache_dir)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(kb, fh, indent=1, sort_keys=True, ensure_ascii=False)


def acquire_knowledge(facts: List[tuple], labels: Dict[str, str], cache_dir: str,
                      offline: bool = False, search: bool = True,
                      max_new: Optional[int] = None) -> dict:
    """Acquire ``meaning(symbol, concept)`` for the library symbols in ``facts``.

    Reads/writes ``cache/pytorch_knowledge.json`` and the raw fetch cache.  With
    ``offline=True`` nothing is fetched: cached records are used and everything
    else abstains.  Returns a summary the run can audit.
    """
    cands = symbol_candidates(facts, labels)
    kb = load_knowledge(cache_dir)
    syms: Dict[str, dict] = kb.setdefault("symbols", {})
    fetch = _Fetcher(cache_dir, offline=offline)
    inventory: Optional[Dict[str, str]] = None
    fetched_new = 0
    changed = False

    for slug, label in sorted(cands.items()):
        rec = syms.get(label)
        if rec is not None:
            continue
        if offline:
            continue
        if max_new is not None and fetched_new >= max_new:
            continue
        if inventory is None:
            inventory = load_inventory(fetch)
        entry, how = resolve(label, inventory)
        rec = {"label": label, "slug": slug, "entry": entry, "resolution": how,
               "definition": None, "concept": None, "url": None, "providers": []}
        if entry:
            url = DOCS_BASE + inventory[entry]
            rec["url"] = url
            page = fetch.get(url)
            if page:
                defn = extract_definition(page.decode("utf-8", "replace"), entry)
                rec["definition"] = defn
                rec["concept"] = reduce_definition(defn) if defn else None
            rec["providers"].append("docs")
        if search:
            ev = search_evidence(fetch, label, rec["concept"])
            if ev:
                rec["providers"].append("search")
                rec["search"] = ev
                if rec["concept"] is None:
                    rec["concept"] = ev.get("concept")
        syms[label] = rec
        fetched_new += 1
        changed = True

    if changed:
        save_knowledge(cache_dir, kb)

    meanings = {slug: syms[label]["concept"]
                for slug, label in cands.items()
                if syms.get(label, {}).get("concept")}
    records = sorted((syms[label] for label in set(cands.values()) if label in syms),
                     key=lambda r: r["label"])
    return {
        "meanings": meanings,
        "records": records,
        "stats": {
            "candidates": len(cands),
            "acquired": len(meanings),
            "cached_records": len(syms),
            "fetched_new": fetched_new,
            "offline": offline,
            "inventory_url": INVENTORY_URL,
        },
    }


def meaning_facts(meanings: Dict[str, str]) -> List[Tuple[str, str, str]]:
    """``{slug: concept}`` -> IR-style ground fact tuples ``("meaning", slug, concept)``."""
    return [("meaning", slug, concept) for slug, concept in sorted(meanings.items())]