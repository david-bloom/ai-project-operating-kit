# [PROJECT_NAME] Agent Operating Model

**Status:** Draft / Approved  
**Owner:** [OWNER_NAME]

## Default Pattern

For active work blocks with meaningful parallelizable work, use:

```text
Main Conductor
  + Source / Live-State Agent
  + QA Agent or UX / Prompt Agent
```

The main conductor owns final decisions. Side agents provide evidence and proposed findings.

## Main Conductor

Owns:

- Reading source-of-truth docs first.
- Confirming approval state.
- Creating or updating handoff packets.
- Assigning narrow side-agent scopes.
- Integrating findings.
- Resolving conflicts.
- Publishing final updates.

## Source / Live-State Agent

Use for:

- Backend/source/schema evidence.
- Live-state checks.
- Implementation impact maps.
- Tool/API state checks.

Must not:

- Deploy.
- Migrate.
- Change secrets.
- Publish final decisions.
- Close tasks.
- Mark QA passed.

## QA Agent

Use for:

- Ready-for-QA tasks.
- Re-QA after remediation.
- Independent skeptical review.

Returns:

1. Proposed verdict.
2. Blocking findings.
3. Non-blocking risks/test gaps.
4. Evidence reviewed.
5. Required remediation or next action.
6. Remaining approval boundaries.

Must not publish, approve, close, mark passed, deploy, migrate, or alter live state.

## UX / Prompt Agent

Use for:

- Frontend prompts.
- User-facing route behavior.
- Copy.
- Design-system risks.
- Client/backend contract clarity.

## Manual Sync Handshake

If the project enables an optional manual sync handshake, such as `C` or `c`, agents treat it as a request to refresh from source-of-truth records and report state.

The main conductor should use the handshake to:

- Re-read relevant GitHub docs, task files, issues, and logs.
- Confirm approval boundaries.
- Identify blockers and next action.
- Decide whether a handoff packet or side-agent review is needed.

Side agents and QA agents may respond to the handshake with evidence and proposed findings only. The handshake does not grant authority to execute, publish, approve, close, mark passed, or launch.

## Anti-Patterns

- Asking side agents to review the whole task.
- Treating side-agent findings as final.
- Giving agents overlapping write scopes.
- Treating QA pass as launch approval.
- Relying on chat-only memory.

