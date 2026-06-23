# Project Setup Checklist

Use this checklist when installing the AI Project Operating Kit into a new repository.

## 1. Copy Files

Copy:

```text
docs/team_charter/
docs/activity_log/
docs/tasks/
prompts/
scripts/
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
Owner / Final Approver
Main Conductor
Implementation Agent
QA Agent
UX / Prompt Agent if frontend or design work exists
```

If the project has more than one functional owner, also consider naming Delegated Domain Approvers (see `docs/team_charter/AI_COLLABORATION_RULES.md`) so routine domain-specific approvals don't all route through the Owner.

## 5. Define Standing Approvals

Pre-approve low-risk recurring work such as:

- Read-only repo checks.
- Draft task specs.
- Handoff packets.
- Read-only tool checks.
- Draft prompts.
- QA planning.
- Documentation-only workflow updates.
- Any `Micro`-tier task (see step 6).

## 6. Define Task Tiers and Hard Gates

Confirm the project will use the `Micro` / `Standard` / `Hard-Gate` task tiering in `docs/team_charter/AGENT_OPERATING_MODEL.md` — it's what keeps a one-line reversible fix from going through the same ceremony as a production migration.

Define hard gates, at minimum:

- Migrations.
- Deployments.
- Secret changes.
- Payment live-mode changes.
- Production launch.
- Risk acceptance.
- Done decisions.
- Closing tasks/issues.
- Material changes to `docs/team_charter/` documents.

Add project-specific risks (e.g. content licensing, regulated data, public claims) as they're identified — this list is a floor, not a ceiling.

## 7. Add Startup Prompts

Give the appropriate prompt from `prompts/` to Claude, Codex, or other agents.

## 8. Wire Up `scripts/verify-sync.sh`

Confirm agents in this project can run shell scripts. `verify-sync.sh` replaces a narrated "synced" claim with an actual check (clean working tree, local HEAD matches the current branch's remote, expected paths present in the latest commit) — use it before reporting sync complete, especially before `Ready for Review` or a `SYNC` response.

## 9. Create First Task

Use:

```text
docs/tasks/TASK_TEMPLATE.md
```

Set its `Tier`. Record approval in:

```text
docs/activity_log/APPROVALS_LOG.md
```

## 10. Operate

Use handoff packets before:

- Execution.
- QA.
- Frontend prompt handoff.
- Complex delegation.
- Task owner changes.

Skip the handoff packet for `Micro`-tier work.
