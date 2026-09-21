# AI Operating Kit — Architecture (design of record)

**Status:** APPROVED architecture (2026-09-21), through v0.3 of the proposal after two external (Codex) review rounds. This is the rationale and layer model; the operative rules live once in `docs/CORE_OPERATING_POLICY.md` (this doc does not restate them).

## Decisions recorded

- **Canonical core home:** this repo, `ai-project-operating-kit`, is the one canonical core. Design Studio becomes its first *consumer* (a profile), not a second author of policy. *(David, 2026-09-21.)*
- **Core spine:** the core is an **extraction and generalization of Design Studio `OPERATING_POLICY` 2.0** — its lifecycle, publication invariants, provenance, availability model, receipts, and recovery behavior preserved in semantics; actor/role/path/artifact/protection/profile assumptions made data-driven. Plus two imports from the prior operating kit: **task-risk tiers** and the **authority/approval-lane** matrix.
- **Deferrals (ratified):** no standalone updater/hash-drift tooling yet (dependency contract only); no exhaustive per-scenario recovery handlers (invariants only); no dedicated multi-run engine (compose from isolated handoffs). Each graduates to a feature only by explicit decision if it becomes real and recurring.

## The governing rule (anti-drift)

> Operating-rule **semantics** are defined once, in the core. Profiles add domain methods but never redefine core semantics. Projects declare **parameter values** for core-defined semantics; they never redefine them.

This single rule is the whole anti-drift mechanism. The drift being fixed: three operating models had forked (this kit's `team_charter`, Cramapple's copy of it, and Design Studio's `OPERATING_POLICY` 2.0), and project charters had absorbed operating rules and become semi-alternate protocols.

## Three layers

- **Core** (this repo) — governance, lifecycle, publication/receipts/recovery, the generic roles, and the two primitives below. One authoritative source.
- **Profiles** — Design / UX / QA. Thin modules over the core: domain roles, stages, schemas, evidence rules, selection/escalation triggers, validators/runners, artifact strategy, output namespaces. They may not redefine core mechanics. QA baseline review lives in the core; the QA *profile* is the heavier layer added on need. Standalone use = a profile bundles a **pinned dependency** on the core (never a copied, editable governance folder).
- **Project** — a small **manifest** (parameters: which actors + delivery capabilities, active profiles + versions, owner/orchestrator/steward, default tier, isolation defaults, hard gates, protected paths) plus the **charter** (brief, decisions, scope, content) plus **handoffs** (frozen, independently reviewed work units). The charter holds content and decisions, never operating rules.

## Two core primitives

- **Isolation (read/context)** — a declared, per-handoff field (`open` by default; else `withhold` + a named `lift_when` event). One primitive unifies design clean-room, cross-model QA decorrelation, and independent UX testing. Not an ambient mode.
- **Integration (write path)** — split into **delivery capability** (a property of the actor surface: `airlock | branch | publisher`) and **landing policy** (derived mechanically from the diff by the steward). "Has write" is never a proxy for either. Only the steward writes the source-of-truth branch.

## Intake → manifest

Starting a coordinated project runs a short intake that asks **observable facts** (is a user-facing flow changing? do money/privacy/production/external-publication apply? exploratory/judgment/release-adjacent? visual design involved?) and **derives** recommended profiles + tier + lane, with explicit override + recorded reason. Its only output is the manifest — the single declared record of how the project runs and the source for auto-generating each participant's self-contained instructions.

## What this fixes

Clean-room becomes a declared field with a lift trigger (no "is it on?" ambiguity); the three divergent models collapse to one core + a profile + a migration; charters can no longer be alternate protocols; and airlock/isolation stop being "owned" by Design — they are general core primitives.

## Migration order

Designate canonical core (done) → extract/generalize the core + build the two imports (Increment 1/1b) → pass conformance fixtures (Increment 2) → Design Studio as first profile consumer + end-to-end pilot (Increment 3) → UX profile → QA profile (separating built vs planned) → reconcile Cramapple's fork once its divergence is visible.

*Full proposal history (v0.1 → v0.3) and the Codex review record are retained with the Owner; this file is the durable summary.*
