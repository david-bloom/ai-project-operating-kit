# Operating-kit remediation

Status: Release-ready; publication receipt on v3.1.0; protected Done not inferred
Owner: David Bloom
Conductor: Codex
Tier: Hard-Gate (operating policy and release)
Branch: `codex/operating-kit-remediation`
PR: #3 — https://github.com/david-bloom/ai-project-operating-kit/pull/3
Baseline: `90250146632715ca169cfe59bb3f7f8bf0297e45`
Approval: APPROVAL-0001; DECISION-0001

## Scope

Execute the five-phase remediation sequence authorized by David on 2026-11-08:
unify policy, specify enforcement, repair/test, independently review and pilot,
then publish a pinned release and migration/rollback guide. No Cramapple migration,
production deployment, paid action or credentials/protection change is included.

## Implementation contract

- Python 3.11+ standard-library validator; strict JSON replaces the partial YAML parser.
- Read-only commands: validate manifest/packet, freeze envelope, check transition,
  prepare candidate receipt, verify remote delivery. No automatic commits, merges,
  resets, pushes, deployments or external side effects.
- Native PR/check/merge protection is the enforcement boundary. Local caller-supplied
  identities are assertions, never authentication. Trusted CI must use the pinned
  base validator and authoritative remote policy/approval records, not candidate code.
- Authority is actor + surface + assigned role. Every transition uses one matrix.
- Canonical immutable envelope binds instructions, inputs/outputs, risk, review,
  dependency digests, identity and approval requirements. Live revocations still apply.
- Explicit structured approvals bind task, envelope, action, environment and interval.
  Required risk gates cannot be removed by empty project configuration.
- Reviews bind output digests and an independent context, with explicit disposition.
- A single diff classifier handles additions, changes, renames and deletions. Micro
  cannot alter governance, delete files, replace accepted outputs or carry risk flags.
- Receipts distinguish local validation, remote durability, accessibility, integration,
  acceptance, release and Done. No policy state is inferred from a successful upload.

## Acceptance / QA

Each of the twelve review findings has policy, implementation and negative tests.
Run tests on Linux/macOS with supported Python, exercise a disposable local bare remote,
then obtain a fresh-context independent review against an exact commit. Remediate and
re-review material changes. GitHub checks must pass before native merge/release.

## Handoff

Approved: the remediation sequence and its proposed architecture, implementation,
tests, independent QA, disposable pilot and release preparation/publication.
Not approved: adopting the result for other projects without their adoption record.
Delivered artifacts: implementation, evidence matrix, pilot report and migration/rollback guide.
Independent QA passed exact implementation c20ab92; 53 tests, nine pilot scenarios and
six CI combinations passed. See QA_AND_PILOT.md for review scope and limitations.
Next action at this checkpoint: native PR #3 merge and v3.1.0 publication; their host
receipts establish completion of those actions without rewriting this pre-merge record.
Pending decisions: None for the authorized release; any consumer adoption is separately scoped.
Open risks: authenticated host integration and concurrency protection remain consumer duties.
Next owner: Codex for publication; project owners only if they elect adoption.
Live systems checked: GitHub source only. No application live-state claims.
