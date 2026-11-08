#!/usr/bin/env python3
"""Disposable consumer pilot. Only writes temporary repositories; no network credentials."""
import copy
import datetime as dt
import json
from pathlib import Path
import tempfile
from test_opkit import fixture, k, run_git


def pilot():
    results = []
    now = dt.datetime.now(dt.timezone.utc)
    with tempfile.TemporaryDirectory(prefix="opkit-pilot-") as tmp:
        root = Path(tmp); repo = root / "consumer"; repo.mkdir()
        m, p = fixture(repo)
        (repo / "src/result.txt").unlink()
        run_git(repo, "init", "-b", "main")
        run_git(repo, "config", "user.name", "Disposable pilot")
        run_git(repo, "config", "user.email", "pilot@example.invalid")
        bare = root / "origin.git"; run_git(root, "init", "--bare", str(bare))
        run_git(repo, "remote", "add", "origin", str(bare))
        run_git(repo, "add", "."); run_git(repo, "commit", "-m", "approved base")
        base = run_git(repo, "rev-parse", "HEAD"); run_git(repo, "push", "-u", "origin", "main")
        run_git(repo, "switch", "-c", "codex/pilot")
        (repo / "src/result.txt").write_text("result")
        run_git(repo, "add", "."); run_git(repo, "commit", "-m", "candidate result")
        head = run_git(repo, "rev-parse", "HEAD")
        assert k.verify_candidate(p, m, repo, repo, base, head, []) == head
        hashes = {"src/result.txt": k.digest(b"result")}
        provenance = {path: {"source": "codex/pilot@" + head, "sha256": sha, "modification": "none"} for path, sha in hashes.items()}
        reviews = [{"id": "pilot-review", "review_of": p["id"], "envelope_sha256": p["envelope"]["sha256"],
                    "reviewer": {"name": "reviewer", "surface": "fresh"}, "context_id": "pilot-fresh-review",
                    "outputs": hashes, "verdict": "pass", "blocking_findings": [], "disposition": "current", "evidence": "disposable fixture review"}]

        def check(event, approvals=None, reviews_override=None):
            return k.transition(event, p, copy.deepcopy(p), m, repo, repo, m[k.TRANSITIONS[event][1]],
                                approvals or [], [], reviews if reviews_override is None else reviews_override,
                                provenance, now)

        for event in ["dispatch", "land"]:
            receipt = check(event); p["status"] = receipt["proposed_status"]
            results.append({"event": event, "passed": True})
        bad = copy.deepcopy(reviews); bad[0]["verdict"] = "fail"; bad[0]["blocking_findings"] = ["fixture blocking finding"]
        try:
            check("accept", reviews_override=bad)
            raise AssertionError("failing review accepted")
        except k.Invalid:
            results.append({"event": "failing-review-denied", "passed": True})
        p["status"] = check("accept")["proposed_status"]
        results.append({"event": "accept-after-fresh-pass", "passed": True})
        try:
            check("external-action")
            raise AssertionError("unapproved action accepted")
        except k.Invalid:
            results.append({"event": "unapproved-external-action-denied", "passed": True})
        approval = {"id": "PILOT-1", "approver": m["owner"], "task": p["task"], "envelope_sha256": p["envelope"]["sha256"],
                    "gate": "external-action", "action": p["action"], "environment": p["environment"], "status": "active",
                    "not_before": (now - dt.timedelta(minutes=1)).isoformat(), "expires_at": (now + dt.timedelta(minutes=1)).isoformat(),
                    "evidence": "synthetic approval; not a real human authorization"}
        assert not check("external-action", [approval])["state_changed"]
        results.append({"event": "approved-action-check-only-no-execution", "passed": True})
        run_git(repo, "push", "-u", "origin", "codex/pilot")
        remote = k.verify_remote(repo, "origin", "codex/pilot", head, list(hashes))
        assert remote["paths"] == hashes
        results.append({"event": "feature-branch-remote-receipt", "passed": True})
        run_git(repo, "remote", "set-url", "origin", str(root / "unreachable"))
        before = run_git(repo, "rev-parse", "HEAD")
        try:
            k.verify_remote(repo, "origin", "codex/pilot", head, list(hashes))
            raise AssertionError("unreachable remote passed")
        except k.Invalid:
            assert run_git(repo, "rev-parse", "HEAD") == before
            assert (repo / "src/result.txt").read_text() == "result"
        run_git(repo, "remote", "set-url", "origin", str(bare))
        assert k.verify_remote(repo, "origin", "codex/pilot", head, list(hashes))["remote_verified"]
        results.append({"event": "interrupted-verification-retry-without-data-loss", "passed": True})
        assert k.risk_tier(m, repo, [{"path": "src/typo.txt", "operation": "add"}], []) == "micro"
        assert k.risk_tier(m, repo, [{"path": "src/result.txt", "operation": "delete"}], []) == "protected"
        results.append({"event": "micro-versus-destructive-classification", "passed": True})
    return {"pilot": "passed", "scenarios": results, "host_authentication": "not certified",
            "production_actions": "none", "consumer_adoption": "none"}


if __name__ == "__main__":
    print(json.dumps(pilot(), indent=2))
