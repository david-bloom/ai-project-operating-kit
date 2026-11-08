# Repository operating notes

Read `docs/INDEX.md`, then the named task and relevant policy sections. Classify the
work before expanding reading: micro (reversible/local), governed (implementation),
protected (production/money/privacy/deletion/publication/governance).

Use targeted searches and bounded output. Do not scan generated outputs, archives,
logs, dependencies or other projects without a concrete task reason. Read log indexes
through `<!-- INDEX_END -->`, then search by ID. Name missing indexed sources.

One task/slice per `codex/`, `claude/` or other actor-prefixed branch. Record branch/PR
in its task; resume that branch. All promotion to main uses PRs and native checks.
Do not bypass protection or execute the removed privileged publisher.

For governed/protected implementation, obtain fresh-context independent QA against
an exact commit; address findings and re-review affected evidence. QA is advisory;
required owner decisions remain separate. Use subagents only for real independence
or non-overlapping work, not ceremony.

Before closing durable work: update the task and activity entry with summary, pending
decisions, risks, next owner/action; push and verify exact remote content. Never delete
branches/worktrees with dirty, unique or unpushed work.
