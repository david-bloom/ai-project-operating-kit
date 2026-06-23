# [PROJECT_NAME] Tool and Integration Guide

**Status:** Draft / Approved  
**Owner:** [OWNER_NAME]

## Purpose

This guide covers project-specific tool and integration skills only. Role definitions, agent boundaries, source-of-truth rules, and QA process live in `AI_COLLABORATION_RULES.md` and `AGENT_OPERATING_MODEL.md` — not here. (This file was renamed from `SKILLS_GUIDE.md`; its previous "Source of Truth," "Implementation / Live State," and "QA" sections were removed because they duplicated role rules already defined canonically elsewhere — a second copy of a role rule drifts from the first, and an agent that reads only this file because the task looked technical would miss updates made to the canonical doc.)

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
