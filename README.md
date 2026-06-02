# AI Project Operating Kit

A reusable operating kit for working with AI coding/research agents across projects.

This kit gives a project a shared source-of-truth workflow, approval lanes, handoff packet, task workflow, QA-agent model, and startup prompts for tools such as Claude, Codex, Lovable, and side agents.

## What This Solves

AI agents move faster when the project has durable memory and clear authority boundaries.

This kit helps prevent:

- Chat-only decisions becoming hidden project state.
- Agents executing before approval.
- QA agents acting as final approvers.
- Repeated re-orientation at the start of every session.
- The human project owner becoming the memory and coordination bottleneck.

## Optional Manual Sync Handshake

The kit supports an optional short trigger, such as `C` or `c`, that means:

```text
Re-read the current source-of-truth docs/issues/logs and report state before continuing.
```

This is useful when the owner wants an agent to refresh from durable project records without restating the full workflow. The trigger is sync/review only; it does not authorize execution, deployment, approval, closure, risk acceptance, or launch.

## Contents

```text
docs/team_charter/
  AI_COLLABORATION_RULES.md
  TASK_WORKFLOW.md
  AGENT_OPERATING_MODEL.md
  HANDOFF_PACKET_TEMPLATE.md
  STANDING_APPROVAL_LANES.md
  SKILLS_GUIDE.md
  DEFINITION_OF_DONE.md

docs/activity_log/
  ACTIVITY_LOG.md
  APPROVALS_LOG.md
  DECISIONS_LOG.md

docs/tasks/
  TASK_TEMPLATE.md

prompts/
  CLAUDE_NEW_SESSION_PROMPT.md
  CODEX_NEW_SESSION_PROMPT.md

PROJECT_SETUP.md
```

## Quick Start

1. Copy this repo's `docs/` and `prompts/` folders into a project.
2. Edit placeholders such as `[PROJECT_NAME]`, `[OWNER_NAME]`, and `[HARD_GATES]`.
3. Make GitHub docs the project source of truth.
4. Give Claude/Codex the relevant new-session prompt.
5. Use handoff packets before execution, QA, frontend handoff, or side-agent work.

## Core Pattern

```text
Main Conductor
  + Source / Live-State Agent
  + QA Agent or UX / Prompt Agent
```

The main conductor owns final decisions and publishing. Side agents provide evidence and proposed findings.

