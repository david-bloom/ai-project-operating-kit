# Decisions Log

This log records product, architecture, operating, security, design, and workflow decisions.

## Index

Most recent entries (full chronological list follows below). Once this log grows past a few dozen entries, keep this index to the last ~10 and add a rotation rule: once the log exceeds ~600 lines, archive older entries to `docs/activity_log/archive/DECISIONS_LOG-<range>.md` and update this index to point at the archive. Don't let this slip — an unrotated decisions log becomes too expensive to read in full at session start, which is exactly when it matters most.

- 2026-11-08 — DECISION-0001

<!-- INDEX_END -->

## Decision Format

```markdown
## DECISION-0000 — Decision Title

**Date:** YYYY-MM-DD
**Decision Owner:** [OWNER_NAME]
**Status:** Proposed / Approved / Superseded
**Related Task:** TASK-0000 / N/A
**Area:** Product / Architecture / Security / Design / Operations / Integration

### Context

### Decision

### Rationale

### Consequences

### Risks / Follow-ups
```

## DECISION-0001 — Replace privileged publishing with read-only validation

**Date:** 2026-11-08
**Decision Owner:** David Bloom
**Status:** Approved direction through APPROVAL-0001
**Related Task:** WORK-OPERATING-KIT-REMEDIATION

Retain manifests, explicit handoffs, isolation and exact receipts. Replace broad custom
publisher privileges with strict read-only policy validation and repository-native PR/check/
merge controls. Borrow Cramapple's tier-first startup, canonical index, branch continuity,
scoped approvals and independent QA. Consumer adoption is a separate explicit record.
Runtime evidence is advisory until authenticated host integration binds the inputs.
