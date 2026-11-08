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
All five were corrected and regression tests added. Exact-commit re-review is pending.

## Disposable consumer pilot

`tests/pilot.py` creates temporary consumer and bare-origin repositories, exercises:
dispatch/land; failing review refusal; passing review acceptance; unapproved external-action
refusal; approved check without action execution; remote feature-branch receipt; failed
remote verification and safe retry; micro versus destructive classification.

Synthetic approvals and review assertions test policy logic only. They are not human
authorizations or evidence of real context isolation. No production credentials are used.
The pilot does not certify host authentication, protected environments or consumer adoption.

## Execution record

Initial 40 unit tests passed on macOS / Python 3.12. Expanded suite and pilot are being
verified. Native CI will exercise Linux/macOS on Python 3.11, 3.12 and 3.13.
Final exact-commit results and independent disposition will be recorded before release.
