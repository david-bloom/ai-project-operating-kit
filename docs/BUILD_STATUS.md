# Build and adoption status

Candidate: **3.1.0**, release-ready remediation under APPROVAL-0001 / DECISION-0001.

| Milestone | State |
| --- | --- |
| Policy and enforcement contract | Implemented; reviewed |
| Read-only validator / legacy publisher retirement | Implemented; 53 tests and nine pilot scenarios passed |
| Negative conformance tests | 53 passed locally on Python 3.12/macOS |
| Independent review | Pass on exact implementation commit c20ab92; eight findings fixed |
| Disposable project pilot | Nine scenarios passed; no live action or consumer adoption |
| Native CI portability matrix | All six jobs passed on c20ab92; final closeout checks on PR #3 |
| Pinned release | Release-ready; actual publication/target recorded on the v3.1.0 release |
| Existing-project adoption | Not performed; requires each project's record |

See QA_AND_PILOT.md and WORK-OPERATING-KIT-REMEDIATION.md for evidence and remaining work.
Architecture approval, implementation merge, release validation and consumer adoption are
separate facts. No stage is implied by another. Previous 27-test claims belong to the old
publisher and do not certify this release.

Publication receipt: [v3.1.0](https://github.com/david-bloom/ai-project-operating-kit/releases/tag/v3.1.0).
Until that release exists, this document claims readiness only. Pin its full target commit,
not a moving branch. Implementation review and CI: `c20ab92fa9830aeab3ba43cf79772c912cb047ca`.
