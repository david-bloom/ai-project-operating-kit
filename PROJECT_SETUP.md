# Install a pinned operating kit

1. Choose a released immutable commit/tag and read its BUILD_STATUS and QA evidence.
2. Keep that checkout/package immutable; do not copy and edit core governance in the consumer.
3. Copy the JSON examples into the project's own configuration and fill owner, actor surfaces,
   source repository, allowed output roots, protected paths, risk gates and profile pins.
4. Pin exact policy bytes and version. Validate with Python 3.11+ (no external libraries).
5. Protect the authoritative branch: PR-only promotion, required CI, required governance
   owner review, no agent bypass. Select the exact branch/rules in the host; this kit does
   not change account settings or claim they already exist.
6. Trusted CI must load policy/validator/evidence from an owner-approved base snapshot,
   use authenticated host identity, classify the complete candidate diff and enforce
   compare-and-set lifecycle updates. Never run candidate code with privileged tokens.
7. For external actions, provide a project adapter using protected environments and a fresh
   approval/revocation check immediately before action. Record action ID/outcome. This release
   supplies policy checks, not deployment/payment runners or authenticated approval ingestion.
8. Complete a disposable pilot and fresh-context review. Record adoption commit/version,
   approval, trust setup, pilot evidence and rollback target before calling it adopted.

Until steps 5–8 are verified, local passing checks are advisory only. Existing Cramapple
continues under its installed workflow; installation here does not migrate any consumer.
