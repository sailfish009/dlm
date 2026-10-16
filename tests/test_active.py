import pytest

from dlm import (Atom, Store, acquire_once, acquisition_transition,
                 commit_transition, episode_ir, field, information_needs,
                 lower_paths, new_state, next_need, source_document)


def A(pred, *args):
    return Atom(pred, args)


def proof_hole_state():
    return new_state((episode_ir("task", {A("premise", "a")},
                                         {A("goal", "a")}),))


def test_model_derives_and_records_its_own_external_information_need(tmp_path):
    state = proof_hole_state()
    need = next_need(state)
    assert field(need, "kind")[1] == "proof-hole"
    assert "goal" in field(need, "query")[1]
    document = source_document(
        provider="wikipedia", uri="https://example.test/a", title="A",
        content="Alpha uses Beta.", source_group="wikipedia:a")
    transition = acquisition_transition(state, need, (document,))
    after = commit_transition(state, transition)
    record = field(field(after, "agenda"), "acquisitions")[-1]
    assert field(record, "need")[1] == need
    assert field(record, "status")[1] == "acquired"
    assert field(after, "documents")[1:] == (document,)

    store = Store(tmp_path / "store")
    store.create(state)
    persisted = store.append(state, transition)
    assert store.load() == persisted


class FakeWikipedia:
    def get_json(self, url):
        if "w/api.php" in url:
            return {"query": {"search": [{"title": "A"}]}}
        return {"title": "A", "pageid": 1, "revision": 3,
                "extract": "Alpha uses Beta.",
                "content_urls": {"desktop": {"page": "https://w.example/A"}}}


def test_round_can_query_a_provider_from_the_model_selected_need(tmp_path):
    state = proof_hole_state()
    transition = acquire_once(state, cache_dir=tmp_path, offline=False,
                              providers=("wikipedia",), limit=1,
                              web=FakeWikipedia())
    assert transition is not None
    after = commit_transition(state, transition)
    record = field(field(after, "agenda"), "acquisitions")[-1]
    assert field(record, "status")[1] == "acquired"
    assert len(field(after, "documents")) == 2


def test_offline_miss_is_an_abstention_and_remains_retryable():
    state = proof_hole_state()
    need = next_need(state)
    after = commit_transition(state, acquisition_transition(state, need, ()))
    record = field(field(after, "agenda"), "acquisitions")[-1]
    assert field(record, "status")[1] == "abstained"
    assert field(next_need(after), "id")[1] == field(need, "id")[1]


def test_caller_cannot_substitute_a_different_query():
    state = proof_hole_state()
    need = next_need(state)
    forged = tuple(("query", "unrelated") if isinstance(item, tuple) and item[0] == "query"
                   else item for item in need)
    with pytest.raises(ValueError, match="current next need"):
        acquisition_transition(state, forged, ())


def test_unresolved_source_symbol_becomes_a_need(tmp_path):
    source = tmp_path / "subject.py"
    source.write_text("def f():\n    external_api()\n")
    package = lower_paths((source,), tmp_path)
    subject = ("source-subject", ("sha256", "fixture"), ("pyir", package))
    state = new_state((), subject=subject)
    needs = information_needs(state)
    matching = [need for need in needs
                if field(need, "kind")[1] == "unresolved-symbol"
                and "external_api" in field(need, "query")[1]]
    assert matching
    assert field(matching[0], "providers")[1] == "github"
