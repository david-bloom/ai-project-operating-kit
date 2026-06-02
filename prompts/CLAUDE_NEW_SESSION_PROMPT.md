# Claude New Session Prompt

```text
Before doing any work, read this project's current GitHub documentation. GitHub documentation is the source of truth. Do not rely on prior chat memory unless it has been recorded in GitHub.

Start by reading the relevant docs for the task. If the task is unclear or broad, orient from:

- docs/team_charter/AI_COLLABORATION_RULES.md
- docs/team_charter/TASK_WORKFLOW.md
- docs/team_charter/AGENT_OPERATING_MODEL.md
- docs/team_charter/HANDOFF_PACKET_TEMPLATE.md
- docs/team_charter/STANDING_APPROVAL_LANES.md
- docs/team_charter/SKILLS_GUIDE.md
- docs/activity_log/ACTIVITY_LOG.md
- docs/activity_log/APPROVALS_LOG.md

Then report:

1. Current task or issue.
2. Approval state.
3. Whether owner approval is required.
4. Open risks/blockers.
5. Next recommended action.
6. Handoff packet if execution, QA, frontend handoff, or side-agent coordination is next.

Use the project operating model:
- Main Conductor owns source-of-truth, approval boundaries, final decisions, and GitHub publishing.
- Source / Live-State Agent provides implementation evidence.
- QA Agent proposes findings only.
- UX / Prompt Agent handles frontend prompts and route behavior where relevant.

Follow standing approval lanes. Stop at hard gates.
```

