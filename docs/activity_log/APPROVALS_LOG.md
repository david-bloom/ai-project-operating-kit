# Approvals Log

This log records approvals, rejections, Done decisions, and risk acceptances.

## Index

Most recent entries (full chronological list follows below). Once this log grows past a few dozen entries, keep this index to the last ~10 and add a rotation rule: once the log exceeds ~400 lines, archive older entries to `docs/activity_log/archive/APPROVALS_LOG-<range>.md` and update this index to point at the archive.

- 2026-11-08 — APPROVAL-0001

<!-- INDEX_END -->

## Approval Format

```markdown
## APPROVAL-0000 — Approval Title

**Date:** YYYY-MM-DD
**Approved By:** [OWNER_NAME] / [Delegated Domain Approver name]
**Related Task:** TASK-0000 / N/A
**Decision:** Approved / Rejected / Approved with Notes / Done / Not Done / Do Not Do / Approved (Batch) / Approved (Domain)
**Decided By:** (required when Decision is Approved (Domain) — names the domain approver)
**Applies To:** (required when Decision is Approved (Batch) or Approved (Domain) — agents/roles/tasks the approval covers)
**Expires / Review Trigger:** (required when Decision is Approved (Batch) or Approved (Domain); state the operating timezone explicitly, or use a named condition)
**Status:** Active / Expired / Superseded (required when Decision is Approved (Batch) or Approved (Domain))

### Summary

What was approved or rejected?

### Notes

-
```

**Conflict rule:** if `Expires` has passed but `Status` still reads `Active`, the approval is treated as expired regardless of the recorded status — the date wins. `Status: Superseded` overrides date-based validity even before expiration.

## APPROVAL-0001 — Operating-kit remediation sequence

**Date:** 2026-11-08
**Approved By:** David Bloom (explicit instruction in the originating Codex chat)
**Related Task:** WORK-OPERATING-KIT-REMEDIATION
**Decision:** Approved
**Approved Scope:** Execute the proposed five-phase remediation: policy/specification,
implementation, tests, independent review, disposable pilot, pinned release and migration guide.
**Not Approved:** Automatic adoption by Cramapple or other consumers, production application
changes, spending, secret changes or repository-protection bypass.
**Source instruction:** "execute the proposed remediation sequence". The later "restart"
was treated as resuming this work while preserving existing changes.
**Notes:** This records the user's authorization; it is not an authenticated machine-action
approval. Consumer external actions need their own trusted, structured approval records.
