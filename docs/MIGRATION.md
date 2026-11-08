# Migration and rollback — 3.1.0

## Compatibility

This is an explicit migration from the unadopted 3.0 draft, not an in-place patch.
The privileged publisher, partial YAML parser and editable charter copies are removed
from executable entry points. Old command shapes fail with guidance. History remains at
`90250146632715ca169cfe59bb3f7f8bf0297e45` for inspection, not production execution.

Map Micro/Standard/Hard-Gate to micro/governed/protected; this changes vocabulary, not
permission. Preserve project-specific protections and prior decisions. New records use
strict JSON and exact digests. Old Markdown approval headings do not automatically become
valid structured grants. Review and record their scope, environment, interval and authority.

## Procedure

1. Inventory active tasks, branches, installed rules, approvals and external adapters.
2. Make a compatibility map; conflicts retain the installed rule until explicitly resolved.
3. Pin the released core and profiles. Convert one representative packet and manifest.
4. Configure native branch/environment controls and trusted evidence ingestion. Run the
   documented conformance tests and a disposable project pilot without production tokens.
5. Independently review the exact candidate and record adoption in the consuming project.
6. Transition one bounded task; preserve legacy records and name their replacement pointers.

Required adoption record: project/owner, previous and new policy commit, resolved conflicts,
allowed surfaces/roles, configured host protections, evidence-ingestion method, pilot/review
links, adoption approval, effective date and rollback owner/target. Cramapple has no new
adoption record from this remediation and therefore remains on its installed workflow.

## Rollback and interrupted work

Do not delete candidate work or reset a shared checkout. Disable the new integration, pin
back to the previously adopted safe version, retain new records as historical, and assign
an owner to reconcile any in-flight handoffs. Never roll back to the unsafe draft publisher
as an automatic recovery step. Query the remote PR/commit first before retrying delivery;
verify exact path hashes after merge. Locally preserved work is not a remote backup.

## What this release does not certify

Authenticated approval ingestion, private-context isolation, actual protected-branch settings,
external-action side effects and production adoption require project-host verification.
The disposable local pilot validates the engine and remote-receipt behavior, not those systems.
