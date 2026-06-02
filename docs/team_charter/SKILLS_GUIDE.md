# [PROJECT_NAME] Skills Guide

**Status:** Draft / Approved  
**Owner:** [OWNER_NAME]

## Purpose

Define project-specific skill equivalents that agents should follow even when local skills are unavailable.

## Skill Equivalent: Source of Truth

Use for:

- Docs.
- Task state.
- Issues.
- Activity logs.
- Approval records.
- Handoff packets.

Rules:

- Source-of-truth docs override chat memory.
- Read relevant task/docs before executing.
- Preserve approval boundaries.

## Skill Equivalent: Implementation / Live State

Use for:

- Source code.
- Schema/data.
- Services.
- Logs.
- Live QA.

Rules:

- Read source-of-truth docs first.
- Live state is authority for deployed/runtime behavior.
- Do not change live state without approval.

## Skill Equivalent: Payments / Integrations

Use for:

```text
[PAYMENT_OR_INTEGRATION_TOOLS]
```

Rules:

- Secrets stay backend-only.
- Client redirects or UI state do not prove trusted outcomes.
- Webhooks/events should be idempotent where relevant.

## Skill Equivalent: Deployment / Serverless Routes

Use for:

```text
[DEPLOYMENT_OR_SERVERLESS_TOOLS]
```

Examples:

- Vercel routes.
- Serverless functions.
- Provider signing routes.
- Environment variables.
- Deployment logs.
- Preview vs production behavior.

Rules:

- Secrets stay server-side.
- Frontend clients must not receive private keys, service-role keys, certificates, or provider signing material.
- Production deployments and env var changes should be hard gates unless explicitly moved to a standing approval lane.
- Live provider state should be persisted in the system of record before downstream status treats it as durable.
- Preview and production behavior must be distinguished.

## Skill Equivalent: Frontend / UX

Use for:

- Frontend prompts.
- Route instructions.
- User-facing copy.
- Client/backend wiring.

Rules:

- Frontend does not own trust decisions.
- Backend/status APIs own gates.
- UI hiding is not security.

## Skill Equivalent: QA

Use for:

- Ready-for-QA tasks.
- Re-QA.
- Evidence review.

Rules:

- QA proposes findings.
- Main conductor owns final verdict.
- QA pass does not approve launch.
