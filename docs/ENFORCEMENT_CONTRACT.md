# Enforcement contract

Status: Approved design for remediation under APPROVAL-0001 / DECISION-0001.

The validator is a read-only policy checker, not a credential broker or a sandbox.
It cannot authenticate the person who supplied a local JSON file. Trusted CI and
native repository/environment controls must bind its input to authenticated actors.
Its output says `policy_check: passed`, never `authorized: true`.

| Action | Role | Required evidence |
| --- | --- | --- |
| ready | orchestrator | Valid packet and policy |
| dispatch | orchestrator | Frozen envelope and applicable dispatch approvals |
| land | steward | Exact output bytes and provenance; protected-path approval |
| accept / return | orchestrator | Exact reviewed outputs; accept requires independent passing review |
| block | orchestrator | Reason; completed work cannot be blocked |
| external-action | steward | Live owner approval bound to envelope, environment and named action |
| done | orchestrator | Accepted work; protected work requires owner Done approval |

Micro work uses a compact candidate record rather than a handoff lifecycle. It is
validated with the same risk classifier. The tool never lowers a declared tier.

## Inputs and trust

Strict, duplicate-key-free JSON, exact schema versions, no unknown keys. Paths are
relative, normalized POSIX paths; no traversal, symlinks or control characters.
Core and profile dependencies are immutable digests. Policy must be loaded from a
trusted checkout of the adoption commit; the candidate is a separate checkout.
Approvals and reviews are read from explicitly supplied authoritative evidence.
Trusted CI checks the record provenance before invoking this library. A project
without that integration can use it for diagnostics, not unattended authorization.

## Mutation and revocation

All transitions compare a frozen packet with the authoritative prior packet. Only
status and the append-only amendments list may differ; the input to a transition
still names the prior status. Output changes invalidate review digests. Owner
revocation applies immediately even though original policy remains pinned.

## Test matrix

Tests cover schema/paths, roles/surfaces, risk and protected paths on every route,
expiry/revocation/wrong-scope approvals, frozen field tampering, stale/failing/self
reviews, exact-byte provenance, remote fetch failure/path equality, interrupted
delivery and portability. `docs/QA_AND_PILOT.md` records executed evidence.
