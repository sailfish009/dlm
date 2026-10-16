import argparse
import base64

import pytest

from dlm import (Atom, CachedWeb, Store, acquire_documents, atom_from_ir, commit_transition,
                 document_to_episode, field, ingest_transition, new_state,
                 source_document, validate_document)
from dlm.ir import replace_field


def facts(episode):
    return {atom_from_ir(atom) for atom in field(episode, "facts")[1:]}


def test_transport_cache_replays_bytes_offline(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("cached evidence")
    url = source.as_uri()
    assert CachedWeb(tmp_path / "cache").get_text(url) == "cached evidence"
    source.unlink()
    assert CachedWeb(tmp_path / "cache", offline=True).get_text(url) == "cached evidence"


def test_external_text_becomes_a_complete_typed_document_tree():
    document = source_document(
        provider="wikipedia", uri="https://example.test/python", title="Python",
        content="<p>Python is a programming language.</p><p>Python uses indentation.</p>",
        media_type="text/html", source_group="wikipedia:python", revision="7")
    validate_document(document)
    assert field(document, "document-tree")[0] == "document-tree"
    assert len(field(document, "claims")) == 3
    episode = document_to_episode(document)
    assert facts(episode) == {
        Atom("is-a", ("python", "programming language")),
        Atom("uses", ("python", "indentation")),
    }
    assert field(episode, "source")[1] == "wikipedia:python"
    assert field(episode, "document-id")[1] == field(document, "id")[1]


def test_uncertain_or_guessed_text_remains_in_ir_but_not_kernel_evidence():
    uncertain = source_document(
        provider="search", uri="https://example.test/rumor", title="Rumor",
        content="Alpha might use Beta. Alpha is not a database.",
        source_group="search:rumor")
    assert field(uncertain, "content")[1]
    assert not facts(document_to_episode(uncertain))
    guessed = source_document(
        provider="search", uri="https://example.test/guess", title="Guess",
        content="Alpha uses Beta.", source_group="search:guess", trust="guessed")
    assert field(guessed, "claims")[1:]
    assert not facts(document_to_episode(guessed))


def test_python_source_uses_ast_without_execution():
    document = source_document(
        provider="github", uri="https://example.test/tool.py", title="tool.py",
        content="import os\n\ndef helper():\n    return 1\n\ndef run():\n    helper()\n    return dangerous()\n",
        media_type="text/x-python", source_group="github:o/r", revision="abc")
    episode = document_to_episode(document)
    assert Atom("imports", ("tool.py", "os")) in facts(episode)
    assert Atom("defines", ("tool.py", "run")) in facts(episode)
    assert Atom("calls", ("tool.py.run", "helper")) in facts(episode)
    assert Atom("calls", ("tool.py.run", "dangerous")) not in facts(episode)
    assert "python-tree" in {item[0] for item in field(document, "document-tree")[1:]}


def test_ingest_is_recomputed_then_journaled_and_replayed(tmp_path):
    document = source_document(
        provider="github", uri="https://example.test/readme", title="o/r",
        content="DLM depends on Python.", media_type="text/markdown",
        source_group="github:o/r", revision="abc")
    initial = new_state(())
    transition = ingest_transition(initial, (document,))
    after = commit_transition(initial, transition)
    forged = replace_field(transition, "after", ("after", initial))
    with pytest.raises(ValueError, match="re-verification"):
        commit_transition(initial, forged)
    assert field(after, "documents")[1:] == (document,)
    assert Atom("depends-on", ("dlm", "python")) in facts(field(after, "evidence")[1])
    store = Store(tmp_path / "store")
    store.create(initial)
    persisted = store.append(initial, transition)
    assert store.load() == persisted == after
    assert field(store.load(), "documents")[1:] == (document,)


def test_document_integrity_tampering_is_rejected():
    document = source_document(provider="web", uri="https://example.test/a",
                               title="A", content="A uses B.")
    tampered = replace_field(document, "content", ("content", "A uses C."))
    with pytest.raises(ValueError, match="hash"):
        validate_document(tampered)
    forged_claims = replace_field(document, "claims", ("claims",))
    with pytest.raises(ValueError, match="not canonical"):
        validate_document(forged_claims)


class FakeWeb:
    def get_json(self, url):
        if "w/api.php" in url:
            return {"query": {"search": [{"title": "DLM"}]}}
        if "page/summary" in url:
            return {"title": "DLM", "pageid": 10, "revision": 2,
                    "extract": "DLM is a reasoning system.",
                    "content_urls": {"desktop": {"page": "https://w.example/DLM"}}}
        if "search/repositories" in url:
            return {"items": [{"full_name": "o/r", "html_url": "https://github.com/o/r",
                                "default_branch": "main", "description": "fallback"}]}
        if "/repos/o/r/readme" in url:
            return {"content": base64.b64encode(b"DLM uses IR trees.").decode(), "sha": "abc"}
        if "stackexchange" in url:
            return {"items": [{"question_id": 42, "title": "DLM",
                                "body": "<p>DLM depends on evidence.</p>",
                                "link": "https://stackoverflow.com/q/42",
                                "last_activity_date": 9}]}
        return None


def test_heterogeneous_acquisition_produces_one_ir_document_contract(tmp_path):
    documents = acquire_documents(
        "DLM", cache_dir=tmp_path, web=FakeWeb(), limit=1,
        providers=("wikipedia", "github", "web-search"))
    assert len(documents) == 3
    providers = {field(field(document, "provenance"), "provider")[1]
                 for document in documents}
    assert providers == {"wikipedia", "github", "web-search"}
    for document in documents:
        validate_document(document)
        assert field(document, "content")[1]
        assert field(document, "normalized")[1]
        assert field(document, "claims")[1:]


def test_ingest_experiment_accepts_local_text_and_resumes(tmp_path):
    path = tmp_path / "source.md"
    path.write_text("DLM uses typed IR trees.\n")
    args = argparse.Namespace(
        store=tmp_path / "store", fresh=True, file=[str(path)], url=[], query="",
        cache=tmp_path / "cache", offline=True, max_bytes=10000,
        providers="wikipedia,github,web-search", limit=1, min_confidence=.85)
    from experiments.ingest.run import run
    first = run(args)
    assert first["status"] == "ingested" and first["new_documents"] == 1
    args.fresh = False
    second = run(args)
    assert second["status"] == "abstain-no-new-document"
    assert second["total_documents"] == 1


class MirrorWeb(FakeWeb):
    def get_json(self, url):
        data = super().get_json(url)
        if "page/summary" in url:
            data["extract"] = "DLM uses IR trees."
        elif "/repos/o/r/readme" in url:
            data["content"] = base64.b64encode(b"DLM uses IR trees.").decode()
        elif "stackexchange" in url:
            data["items"][0]["body"] = "DLM uses IR trees."
        return data


def test_exact_mirrors_do_not_fake_independent_sources(tmp_path):
    documents = acquire_documents("DLM", cache_dir=tmp_path, web=MirrorWeb(), limit=1)
    groups = {field(field(document, "provenance"), "source-group")[1]
              for document in documents}
    assert len(groups) == 1
    assert next(iter(groups)).startswith("content:")


def test_extractor_is_candidate_blind_and_deterministic():
    kwargs = dict(provider="web", uri="https://example.test/x", title="X",
                  content="Alpha uses Beta.", source_group="web:x")
    assert source_document(**kwargs) == source_document(**kwargs)
