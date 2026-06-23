# [PROJECT_NAME] Definition of Done

**Status:** Draft / Approved  
**Owner:** [OWNER_NAME]

A task is Done only when:

- Approved scope is implemented.
- Acceptance criteria are met.
- Tests/QA checks are documented.
- Deviations are documented.
- Risks or residual gaps are documented.
- Required approvals are recorded.
- Required source-of-truth docs are updated.
- For `Standard` and `Hard-Gate` tier tasks: the QA Agent's recommended verdict is `Pass` and the Main Conductor has integrated it — only the Main Conductor sets status to `Done`.
- For `Hard-Gate` tier tasks: Owner (or relevant Delegated Domain Approver) sign-off is recorded at `Awaiting Owner Approval` before the status moves to `Done`.
- `Micro` tier tasks skip the QA-verdict and sign-off requirements above — log completion in `ACTIVITY_LOG.md` and move directly to `Done`.

Not Done:

- Code exists but no QA evidence, for any tier above `Micro`.
- QA verdict is `Pass` but a required Owner/domain-approver sign-off is missing on a `Hard-Gate` tier task.
- Implementation relies on chat-only decisions.
- A Hard Gate was crossed without approval.
- A task tagged `Micro` actually had cross-domain, financial, legal, or production impact — wrong tier, not an exemption.
