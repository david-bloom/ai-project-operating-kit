# v-next Build Status

Tracks the migration from three divergent operating models to one canonical core.
Architecture: `docs/architecture/AI_OPERATING_KIT_ARCHITECTURE.md`. Rulebook: `docs/CORE_OPERATING_POLICY.md`.

| Increment | Scope | Status |
|---|---|---|
| 0 — Record | Land approved architecture + decisions as design-of-record | **drafted (this branch)** |
| 1 — Core (docs/schema) | Generalized core policy, manifest schema, handoff template, actor/role registries | **drafted (this branch)** |
| 1b — Core (scripts) | Generalize `handoff-check` + `publish` to be config/manifest-driven (data-driven actors/roles/paths/protection/namespaces; delivery→landing; tiers; approval gates; review linkage; isolation lift; manifest hashing) | not started |
| 2 — Conformance fixtures | See list below; core does not migrate until these pass | not started |
| 3 — Design Studio as first profile consumer + pilot | Convert design-studio to consume the core; run one project end-to-end | not started |
| 4 — UX profile | Quick/Standard modes; Deep composed from isolated handoffs + synthesis | not started |
| 5 — QA profile | Diff/risk analyzer, deterministic runners, specialists, evidence schema, default-off auto-fix; automation actor | not started |
| 6 — Cramapple reconciliation | Fold its forked `team_charter/` back to the core once its divergence is visible | not started |

## Increment 2 — required conformance fixtures
valid/invalid lifecycle transitions · branch and airlock delivery · protected-path review · protected-approval timing at each gate · required-review linkage + block-acceptance-until-reviewed · tier escalation · micro logging · project-defined protected paths · manifest staleness · incompatible profile/core versions · isolation lift · scheduled-automation intake · remote-source-of-truth rejection + rescue · revision/supersession · duplicate/at-most-once publication.

## Deferred (one-off unless recurring — ratified 2026-09-21)
standalone updater / hash-drift tooling (dependency contract only for now) · exhaustive per-scenario recovery handlers (invariants only) · dedicated multi-run engine (compose from isolated handoffs).

## Constraints
- The drafting session is branch-bound: it produces increments as reviewable branches; landing to this repo's source-of-truth branch is the Owner's review PR (core governance is protected).
- Predecessor kits should be frozen from further governance edits during extraction to avoid mid-migration drift.
