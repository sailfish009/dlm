import struct
from pathlib import Path

import pytest

from dlm import Atom, Const, KnowledgeBase, Rule, Var, closure, dump, atom_to_form
from dlm import io
from dlm.ssl import frame_sexp


# --- media sniffing --------------------------------------------------------
def test_detect_by_magic_bytes():
    assert io.detect_media("", b"\x89PNG\r\n\x1a\n" + bytes(8)) == "image/png"
    assert io.detect_media("", b"GIF89a" + bytes(8)) == "image/gif"
    assert io.detect_media("", b"\xff\xd8\xff" + bytes(8)) == "image/jpeg"
    assert io.detect_media("", b"RIFF\x00\x00\x00\x00WAVE") == "audio/wav"
    assert io.detect_media("", b"\x00\x00\x00\x18ftypisom") == "video/mp4"


def test_detect_by_extension():
    assert io.detect_media("a.csv") == "text/csv"
    assert io.detect_media("a.dlm") == "application/x-dlm"
    assert io.detect_media("weird.xyz") == "application/octet-stream"


# --- text / datasets -------------------------------------------------------
def test_text_sentences():
    b = io.decode("Tom is a cat. A cat is an animal.\n", "text/plain", name="s.txt")
    assert b.kind == "text" and b.name == "s.txt"
    assert b.sentences == ("Tom is a cat.", "A cat is an animal.")


def test_csv_atoms_and_roles():
    csv = "pred,subj,obj\nis_a,cat,animal\nis_a,tom,cat\n"
    b = io.decode(csv, "text/csv")
    assert b.kind == "table" and b.columns == ("pred", "subj", "obj")
    assert [dump(atom_to_form(a)) for a in b.atoms] == ["(is_a cat animal)", "(is_a tom cat)"]
    # explicit roles for a headerless/oddly-named table
    tsv = "tom\tcat\nparis\tfrance\n"
    b2 = io.decode(tsv, "text/tab-separated-values", header=False,
                   roles={"pred": -1, "subj": 0, "obj": 1})
    assert b2.media == "text/tab-separated-values"


def test_json_and_ndjson():
    b = io.decode('[{"pred":"is_a","subj":"tom","obj":"cat"}]', "application/json")
    assert [str(a.pred) for a in b.atoms] == ["is_a"]
    assert io.decode('["hi.", "there."]', "application/json").sentences == ("hi.", "there.")
    nb = io.decode('{"pred":"is_a","subj":"cat","obj":"animal"}\n', "application/x-ndjson")
    assert [dump(atom_to_form(a)) for a in nb.atoms] == ["(is_a cat animal)"]


def test_dlm_form_roundtrip_preserves_atoms_rules_frames():
    atoms = [Atom(Const("is_a"), (Const("tom"), Const("cat")))]
    from dlm.ssl import FRAMES
    src = io.encode(atoms, "application/x-dlm")
    src += "\n" + frame_sexp(FRAMES[0])
    b = io.decode(src, "application/x-dlm")
    assert [dump(atom_to_form(a)) for a in b.atoms] == ["(is_a tom cat)"]
    assert b.frames and frame_sexp(b.frames[0]) == frame_sexp(FRAMES[0])


# --- media metadata --------------------------------------------------------
def test_png_gif_jpeg_wav_mp4_metadata():
    png = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + \
        struct.pack(">II", 640, 480) + b"\x08\x02\x00\x00\x00"
    b = io.decode(png, "image/png", name="p.png")
    assert b.meta_dict()["width"] == "640" and b.meta_dict()["height"] == "480"

    gif = b"GIF89a" + struct.pack("<HH", 320, 240) + b"\x00\x00\x00"
    assert io.decode(gif, "image/gif").meta_dict()["width"] == "320"

    jpeg = (b"\xff\xd8\xff\xe0" + struct.pack(">H", 16) + bytes(16)
            + b"\xff\xc0" + struct.pack(">H", 17) + b"\x08"
            + struct.pack(">HH", 480, 640) + b"\x03" + bytes(9))
    jb = io.decode(jpeg, "image/jpeg")
    assert jb.meta_dict()["width"] == "640" and jb.meta_dict()["height"] == "480"

    wav = (b"RIFF" + struct.pack("<I", 36) + b"WAVE" + b"fmt " + struct.pack("<I", 16)
           + struct.pack("<HHI", 1, 2, 44100) + struct.pack("<IHH", 176400, 4, 16))
    wb = io.decode(wav, "audio/wav")
    assert wb.meta_dict()["sample_rate"] == "44100" and wb.meta_dict()["channels"] == "2"

    mp4 = b"\x00\x00\x00\x18ftypisom" + bytes(8)
    assert io.decode(mp4, "video/mp4").meta_dict()["brand"] == "isom"


def test_media_atoms_and_octet_digest():
    png = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + \
        struct.pack(">II", 1, 1) + b"\x08\x02\x00\x00\x00"
    b = io.decode(png, "image/png", name="p.png")
    preds = sorted(str(a.pred) for a in io.media_atoms(b))
    assert preds == ["height", "media_kind", "nbytes", "width"]
    assert io.decode(b"abc", "application/octet-stream").meta_dict()["sha1"] == \
        __import__("hashlib").sha1(b"abc").hexdigest()


# --- natural-language egress ----------------------------------------------
def test_atom_to_sentence_and_unknown_predicate():
    assert io.encode(Atom(Const("is_a"), (Const("tom"), Const("cat"))), "text/plain") == "tom a kind of cat"
    # unknown predicate falls back to its own words, never crashes
    assert io.encode(Atom(Const("likes_x"), (Const("tom"), Const("fish"))), "text/plain") == "tom likes x fish"


def test_result_to_text_and_block():
    atoms = [Atom(Const("is_a"), (Const("tom"), Const("cat")))]
    assert "tom" in io.result_to_text(atoms)
    b = io.decode("hello there", "text/plain")
    assert io.result_to_text(b) == "hello there"


def test_encode_csv_json_sexp():
    a = Atom(Const("is_a"), (Const("tom"), Const("cat")))
    assert io.encode([a], "text/csv") == "pred,subj,obj\nis_a,tom,cat\n"
    assert '"pred": "is_a"' in io.encode(a, "application/json")
    assert io.encode([a], "application/x-dlm") == "(is_a tom cat)"


# --- registry + files ------------------------------------------------------
def test_register_replaces_and_rejects():
    with pytest.raises(KeyError):
        io.register_reader("text/plain", lambda p, **k: p)
    with pytest.raises(KeyError):
        io.encode(1, "text/nope")
    io.register_writer("text/x-up", lambda v, **k: str(v).upper(), replace=True)
    assert io.encode("hi", "text/x-up") == "HI"


def test_file_roundtrip(tmp_path):
    p = tmp_path / "facts.csv"
    a = [Atom(Const("is_a"), (Const("tom"), Const("cat")))]
    io.write_file(p, a, "text/csv")
    b = io.read_file(p)
    assert [dump(atom_to_form(x)) for x in b.atoms] == ["(is_a tom cat)"]


def test_determinism():
    csv = "pred,subj,obj\nis_a,cat,animal\n"
    assert io.decode(csv, "text/csv") == io.decode(csv, "text/csv")
    assert io.encode([Atom(Const("is_a"), (Const("a"), Const("b")))], "text/csv") == \
        io.encode([Atom(Const("is_a"), (Const("a"), Const("b")))], "text/csv")


# --- end-to-end: data -> logic -> kernel -> text ---------------------------
def test_pipeline_data_to_kernel_to_nl():
    b = io.decode("pred,subj,obj\nis_a,cat,animal\n", "text/csv")
    kb = KnowledgeBase()
    for a in b.atoms:
        kb.add_fact(a)
    kb.add_rule(Rule(Atom(Const("animal"), (Var("x"),)),
                     (Atom(Const("is_a"), (Var("x"), Const("animal"))),)))
    proved = closure(kb)
    assert "(animal cat)" in [dump(atom_to_form(a)) for a in proved]
    assert "cat animal" in io.result_to_text(proved)
