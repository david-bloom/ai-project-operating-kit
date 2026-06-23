# [PROJECT_NAME] Handoff Packet Template

Use before execution, QA, frontend handoff, complex delegation, or task owner changes — for `Standard` and `Hard-Gate` tier work. `Micro` tier tasks (see `AGENT_OPERATING_MODEL.md`, Task Tiers) skip this template entirely.

```text
Task:
- TASK-XXXX — Title

Prompts Included:
- [ ] Implementation Agent
- [ ] QA Agent
- [ ] UX / Prompt Agent

Current Source:
- Task doc:
- Related docs:
- Relevant issue/comment:
- Latest commits reviewed:

Approval State:
- Approved:
- Not approved:
- Required before execution:

Live / Tool State:
- Environments checked:
- Services checked:
- Not checked / unavailable:

Files / Systems Affected:
- Docs:
- Code:
- Data/schema:
- Integrations:
- Frontend/routes:
- Other:

Open Risks / Blockers:
- P1:
- P2:
- Pending owner decisions:

Do Not Touch:
- Scope exclusions:
- Deferred features:
- Hard gates:

Next Expected Output:
- Spec / implementation / QA / prompt / issue comment:
- Required files to update:
- Required evidence:

Include only the prompt(s) for the agent(s) checked in `Prompts Included` above. Omit the others entirely — do not leave empty triple-quoted blocks or placeholder text.

Recommended Prompt for Implementation Agent:
"""
[Paste concise execution instruction here.]
"""

Recommended Prompt for QA Agent:
"""
[Paste concise QA instruction here.]
"""

Recommended Prompt for UX / Prompt Agent:
"""
[Paste concise frontend/prompt instruction here.]
"""
```
