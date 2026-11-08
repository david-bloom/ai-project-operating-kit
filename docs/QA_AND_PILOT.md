# QA and disposable pilot

Scope: core 3.1.0 remediation; no production actions or existing-project adoption.

## Finding-to-evidence matrix

| Audit finding | Implementation / verification |
| --- | --- |
| 1. Competing authority/adoption | README, INDEX, core and migration guide; predecessor pointers |
| 2. Role/surface authority | transition matrix; all-transition wrong-actor tests and surface test |
| 3. Approval scope/timing | owner/envelope/action/environment/interval checks; revocation and external-action tests |
| 4. Review quality/linkage | context, verdict, exact artifacts and unresolved findings tests |
| 5. Frozen contract | canonical full packet/manifest envelope; tampering and manifest-change tests |
| 6. Alternate-path protection | shared classifier, accepted inventory and complete Git diff checks |
| 7. Privileged publisher | wrappers now read-only; old mutation flags rejected; native PR CI |
| 8. Availability/completion | remote receipt explicitly does not infer integration/acceptance/release |
| 9. Schema/parser mismatch | strict JSON, duplicate/unknown-field rejection, example validation |
| 10. Provenance/sync | exact byte checks, mandatory provenance, real remote check and exact path tests |
| 11. Recovery/portability | no destructive mutations; interrupted verification pilot; Python CI matrix |
| 12. Overstated coverage | explicit evidence scope and limits; independent review below |

## Independent review round 1

Fresh reviewer examined engine SHA-256
`62602ba4939106c481d3ebf0f73ed06884bcd9bd8ac039764bc9aa8f7a4c47fd`
and reproduced five defects despite the initial 40 passing tests:
accepted-output micro revision, overlapping review outputs, falsey JSON CLI validation,
return without artifact verification, boolean schema / control-character validation.
All five were corrected and regression tests added. The exact-commit re-review of
`7ee17b9f6fd58d7cfe0cd72b86ad0c05bdf9b702` found three further defects: Git revision
option injection, committed symlink acceptance on the micro candidate route, and hidden
worktree/commit byte mismatches. These were corrected with shared safe commit resolution,
regular-file mode and exact-byte validation, plus regression tests.

Final independent verdict: **pass** for exact commit
`c20ab92fa9830aeab3ba43cf79772c912cb047ca` within the advisory-validator scope.
The reviewer reran all 53 tests and nine pilot scenarios and separately probed option
injection (sentinel unchanged), committed symlinks and hidden worktree edits. All eight
findings are addressed; no blocking findings remain. The subsequent closeout commit only
records this evidence and release readiness; executable and policy bytes are unchanged.

Review limits: this does not certify authenticated evidence ingestion, deployed host
protections, concurrent filesystem mutation resistance or consumer/production adoption.

## Disposable consumer pilot

`tests/pilot.py` creates temporary consumer and bare-origin repositories, exercises:
dispatch/land; failing review refusal; passing review acceptance; unapproved external-action
refusal; approved check without action execution; remote feature-branch receipt; failed
remote verification and safe retry; micro versus destructive classification.

Synthetic approvals and review assertions test policy logic only. They are not human
authorizations or evidence of real context isolation. No production credentials are used.
The pilot does not certify host authentication, protected environments or consumer adoption.

## Execution record

The expanded suite has 53 passing tests and nine passing pilot scenarios locally on
macOS / Python 3.12. The exact implementation commit above passed all six native CI combinations
(Linux/macOS × Python 3.11/3.12/3.13), [run 42513993792](https://github.com/david-bloom/ai-project-operating-kit/actions/runs/42513993792).
The earlier 50-test revision also passed all six combinations in run 42513799322.
Final PR checks and the release target are externally recorded on PR #3 and the v3.1.0
release, rather than asserting a future merge or release in this pre-merge artifact.

This sandbox blocks DNS for Python subprocesses accessing GitHub; the real GitHub branch
was verified through direct Git and the connector. Local bare-remote tests exercise the
validator receipt itself. No cached remote was reported as a successful live verification.
