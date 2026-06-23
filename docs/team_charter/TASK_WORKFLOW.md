# [PROJECT_NAME] Task Workflow

**Status:** Draft / Approved  
**Owner:** [OWNER_NAME]

## Standard Task Flow

1. Owner sets direction or identifies need.
2. Main conductor writes or updates task spec, including its Tier.
3. Owner (or relevant Delegated Domain Approver) approves task spec when required.
4. Implementation agent executes approved scope.
5. Implementation agent documents result.
6. QA agent or conductor performs review.
7. Implementation agent remediates if needed.
8. Owner reviews when required.
9. Task closes only after Done criteria are satisfied.

## Required Task Metadata

```text
Task ID:
Title:
Owner:
Tier:
Status:
Priority:
Created Date:
Approved Date:
Product Goal:
Technical Scope:
Out of Scope:
Routes / Components / Systems Affected:
Data / Security / Integration Impact:
Acceptance Criteria:
QA Plan:
Implementation Summary:
Test Results:
Risks / Issues:
Approval State:
QA Result:
Done Decision:
```

`Tier` is `Micro`, `Standard`, or `Hard-Gate` — see `AGENT_OPERATING_MODEL.md`, Task Tiers. It determines how much of the rest of this workflow actually applies: `Micro` skips the handoff packet and most status states below; `Standard` uses the full flow; `Hard-Gate` uses the full flow plus the `Awaiting Owner Approval` status.

## Status Values

Use one clear status at all times. Six states cover `Micro` and `Standard` tier work; `Hard-Gate` tier adds one more before `Done`:

```text
Not Started
In Progress
Blocked
Ready for Review
Awaiting Owner Approval   (Hard-Gate tier only)
Done
Do Not Do
```

### Status Definitions

- **Not Started** — no work has begun.
- **In Progress** — work is underway. Covers what some projects track separately as "Spec Drafted" or "Approved for Execution"; those don't change what anyone should do next.
- **Blocked** — deferred pending input or a dependency, including a QA-side dependency. The QA Agent may set this status.
- **Ready for Review** — someone needs to look at this next. Who that is comes from the task's tier and current state (QA Agent, then Main Conductor; Owner or domain approver for `Hard-Gate` tier), not from a separate status word per reviewer.
- **Awaiting Owner Approval** — `Hard-Gate` tier only; explicit Owner or delegated domain approver sign-off is the only thing blocking `Done`.
- **Done** — completed. Only the Main Conductor sets this status, after integrating the QA Agent's recommended verdict.
- **Do Not Do** — the Owner evaluated the task and explicitly declined or descoped it. The work will not be done. Different from `Blocked` (deferred, not rejected) and `Done` (completed, not declined). The Main Conductor records the decision in `APPROVALS_LOG.md` and updates the task status.

If a project's work genuinely needs more granularity than this (e.g. distinguishing *why* something is blocked), prefer adding detail in the task's own notes over adding a new global status word — a status should change what a human does next, not just record a flavor of the same thing.

## Approval Classes

See `STANDING_APPROVAL_LANES.md` for the full definitions of Standing Approval (Lane 1), Batch Approval (Lane 2, including the optional silence-is-consent SLA and delegated domain approvals), and Hard Gate (Lane 3). Do not restate the lane definitions here — this section is a pointer, not a second copy.
