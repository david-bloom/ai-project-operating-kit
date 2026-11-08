# Read-only commands — 3.1.0

Python 3.11+ and Git. No third-party libraries; JSON only. Set OPKIT_PYTHON if `python3`
is older (macOS may ship 3.9). All validators emit JSON on stdout and errors on stderr.

```sh
python3.12 scripts/opkit.py validate --manifest manifest.json --policy-root trusted-checkout --packet packet.json
python3.12 scripts/opkit.py freeze --manifest manifest.json --policy-root trusted-checkout --packet packet.json
python3.12 scripts/opkit.py check --manifest manifest.json --policy-root trusted-checkout --packet packet.json --previous authoritative-previous.json --event dispatch --evidence evidence.json --candidate-root candidate-checkout --actor codex --surface local --accepted-outputs accepted-outputs.json
python3.12 scripts/opkit.py candidate --manifest manifest.json --policy-root trusted-checkout --repo candidate-checkout --base BASE_SHA --head HEAD_SHA --tier governed --accepted-outputs accepted-outputs.json
python3.12 scripts/opkit.py verify-remote --repo checkout --remote origin --branch codex/work --commit FULL_SHA docs/result.md
```

`freeze` prints a new packet; the host reviews and records it. `check` proposes a transition;
it does not mutate state or authorize the supplied identity. `candidate` requires a clean,
committed checkout, checks the complete diff, and classifies deletions/renames/protected or
accepted-output changes. `--risks` adds semantic risks. The accepted-output inventory is an
explicit authoritative JSON list, even when empty. A self-declared low tier is not proof.

`verify-remote` checks the actual remote branch and exact paths at the expected full commit.
It may fetch Git objects but does not alter working files or branches. No command commits,
merges, pushes, resets, deploys, charges money, sends email or modifies a live service.

`publish` now delegates only to `candidate`. `handoff-check` delegates to `validate`.
`verify-sync.sh` delegates to `verify-remote`; old positional/current-branch guesses fail.

Evidence object fields: approvals, revocations (IDs), reviews, provenance (path → source,
SHA-256, modification=none), related_packets (authoritative predecessor/review targets).
Approval fields are demonstrated in tests/test_opkit.py and documented in the enforcement
contract; timestamps require explicit zones and expiry is exclusive. Reviews bind exact
output hashes and a different context ID; current failing reviews block acceptance.

Trust requirement: host-authenticated evidence and pinned base code, not candidate-controlled
JSON or a claimed actor string. This library checks structure/consistency; it cannot prove
human identity, private context isolation or actual repository access settings.

For artifact transitions (land/accept/return/external-action/done), supply --base BASE_SHA
and --head HEAD_SHA. The clean candidate Git diff must exactly match the packet changes.
Review handoffs bind review_target (envelope_sha256 and outputs hash map); related_packets
records include the target packet plus artifact_hashes recorded at delivery.
