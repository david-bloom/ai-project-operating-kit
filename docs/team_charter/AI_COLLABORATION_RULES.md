# [PROJECT_NAME] AI Collaboration Rules

**Status:** Draft / Approved  
**Owner:** [OWNER_NAME]  
**Canonical Folder:** `docs/team_charter/`

## Purpose

This document defines how humans and AI agents collaborate on [PROJECT_NAME].

GitHub documentation is the source of truth. Chat is useful for discussion, but durable project state must be written into GitHub.

## Roles

### Owner / Final Approver

Owns:

- Product direction.
- Scope decisions.
- Priority decisions.
- Task approval.
- Risk acceptance.
- Done decisions.
- Launch/deployment decisions unless delegated.

### Main Conductor

Owns:

- Source-of-truth orientation.
- Approval boundaries.
- Agent coordination.
- Final QA verdicts.
- GitHub publishing.

### Implementation Agent

Owns:

- Execution against approved scope.
- Implementation notes.
- Test results.
- Deviation reports.
- Remediation.

### QA Agent

Owns:

- Proposed findings.
- Evidence review.
- Blocking/non-blocking risk separation.
- Proposed verdict only.

The QA Agent must not approve, close, publish final decisions, deploy, migrate, or mark tasks passed as final.

## Source-of-Truth Rule

If it is not written in GitHub, it does not exist for operating purposes.

Relevant records may include:

- Task files.
- Issues.
- PRs.
- Activity logs.
- Approval logs.
- Decision logs.
- Architecture docs.
- Feature docs.
- QA notes.

## Optional Manual Sync Handshake

Projects may define a short manual trigger that tells an agent to re-sync from the source of truth before continuing.

Recommended example:

```text
C / c
```

When the owner sends the configured trigger, the agent should:

- Re-read current GitHub source-of-truth docs, task files, issues, and activity/approval logs relevant to the active work.
- Report current task or issue state, approval state, blockers, and next recommended action.
- Produce or refresh a handoff packet when execution, QA, frontend handoff, or side-agent coordination is next.
- Treat the trigger as a sync/review instruction only.

The manual sync handshake does not authorize implementation, deployment, migration, secret changes, task closure, QA pass decisions, Done decisions, risk acceptance, or production launch. Those actions still require the normal approval path.

## Startup Rule

At session start, agents should read relevant current GitHub docs before execution.

If the task is unclear or broad, orient from:

```text
docs/team_charter/
docs/tasks/
docs/activity_log/
docs/prd/ or product docs, if present
docs/architecture/, if present
docs/features/, if present
docs/flows/, if present
```

