"""Re-export the proven web extractor from the sibling webssl experiment.

The webloop experiment reuses ``web.py`` (cache, Wikidata/Wikipedia clients,
Doc/Fact/slug/split_sentences) and ``bridge.py`` (facts -> Horn KB + general
rules -> kernel closure) instead of forking them.  Import order matters: the
webssl directory is put on ``sys.path`` first, so ``import web`` resolves to it.
"""
from __future__ import annotations

import sys
from pathlib import Path

_WEBS = Path(__file__).resolve().parents[1] / "webssl"
if str(_WEBS) not in sys.path:
    sys.path.insert(0, str(_WEBS))

import bridge  # noqa: E402
import web  # noqa: E402

__all__ = ["bridge", "web"]
