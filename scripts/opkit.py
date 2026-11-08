#!/usr/bin/env python3
"""Read-only operating-policy checks. Authentication belongs to trusted host adapters."""
import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import unicodedata

VERSION = "3.1.0"
TIERS = ("micro", "governed", "protected")
ROLES = {"owner", "orchestrator", "steward", "worker", "reviewer"}
RISKS = {"production", "money", "privacy", "deletion", "publication", "governance"}
STATUSES = {"draft", "ready", "dispatched", "landed", "accepted", "returned", "blocked", "done"}
FLOOR = ("AGENTS.md", "CLAUDE.md", "PROJECT_MANIFEST.json", "README.md",
         "PROJECT_SETUP.md", "docs/CORE_OPERATING_POLICY.md", "docs/team_charter/*",
         "docs/architecture/*", "docs/activity_log/*", "config/*", "scripts/*",
         "templates/*", "profiles/*", ".github/*")
HEX = re.compile(r"^[0-9a-f]{64}$")
ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._/-]*$")


class Invalid(ValueError):
    pass


def require(value, message):
    if not value:
        raise Invalid(message)


def strict_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out


def parse(data):
    try:
        return json.loads(data, object_pairs_hook=strict_object,
                          parse_constant=lambda x: (_ for _ in ()).throw(Invalid("non-finite JSON")))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise Invalid("invalid JSON: " + str(exc)) from exc


def read_json(path):
    return parse(Path(path).read_text(encoding="utf-8"))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def object_keys(value, required, optional=()):
    require(isinstance(value, dict), "expected JSON object")
    require(set(required) <= value.keys(), "missing fields: " + str(set(required) - value.keys()))
    require(value.keys() <= set(required) | set(optional), "unknown fields: " + str(value.keys() - set(required) - set(optional)))


def text(value, label):
    require(isinstance(value, str) and value.strip() and not any(unicodedata.category(c).startswith("C") for c in value), "invalid " + label)


def identifier(value, label):
    require(isinstance(value, str) and ID.fullmatch(value) and ".." not in value and "//" not in value,
            "invalid " + label)


def strings(value, label, allowed=None):
    require(isinstance(value, list), label + " must be a list")
    for item in value:
        text(item, label)
        if allowed is not None:
            require(item in allowed, "unsupported " + label + ": " + item)
    require(len(set(value)) == len(value), "duplicate " + label)


def safe_path(value):
    text(value, "path")
    p = PurePosixPath(value)
    require(not p.is_absolute() and str(p) == value and ".." not in p.parts and
            not value.startswith("-") and "\\" not in value and ".git" not in p.parts,
            "unsafe path: " + value)
    return value


def file_in(root, name):
    safe_path(name)
    root = Path(root).resolve()
    p = root
    for part in PurePosixPath(name).parts:
        p = p / part
        require(not p.is_symlink(), "symlink refused: " + name)
    require(p.is_file(), "missing regular file: " + name)
    require(p.resolve().is_relative_to(root), "path escaped root")
    return p


def stamp(value):
    text(value, "timestamp")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Invalid("invalid timestamp") from exc
    require(parsed.tzinfo is not None, "timestamp requires explicit timezone")
    return parsed.astimezone(dt.timezone.utc)


def hashed_paths(value, label):
    require(isinstance(value, dict), label + " must map paths to SHA-256")
    for p, h in value.items():
        safe_path(p)
        require(isinstance(h, str) and HEX.fullmatch(h), "invalid content hash: " + p)


def validate_manifest(m, policy_root):
    object_keys(m, {"schema_version", "project", "core", "source_of_truth", "owner", "orchestrator",
                    "steward", "actors", "defaults", "allowed_outputs", "protected_paths", "hard_gates", "profiles"})
    require(type(m["schema_version"]) is int and m["schema_version"] == 1, "unsupported manifest schema")
    identifier(m["project"], "project")
    object_keys(m["core"], {"version", "path", "sha256"})
    require(m["core"]["version"] == VERSION, "exact core version required: " + VERSION)
    require(digest(file_in(policy_root, m["core"]["path"]).read_bytes()) == m["core"]["sha256"], "core digest mismatch")
    object_keys(m["source_of_truth"], {"repo", "branch"})
    text(m["source_of_truth"]["repo"], "source repo")
    identifier(m["source_of_truth"]["branch"], "source branch")
    require(isinstance(m["actors"], list) and m["actors"], "actors required")
    seen = set()
    for a in m["actors"]:
        object_keys(a, {"name", "surface", "roles", "delivery", "authority"})
        identifier(a["name"], "actor"); identifier(a["surface"], "surface")
        strings(a["roles"], "roles", ROLES)
        require(a["roles"], "actor needs a role")
        require(a["delivery"] in {"airlock", "branch", "publisher"}, "invalid delivery")
        require(a["authority"] in {"full", "none"}, "invalid authority")
        k = (a["name"], a["surface"])
        require(k not in seen, "duplicate actor surface"); seen.add(k)
    for role in ("owner", "orchestrator", "steward"):
        object_keys(m[role], {"name", "surface"})
        a = actor(m, m[role])
        require(role in a["roles"] and a["authority"] == "full", "invalid designated " + role)
    require(actor(m, m["steward"])["delivery"] == "publisher", "steward needs publisher delivery")
    object_keys(m["defaults"], {"tier", "isolation"})
    require(m["defaults"]["tier"] in TIERS, "invalid default tier")
    require(m["defaults"]["isolation"] in {"open", "fresh"}, "invalid default isolation")
    strings(m["allowed_outputs"], "allowed outputs")
    require(m["allowed_outputs"], "allowed outputs required")
    for p in m["allowed_outputs"]: safe_path(p)
    strings(m["protected_paths"], "protected paths")
    for pattern in m["protected_paths"]:
        require(not pattern.startswith("/") and ".." not in pattern and "\\" not in pattern, "unsafe protection pattern")
    strings(m["hard_gates"], "hard gates")
    for gate in m["hard_gates"]: identifier(gate, "gate")
    require(isinstance(m["profiles"], list), "profiles must be a list")
    names = set()
    for dep in m["profiles"]:
        object_keys(dep, {"name", "version", "path", "sha256"})
        identifier(dep["name"], "profile"); text(dep["version"], "profile version")
        require(dep["name"] not in names, "duplicate profile"); names.add(dep["name"])
        raw = file_in(policy_root, dep["path"]).read_bytes()
        require(digest(raw) == dep["sha256"], "profile digest mismatch")
        profile = parse(raw)
        object_keys(profile, {"name", "version", "minimum_tier", "requires_isolation", "protected_paths", "hard_gates"})
        require(profile["name"] == dep["name"] and profile["version"] == dep["version"], "profile identity mismatch")
        require(profile["minimum_tier"] in TIERS, "invalid profile tier")
        require(type(profile["requires_isolation"]) is bool, "invalid profile isolation")
        strings(profile["protected_paths"], "profile protected paths")
        for pattern in profile["protected_paths"]:
            require(not pattern.startswith("/") and ".." not in pattern and "\\" not in pattern, "unsafe profile pattern")
        strings(profile["hard_gates"], "profile hard gates")
        for gate in profile["hard_gates"]: identifier(gate, "profile gate")
    return m


def actor(m, who):
    object_keys(who, {"name", "surface"})
    matches = [a for a in m["actors"] if a["name"] == who["name"] and a["surface"] == who["surface"]]
    require(len(matches) == 1, "unknown actor surface")
    return matches[0]


def profiles(m, root):
    return [read_json(file_in(root, dep["path"])) for dep in m["profiles"]]


def protected(m, root, path):
    patterns = list(FLOOR) + m["protected_paths"]
    for p in profiles(m, root): patterns += p["protected_paths"]
    return any(fnmatch.fnmatchcase(path, pat) for pat in patterns)


def allowed(m, path):
    return any(path == p or path.startswith(p + "/") for p in m["allowed_outputs"])


def risk_tier(m, root, changes, risks, accepted=()):
    strings(risks, "risks", RISKS)
    require(isinstance(changes, list), "changes must be a list")
    seen = set(); tier = m["defaults"]["tier"]
    for p in profiles(m, root): tier = max(tier, p["minimum_tier"], key=TIERS.index)
    for c in changes:
        object_keys(c, {"path", "operation"}, {"old_path"})
        path = safe_path(c["path"])
        require(path not in seen, "duplicate change path"); seen.add(path)
        require(c["operation"] in {"add", "modify", "delete", "rename"}, "invalid operation")
        require((c["operation"] == "rename") == ("old_path" in c), "rename needs old_path only")
        paths = [path] + ([safe_path(c["old_path"])] if "old_path" in c else [])
        require(all(allowed(m, p) for p in paths), "change outside allowed outputs")
        if c["operation"] in {"delete", "rename"} or any(protected(m, root, p) or p in accepted for p in paths):
            tier = "protected"
    if risks: tier = "protected"
    return tier


def validate_packet(p, m, root):
    object_keys(p, {"schema_version", "id", "task", "actor", "context_id", "lane", "tier", "status", "isolation",
                    "inputs", "outputs", "changes", "risks", "required_reviews", "review_of", "review_target", "supersedes", "revises",
                    "required_approvals", "environment", "action", "instructions", "amendments"}, {"envelope"})
    require(type(p["schema_version"]) is int and p["schema_version"] == 1, "unsupported packet schema")
    for k in ("id", "task", "context_id"): identifier(p[k], k)
    actor(m, p["actor"])
    require(p["lane"] in {"routine", "judgment", "divergence"}, "invalid lane")
    require(p["tier"] in TIERS and p["status"] in STATUSES, "invalid tier/status")
    object_keys(p["isolation"], {"mode", "withhold", "lift_when"})
    require(p["isolation"]["mode"] in {"open", "fresh"}, "invalid isolation mode")
    strings(p["isolation"]["withhold"], "withhold")
    if p["isolation"]["mode"] == "fresh":
        require(p["isolation"]["withhold"], "fresh isolation needs withheld inputs")
        text(p["isolation"]["lift_when"], "observable lift event")
    else:
        require(not p["isolation"]["withhold"] and p["isolation"]["lift_when"] is None, "open isolation cannot withhold")
    if m["defaults"]["isolation"] == "fresh" or any(x["requires_isolation"] for x in profiles(m, root)):
        require(p["isolation"]["mode"] == "fresh", "profile/default requires fresh context")
    hashed_paths(p["inputs"], "inputs")
    strings(p["outputs"], "outputs")
    require(p["outputs"], "outputs required")
    for path in p["outputs"]:
        safe_path(path); require(allowed(m, path), "output outside allowed roots")
    required_tier = risk_tier(m, root, p["changes"], p["risks"])
    require(TIERS.index(p["tier"]) >= TIERS.index(required_tier), "packet lowers derived tier")
    require(set(p["outputs"]) == {c["path"] for c in p["changes"] if c["operation"] != "delete"}, "outputs must equal resulting changed files")
    require(p["required_reviews"] in {"none", "independent"}, "invalid review requirement")
    for k in ("review_of", "supersedes", "revises"):
        if p[k] is not None: identifier(p[k], k); require(p[k] != p["id"], "self-reference refused")
    require(not (p["supersedes"] and p["revises"]), "cannot supersede and revise together")
    if p["review_of"] is not None:
        require(not p["revises"] and not p["supersedes"], "review cannot also revise/supersede work")
        object_keys(p["review_target"], {"envelope_sha256", "outputs"})
        require(isinstance(p["review_target"]["envelope_sha256"], str) and HEX.fullmatch(p["review_target"]["envelope_sha256"]), "invalid review target envelope")
        hashed_paths(p["review_target"]["outputs"], "review target outputs")
        require(p["review_target"]["outputs"], "review target output hashes required")
        require(all(p["inputs"].get(path) == sha for path, sha in p["review_target"]["outputs"].items()), "reviewed artifacts must be exact inputs")
    else:
        require(p["review_target"] is None, "review_target only allowed on review handoffs")
    if p["tier"] != "micro" and p["review_of"] is None:
        require(p["required_reviews"] == "independent", "independent review required")
    object_keys(p["required_approvals"], {"dispatch", "land", "accept", "external-action", "done"})
    for gates in p["required_approvals"].values():
        strings(gates, "approval gates")
        for gate in gates: identifier(gate, "approval gate")
    text(p["environment"], "environment"); text(p["action"], "action"); text(p["instructions"], "instructions")
    require(isinstance(p["amendments"], list), "amendments must be a list")
    for note in p["amendments"]: text(note, "amendment")
    return p


def envelope_payload(p, m):
    return {"packet": {k: v for k, v in p.items() if k not in {"envelope", "status", "amendments"}}, "manifest": m}


def freeze(p, m, root):
    validate_manifest(m, root); validate_packet(p, m, root)
    require(p["status"] in {"draft", "ready"}, "only draft/ready can freeze")
    result = dict(p)
    result["envelope"] = {"sha256": digest(canonical(envelope_payload(p, m))), "manifest_sha256": digest(canonical(m))}
    return result


def verify_envelope(p, m):
    require("envelope" in p, "frozen envelope required")
    object_keys(p["envelope"], {"sha256", "manifest_sha256"})
    require(p["envelope"]["manifest_sha256"] == digest(canonical(m)), "pinned manifest changed; load original policy or reauthorize")
    require(p["envelope"]["sha256"] == digest(canonical(envelope_payload(p, m))), "frozen envelope changed")


def gate_ids(p, m, root, event):
    gates = set(p["required_approvals"][event])
    if p["tier"] == "protected":
        gates.add({"dispatch": "scope", "land": "landing", "accept": "acceptance", "external-action": "external-action", "done": "done"}[event])
    if event == "external-action": gates.add("external-action")
    if event in {"dispatch", "external-action"}:
        gates.update(m["hard_gates"])
        for prof in profiles(m, root): gates.update(prof["hard_gates"])
    return gates


def check_approvals(records, p, m, gates, now, revocations):
    require(isinstance(records, list) and isinstance(revocations, list), "approval records and revocations must be lists")
    strings(revocations, "revoked approvals")
    ids = set(); valid = set()
    for a in records:
        object_keys(a, {"id", "approver", "task", "envelope_sha256", "gate", "action", "environment", "status", "not_before", "expires_at", "evidence"})
        identifier(a["id"], "approval id"); require(a["id"] not in ids, "duplicate approval ID"); ids.add(a["id"])
        object_keys(a["approver"], {"name", "surface"})
        require(a["status"] in {"active", "revoked", "superseded"}, "invalid approval status")
        begin, end = stamp(a["not_before"]), stamp(a["expires_at"])
        require(begin < end, "invalid approval interval")
        text(a["evidence"], "approval evidence")
        if (a["status"] == "active" and a["id"] not in revocations and begin <= now < end and
            a["approver"] == m["owner"] and a["task"] == p["task"] and
            a["envelope_sha256"] == p["envelope"]["sha256"] and a["environment"] == p["environment"] and
            a["action"] == p["action"]): valid.add(a["gate"])
    require(gates <= valid, "missing live owner approvals: " + ", ".join(sorted(gates - valid)))


def verify_outputs(p, candidate_root):
    result = {}
    for name in p["outputs"]: result[name] = digest(file_in(candidate_root, name).read_bytes())
    for c in p["changes"]:
        if c["operation"] in {"delete", "rename"}:
            old = c.get("old_path", c["path"])
            require(not (Path(candidate_root) / old).exists() and not (Path(candidate_root) / old).is_symlink(), "deleted/renamed old path remains")
    return result


def check_reviews(reviews, p, m, hashes):
    require(isinstance(reviews, list), "reviews must be a list")
    relevant = []; seen = set()
    for r in reviews:
        object_keys(r, {"id", "review_of", "envelope_sha256", "reviewer", "context_id", "outputs", "verdict", "blocking_findings", "disposition", "evidence"})
        identifier(r["id"], "review id"); require(r["id"] not in seen, "duplicate review ID"); seen.add(r["id"])
        hashed_paths(r["outputs"], "reviewed outputs")
        require(r["verdict"] in {"pass", "fail"}, "review verdict required")
        strings(r["blocking_findings"], "blocking findings")
        require(r["disposition"] in {"current", "superseded"}, "invalid review disposition")
        text(r["evidence"], "review evidence")
        if r["review_of"] != p["id"] or r["disposition"] != "current": continue
        a = actor(m, r["reviewer"])
        require("reviewer" in a["roles"], "reviewer role required")
        identifier(r["context_id"], "review context")
        require(r["context_id"] != p["context_id"], "independent fresh context required")
        require(r["envelope_sha256"] == p["envelope"]["sha256"] and r["outputs"] == hashes, "stale review")
        require(r["verdict"] == "pass" and not r["blocking_findings"], "unresolved failing review")
        relevant.append(r)
    require(relevant, "independent passing review required")


def check_provenance(provenance, hashes):
    require(isinstance(provenance, dict) and set(provenance) == set(hashes), "exact provenance required for every output")
    for path, entry in provenance.items():
        object_keys(entry, {"source", "sha256", "modification"})
        text(entry["source"], "provenance source")
        require(entry["modification"] == "none", "normalized/substantive modifications require a new reviewed artifact")
        require(entry["sha256"] == hashes[path], "provenance bytes differ")


TRANSITIONS = {"ready": ({"draft"}, "orchestrator", "ready"), "dispatch": ({"ready"}, "orchestrator", "dispatched"),
               "land": ({"dispatched"}, "steward", "landed"), "accept": ({"landed"}, "orchestrator", "accepted"),
               "return": ({"landed"}, "orchestrator", "returned"), "block": ({"draft", "ready", "dispatched", "landed"}, "orchestrator", "blocked"),
               "external-action": ({"accepted"}, "steward", "accepted"), "done": ({"accepted"}, "orchestrator", "done")}


def transition(event, p, previous, m, root, candidate, who, approvals, revocations, reviews, provenance, now, reason="", related=None, accepted_outputs=()):
    validate_manifest(m, root); validate_packet(p, m, root)
    require(event in TRANSITIONS, "unknown transition")
    states, role, target = TRANSITIONS[event]
    a = actor(m, who)
    require(who == m[role] and role in a["roles"] and a["authority"] == "full", "caller not designated " + role)
    if role == "steward": require(a["delivery"] == "publisher", "publisher surface required")
    require(p["status"] in states, "invalid lifecycle transition")
    require(isinstance(previous, dict), "authoritative previous packet required")
    require(p["status"] == previous.get("status"), "status differs from authoritative previous state")
    require(envelope_payload(p, m) == envelope_payload(previous, m), "packet differs from authoritative previous state")
    require(p["amendments"][:len(previous["amendments"])] == previous["amendments"], "amendments must be append-only")
    related = related or {}
    require(isinstance(related, dict), "related packets must be a map")
    accepted = set(accepted_outputs)
    for record in related.values():
        if isinstance(record, dict) and record.get("status") in {"landed", "accepted", "done"}:
            accepted.update(record.get("outputs", []))
    derived = risk_tier(m, root, p["changes"], p["risks"], accepted)
    require(TIERS.index(p["tier"]) >= TIERS.index(derived), "packet lowers accepted-output risk")
    for field, statuses in (("revises", {"landed", "accepted", "done"}), ("supersedes", {"returned", "blocked"}), ("review_of", {"dispatched", "landed", "accepted"})):
        if p[field] is not None:
            target_packet = related.get(p[field])
            require(isinstance(target_packet, dict) and target_packet.get("id") == p[field] and target_packet.get("status") in statuses,
                    "invalid authoritative " + field + " target")
            if field == "review_of":
                require("reviewer" in actor(m, p["actor"])["roles"], "review handoff needs reviewer actor")
                require(p["context_id"] != target_packet["context_id"], "review handoff requires fresh context")
                binding = p["review_target"]
                require(target_packet.get("envelope", {}).get("sha256") == binding["envelope_sha256"] and
                        target_packet.get("artifact_hashes") == binding["outputs"] and
                        set(target_packet["outputs"]) == set(binding["outputs"]), "stale/unbound review target")
                touched = {c["path"] for c in p["changes"]} | {c["old_path"] for c in p["changes"] if "old_path" in c}
                require(not touched.intersection(target_packet["outputs"]), "review must not alter reviewed artifacts")
            else:
                require(set(p["outputs"]) <= set(target_packet["outputs"]), "revision exceeds prior output scope; use a new handoff")
    if event != "ready":
        verify_envelope(p, m); verify_envelope(previous, m)
        require(p["envelope"] == previous["envelope"], "envelope differs from authoritative previous state")
    if event in {"dispatch", "land", "accept", "external-action", "done"}:
        check_approvals(approvals, p, m, gate_ids(p, m, root, event), now, revocations)
    if event == "dispatch":
        for path, sha in p["inputs"].items():
            require(digest(file_in(root, path).read_bytes()) == sha, "input snapshot differs from declared hash")
    if event in {"land", "accept", "return", "external-action", "done"}:
        hashes = verify_outputs(p, candidate)
        check_provenance(provenance, hashes)
        if event in {"accept", "external-action", "done"} and p["required_reviews"] == "independent":
            check_reviews(reviews, p, m, hashes)
    if event in {"return", "block"}: text(reason, "transition reason")
    return {"policy_check": "passed", "event": event, "proposed_status": target, "packet": p["id"],
            "output_hashes": hashes if event in {"land", "accept", "return", "external-action", "done"} else {},
            "authentication": "must be enforced by trusted host", "state_changed": False}


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    require(result.returncode == 0, "git operation failed: " + " ".join(args[:2]))
    return result.stdout


def git_changes(repo, base, head):
    tokens = git(repo, "diff", "--name-status", "-z", "--find-renames", base, head).decode().split("\0")
    changes = []; i = 0
    while i < len(tokens) and tokens[i]:
        status, path = tokens[i], tokens[i + 1]; i += 2
        if status.startswith("R"):
            new = tokens[i]; i += 1; changes.append({"path": safe_path(new), "old_path": safe_path(path), "operation": "rename"})
        else:
            require(status in {"A", "M", "D"}, "unsupported git change: " + status)
            changes.append({"path": safe_path(path), "operation": {"A": "add", "M": "modify", "D": "delete"}[status]})
    return changes


def verify_candidate(p, m, root, repo, base, head, accepted):
    require(base and head, "base and head commits required for artifact transitions")
    require(not git(repo, "status", "--porcelain").strip(), "candidate requires clean committed workspace")
    actual_head = git(repo, "rev-parse", head).decode().strip()
    require(git(repo, "rev-parse", "HEAD").decode().strip() == actual_head, "candidate HEAD mismatch")
    changes = git_changes(repo, base, head)
    require(sorted(changes, key=lambda x: x["path"]) == sorted(p["changes"], key=lambda x: x["path"]), "candidate diff differs from declared changes")
    require(TIERS.index(p["tier"]) >= TIERS.index(risk_tier(m, root, changes, p["risks"], accepted)), "candidate lowers derived risk")
    for c in changes:
        if c["operation"] != "delete":
            file_in(repo, c["path"])
    return actual_head


def verify_remote(repo, remote, branch, commit, paths):
    require(re.fullmatch(r"[0-9a-f]{40,64}", commit), "full expected commit required")
    identifier(remote, "remote"); identifier(branch, "branch")
    require(not git(repo, "status", "--porcelain").strip(), "working tree is not clean")
    require(git(repo, "rev-parse", "HEAD").decode().strip() == commit, "HEAD differs from expected commit")
    # ls-remote checks the actual server; a cached tracking ref cannot satisfy this.
    rows = git(repo, "ls-remote", "--exit-code", remote, "refs/heads/" + branch).decode().splitlines()
    require(len(rows) == 1 and rows[0].split()[0] == commit, "remote branch differs from expected commit")
    git(repo, "fetch", "--quiet", remote, "refs/heads/" + branch)
    verified = {}
    for p in paths:
        safe_path(p)
        mode = git(repo, "ls-tree", commit, "--", p).decode().split()
        require(mode and mode[0] in {"100644", "100755"}, "remote path is not a regular file: " + p)
        verified[p] = digest(git(repo, "show", commit + ":" + p))
    return {"remote_verified": True, "commit": commit, "branch": branch, "paths": verified,
            "integration": "not inferred", "acceptance": "not inferred", "release": "not inferred"}


def main():
    require(sys.version_info >= (3, 11), "Python 3.11+ required; set OPKIT_PYTHON or invoke python3.12 scripts/opkit.py")
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    for name in ("validate", "freeze", "check", "candidate"):
        sp = sub.add_parser(name)
        sp.add_argument("--manifest", required=True); sp.add_argument("--policy-root", required=True)
        sp.add_argument("--packet", required=name in {"freeze", "check"})
        if name == "check":
            sp.add_argument("--event", choices=TRANSITIONS, required=True)
            for x in ("previous", "evidence", "candidate-root", "actor", "surface"): sp.add_argument("--" + x, required=True)
            sp.add_argument("--accepted-outputs", required=True)
            sp.add_argument("--base"); sp.add_argument("--head", default="HEAD")
            sp.add_argument("--reason", default="")
        if name == "candidate":
            sp.add_argument("--repo", required=True); sp.add_argument("--base", required=True)
            sp.add_argument("--head", default="HEAD"); sp.add_argument("--tier", choices=TIERS, required=True)
            sp.add_argument("--risks", nargs="*", default=[]); sp.add_argument("--accepted-outputs", required=True)
    sp = sub.add_parser("verify-remote")
    for x in ("repo", "remote", "branch", "commit"): sp.add_argument("--" + x, required=True)
    sp.add_argument("paths", nargs="+")
    args = ap.parse_args()
    if args.command == "verify-remote":
        result = verify_remote(args.repo, args.remote, args.branch, args.commit, args.paths)
    else:
        m = read_json(args.manifest); validate_manifest(m, args.policy_root)
        p = read_json(args.packet) if args.packet else None
        if args.command == "validate":
            if args.packet is not None: validate_packet(p, m, args.policy_root)
            result = {"policy_check": "passed", "version": VERSION}
        elif args.command == "freeze": result = freeze(p, m, args.policy_root)
        elif args.command == "check":
            e = read_json(args.evidence)
            object_keys(e, {"approvals", "revocations", "reviews", "provenance", "related_packets"})
            accepted = read_json(args.accepted_outputs); strings(accepted, "accepted output paths")
            for path in accepted: safe_path(path)
            if args.event in {"land", "accept", "return", "external-action", "done"}:
                verify_candidate(p, m, args.policy_root, args.candidate_root, args.base, args.head, accepted)
            result = transition(args.event, p, read_json(args.previous), m, args.policy_root, args.candidate_root,
                                {"name": args.actor, "surface": args.surface}, e["approvals"], e["revocations"],
                                e["reviews"], e["provenance"], dt.datetime.now(dt.timezone.utc), args.reason, e["related_packets"], accepted)
        else:
            require(not git(args.repo, "status", "--porcelain").strip(), "candidate requires clean committed workspace")
            accepted = read_json(args.accepted_outputs); strings(accepted, "accepted output paths")
            for path in accepted: safe_path(path)
            changes = git_changes(args.repo, args.base, args.head)
            derived = risk_tier(m, args.policy_root, changes, args.risks, accepted)
            require(TIERS.index(args.tier) >= TIERS.index(derived), "declared tier lowers derived risk")
            result = {"policy_check": "passed", "changes": changes, "minimum_tier": derived,
                      "delivery": "open a PR; required GitHub checks/reviews govern merge", "state_changed": False}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (Invalid, OSError, KeyError, TypeError) as exc:
        print("opkit: " + str(exc), file=sys.stderr)
        sys.exit(1)
