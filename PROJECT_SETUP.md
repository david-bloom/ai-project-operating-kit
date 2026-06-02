# Project Setup Checklist

Use this checklist when installing the AI Project Operating Kit into a new repository.

## 1. Copy Files

Copy:

```text
docs/team_charter/
docs/activity_log/
docs/tasks/
prompts/
```

## 2. Replace Placeholders

Search and replace:

```text
[PROJECT_NAME]
[OWNER_NAME]
[PRIMARY_REPO]
[PRIMARY_STACK]
[HARD_GATES]
[STANDING_APPROVALS]
[TOOLS_OR_SKILLS]
```

## 3. Confirm Source of Truth

Decide where durable project state lives.

Recommended:

```text
GitHub docs, task files, issues, PRs, activity log, approvals log, and decisions log.
```

## 4. Define Roles

At minimum:

```text
Owner / Product Approver
Main Conductor
Implementation Agent
QA Agent
UX / Prompt Agent if frontend or design work exists
```

## 5. Define Standing Approvals

Pre-approve low-risk recurring work such as:

- Read-only repo checks.
- Draft task specs.
- Handoff packets.
- Read-only tool checks.
- Draft prompts.
- QA planning.
- Documentation-only workflow updates.

## 6. Define Hard Gates

Examples:

- Migrations.
- Deployments.
- Secret changes.
- Payment live-mode changes.
- Production launch.
- Risk acceptance.
- Done decisions.
- Closing tasks/issues.

## 7. Add Startup Prompts

Give the appropriate prompt from `prompts/` to Claude, Codex, or other agents.

## 8. Create First Task

Use:

```text
docs/tasks/TASK_TEMPLATE.md
```

Record approval in:

```text
docs/activity_log/APPROVALS_LOG.md
```

## 9. Operate

Use handoff packets before:

- Execution.
- QA.
- Frontend prompt handoff.
- Complex delegation.
- Task owner changes.

