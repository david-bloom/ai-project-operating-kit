# Activity Log

This log records meaningful operating activity, approvals, closeouts, blockers, and handoffs — including a **Session Close** entry at the end of any work session that changed durable state (see `AI_COLLABORATION_RULES.md`, Session Close Rule).

## Index

Most recent entries (full chronological list follows below). Once this log grows past a few dozen entries, keep this index to the last ~10 and add a rotation rule: once the log exceeds ~400 lines, archive older entries to `docs/activity_log/archive/ACTIVITY_LOG-<range>.md` and update this index to point at the archive.

## Entry Format

```markdown
## [Task or Session Title] — YYYY-MM-DD

**Task:** what this entry covers — a task ID/title, or a session-level summary label if the session touched multiple tasks/projects
**Status:** Initialized / In Progress / Blocked / Done / etc. — or N/A for a pure session-close summary that isn't itself one task
**Summary:** what happened, in enough detail that a fresh reader doesn't need the prior conversation

**Pending Decisions:** anything raised but not yet decided, and who decides it — state `None` explicitly rather than omitting the field
**Open Risks / Blockers:** anything that could derail the next session if not flagged — `None` explicitly if there aren't any
**Next Owner:** who picks this up next
**Next Required Action:** the concrete next step, not "continue work"
```

Every entry — task-level or session-close — uses this shape. A Session Close entry is the same format with `Task` naming the session rather than a single task ID when the session spanned more than one.

- Project Initialized — YYYY-MM-DD

---

## Project Initialized — YYYY-MM-DD

**Task:** Project operating kit setup  
**Status:** Initialized  
**Summary:** AI Project Operating Kit installed.

**Pending Decisions:** None  
**Open Risks / Blockers:** None  
**Next Owner:** [OWNER_NAME]  
**Next Required Action:** Customize placeholders and approve workflow docs.
