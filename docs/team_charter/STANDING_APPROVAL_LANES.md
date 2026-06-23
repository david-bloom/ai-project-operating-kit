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
- Any `Micro`-tier task (see `AGENT_OPERATING_MODEL.md`, Task Tiers) — reversible, local, low blast radius.

Standing approvals do not authorize implementation, deployments, migrations, secret changes, QA pass decisions, task closure, Done decisions, risk acceptance, or launch.

## Lane 2 — Batch Approvals

Recorded in `docs/activity_log/APPROVALS_LOG.md` — there is no separate index; the per-entry record is the only authoritative list. Agents who need to know which batch approvals are currently in force grep the log for `Decision: Approved (Batch)` and evaluate the per-entry `Expires` and `Status` fields.

```text
## APPROVAL-NNNN — Batch Title

**Date:**
**Approved By:**
**Related Task:**
**Decision:** Approved (Batch)
**Applies To:**
**Expires / Review Trigger:**
**Status:** Active / Expired / Superseded

### Approved Scope
### Not Approved
### Notes
```

**Expiration semantics.** `Expires` is end-of-day inclusive in the project's stated operating timezone (record the timezone explicitly the first time this lane is used — do not leave it implicit). If today is after `Expires` but `Status` still reads `Active`, treat the approval as expired regardless of the recorded status — the date wins; flag the stale record in the next commit. `Status: Superseded` overrides date-based validity even before expiration. A named condition (e.g., "when TASK-0012 closes") may substitute for a date.

**Silence-is-consent SLA for `Standard`-tier approvals (optional).** Projects may let a `Standard`-tier item awaiting owner sign-off default-approve after the window stated in its `Expires` field if the owner has not objected. This reuses the same `Expires`/`Status` machinery as any other batch approval — it is not a separate mechanism. Should not apply to `Hard-Gate`-tier items. Adopt only if the project's risk tolerance and review cadence support it.

**Delegated domain-approver decisions** (if the project uses the optional Delegated Domain Approvers role — see `AI_COLLABORATION_RULES.md`) are recorded the same way as a batch approval, with `Decision: Approved (Domain)` and a `Decided By:` field naming the domain approver. Do not record a domain approval as plain `Approved`, which would obscure who actually made the call.

**Per-task citation.** A task invoking a batch approval (including an SLA default-approval) cites the `APPROVAL-NNNN` ID in its `Approval State` block.

## Lane 3 — Hard Gates

Owner approval is required before — **or** clearance from the relevant Delegated Domain Approver, if the project uses that role, when the decision stays entirely inside their domain and does not touch money, legal, privacy, production, or a second domain:

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
- Material changes to `docs/team_charter/` documents — the operating model itself.

This list is a floor, not a ceiling — a project's actual hard-gate list (recorded where `[HARD_GATES]` is filled in) should be at least this broad, and typically grows to cover project-specific risk (e.g. content licensing, regulated-data handling, public claims) as those risks are identified. Narrowing this list later should remove categories that are ambiguous or rarely triggered, never a category that exists because of a specific past incident.

**Ambiguity does not automatically mean Hard Gate.** If classification is unclear:
- ambiguous, reversible, and low blast radius → ask one clarifying question and proceed under Standing Approval;
- ambiguous and irreversible, or high blast radius → treat as a Hard Gate.
