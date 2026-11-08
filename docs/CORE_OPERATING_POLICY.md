# Core Operating Policy

Version: **3.1.0**
Status: Remediation design approved by APPROVAL-0001 / DECISION-0001; release/adoption
status is recorded separately in BUILD_STATUS.md. Adoption is never inferred from merge.

## 1. Authority and trust

Core defines semantics once. Profiles add requirements and projects parameterize them;
neither can remove a core protection. Installed project policy governs until an explicit
migration is approved and recorded. User direction is recorded as a scoped decision;
merely reviewing or syncing a plan does not authorize its execution.

The owner decides product scope, protected actions, risk acceptance and protected Done.
The orchestrator coordinates and proposes lifecycle changes; the steward prepares and
verifies deliveries; workers produce assigned outputs; reviewers return findings in a
fresh context. Every actor is resolved by **name and surface**, not name alone.
Authority `none` is evidence-only. Roles do not grant credentials.

The runtime is a read-only policy checker. It accepts caller assertions but does not
authenticate them. Trusted CI must bind identities and authoritative records to the
host, execute a pinned validator from the trusted base, and reject candidate attempts
to replace that trust input. A project without such integration may use local checks
for diagnostics, never as unattended authorization. No kit command executes an external
action. A project action adapter must recheck current owner approval/revocation immediately
before the action, using protected environments or equivalent host permissions.

## 2. Tiers and protection

`micro`: reversible low-impact change, compact candidate record, no packet required.
`governed`: implementation or substantial deliverable, packet plus independent review.
`protected`: governed plus scoped owner approvals for dispatch, landing, acceptance,
external action and Done. Production, money, privacy, deletion, publication and governance
are protected. The file classifier adds protection for core/project/profile paths,
renames/deletions and previously accepted outputs. Semantic risks must be declared by
an accountable conductor; filename classification cannot prove that arbitrary code is safe.

The effective tier is the maximum of default, profile minimum, declared risks and diff
classification. No lowering override exists. Every route uses the same classifier.
The authoritative accepted-output inventory is a required candidate-check input.

Standing scope includes read-only inspection, drafting and accurate recording of decisions.
Execution needs an approved task. Approval scope is concrete and reviewable, not a request
for each routine step. Silence-is-consent is disabled. Approvals have explicit timezone-aware
not-before/expiry timestamps (expiry exclusive), status and revocation; expiry is not a
response deadline. This release supports owner approvals only; domain delegation requires
an explicit future schema, not inferred authority.

## 3. Lifecycle and independent review

A handoff moves `draft → ready → dispatched → landed → accepted → done`; landed work may
be returned and open work blocked. Returned/blocked work uses a new superseding packet.
Revisions name a landed/accepted/done predecessor and stay within its declared output scope.
The runtime returns a **proposed** next state and never edits a record. The host must verify
and persist the transition against the authoritative previous state with a compare-and-set
on the revision, so two concurrent proposals cannot both overwrite it.

A review is its own artifact and context, bound to envelope and exact output digests.
A fresh context may use the same model/tool; a different actor string alone proves nothing.
Passing disposition with no open blocking findings is required. A delivered failing report
is still delivered, but does not permit acceptance. Superseded findings remain in history;
remediation requires review of changed bytes. No implicit risk acceptance is supported.

Micro completion is delegated to the conductor. Governed Done follows accepted work and
review. Protected Done additionally requires current owner approval. Release and external
publication remain separate from task completion.

## 4. Frozen envelope, isolation and versioning

Strict JSON schema version 1 is the sole executable format. Unknown fields, duplicate keys,
non-finite numbers, malformed paths and unsupported versions fail. The manifest pins the
exact core version/digest and each profile version/digest. The envelope hashes every packet
field except status, append-only amendments and the envelope itself, plus the full manifest.
Inputs are exact content digests. Later policy changes require using the original pinned
snapshot or creating a newly authorized packet; they do not silently rewrite prior work.
Current owner revocation still blocks future actions.

Isolation resolves to `open` or `fresh`, with withheld inputs and a named observable lift
event. Fresh profiles cannot resolve to open. Actual context isolation and lift evidence are
host responsibilities; the validator checks the declaration, not a model's private memory.

## 5. Delivery, integration and evidence

Keep these facts separate: local, durably stored, accessible to a named recipient,
integrated, accepted, released and Done. A pinned feature-branch artifact can be reviewed
before merge. GitHub branch reachability does not prove every participant has permission;
a reader/access check must support that claim. Unmerged work is not automatically invisible.

One reviewable slice per actor-prefixed branch. Record branch/PR in the task and continue it.
All promotion to the authoritative branch uses PRs, required checks/reviews and native merge
queue/auto-merge. No agent bypasses protection. Emergency access is human-only and auditable.
The kit never commits, merges, pushes, resets or deletes working data. Native-host adapters
are deliberately outside the validator's privilege boundary.

Every output needs exact-byte provenance; normalization requires a new artifact and review.
Remote receipts identify the repository/ref, full commit and exact path hashes. A remote
failure cannot yield verified success from a cached ref. Receipts never infer acceptance,
release, QA or Done from a successful transfer.

## 6. Recovery, sessions and records

Validators have no destructive recovery operation. On failure, retain the workspace and
candidate branch; record the failure and exact next action. Before retrying publication,
query the host for the existing commit/PR/action receipt. Use idempotency keys in project
external-action adapters. Preserve local-only rescue as such until remote backup is verified.
Never delete a branch/worktree without checking dirty, unique and unpushed work.

Start tier-first: bootstrap/index, named task, then relevant current sources. Missing sources
are reported, not replaced by broad repository scans. Logs use indexes and exact-ID searches.
Do not trust superseded docs or stale live-system claims. Verify required tool/environment
access for the active task.

Before ending durable work, record summary, pending decisions, risks/blockers, next owner
and concrete next action. Record None explicitly where applicable. Push and verify the
remote artifact before claiming synchronization. Source records are hand-authored through
review; generated views must be reproducible derivatives, never competing authority.
