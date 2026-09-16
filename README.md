# AI Project Operating Kit

A reusable operating kit for working with AI coding/research agents across projects.

This kit gives a project a shared source-of-truth workflow, approval lanes, handoff packet, task workflow, QA-agent model, task tiering, model/effort routing, and startup prompts for tools such as Claude, Codex, Lovable, and side agents.

## What This Solves

AI agents move faster when the project has durable memory and clear authority boundaries — but only when that machinery is applied conditionally, not uniformly. This kit helps prevent:

- Chat-only decisions becoming hidden project state.
- Agents executing before approval.
- QA agents acting as final approvers.
- Repeated re-orientation at the start of every session.
- A session ending with no record of what happened, what's still pending, or what's next — leaving the next session (or the next person) to reconstruct it from chat history that may not exist anymore.
- The human project owner becoming the memory and coordination bottleneck — including the version of that bottleneck where every routine approval, not just the hard ones, has to pass through one person.
- Self-reported "synced" or "done" claims standing in for an actual check.
- Heavy process ceremony applied to small, reversible, low-risk work.

## Manual Sync Handshake

The kit supports an optional trigger, `SYNC` (uppercase, standalone — not a single character, which is too easy to fire by accident in normal chat, code, or a typo), that means:

```text
Re-read the current source-of-truth docs/issues/logs and report state before continuing.
```

This is useful when the owner wants an agent to refresh from durable project records without restating the full workflow. The trigger is sync/review only; it does not authorize execution, deployment, approval, closure, risk acceptance, or launch.

## Session Start / Session Close Triggers

Same convention as `SYNC`, for the two other moments that matter most: `SESSION START` tells an agent to orient from the Startup Rule plus the last Session Close entry before doing anything; `SESSION CLOSE` tells it to write that session's `ACTIVITY_LOG.md` entry (Summary, Pending Decisions, Open Risks/Blockers, Next Required Action) before stopping. Works the same way in any tool given a new-session prompt from this kit — Claude, Codex, or otherwise — not just ones that apply the rule automatically. See `docs/team_charter/AI_COLLABORATION_RULES.md`.

## Task Tiers

Every task gets a tier — `Micro`, `Standard`, or `Hard-Gate` — that determines how much process applies. A one-line reversible fix and a production migration should not go through the same ceremony. See `docs/team_charter/AGENT_OPERATING_MODEL.md`.

## Contents

```text
docs/team_charter/
  AI_COLLABORATION_RULES.md
  TASK_WORKFLOW.md
  AGENT_OPERATING_MODEL.md
  HANDOFF_PACKET_TEMPLATE.md
  STANDING_APPROVAL_LANES.md
  TOOL_AND_INTEGRATION_GUIDE.md
  DEFINITION_OF_DONE.md
  CHANGELOG.md

docs/activity_log/
  ACTIVITY_LOG.md
  APPROVALS_LOG.md
  DECISIONS_LOG.md

docs/tasks/
  TASK_TEMPLATE.md

prompts/
  CLAUDE_NEW_SESSION_PROMPT.md
  CODEX_NEW_SESSION_PROMPT.md

scripts/
  verify-sync.sh

PROJECT_SETUP.md
```

## Quick Start

1. Copy this repo's `docs/`, `prompts/`, and `scripts/` folders into a project.
2. Edit placeholders such as `[PROJECT_NAME]`, `[OWNER_NAME]`, and `[HARD_GATES]`.
3. Make GitHub docs the project source of truth.
4. Give Claude/Codex the relevant new-session prompt.
5. Use handoff packets before execution, QA, frontend handoff, or side-agent work — for `Standard`/`Hard-Gate` tier work; `Micro` tier skips them.
6. Use `scripts/verify-sync.sh` instead of trusting a narrated "synced" claim before reporting sync complete.
7. Write a `docs/activity_log/ACTIVITY_LOG.md` entry before ending any session that changed durable state — summary, pending decisions, open risks/blockers, and the next required action, so a brand-new session can pick up cold. See the Session Close Rule in `AI_COLLABORATION_RULES.md`.

## Core Pattern

```text
Main Conductor
  + Source / Live-State Agent
  + QA Agent or UX / Prompt Agent
```

The main conductor owns final decisions and publishing, auto-triggers QA on `Standard`/`Hard-Gate` work reaching `Ready for Review`, and auto-applies the Model and Effort Policy without asking per call. Side agents provide evidence and proposed findings.

## Optional: Delegated Domain Approvers

Projects with more than one functional owner (engineering, content, marketing, etc.) can name Delegated Domain Approvers — people with hard-gate clearance authority inside their own named domain, escalating to the project Owner only when a decision crosses domains or touches money/legal/privacy/production. This is the mechanism that keeps a single Owner from becoming the approval bottleneck once a project has more than one functional area generating approvable work. See `AI_COLLABORATION_RULES.md`.
