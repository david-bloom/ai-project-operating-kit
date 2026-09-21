# Scripts — the generalized workflow engine (Increment 1b)

These are the data-driven successors to the Design Studio `scripts/` (`studio.sh`,
`handoff-check`, `publish`). They enforce `docs/CORE_OPERATING_POLICY.md` and read
every project-specific parameter from a **project manifest** + the `config/`
registries — nothing about actors, roles, branches, layout, protection or limits
is hard-coded.

**Status:** DRAFT, unproven until the Increment 2 conformance fixtures pass
(`docs/BUILD_STATUS.md`). The happy path and the key gates have been smoke-tested
in a throwaway git fixture (create → dispatch → land → accept, §4 review linkage,
§8 approval gates, freeze/hashes, state generation); the fixtures formalize this.

## Files

| File | Role |
|---|---|
| `lib/core.sh` | Shared helpers: the immutable core floor (statuses/lanes/tiers/events/gates), portable wrappers, minimal YAML readers, manifest resolution, header parsing, hashing, source-of-truth helpers. |
| `handoff-check` | Validate a packet against the policy; `draft → ready` stamps `source_sha`. |
| `publish` | The **only** writer to the source-of-truth branch: classify → validate → land (direct / auto-merge branch / human-review PR) → regenerate records → push → receipt. |

## Running

Every command resolves a manifest first (`--manifest <path>`, or `$MANIFEST`, or
`./PROJECT_MANIFEST.yaml`). `publish` must run on a checkout of the manifest's
`source_of_truth.branch` with push rights (the steward's environment).

```
scripts/handoff-check projects/<slug>/handoff/<NNN>-<role>.md
scripts/publish <slug>/<NNN> --actor <actor>                 # create on the sot branch
scripts/publish <slug>/<NNN> --actor <actor> --dispatch --model <id>
scripts/publish <slug>/<NNN> --actor <actor>                 # land the declared outputs
scripts/publish <slug>/<NNN> --actor <actor> --set-status accepted|returned
scripts/publish --regen | --drift
```

## Format contracts the readers expect

The YAML readers in `lib/core.sh` are minimal and dependency-free (no `yq`), so
author manifests in this style:

- **Scalars** at column 0 (`project:`) or one 2-space level under a block key
  (`core:` → `  version:`, `source_of_truth:` → `  branch:`).
- **Top-level lists** (`protected_paths:`, `hard_gates:`) as block items
  (`  - '<regex>'`) or an inline `[a, b]`. `[]` = empty.
- **`required_approvals`** values are inline lists of gate ids:
  `before_acceptance: [design-signoff]`.
- **`actors`** as inline flow maps, one surface per row:
  `- { actor: claude-code, surface: local, delivery: publisher }`.
- **`profiles`** as 2-space keys: `  design: { version: 1.0 }`.

## Approval records (§8)

Approval gates named in `required_approvals` are satisfied by a record in
`docs/activity_log/APPROVALS_LOG.md`, one block per approval:

```
## APPROVAL <handoff-id> <gate-id> — <approver> — <YYYY-MM-DD>
<one line of context; the Owner records this>
```

`publish` refuses the gated transition (dispatch / external-action landing /
acceptance) until a matching record exists on the source-of-truth branch.

## What is generalized vs. the core floor

Resolved from data: policy/core version, actors + surfaces + delivery, roles
(core registry + profile registries), source-of-truth repo/branch, project
layout (`paths.projects_root`), protected paths (floor **+** manifest additions,
monotonic §6), approval gates, size/staleness limits.

Fixed by the policy (the immutable floor, not project-configurable): the status /
lane / tier / event / gate vocabularies, the lifecycle transitions, the
protected-path floor (the operating system's own governance always needs review),
and the "publisher is the only writer" invariant.
