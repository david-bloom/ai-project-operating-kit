# Build and adoption status

Candidate: **3.1.0**, remediation under APPROVAL-0001 / DECISION-0001.

| Milestone | State |
| --- | --- |
| Policy and enforcement contract | Implemented in remediation branch |
| Read-only validator / legacy publisher retirement | Implemented; validation in progress |
| Negative conformance tests | 53 passed locally on Python 3.12/macOS |
| Independent review | In progress in a fresh context |
| Disposable project pilot | Nine scenarios passed; no live action or consumer adoption |
| Native CI portability matrix | First revision six jobs passed; final revision pending |
| Pinned release | Pending merge and exact-revision verification |
| Existing-project adoption | Not performed; requires each project's record |

See QA_AND_PILOT.md and WORK-OPERATING-KIT-REMEDIATION.md for evidence and remaining work.
Architecture approval, implementation merge, release validation and consumer adoption are
separate facts. No stage is implied by another. Previous 27-test claims belong to the old
publisher and do not certify this release.
