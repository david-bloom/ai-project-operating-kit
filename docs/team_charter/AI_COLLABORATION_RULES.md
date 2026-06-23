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

### Delegated Domain Approvers (optional)

Projects with more than one functional owner (e.g. engineering, content, marketing) may name Delegated Domain Approvers — people or roles with approval authority inside a specific, named domain, without routing every decision through the Owner.

If used:

- Within their named domain, a Delegated Domain Approver may clear a hard gate without the Owner's separate review.
- A decision stays in its domain lane by default. It escalates to the Owner only when it visibly: (1) touches a second named domain, (2) touches money, legal, privacy, or production, or (3) the domain approver explicitly punts it.
- Domain approval does not replace Owner approval where one of the three escalation conditions applies.

This exists because a single-Owner approval model — even with standing approval lanes — recreates the Owner as a bottleneck once a project has more than one functional area generating approvable work. Projects with one Owner and no separable domains can skip this section.

### Main Conductor

Owns:

- Source-of-truth orientation.
- Approval boundaries.
- Agent coordination.
- Final QA verdicts.
- GitHub publishing.
- Setting a task's status to `Done` after integrating the QA Agent's recommended verdict and verifying evidence. This is the only role that may make that transition.

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

The QA Agent **may** set a task's status to `Blocked` when QA cannot proceed (missing evidence, blocked dependency, environment issue), and may populate the task's `QA Result` and `Test Results` fields with proposed findings, evidence, and a recommended verdict (`Pass` / `Fail`).

The QA Agent **must not** set status to `Done` or `Do Not Do`, approve, close, publish final decisions, deploy, migrate, alter live state, or otherwise mark a task passed as final. Those are Main Conductor or Owner actions.

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

Material changes to charter documents are Hard Gates, recorded in `docs/team_charter/CHANGELOG.md` with cross-references to the governing `APPROVAL-NNNN` and `DECISION-NNNN`.

### In-Progress Drafts and Branches

Durability (has the work reached GitHub so it isn't trapped on one machine) and approval lifecycle (is the underlying work approved) are independent axes. Do not conflate them.

**Branch convention.** In-flight work happens on a feature branch off `main`, pushed to GitHub. Actor-prefixed branches (`codex/...`, `claude/...`, other descriptive prefixes) are standard; what matters is the branch is descriptively named and pushed to the remote. A doc on a pushed feature branch satisfies the Source-of-Truth Rule — it does not need to be on `main` to be durably synced.

**Branch and status are independent.** A governed document with `Status: Draft` may live on a feature branch or on `main`. A `Proposed` document may live on either; recording a `Proposed` decision on `main` durably captures it without implying approval. An `Approved` document typically lives on `main` once merged, or on a feature branch if approved before merge. No combination is implicitly forbidden.

**Merging is mechanical.** A merge to `main` does not itself require a fresh approval — it inherits the approval state of the work it carries:
- Implementation within an approved task: already approved, merge proceeds.
- Documentation-only updates recording an already-approved decision: Standing Approval, merge proceeds.
- Recording a new `Proposed` decision: Standing Approval; the doc lands on `main` with `Status: Proposed`; approving the proposal itself is a separate, later event.
- Implementation not covered by an approved task, or material charter changes: Hard Gate before any merge that lands it. The gate is on the work, not the merge.

**PR policy.** Direct pushes to a feature branch are acceptable — no PR required for ongoing work. Promotion to `main` uses a PR only when the underlying work requires review (Hard Gate review or batch-approval verification); Standing Approval work can merge directly.

**Push cadence.** Push at the end of each work session; push before any handoff; push before reporting `Ready for Review` or invoking `SYNC` on this work; always verify the remote contains the commit before reporting sync complete — see `scripts/verify-sync.sh`.

**What "synchronization complete" means.** Applies to the branch the agent is working on, not necessarily `main`. A sync report must state: the branch name; that the latest commit is verified present on the remote; and, for governed documents in the change, the document's `Status:` value.

## Universal Document Format Rule

Markdown (`.md`) is the default and canonical medium for project documents. Keep durable plans, requirements, policies, architecture docs, decisions, logs, and task records as Markdown in GitHub unless a different format is required by the artifact itself.

### Document Status

Apply a lifecycle `Status:` header to **governed documents** only: proposals, specifications, policies, charter docs, and individual entries in `DECISIONS_LOG.md`. Recognized values: `Draft` (actively being written), `Proposed` (stable enough to review, awaiting a decision), `Approved` (approval recorded), `Superseded` (replaced, preserved for history).

Do not apply this lifecycle `Status:` to append-only logs themselves, to `APPROVALS_LOG.md` entries (which use a `Decision:` enum, not lifecycle `Status:`), or to templates, indexes, README files, or non-Markdown files. Batch-approval entries in `APPROVALS_LOG.md` carry their own separate operational `Status: Active / Expired / Superseded` — a distinct vocabulary that never mixes with lifecycle `Status:` on the same entry.

## Manual Sync Handshake — `SYNC`

Projects may define a short manual trigger that tells an agent to re-sync from the source of truth before continuing.

Trigger:

```text
SYNC
```

`SYNC` is used in full, uppercase, standalone — not a single character — because a one-character trigger is too easy to fire accidentally in normal chat, code, or typos, and a missed deliberate trigger is worse than a rare false one. `SYNC` is also portable across clients that intercept slash-prefixed tokens before they reach an agent.

When the owner sends the trigger, the agent should:

- Re-read current GitHub source-of-truth docs, task files, issues, and activity/approval logs relevant to the active work.
- Check `docs/team_charter/CHANGELOG.md` for entries newer than the last read and re-read any affected charter docs before reporting state.
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
