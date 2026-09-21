# v-next Build Status

Tracks the migration from three divergent operating models to one canonical core.
Architecture: `docs/architecture/AI_OPERATING_KIT_ARCHITECTURE.md`. Rulebook: `docs/CORE_OPERATING_POLICY.md`.

| Increment | Scope | Status |
|---|---|---|
| 0 — Record | Land approved architecture + decisions as design-of-record | **drafted (this branch)** |
| 1 — Core (docs/schema) | Generalized core policy, manifest schema, handoff template, actor/role registries | **drafted (this branch)** |
| 1b — Core (scripts) | Generalize `handoff-check` + `publish` to be config/manifest-driven (data-driven actors/roles/paths/protection/limits; delivery→landing; tiers; approval gates; review linkage; manifest/instructions hashing) | **drafted (this branch)** |
| 2 — Conformance fixtures | Runnable suite (`tests/run.sh`); core does not migrate until these pass | **drafted — 27/27 passing** |
| 3 — Design Studio as first profile consumer + pilot | Convert design-studio to consume the core; run one project end-to-end | not started |
| 4 — UX profile | Quick/Standard modes; Deep composed from isolated handoffs + synthesis | not started |
| 5 — QA profile | Diff/risk analyzer, deterministic runners, specialists, evidence schema, default-off auto-fix; automation actor | not started |
| 6 — Cramapple reconciliation | Fold its forked `team_charter/` back to the core once its divergence is visible | not started |

## Increment 2 — conformance fixtures (`tests/run.sh`)
A dependency-free runner (git + bash + awk). Each case runs in a throwaway git
repo with its own bare origin, so cases are isolated; `tests/run.sh` exits non-zero
on any failure. **27/27 passing** as of this branch.

Covered: valid + invalid lifecycle transitions · branch delivery (auto-merge) ·
delivery provenance verified against the raw return (airlock/branch) · protected-path
review (floor **and** project-defined) · approval-gate timing at each transition
(before_dispatch / before_external_action / before_acceptance) · required-review
linkage (accept blocked until the independent review lands) · tier→review requirement ·
micro logging (compact event, drift-clean, protected paths refused) · manifest
staleness (warning, not failure) · incompatible core version (refused) · isolation
shape (withhold requires a lift event) · automation actor authority: none (cannot
set lifecycle state) · rejected-push rescue (work preserved on a `rescue/` branch) ·
revision/supersession authorization · at-most-once (a completed handoff is not
re-dispatched).

Enforcements added in Increment 2 to make these guarantees real (each small,
policy-mandated, not speculative): a `--micro` path (§12), core-version major
compatibility check (§ pinning), a post-dispatch manifest-staleness warning
(§4/§10), and actor `authority: none` (§2).

Deferred fixture items handled as one-offs (per the simplicity rule), not blocking:
a dedicated scheduled-automation *intake* runner (the automation actor's authority
constraint is enforced and tested; a CI ingestion harness is Increment 5/QA scope)
and a distinct isolation-*lift* event recorder (the withhold/lift_when shape is
enforced; recording a lift is an amendment on the packet).

## Deferred (one-off unless recurring — ratified 2026-09-21)
standalone updater / hash-drift tooling (dependency contract only for now) · exhaustive per-scenario recovery handlers (invariants only) · dedicated multi-run engine (compose from isolated handoffs).

## Constraints
- The drafting session is branch-bound: it produces increments as reviewable branches; landing to this repo's source-of-truth branch is the Owner's review PR (core governance is protected).
- Predecessor kits should be frozen from further governance edits during extraction to avoid mid-migration drift.
