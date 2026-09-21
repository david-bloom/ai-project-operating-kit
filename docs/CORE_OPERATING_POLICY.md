# Core Operating Policy

**Version:** 3.0-draft (Increment 1). Successor to the Design Studio `OPERATING_POLICY` 2.0, **generalized and data-driven.** This is the single operating rulebook for any project that adopts the kit via a project manifest. **Profiles extend it; projects parameterize it; neither restates or overrides it.**

**Status:** DRAFT on branch `claude/optimistic-bell-b8bxwn` for review/PR. Not adopted; the generalized scripts that enforce it are Increment 1b (see `docs/BUILD_STATUS.md`). Where this doc and any other file disagree, this file wins.

---

## 1. Source of truth and availability

The manifest names the **source-of-truth** repo + branch (`source_of_truth.repo`, `.branch`; default branch `main`). Chat is never source of truth. Three states:
- **local** — exists only in a tool's filesystem or chat. Not real for operating purposes.
- **durable** — pushed to a remote feature branch. Safe from loss; not visible to other participants.
- **available** — on the source-of-truth branch at a recorded commit, every declared output present, verified by the publisher.

A handoff is complete only when **available**. A pushed branch, PR, chat paste, or serve URL is never completion. Completion is distinct from acceptance and from Done (§8).

## 2. Actors, roles, lanes, tiers

- **Actor** = a tool identity (from `config/actors`). An actor has one or more **surfaces** (a specific integration, e.g. local vs cloud). Each surface declares a **delivery capability**: `airlock | branch | publisher` (§5).
- **Role** = a responsibility (from `config/roles`): **Owner/Done-Decider, Orchestrator, Specialist/Worker, Reviewer, Steward.** Profiles may add domain roles; none may redefine these.
- **Lane** = one handoff's *production topology*: `routine` (one producing context) · `judgment` (two independent evaluative contexts) · `divergence` (independent option generation). Set per packet.
- **Tier** = a *work-item's* risk/approval depth: `micro | governed | protected`. Manifest sets `default_tier`; each handoff carries `tier`. A profile or risk classifier may **raise** tier; lowering a derived tier requires a recorded reason. Lane and tier are independent (a routine production handoff can carry an independent review handoff — §4).

## 3. Authority

- **Owner / Done-Decider** — reserves: every Done decision, destructive changes, scope/constraint changes, external publication, revealing deliberately withheld information, and anything the scripts cannot classify. Never routine landings.
- **Orchestrator** — owns flow: picks the next handoff, its lane/tier/isolation; writes packets; dispatches; sets `accepted`/`returned`. Never hand-edits generated files; never writes the source-of-truth branch except through the publisher.
- **Steward / publisher** — the **only** writer to the source-of-truth branch. Exactly one active steward per execution environment (`manifest.steward`). Runs the publisher; may normalize formatting/paths, never substantive content.
- **Specialist/Worker** — produces exactly the declared outputs; sets no lifecycle state; edits no logs/state/manifest/governance.
- **Reviewer** — advisory only; output goes to its own handoff; never overwrites the work under review.

Approvals are enforced at transitions via `required_approvals` (§8), not by role goodwill.

## 4. Handoff packets and lifecycle

Path and ID conventions come from the manifest/profile (not hard-coded). Every packet header:
```yaml
handoff:            # <project>/<NNN>
role:
actor: { name:, surface: }
lane:               # routine | judgment | divergence
tier:               # micro | governed | protected
status:             # see lifecycle
isolation:          # open | {withhold:[...], lift_when:<event>}   (§7)
inputs: []
outputs: []
required_reviews:   # none | independent
review_of:          # <handoff-id> | none   (set on review handoffs)
supersedes:         # <handoff-id> | none
revises:            # <handoff-id> | none
source_sha:         # stamped at ready
frozen_hash:        # stamped at dispatched
manifest_sha:       # source-of-truth commit holding the manifest at dispatch
manifest_hash:      # canonical hash of the resolved manifest + referenced profile configs
instructions_hash:  # hash of the generated participant instructions
```

**Lifecycle** (unchanged from Policy 2.0): `draft → ready → dispatched → landed → accepted | returned`, with `↘ blocked`, and `returned/blocked → superseding handoff (supersedes:)`. Who sets each: `ready` = the checker; `dispatched`/`accepted`/`returned` = Orchestrator; `landed` = publisher; `blocked` = Orchestrator or a script with a reason. A Specialist sets none.

**Status namespaces.** `status` (and the derived core state) is *operational movement of the artifact*. A profile's domain outcome is separate and namespaced:
```yaml
handoff_status: landed
profile_state: { qa: fail }        # or { ux_run: completed_with_limitations }, etc.
```
A successfully delivered *failing* QA report is `landed` with `profile_state.qa: fail`. Profile state never drives a core transition except through a declared gate/disposition mapping.

**Review linkage.** For `governed` and `protected` work, the producing handoff sets `required_reviews: independent`; the review is its own handoff with `review_of:` pointing back. The publisher **blocks `accepted`** until the required review has landed with a recorded disposition. Remediation re-reviews the affected evidence.

**Freeze.** From `dispatched`, the body above `## Amendments` is frozen at `frozen_hash`. Post-dispatch manifest/policy changes do not retroactively alter frozen work (§10).

**Re-delivery / revision.** Outputs must not already exist on the source-of-truth branch, except: a packet whose `supersedes:` names a `returned`/`blocked` handoff may re-declare its outputs; a packet whose `revises:` names a `landed`/`accepted` handoff may overwrite them (the Orchestrator's dispatch is the authorization).

## 5. Delivery capability and landing policy (separate concerns)

**Delivery capability** (per actor surface) = how output reaches the steward:
- `airlock` — no repo write: structured return; the steward lands it.
- `branch` — can push a feature branch but not the source-of-truth branch: the steward checks the declared outputs out of the branch and lands them.
- `publisher` — can run the trusted publisher and write the source-of-truth branch.

**Landing policy** = how the steward lands it, **derived mechanically from the diff**, never chosen by an agent: direct workflow commit · short-lived auto-merge branch · human-review branch for protected paths (§6). "Direct" is a publisher-selected form, not an agent permission. Only the steward writes the source-of-truth branch.

## 6. Protection precedence (monotonic)

```
effective protection = immutable core floor
                     + active profile requirements
                     + project additions (manifest.hard_gates / protected_paths)
                     + handoff-specific escalation
```
A lower layer may **add** protection; it may never **remove** a higher layer's. Reducing the core floor is itself a core governance change requiring the Owner. Gates use structured identifiers (not only free text); path patterns are validated before dispatch; the resolved protection set is shown in the generated participant instructions.

## 7. Isolation (per handoff)

The manifest sets `defaults.isolation`; **every dispatched packet resolves it**:
```yaml
isolation: open                                           # default
isolation: { withhold: [prior-review-output, real-identity], lift_when: <named-event> }
```
`lift_when` names an **observable event** the Orchestrator/publisher can check (e.g. `direction-locked`, `both-reviews-landed`). Preflight **blocks dispatch** if a profile requiring fresh context resolves to `open`; the lift is recorded when it fires. A genuinely exotic case is a **recorded exception** on the packet, never free-text bypass. This one primitive covers design clean-room (anti-convergence), cross-model QA decorrelation (anti-bias), and independent UX testing.

## 8. Tiers and approval gates

- **micro** — reversible, low-blast-radius: no packet, a compact **event** instead (§12).
- **governed** — normal packet + independent review (§4).
- **protected** — governed + explicit human approval, enforced at the relevant transition:
```yaml
required_approvals:
  before_dispatch: []
  before_external_action: []
  before_acceptance: []
  before_done: []
```
Defaults: protected work touching production / money / privacy / deletion / external publication → approval **before the action**; a protected deliverable → approval **before `accepted`**; **every Done** → an Owner/Done-Decider record. Landing may precede acceptance so a human can review an available artifact. The publisher refuses a gated transition without a matching approval record. Empty maps = no gates.

## 9. Records

Generated by the publisher, never hand-edited: current-state file, per-project handoff index, one activity log (one entry per landing/governance/recovery event), a decisions log (real decisions with the approval recorded inside). The publisher ends every run with a **delivery receipt**: repo; handoff; event; delivery form; source-of-truth SHA after push; each verified path; branch disposition; validation result; and `Available to other agents: yes | no`. Not `yes` → not complete.

## 10. Recovery invariants

- A failed publish never destroys unpublished work (rejected pushes are preserved for rescue).
- Partial delivery cannot reach `landed`.
- Rejected work stays in history and is superseded, never rewritten.
- Post-dispatch policy/manifest changes do not retroactively alter frozen work.
- An isolation breach blocks the handoff and requires a recorded recovery decision.
- Publication is **duplicate-safe / at-most-once by handoff ID** (a completed handoff is not re-run). *(Whether to add true replay-idempotency is a fixture decision in Increment 2.)*

Exhaustive per-scenario handlers are deliberately out of scope (handled as one-offs unless recurring).

## 11. Session start

A session reads, in order, and nothing else unless the packet names it: (1) the **project manifest**; (2) this core policy at the manifest's `core.version`; (3) the active **profiles** at their pinned versions; (4) generated current-state; (5) the packet named in the dispatch and its declared inputs. Role is told explicitly in the dispatch, never inferred.

## 12. Micro path

Micro work skips the packet and records a compact event (append-only), preserving a light audit trail without ceremony:
```yaml
event: micro-change
actor: { name:, surface: }
scope:
paths: []
evidence:
result:
```

---

*Profiles (Design / UX / QA) add domain roles, stages, schemas, evidence rules, triggers, validators/runners, artifact strategy, and output namespaces — never core authority, publication, lifecycle, or state semantics. See each profile's README. The generalized `handoff-check` and `publish` that enforce this policy are Increment 1b.*
