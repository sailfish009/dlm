import json

import pytest

from dlm import Atom, Store, episode_ir, evaluate_expr, new_state, node_id


def A(pred, *args):
    return Atom(pred, args)


def state():
    episode = episode_ir("s", {A("edge", "a", "b"), A("edge", "b", "c")},
                         {A("reach", "a", "c")}, role="validation")
    return new_state((episode,))


def test_snapshot_journal_replay_and_rebuildable_index(tmp_path):
    store = Store(tmp_path / "store")
    initial = state()
    store.create(initial)
    transition = evaluate_expr(("step", 64), initial)
    after = store.append(initial, transition)
    assert store.load() == after
    index = json.loads(store.index.read_text())
    assert index["root"] == node_id(after)
    assert index["journal_transitions"] == 1
    assert index["experience"] == 1


def test_journal_tampering_is_rejected(tmp_path):
    store = Store(tmp_path / "store")
    initial = state()
    store.create(initial)
    transition = evaluate_expr(("step", 64), initial)
    store.append(initial, transition)
    store.journal.write_text(store.journal.read_text().replace("learn-round", "forged"))
    with pytest.raises(ValueError, match="line 1"):
        store.load()


def test_append_refuses_a_fork_behind_the_disk_tip(tmp_path):
    store = Store(tmp_path / "store")
    initial = state()
    store.create(initial)
    store.append(initial, evaluate_expr(("step", 64), initial))
    with pytest.raises(ValueError, match="journal tip"):
        store.append(initial, evaluate_expr(("step", 1), initial))


def test_checkpoint_keeps_old_journal_as_audit_archive(tmp_path):
    store = Store(tmp_path / "store")
    initial = state()
    store.create(initial)
    after = store.append(initial, evaluate_expr(("step", 64), initial))
    store.checkpoint(after)
    assert (store.root / "experience.0.irlog").exists()
    assert store.journal.read_text() == ""
    assert store.load() == after
