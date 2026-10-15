"""DLM v0.0039 tests: the online streaming instrument logs a sound trajectory."""
import json

from experiments.online.run import online_run, run, analyze, ARMS, RECORD_FIELDS

CFG = dict(n_train=10, n_test=8, chains=1, chain_len=4, rounds=3, max_body=2,
           extra_vars=1, max_rules=4, max_neg=2000, depth_cap=4)


def test_record_shape_and_rounds():
    rows = online_run("plain", 0, **CFG)
    assert len(rows) == CFG["rounds"]
    assert set(RECORD_FIELDS) <= set(rows[0])
    assert [r["round"] for r in rows] == [1, 2, 3]
    assert all(r["arm"] == "plain" and r["seed"] == 0 for r in rows)
    # rich facets are present and sane
    assert all(r["train_recovery"] >= r["held_recovery"] - 1e-9 for r in rows)
    assert all(isinstance(r["intra_curve"], list) for r in rows)
    assert rows[-1]["max_depth"] >= 0


def test_frozen_asserts_nothing():
    rows = online_run("frozen", 0, **CFG)
    assert all(r["false_assert"] == 0 for r in rows)
    assert all(r["clauses"] == 0 for r in rows)


def test_determinism():
    # wall-clock `learn_seconds` is the only volatile field; everything else is exact.
    a = online_run("plain", 1, **CFG)
    b = online_run("plain", 1, **CFG)
    strip = lambda rows: [{k: v for k, v in r.items() if k != "learn_seconds"} for r in rows]
    assert strip(a) == strip(b)


def test_learning_beats_frozen_on_unseen_entities():
    frozen = online_run("frozen", 0, **CFG)[-1]["held_recovery"]
    plain = online_run("plain", 0, **CFG)[-1]["held_recovery"]
    assert plain > frozen


def test_run_and_analyze(tmp_path):
    rows, agg = run("plain", [0, 1], CFG)
    assert agg["arm"] == "plain" and agg["final_held_recovery"] >= 0
    assert len(agg["curve"]) == CFG["rounds"]
    frozen, _ = run("frozen", [0, 1], CFG)
    for arm, all_rows in (("plain", rows), ("frozen", frozen)):
        for s in (0, 1):
            sub = [r for r in all_rows if r["seed"] == s]
            with open(tmp_path / f"{arm}_s{s}.jsonl", "w", encoding="utf-8") as fh:
                for r in sub:
                    fh.write(json.dumps(r) + "\n")
    text, table = analyze(tmp_path)
    assert "plain" in table and "plain" in text
    for aspect in ("[coverage]", "[soundness]", "[generalisation]", "[dynamics]",
                   "[intra-round]", "[verdict]"):
        assert aspect in text
    assert set(ARMS) == {"frozen", "plain", "abstract", "random"}