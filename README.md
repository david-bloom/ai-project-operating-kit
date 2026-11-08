# AI Project Operating Kit

A versioned workflow policy and **read-only validator** for AI-assisted projects.

Start with [the canonical index](docs/INDEX.md) and [core policy](docs/CORE_OPERATING_POLICY.md).
Current candidate: **3.1.0**. See [build and adoption status](docs/BUILD_STATUS.md).
The September 2026 v-next publisher and copied `team_charter` operating rules are
superseded. They are preserved in Git history at `9025014`, not alternate instructions.

## Boundaries

The validator checks declared evidence. It does not authenticate local JSON, execute
external actions, commit, merge, push, reset, or grant permissions. Use native GitHub
PR protections and protected environments. A local passing check is not authorization,
independent QA, deployment approval or Done.

## Start

Python **3.11+** and Git are required. No third-party runtime libraries.

```sh
OPKIT_PYTHON=python3.12 tests/run.sh
python3.12 scripts/opkit.py validate --manifest templates/PROJECT_MANIFEST.example.json --policy-root . --packet templates/HANDOFF_PACKET.example.json
```

[Install a pinned release](PROJECT_SETUP.md), then use the
[migration and rollback guide](docs/MIGRATION.md). Do not copy editable governance
folders into an existing project or silently supersede its installed rules.

Key practices: tier-first reading, bounded searches, scoped and expiring approvals,
one reviewable slice per branch, exact-revision independent QA, PR-only promotion,
and durable closeout with the next owner/action. The project supplies its owner,
actors, allowed output roots, protected paths, approval additions and pinned profiles.
