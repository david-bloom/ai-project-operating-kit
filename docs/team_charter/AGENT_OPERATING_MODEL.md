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

**When to spawn additional agents.** Use another agent only when it creates real parallelism or independence — not as ceremony.

Good uses: one implementation agent; one fresh QA agent; one research or live-state agent when genuinely needed; one orchestrator to coordinate the work.

Bad uses: extra agents that all need the same context; agents that simply re-read the same material someone already has; agent sprawl that recreates the same bottleneck in a new form, just with more steps.

## Main Conductor

Owns:

- Reading source-of-truth docs first.
- Confirming approval state.
- Creating or updating handoff packets.
- Assigning narrow side-agent scopes.
- Integrating findings.
- Resolving conflicts.
- Publishing final updates.
- **Auto-triggering QA** for any `Standard` or `Hard-Gate` tier task that reaches `Ready for Review` — QA is a workflow step that fires automatically, not a request someone has to remember to make. `Micro` tier QA is optional, at the conductor's judgment.
- **Auto-applying the Model and Effort Policy** below for every agent it spawns, without asking the Owner to pick a model each time. Model choice is policy, not a per-call decision.

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

- Tasks at `Ready for Review` (tier: Standard or Hard-Gate) — **auto-triggered by the Main Conductor**, not invoked only on request. `Micro` tier: optional, conductor's judgment.
- Re-QA after remediation.
- Independent skeptical review.

**QA must be a genuinely fresh, independent context — not a relabeled continuation of the implementer's own thread.** That independence is the actual mechanism that catches blind spots; a QA pass run in the same context as the implementation is QA in name only.

Returns:

1. Proposed verdict (Pass / Fail).
2. Blocking findings.
3. Non-blocking risks/test gaps.
4. Evidence reviewed.
5. Required remediation or next action.
6. Remaining approval boundaries.

May set status to `Blocked` when QA cannot proceed. Must not publish, approve, close, set status to `Done` or `Do Not Do`, deploy, migrate, or alter live state.

## UX / Prompt Agent

Use for:

- Frontend prompts.
- User-facing route behavior.
- Copy.
- Design-system risks.
- Client/backend contract clarity.

## Manual Sync Handshake — `SYNC`

If the project enables the manual sync handshake, agents treat `SYNC` (uppercase, standalone — not a single character, which is too easy to trigger by accident) as a request to refresh from source-of-truth records and report state.

The main conductor should use the handshake to:

- Re-read relevant GitHub docs, task files, issues, and logs.
- Check `docs/team_charter/CHANGELOG.md` for changes since the last read.
- Confirm approval boundaries.
- Identify blockers and next action.
- Decide whether a handoff packet or side-agent review is needed.

Side agents and QA agents may respond to the handshake with evidence and proposed findings only. The handshake does not grant authority to execute, publish, approve, close, mark passed, or launch.

## Model and Effort Policy

Match reasoning depth to risk, not to role title, and keep the policy portable across whichever harness is in use (Claude, Codex, Lovable, or others):

- **Fast/default tier** — drafting, routine edits, summaries, straightforward implementation support, handoff-packet and task-spec scaffolding.
- **Strongest available tier** — final QA verdicts, hard-gate classification, Main Conductor judgment calls, and any ambiguous or sensitive policy reasoning. These are low-frequency, high-blast-radius decisions; they're exactly where extra reasoning depth earns its cost.
- **Deterministic scripts and tools** — whenever the task can be made mechanical (e.g. `scripts/verify-sync.sh`), prefer a script over an agent narrating compliance.

Don't keep additional model/effort variants beyond this unless they earn their place with a measurable quality or cost win.

**This is applied automatically by the Main Conductor, not negotiated per call.** The conductor picks the tier from the policy above and proceeds — it does not ask the Owner which model to use. The conductor records which tier it used and why only when it deviates from the default (i.e., escalates to the strongest tier for a judgment call) — logging every routine fast-tier call would recreate the ceremony this policy exists to remove.

The orchestrator stays within the existing approval boundary regardless of model choice: model selection never substitutes for required Hard-Gate sign-off on legal, privacy, production, money, or irreversible decisions.

## Task Tiers

Every task gets a tier, set at creation:

- **Micro** — standing-approved, reversible, low blast radius. Skips the handoff packet; uses a minimal status path (`Not Started` → `In Progress` → `Done`); logged, not packeted.
- **Standard** — the default workflow: handoff packets where meaningful, full status path, QA as needed.
- **Hard-Gate** — Standard workflow plus explicit Owner (or delegated domain approver) sign-off before `Done`.

A diff touching only docs, tests, or an already-low-risk path may be tagged `Micro` by file-pattern alone rather than requiring a fresh judgment call every time.

## Anti-Patterns

- Asking side agents to review the whole task.
- Treating side-agent findings as final.
- Giving agents overlapping write scopes.
- Treating QA pass as launch approval.
- Relying on chat-only memory.
- Running QA in the same context/thread as the implementation it's reviewing.
- Defaulting ambiguous-but-reversible work to a hard gate instead of asking a clarifying question.
- Applying Hard-Gate ceremony to Micro-tier work, or skipping QA on Hard-Gate work to save time.
- Waiting for someone to explicitly ask for QA on `Standard`/`Hard-Gate` work instead of auto-triggering it.
- Asking the Owner to choose a model per call instead of applying the Model and Effort Policy automatically.
- Spawning agent sprawl that recreates the same coordination bottleneck in a new form, just with more steps.
