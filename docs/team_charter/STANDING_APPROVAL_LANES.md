# [PROJECT_NAME] Standing Approval Lanes

**Status:** Draft / Approved  
**Owner:** [OWNER_NAME]

## Purpose

Define which recurring work is pre-approved, which work can be batch-approved, and which work remains a hard gate.

## Lane 1 — Standing Approvals

Approved without separate owner review, as long as no hard gate is triggered:

- Reading/syncing source-of-truth docs.
- Creating draft task specs.
- Creating handoff packets.
- Writing frontend/UX prompts.
- Updating activity log with non-execution status.
- Running read-only repository checks.
- Running read-only service/tool checks.
- Spawning read-only side agents.
- Drafting implementation plans, QA plans, remediation instructions, and review checklists.

Standing approvals do not authorize implementation, deployments, migrations, secret changes, QA pass decisions, task closure, Done decisions, risk acceptance, or launch.

## Lane 2 — Batch Approvals

Recommended format:

```text
Decision:
Scope:
Approved:
Not approved:
Applies to:
Expires / review trigger:
```

## Lane 3 — Hard Gates

Owner approval is required before:

```text
[HARD_GATES]
```

Common examples:

- Applying migrations.
- Deploying live services.
- Changing secrets.
- Changing production configuration.
- Payment live-mode changes.
- Launch decisions.
- Risk acceptance.
- Done decisions.
- Closing tasks/issues as complete.

If classification is unclear, treat it as a hard gate.

