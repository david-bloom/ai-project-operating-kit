import copy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("opkit", ROOT / "scripts/opkit.py")
k = importlib.util.module_from_spec(spec)
spec.loader.exec_module(k)
NOW = dt.datetime(2026, 11, 8, 12, tzinfo=dt.timezone.utc)


def fixture(root):
    (root / "policy.md").write_text("approved test policy")
    (root / "src").mkdir(exist_ok=True)
    (root / "src/input.txt").write_text("input")
    (root / "src/result.txt").write_text("result")
    m = {
        "schema_version": 1, "project": "demo", "core": {"version": k.VERSION, "path": "policy.md", "sha256": k.digest(b"approved test policy")},
        "source_of_truth": {"repo": "owner/demo", "branch": "main"},
        "owner": {"name": "david", "surface": "human"}, "orchestrator": {"name": "codex", "surface": "local"},
        "steward": {"name": "bot", "surface": "ci"},
        "actors": [
            {"name": "david", "surface": "human", "roles": ["owner"], "delivery": "branch", "authority": "full"},
            {"name": "codex", "surface": "local", "roles": ["orchestrator", "worker"], "delivery": "branch", "authority": "full"},
            {"name": "codex", "surface": "cloud", "roles": ["worker"], "delivery": "branch", "authority": "none"},
            {"name": "bot", "surface": "ci", "roles": ["steward"], "delivery": "publisher", "authority": "full"},
            {"name": "reviewer", "surface": "fresh", "roles": ["reviewer"], "delivery": "branch", "authority": "none"}],
        "defaults": {"tier": "micro", "isolation": "open"}, "allowed_outputs": ["src", "docs", "scripts"],
        "protected_paths": ["src/locked/*"], "hard_gates": [], "profiles": []}
    p = {"schema_version": 1, "id": "demo/001", "task": "WORK-001", "actor": m["orchestrator"], "context_id": "implementation-1",
         "lane": "routine", "tier": "governed", "status": "ready", "isolation": {"mode": "open", "withhold": [], "lift_when": None},
         "inputs": {"src/input.txt": k.digest(b"input")}, "outputs": ["src/result.txt"],
         "changes": [{"path": "src/result.txt", "operation": "add"}], "risks": [], "required_reviews": "independent",
         "review_of": None, "review_target": None, "supersedes": None, "revises": None,
         "required_approvals": {e: [] for e in ["dispatch", "land", "accept", "external-action", "done"]},
         "environment": "development", "action": "produce-result", "instructions": "Produce a result.", "amendments": []}
    return m, k.freeze(p, m, root)


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.m, self.p = fixture(self.root)

    def frozen(self, mutate):
        mutate(self.p); self.p["status"] = "ready"; self.p = k.freeze(self.p, self.m, self.root)

    def evidence(self):
        hashes = {"src/result.txt": k.digest(b"result")}
        return {"provenance": {x: {"source": "branch@full-sha", "sha256": h, "modification": "none"} for x, h in hashes.items()},
                "reviews": [{"id": "review/1", "review_of": self.p["id"], "envelope_sha256": self.p["envelope"]["sha256"],
                             "reviewer": {"name": "reviewer", "surface": "fresh"}, "context_id": "review-context-1",
                             "outputs": hashes, "verdict": "pass", "blocking_findings": [], "disposition": "current", "evidence": "review report"}]}

    def approval(self, gate):
        return {"id": "APPROVAL-" + gate, "approver": self.m["owner"], "task": self.p["task"],
                "envelope_sha256": self.p["envelope"]["sha256"], "gate": gate, "action": self.p["action"],
                "environment": self.p["environment"], "status": "active", "not_before": "2026-11-08T00:00:00Z",
                "expires_at": "2026-11-09T00:00:00Z", "evidence": "owner decision on authoritative branch"}

    def run_event(self, event, **overrides):
        role = k.TRANSITIONS[event][1]
        e = self.evidence()
        args = dict(event=event, p=self.p, previous=copy.deepcopy(self.p), m=self.m, root=self.root, candidate=self.root,
                    who=self.m[role], approvals=[], revocations=[], reviews=e["reviews"], provenance=e["provenance"], now=NOW)
        args.update(overrides)
        return k.transition(**args)

    def test_valid_lifecycle(self):
        for event in ["dispatch", "land", "accept", "done"]:
            result = self.run_event(event)
            self.assertFalse(result["state_changed"])
            self.p["status"] = result["proposed_status"]
        self.assertEqual(self.p["status"], "done")

    def test_wrong_actor_all_transitions(self):
        for event, (states, _, _) in k.TRANSITIONS.items():
            with self.subTest(event=event):
                self.p["status"] = sorted(states)[0]
                with self.assertRaisesRegex(k.Invalid, "caller not designated"):
                    self.run_event(event, who={"name": "codex", "surface": "cloud"})

    def test_wrong_surface_cannot_borrow_local_authority(self):
        with self.assertRaises(k.Invalid): self.run_event("dispatch", who={"name": "codex", "surface": "cloud"})

    def test_no_privilege_from_role_string(self):
        with self.assertRaises(k.Invalid): self.run_event("dispatch", who=self.m["owner"])

    def test_invalid_transition(self):
        with self.assertRaisesRegex(k.Invalid, "lifecycle"): self.run_event("accept")

    def test_previous_state_required(self):
        previous = copy.deepcopy(self.p); previous["status"] = "accepted"
        with self.assertRaisesRegex(k.Invalid, "previous state"): self.run_event("dispatch", previous=previous)

    def test_all_authority_fields_frozen(self):
        for field, value in [("actor", {"name": "codex", "surface": "cloud"}), ("context_id", "changed"),
                             ("required_reviews", "none"), ("review_of", "demo/999"), ("revises", "demo/777"),
                             ("environment", "production"), ("action", "deploy"), ("instructions", "different")]:
            with self.subTest(field=field):
                changed = copy.deepcopy(self.p); changed[field] = value
                with self.assertRaises(k.Invalid): k.verify_envelope(changed, self.m)

    def test_approval_fields_frozen(self):
        self.p["required_approvals"]["dispatch"].append("added")
        with self.assertRaises(k.Invalid): k.verify_envelope(self.p, self.m)

    def test_manifest_change_requires_original_snapshot(self):
        self.m["hard_gates"] = ["new-gate"]
        with self.assertRaisesRegex(k.Invalid, "pinned manifest"): k.verify_envelope(self.p, self.m)

    def test_changed_inputs_fail_dispatch(self):
        (self.root / "src/input.txt").write_text("different")
        with self.assertRaisesRegex(k.Invalid, "input snapshot"): self.run_event("dispatch")

    def test_amendments_append_only(self):
        previous = copy.deepcopy(self.p); previous["amendments"] = ["old"]
        self.p["amendments"] = ["rewritten"]
        with self.assertRaisesRegex(k.Invalid, "append-only"): self.run_event("dispatch", previous=previous)

    def test_protected_requires_scope_approval_even_empty_config(self):
        self.frozen(lambda p: p.update(tier="protected", risks=["money"]))
        with self.assertRaisesRegex(k.Invalid, "scope"): self.run_event("dispatch")
        self.assertEqual(self.run_event("dispatch", approvals=[self.approval("scope")])["proposed_status"], "dispatched")

    def test_scope_approval_cannot_authorize_action(self):
        self.p["status"] = "accepted"
        with self.assertRaisesRegex(k.Invalid, "external-action"):
            self.run_event("external-action", approvals=[self.approval("scope")])

    def test_external_action_always_requires_approval(self):
        self.p["status"] = "accepted"
        with self.assertRaises(k.Invalid): self.run_event("external-action")
        self.assertFalse(self.run_event("external-action", approvals=[self.approval("external-action")])["state_changed"])

    def test_approval_wrong_scope_or_revoked(self):
        self.frozen(lambda p: p.update(tier="protected"))
        for field, value in [("approver", self.m["orchestrator"]), ("task", "OTHER"), ("action", "other"),
                             ("environment", "production"), ("status", "revoked"), ("status", "superseded"),
                             ("envelope_sha256", "0" * 64), ("expires_at", "2026-11-08T12:00:00Z"),
                             ("not_before", "2026-11-08T13:00:00Z")]:
            with self.subTest(field=field, value=value):
                a = self.approval("scope"); a[field] = value
                with self.assertRaises(k.Invalid): self.run_event("dispatch", approvals=[a])

    def test_live_revocation_overrides_frozen_approval(self):
        self.frozen(lambda p: p.update(tier="protected")); a = self.approval("scope")
        with self.assertRaises(k.Invalid): self.run_event("dispatch", approvals=[a], revocations=[a["id"]])

    def test_duplicate_approval_id_rejected(self):
        a = self.approval("scope")
        with self.assertRaisesRegex(k.Invalid, "duplicate approval"): self.run_event("dispatch", approvals=[a, a])

    def test_missing_review(self):
        self.p["status"] = "landed"
        with self.assertRaises(k.Invalid): self.run_event("accept", reviews=[])

    def test_review_failure_missing_independence_staleness(self):
        self.p["status"] = "landed"
        for field, value in [("verdict", "fail"), ("context_id", self.p["context_id"]),
                             ("blocking_findings", ["P1 open"]), ("outputs", {"src/result.txt": "0" * 64}),
                             ("envelope_sha256", "0" * 64), ("reviewer", self.m["orchestrator"])]:
            with self.subTest(field=field):
                reviews = self.evidence()["reviews"]; reviews[0][field] = value
                with self.assertRaises(k.Invalid): self.run_event("accept", reviews=reviews)

    def test_missing_verdict(self):
        self.p["status"] = "landed"; reviews = self.evidence()["reviews"]; del reviews[0]["verdict"]
        with self.assertRaises(k.Invalid): self.run_event("accept", reviews=reviews)

    def test_changed_output_invalidates_review(self):
        self.p["status"] = "landed"; (self.root / "src/result.txt").write_text("changed")
        e = self.evidence(); e["provenance"]["src/result.txt"]["sha256"] = k.digest(b"changed")
        with self.assertRaisesRegex(k.Invalid, "stale review"): self.run_event("accept", provenance=e["provenance"])

    def test_missing_and_changed_provenance(self):
        self.p["status"] = "dispatched"
        for prov in [{}, {"src/result.txt": {"source": "branch", "sha256": "0" * 64, "modification": "none"}},
                     {"src/result.txt": {"source": "branch", "sha256": k.digest(b"result"), "modification": "formatting-only"}}]:
            with self.assertRaises(k.Invalid): self.run_event("land", provenance=prov)

    def test_duplicate_keys_and_nonfinite_json(self):
        for data in ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}']:
            with self.assertRaises(k.Invalid): k.parse(data)

    def test_unknown_manifest_and_packet_fields(self):
        self.m["typo"] = 1
        with self.assertRaises(k.Invalid): k.validate_manifest(self.m, self.root)
        del self.m["typo"]; self.p["typo"] = 1
        with self.assertRaises(k.Invalid): k.validate_packet(self.p, self.m, self.root)

    def test_version_and_digest_required(self):
        for version in ["3.0", "3.1", "3.2.0", "unspecified", ""]:
            self.m["core"]["version"] = version
            with self.assertRaises(k.Invalid): k.validate_manifest(self.m, self.root)
        self.m["core"]["version"] = k.VERSION; self.m["core"]["sha256"] = "0" * 64
        with self.assertRaises(k.Invalid): k.validate_manifest(self.m, self.root)

    def test_path_traversal_and_ambiguous_forms(self):
        for path in ["../x", "src/../x", "/tmp/x", "src//x", "src/./x", "src\\x", ".git/config", "-x", "src/x\ny"]:
            with self.subTest(path=path), self.assertRaises(k.Invalid): k.safe_path(path)

    def test_symlinks_refused(self):
        (self.root / "src/link").symlink_to(self.root / "src/result.txt")
        with self.assertRaises(k.Invalid): k.file_in(self.root, "src/link")

    def test_profile_pinning_protection_and_isolation(self):
        profile = {"name": "strict", "version": "1", "minimum_tier": "protected", "requires_isolation": True,
                   "protected_paths": ["src/special/*"], "hard_gates": ["special"]}
        raw = k.canonical(profile); (self.root / "profile.json").write_bytes(raw)
        self.m["profiles"] = [{"name": "strict", "version": "1", "path": "profile.json", "sha256": k.digest(raw)}]
        k.validate_manifest(self.m, self.root)
        with self.assertRaises(k.Invalid): k.validate_packet(self.p, self.m, self.root)
        self.assertTrue(k.protected(self.m, self.root, "src/special/x"))
        (self.root / "profile.json").write_text("{}")
        with self.assertRaises(k.Invalid): k.validate_manifest(self.m, self.root)

    def test_risk_classifier_all_routes(self):
        for change in [{"path": "src/x", "operation": "delete"},
                       {"path": "src/x", "old_path": "src/y", "operation": "rename"},
                       {"path": "scripts/engine.py", "operation": "modify"},
                       {"path": "src/locked/file", "operation": "add"}]:
            with self.subTest(change=change):
                self.assertEqual(k.risk_tier(self.m, self.root, [change], []), "protected")
                p = copy.deepcopy(self.p); p["changes"] = [change]; p["outputs"] = [] if change["operation"] == "delete" else [change["path"]]; p["tier"] = "micro"
                with self.assertRaises(k.Invalid): k.validate_packet(p, self.m, self.root)

    def test_accepted_output_replacement_escalates(self):
        self.assertEqual(k.risk_tier(self.m, self.root, self.p["changes"], [], ["src/result.txt"]), "protected")

    def test_no_outside_output_roots(self):
        with self.assertRaises(k.Invalid): k.risk_tier(self.m, self.root, [{"path": "other/x", "operation": "add"}], [])

    def test_review_exemption_requires_real_target(self):
        binding = {"envelope_sha256": "0" * 64, "outputs": dict(self.p["inputs"])}
        self.frozen(lambda p: p.update(review_of="demo/999", review_target=binding, required_reviews="none"))
        with self.assertRaisesRegex(k.Invalid, "review_of target"): self.run_event("dispatch")

    def test_revision_requires_authoritative_target_and_scope(self):
        self.frozen(lambda p: p.update(revises="demo/000", tier="protected"))
        with self.assertRaises(k.Invalid): self.run_event("dispatch")
        self.assertEqual(self.run_event("dispatch", approvals=[self.approval("scope")], related={"demo/000": {"id": "demo/000", "status": "accepted", "outputs": self.p["outputs"]}})["proposed_status"], "dispatched")

    def test_micro_revision_cannot_skip_approval(self):
        self.frozen(lambda p: p.update(revises="demo/000", tier="micro", required_reviews="none"))
        with self.assertRaisesRegex(k.Invalid, "accepted-output risk"):
            self.run_event("dispatch", related={"demo/000": {"id": "demo/000", "status": "accepted", "outputs": self.p["outputs"]}})

    def test_accepted_inventory_applies_at_dispatch(self):
        with self.assertRaisesRegex(k.Invalid, "accepted-output risk"):
            self.run_event("dispatch", accepted_outputs=["src/result.txt"])

    def test_return_binds_artifact_bytes(self):
        self.p["status"] = "landed"
        result = self.run_event("return", reason="blocking defect")
        self.assertEqual(result["output_hashes"], {"src/result.txt": k.digest(b"result")})
        (self.root / "src/result.txt").unlink()
        with self.assertRaises(k.Invalid): self.run_event("return", reason="blocking defect")

    def test_bool_schema_and_del_path_rejected(self):
        self.m["schema_version"] = True
        with self.assertRaises(k.Invalid): k.validate_manifest(self.m, self.root)
        self.m["schema_version"] = 1; self.p["schema_version"] = True
        with self.assertRaises(k.Invalid): k.validate_packet(self.p, self.m, self.root)
        for path in ["src/\x7f", "src/\u0085", "src/\u202e"]:
            with self.assertRaises(k.Invalid): k.safe_path(path)

    def test_falsey_packet_cli_fails(self):
        mf = self.root / "manifest.json"; mf.write_text(json.dumps(self.m))
        pkt = self.root / "packet.json"
        for value in [{}, [], None, False]:
            pkt.write_text(json.dumps(value))
            r = subprocess.run([__import__('sys').executable, str(ROOT / "scripts/opkit.py"), "validate", "--manifest", str(mf),
                                "--policy-root", str(self.root), "--packet", str(pkt)], capture_output=True)
            self.assertNotEqual(r.returncode, 0, value)

    def test_review_cannot_overwrite_or_misbind_target(self):
        original = copy.deepcopy(self.p)
        target = copy.deepcopy(original); target.update(status="accepted", artifact_hashes={"src/result.txt": k.digest(b"result")})
        self.p["actor"] = {"name": "reviewer", "surface": "fresh"}; self.p["context_id"] = "fresh-2"
        self.p.update(review_of="demo/000", required_reviews="none", tier="protected")
        self.p["inputs"]["src/result.txt"] = k.digest(b"result")
        self.p["review_target"] = {"envelope_sha256": original["envelope"]["sha256"], "outputs": target["artifact_hashes"]}
        target["id"] = "demo/000"
        self.p = k.freeze(self.p, self.m, self.root)
        with self.assertRaisesRegex(k.Invalid, "must not alter"):
            self.run_event("dispatch", related={"demo/000": target}, approvals=[self.approval("scope")])
        self.p["outputs"] = ["src/review.txt"]; self.p["changes"] = [{"path": "src/review.txt", "operation": "add"}]
        self.p = k.freeze(self.p, self.m, self.root)
        target["artifact_hashes"] = {"src/result.txt": "0" * 64}
        with self.assertRaisesRegex(k.Invalid, "stale/unbound"):
            self.run_event("dispatch", related={"demo/000": target}, approvals=[self.approval("scope")])

    def test_completed_handoff_cannot_redispatch(self):
        self.p["status"] = "done"
        with self.assertRaises(k.Invalid): self.run_event("dispatch")


def run_git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.DEVNULL).decode().strip()


class RemoteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.repo = self.root / "work"; self.bare = self.root / "origin.git"
        self.repo.mkdir(); run_git(self.repo, "init", "-b", "main")
        run_git(self.repo, "config", "user.email", "test@example.invalid"); run_git(self.repo, "config", "user.name", "Fixture")
        run_git(self.root, "init", "--bare", str(self.bare)); run_git(self.repo, "remote", "add", "origin", str(self.bare))
        (self.repo / "file.txt").write_text("data"); (self.repo / "other-file.txt").write_text("other")
        run_git(self.repo, "add", "."); run_git(self.repo, "commit", "-m", "initial"); run_git(self.repo, "push", "-u", "origin", "main")
        self.sha = run_git(self.repo, "rev-parse", "HEAD")

    def test_remote_verified_exact_outputs(self):
        r = k.verify_remote(self.repo, "origin", "main", self.sha, ["file.txt"])
        self.assertEqual(r["paths"], {"file.txt": k.digest(b"data")})
        self.assertEqual(r["acceptance"], "not inferred")

    def test_remote_failure_not_cached_success(self):
        run_git(self.repo, "remote", "set-url", "origin", str(self.root / "missing"))
        with self.assertRaises(k.Invalid): k.verify_remote(self.repo, "origin", "main", self.sha, ["file.txt"])

    def test_remote_paths_are_exact_not_substrings(self):
        with self.assertRaises(k.Invalid): k.verify_remote(self.repo, "origin", "main", self.sha, ["file"])

    def test_dirty_workspace_fails_without_mutation(self):
        (self.repo / "file.txt").write_text("uncommitted")
        with self.assertRaises(k.Invalid): k.verify_remote(self.repo, "origin", "main", self.sha, ["file.txt"])
        self.assertEqual((self.repo / "file.txt").read_text(), "uncommitted")

    def test_remote_advance_fails_without_reset(self):
        old = self.sha; (self.repo / "new").write_text("new")
        run_git(self.repo, "add", "."); run_git(self.repo, "commit", "-m", "advance"); run_git(self.repo, "push")
        with self.assertRaises(k.Invalid): k.verify_remote(self.repo, "origin", "main", old, ["file.txt"])
        self.assertTrue((self.repo / "new").exists())

    def test_diff_handles_rename_and_deletion(self):
        run_git(self.repo, "mv", "file.txt", "renamed.txt"); run_git(self.repo, "rm", "other-file.txt")
        run_git(self.repo, "commit", "-m", "move/delete")
        c = k.git_changes(self.repo, self.sha, "HEAD")
        self.assertEqual({x["operation"] for x in c}, {"rename", "delete"})


if __name__ == "__main__":
    unittest.main()
