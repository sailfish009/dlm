#!/usr/bin/env python3
"""Review probes, NOT a web learner or a regression suite requiring fixes.

Uses seeded cache records, fake responses and native subprocesses. No HTTP server,
DNS lookup or network request is needed. A reproduced defect is an observation,
not a passing product requirement. All mutable experiment data stays in tempdirs.
Run from any directory; stdout is the review evidence JSON.
"""
from __future__ import annotations

import base64
import http.client
import importlib.util
import json
import os
from pathlib import Path
import resource
import socket
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("review89_web", ROOT / "adapters/web.py")
web = importlib.util.module_from_spec(spec)
spec.loader.exec_module(web)
resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def deny_network(*args, **kwargs):
    raise AssertionError("review probe must not access the network")


# Guard Python probes. Child acquisition commands additionally use --offline;
# native subprocesses only load source files and temporary local data.
socket.create_connection = deny_network
socket.getaddrinfo = deny_network
socket.socket.connect = deny_network
socket.socket.connect_ex = deny_network


def native(code):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".l") as driver:
        driver.write(code)
        driver.flush()
        proc = subprocess.run([str(ROOT / "scripts/run.sh"), "proof", driver.name],
                              text=True, capture_output=True, timeout=60)
    return {"returncode": proc.returncode, "stdout": proc.stdout.strip(),
            "stderr": proc.stderr[-2000:]}


def record(raw=b"offline review fixture; not an independently verified world fact"):
    return dict(url="https://example.invalid/review89/document", final_url="https://example.invalid/review89/document",
                media_type="text/plain; charset=utf-8", fetched_at="2026-01-01T00:00:00Z",
                sha256=web.digest(raw), raw_base64=base64.b64encode(raw).decode("ascii"))


def cached_record(cache, value):
    path = Path(cache) / "fetch" / (web.digest(value["url"].encode()) + ".json")
    web.atomic_write(path, json.dumps(value).encode())


def main():
    results = {"scope": "copied 0088 implementation in 0089 review workspace",
               "network": "none: seeded cache / fake responses / local files only",
               "product_changes": False, "probes": {}}
    probes = results["probes"]
    original = record()
    form = web.document_form(original)
    batch = "(acquisition 74 (" + form + ") ())"

    with tempfile.TemporaryDirectory(prefix="dlm89-review-") as directory:
        root = Path(directory)
        cache = root / "web-store/cache"
        cached_record(cache, original)
        env = dict(os.environ, STORE=str(root / "web-store"))
        cmd = [str(ROOT / "scripts/web.sh"), "--offline", "--url", original["url"]]
        runs = [subprocess.run(cmd, env=env, text=True, capture_output=True, timeout=60)
                for _ in range(2)]
        probes["offline_acquisition_and_repeat"] = [
            {"returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr[-2000:]}
            for p in runs]
        probes["offline_cache_miss"] = web.CachedWeb(cache, offline=True).get_record(
            "https://example.invalid/review89/absent")[1]
        bad = dict(original, sha256="0" * 64)
        cached_record(cache, bad)
        probes["python_cache_hash_corruption"] = web.CachedWeb(cache, offline=True).get_record(original["url"])[1]

        probes["web_ingest_does_not_feed_native_learning"] = native(f"""
(define review-web-state (web-ingest (web-new) '{batch}))
(dlm 'step) (dlm 'step)
(dump (list 'documents (dlm-length (dlm-nth review-web-state 2))
            'native-episodes (dlm-length (a77-episodes *dlm-model*))
            'native-definitions (dlm-length (a77-defs *dlm-model*))
            'contract-goals (dlm-length (dlm 'goals)))) (print "\\n")
""")

        changed_raw = web.document_form(dict(original, raw_base64=base64.b64encode(b"different bytes").decode()))
        changed_group = form.replace("(source-group c" + original["sha256"] + ")", "(source-group arbitrary89)")
        changed_id = "(document arbitrary89 " + form.split(" ", 2)[2]
        checks = []
        for name, document in (("raw-hash-mismatch", changed_raw),
                               ("source-group-mismatch", changed_group),
                               ("document-id-mismatch", changed_id)):
            checks.append(f"(let ((s (web-ingest (web-new) '(acquisition 74 ({document}) ())))) (dump (list '{name} (equal s (web-verify-state s))))) (print \"\\n\")")
        probes["native_replay_accepts_consistently_forged_integrity_fields"] = native("\n".join(checks))
        probes["malformed_document"] = native("(dump (web-document? (cons 'document 42)))")
        probes["malformed_incoming_collection"] = native("(dump (web-ingest (web-new) '(acquisition 74 42 ())))")

        growth = []
        raw_field = "(raw h" + base64.b64decode(original["raw_base64"]).hex() + ")"
        for count in (1, 8, 16):
            result = native(f"(define state89 (web-new)) (times-do {count} (set state89 (web-ingest state89 '{batch}))) (dump state89)")
            growth.append(dict(acquisitions=count, returncode=result["returncode"],
                               snapshot_bytes=len(result["stdout"].encode()),
                               raw_payload_occurrences=result["stdout"].count(raw_field)))
        probes["unchanged_document_reacquisition_growth"] = growth

        probes["ninth_native_episode"] = native("""
(define i89 0)
(times-do 8 (dlm 'observe (concat-strings "source89-" (number->string i89)) '((atom edge (a b)))) (set i89 (+ i89 1)))
(dump (list 'episodes (dlm-length (a77-episodes *dlm-model*)) 'ninth (dlm 'observe 'ninth89 '((atom edge (c d)))))) (print "\\n")
""")
        probes["recursive_definition_is_not_a_new_primitive_fact"] = native("""
(dlm 'demo) (dlm 'search 'nd-ucb) (set *dlm-pair-budget* 4)
(times-do 4 (dlm 'step))
(dump (list 'definitions (dlm-length (a77-defs *dlm-model*))
 'primitive-edge (car (dlm 'query 'demo-a '(atom edge (a e))))
 'composed-path (car (dlm 'query 'demo-a '(atom "c77-2" (a e)))))) (print "\\n")
""")
        snapshot = json.dumps(str(root / "routing.sexp"))
        probes["inherited_routing_checkpoint_process_a"] = native(f"""
(dlm 'open {snapshot}) (dlm 'demo) (dlm 'ground 'on)
(dlm 'curriculum 'relations) (dlm 'relation-budget 1)
(dump (dlm 'step)) (print "\\n") (dump (dlm 'step)) (print "\\n")
(dump (dlm 'save)) (print "\\n")
""")
        probes["inherited_routing_checkpoint_process_b"] = native(f"(dump (dlm 'open {snapshot})) (print \"\\n\")")

        class TruncatedResponse:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self, size):
                raise http.client.IncompleteRead(b"partial", 100)

        class FakeOpener:
            def open(self, *args, **kwargs):
                return TruncatedResponse()

        client = web.CachedWeb(root / "fake-http")
        client.opener = FakeOpener()
        try:
            _, error = client.get_record(original["url"])
            probes["truncated_http_response"] = {"returned_error": error}
        except Exception as exc:
            probes["truncated_http_response"] = {"uncaught_exception": type(exc).__name__}

    probes["url_policy_accepts_private_targets_without_network"] = {
        url: web.valid_url(url) for url in (
            "http://127.0.0.1/private", "http://169.254.169.254/latest/meta-data/",
            "http://[::1]/private")}
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
