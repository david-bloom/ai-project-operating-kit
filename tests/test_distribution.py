import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from test_opkit import ROOT, k, fixture, run_git


class DistributionTests(unittest.TestCase):
    def test_shipped_examples_validate_unchanged(self):
        m = k.read_json(ROOT / "templates/PROJECT_MANIFEST.example.json")
        p = k.read_json(ROOT / "templates/HANDOFF_PACKET.example.json")
        k.validate_manifest(m, ROOT); k.validate_packet(p, m, ROOT)
        k.verify_envelope(k.freeze(p, m, ROOT), m)
        for path, sha in p["inputs"].items(): self.assertEqual(k.digest((ROOT / path).read_bytes()), sha)

    def test_wrappers_reject_legacy_mutations(self):
        import os
        env = dict(os.environ, OPKIT_PYTHON=sys.executable)
        for script, args in [("publish", ["demo/001", "--dispatch", "--actor", "codex"]),
                             ("publish", ["--event", "governance", "--actor", "codex"]),
                             ("handoff-check", ["packet.md"]), ("verify-sync.sh", ["README.md"])]:
            r = subprocess.run([str(ROOT / "scripts" / script), *args], env=env, capture_output=True)
            self.assertNotEqual(r.returncode, 0)

    def test_candidate_rejects_undeclared_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp); m, p = fixture(repo)
            (repo / "src/result.txt").unlink()
            run_git(repo, "init", "-b", "main"); run_git(repo, "config", "user.name", "Test"); run_git(repo, "config", "user.email", "test@example.invalid")
            run_git(repo, "add", "."); run_git(repo, "commit", "-m", "base")
            base = run_git(repo, "rev-parse", "HEAD")
            (repo / "src/result.txt").write_text("result"); (repo / "src/unexpected.txt").write_text("surprise")
            run_git(repo, "add", "."); run_git(repo, "commit", "-m", "candidate")
            with self.assertRaisesRegex(k.Invalid, "declared changes"):
                k.verify_candidate(p, m, repo, repo, base, "HEAD", [])

    def test_candidate_micro_rejects_accepted_output_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp); m, p = fixture(repo)
            run_git(repo, "init", "-b", "main"); run_git(repo, "config", "user.name", "Test"); run_git(repo, "config", "user.email", "test@example.invalid")
            run_git(repo, "add", "."); run_git(repo, "commit", "-m", "base"); base = run_git(repo, "rev-parse", "HEAD")
            (repo / "src/result.txt").write_text("edited"); run_git(repo, "add", "."); run_git(repo, "commit", "-m", "edit")
            p.update(tier="micro", required_reviews="none", changes=[{"path": "src/result.txt", "operation": "modify"}])
            with self.assertRaisesRegex(k.Invalid, "derived risk"):
                k.verify_candidate(p, m, repo, repo, base, "HEAD", ["src/result.txt"])


if __name__ == "__main__":
    unittest.main()
