"""IO boundary demo: heterogeneous input -> logic -> kernel -> output (incl. NL).

Run:  python3 -m experiments.io_demo.run   (from the repo root)

Deterministic, stdlib only.  Shows that the same boundary accepts sentences,
tabular datasets, a DLM program, and binary media; that only the kernel
asserts; and that results render back to natural language or structured data.
"""
from __future__ import annotations

import json
import struct

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure, dump, atom_to_form
from dlm import io


def _form(a: Atom) -> str:
    return dump(atom_to_form(a))


PNG = (b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR"
       + struct.pack(">II", 1024, 768) + b"\x08\x02\x00\x00\x00")
WAV = (b"RIFF" + struct.pack("<I", 36) + b"WAVE" + b"fmt " + struct.pack("<I", 16)
       + struct.pack("<HHI", 1, 1, 16000) + struct.pack("<IHH", 32000, 2, 16))


def main() -> dict:
    report: dict = {}

    # 1. natural-language text -> sentences -> IR frames (proposals only)
    text = "Paris is the capital of France. France is a country in Europe."
    tb = io.decode(text, "text/plain", name="web.txt")
    tframes = io.frames_from_sentences(tb.sentences)
    report["text_sentences"] = list(tb.sentences)
    report["text_frames"] = [f.name or "(unnamed)" for f in tframes]

    # 2. tabular dataset -> ground atoms
    csv = "pred,subj,obj\ncountry_of,france,paris\npart_of,france,europe\n"
    cb = io.decode(csv, "text/csv", name="facts.csv")
    report["csv_atoms"] = [_form(a) for a in cb.atoms]

    # 3. binary media -> metadata atoms (pluggable decoder seam)
    pb = io.decode(PNG, "image/png", name="map.png")
    wb = io.decode(WAV, "audio/wav", name="anthem.wav")
    media = tuple(io.media_atoms(pb)) + tuple(io.media_atoms(wb))
    report["media_atoms"] = [_form(a) for a in media]

    # 4. only the kernel asserts: facts + rule -> closure
    kb = KnowledgeBase()
    for a in cb.atoms:
        kb.add_fact(a)
    kb.add_rule(Rule(Atom(Const("capital_of"), (Var("x"), Var("y"))),
                     (Atom(Const("country_of"), (Var("y"), Var("x"))),)))
    proved = tuple(sorted(closure(kb), key=_form))
    report["closure"] = [_form(a) for a in proved]
    report["asserted_by_kernel"] = _form(Atom(Const("capital_of"), (Const("paris"), Const("france")))) \
        in [_form(a) for a in proved]

    # 5. DLM one-form -> back to logic (round trip)
    src = io.encode(cb.atoms, "application/x-dlm") + "\n" + io.encode(media, "application/x-dlm")
    back = io.decode(src, "application/x-dlm")
    report["dlm_roundtrip"] = [_form(a) for a in back.atoms] == report["csv_atoms"] + report["media_atoms"]

    # 6. results -> natural language and to structured output
    report["nl_output"] = io.result_to_text(proved)
    report["json_output"] = json.loads(io.encode(proved, "application/json"))
    report["csv_output"] = io.encode(proved, "text/csv").splitlines()[0]
    return report


if __name__ == "__main__":
    print(json.dumps(main(), ensure_ascii=False, indent=2))
