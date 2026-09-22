#!/usr/bin/env bash
# Conformance fixtures for the generalized workflow engine (Increment 2).
# docs/CORE_OPERATING_POLICY.md is enforced by scripts/handoff-check + scripts/publish;
# these fixtures prove that enforcement. "Core does not migrate until these pass"
# (docs/BUILD_STATUS.md).
#
# Each case runs in a throwaway git repo with its own bare origin, so cases are
# isolated. No dependencies beyond git + bash + awk. Run: tests/run.sh
#
# Exit 0 = all pass. Exit 1 = one or more failed (offending output is printed).

REPO=$(cd "$(dirname "$0")/.." && pwd)
TMPROOT=$(mktemp -d "${TMPDIR:-/tmp}/opkit-conf.XXXXXX")
trap 'rm -rf "$TMPROOT"' EXIT
PASS=0; FAIL=0; CASE=""
R=$'\033[31m'; G=$'\033[32m'; C=$'\033[36m'; N=$'\033[0m'

_pass() { PASS=$((PASS+1)); printf '  %sok%s   %s\n' "$G" "$N" "$1"; }
_fail() { FAIL=$((FAIL+1)); printf '  %sFAIL%s %s\n' "$R" "$N" "$1"; [ -n "$2" ] && printf '       %s\n' "$2"
          printf '%s\n' "$OUT" | sed 's/^/       | /' | head -n 20; }
case_() { CASE=$1; printf '%s== %s ==%s\n' "$C" "$1" "$N"; }

run() { OUT=$("$@" 2>&1); RC=$?; return 0; }
expect_ok()       { local l=$1; shift; run "$@"; [ $RC -eq 0 ] && _pass "$l" || _fail "$l" "expected success, got rc=$RC"; }
expect_fail()     { local l=$1; shift; run "$@"; [ $RC -ne 0 ] && _pass "$l" || _fail "$l" "expected failure, got rc=0"; }
expect_out()      { local l=$1 n=$2; shift 2; run "$@"; { [ $RC -eq 0 ] && printf '%s' "$OUT" | grep -q -- "$n"; } && _pass "$l" || _fail "$l" "expected success containing: $n"; }
expect_fail_out() { local l=$1 n=$2; shift 2; run "$@"; { [ $RC -ne 0 ] && printf '%s' "$OUT" | grep -q -- "$n"; } && _pass "$l" || _fail "$l" "expected failure containing: $n"; }
step()            { local l=$1; shift; run "$@"; [ $RC -eq 0 ] || _fail "$l (SETUP)" "setup step failed rc=$RC"; }

commit_push() { git add -A >/dev/null 2>&1; git commit -q -m "${1:-fixture}" >/dev/null 2>&1; git push -q origin trunk >/dev/null 2>&1; }

# new_sandbox -> fresh work repo (cd'd), bare origin, scripts+config+manifest+seed input.
new_sandbox() {
  local d="$TMPROOT/sbx.$RANDOM"; local bare="$d.git"
  mkdir -p "$d"; git init -q -b trunk "$d"; git init -q --bare "$bare"
  git -C "$bare" symbolic-ref HEAD refs/heads/trunk   # so clones default to trunk, not master
  cd "$d" || exit 2
  git config user.email t@t; git config user.name t
  mkdir -p scripts/lib config projects/demo/handoff docs/activity_log docs/architecture
  cp "$REPO/scripts/lib/core.sh" scripts/lib/; cp "$REPO/scripts/handoff-check" scripts/; cp "$REPO/scripts/publish" scripts/
  chmod +x scripts/handoff-check scripts/publish
  cp "$REPO/config/roles.yaml" config/
  : > docs/activity_log/ACTIVITY_LOG.md; : > docs/activity_log/APPROVALS_LOG.md; : > docs/activity_log/DECISIONS_LOG.md
  cp "$REPO/docs/CORE_OPERATING_POLICY.md" docs/ 2>/dev/null || echo "# core" > docs/CORE_OPERATING_POLICY.md
  write_manifest
  echo "the brief" > projects/demo/brief.md
  git add -A >/dev/null 2>&1; git commit -q -m init >/dev/null 2>&1; git remote add origin "$bare"; git push -q -u origin trunk >/dev/null 2>&1
}

# Default manifest; a case may call write_manifest with overrides then commit_push.
write_manifest() {
  cat > PROJECT_MANIFEST.yaml <<YAML
schema_version: 0.3
project: demo
core:
  version: ${MF_VERSION:-3.0}
source_of_truth:
  repo: local/demo
  branch: trunk
owner: david
orchestrator: claude-code
steward: claude-code
actors:
  - { actor: claude-code, surface: local, delivery: publisher }
  - { actor: codex, surface: cloud, delivery: branch }
  - { actor: automation, surface: ci, delivery: branch, authority: none }
defaults:
  tier: governed
  isolation: open
required_approvals:
  before_dispatch: [${MF_GATE_DISPATCH:-}]
  before_external_action: [${MF_GATE_EXT:-}]
  before_acceptance: [${MF_GATE_ACCEPT:-}]
  before_done: []
protected_paths:${MF_PROTECTED:- []}
profiles: {}
YAML
}

# mkpkt <path> <id> <role> <lane> <tier> <reqrev> <reviewof> <output> [extra header lines...]
mkpkt() {
  local path=$1 id=$2 role=$3 lane=$4 tier=$5 reqrev=$6 reviewof=$7 out=$8; shift 8
  { echo "---"; echo "handoff: $id"; echo "role: $role"; echo "actor: claude-code"; echo "surface: local"
    echo "lane: $lane"; echo "tier: $tier"; echo "status: draft"; echo "isolation: open"
    echo "inputs:"; echo "  - projects/demo/brief.md"; echo "outputs:"; echo "  - $out"
    echo "required_reviews: $reqrev"; echo "review_of: $reviewof"; echo "supersedes: none"; echo "revises: none"
    for x in "$@"; do echo "$x"; done
    echo "---"; echo; echo "# Handoff $id — $role"; echo; echo "## Task"; echo "Produce $out from projects/demo/brief.md."
    echo; echo "## Amendments"; } > "$path"
}

# lifecycle helpers (setup, not assertions)
ready()    { step "handoff-check $1" scripts/handoff-check "$2" --no-fetch; }
create()   { step "create $1" scripts/publish "$1" --actor claude-code --no-fetch; }
dispatch() { step "dispatch $1" scripts/publish "$1" --actor claude-code --dispatch ${2:+--model "$2"} --no-fetch; }
landfile() { echo "content of $2" > "$2"; step "land $1" scripts/publish "$1" --actor claude-code --no-fetch; }

###############################################################################
case_ "valid lifecycle (create -> dispatch -> land -> review -> accept)"
MF_VERSION= MF_GATE_DISPATCH= MF_GATE_EXT= MF_GATE_ACCEPT= MF_PROTECTED= new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007; dispatch demo/007; landfile demo/007 projects/demo/result.md
# independent review handoff
mkpkt projects/demo/handoff/008-reviewer.md demo/008 reviewer judgment governed none demo/007 projects/demo/review.md
ready 008 projects/demo/handoff/008-reviewer.md; create demo/008; dispatch demo/008 gpt-x; landfile demo/008 projects/demo/review.md
expect_out "accept succeeds once the independent review has landed" "landed → accepted" \
  scripts/publish demo/007 --actor claude-code --set-status accepted --no-fetch

###############################################################################
case_ "review linkage blocks acceptance until the review lands (§4)"
new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007; dispatch demo/007; landfile demo/007 projects/demo/result.md
expect_fail_out "accept blocked with no landed review" "required independent review" \
  scripts/publish demo/007 --actor claude-code --set-status accepted --no-fetch

###############################################################################
case_ "invalid transitions (§4 lifecycle)"
new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
step "create draft" scripts/publish demo/007 --actor claude-code --no-fetch
expect_fail_out "dispatch from draft (not ready) refused" "requires status ready" \
  scripts/publish demo/007 --actor claude-code --dispatch --no-fetch
ready 007 projects/demo/handoff/007-specialist.md; git add -A >/dev/null; git commit -q -m ready >/dev/null; git push -q origin trunk >/dev/null 2>&1
dispatch demo/007
expect_fail_out "accept before land refused" "requires status landed" \
  scripts/publish demo/007 --actor claude-code --set-status accepted --no-fetch

###############################################################################
case_ "branch delivery (multiple outputs -> auto-merge branch, §5)"
new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/a.md \
  "" # placeholder; add a second output below
# rewrite outputs to two files
sed -i 's#  - projects/demo/a.md#  - projects/demo/a.md\n  - projects/demo/b.md#' projects/demo/handoff/007-specialist.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007; dispatch demo/007
echo A > projects/demo/a.md; echo B > projects/demo/b.md
expect_out "two outputs land via a merged --no-ff branch" "merged --no-ff and deleted" \
  scripts/publish demo/007 --actor claude-code --no-fetch

###############################################################################
case_ "delivery provenance verified against the raw return (§5 airlock/branch)"
new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007; dispatch demo/007
printf 'produced elsewhere\n' > projects/demo/result.md
printf 'produced elsewhere\n' > projects/demo/result.md.airlock.txt
expect_out "content-modified=none passes when output matches its raw return" "content-modified=none" \
  scripts/publish demo/007 --actor claude-code --generated-by codex --source "branch codex/demo-007 @ abc" --content-modified none --no-fetch
# mismatch case (fresh)
new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007; dispatch demo/007
printf 'tampered output\n' > projects/demo/result.md
printf 'the real raw return\n' > projects/demo/result.md.airlock.txt
expect_fail_out "content-modified=none fails when output differs from raw return" "differs from its raw return" \
  scripts/publish demo/007 --actor claude-code --generated-by codex --source "paste" --content-modified none --no-fetch

###############################################################################
case_ "protected-path floor forces human-review branch (§6)"
new_sandbox
echo "# touched" >> config/roles.yaml
expect_out "governance touching a floor-protected path routes to review" "HUMAN REVIEW REQUIRED" \
  scripts/publish --event governance --actor claude-code --message "edit roles" --no-fetch

###############################################################################
case_ "project-defined protected path forces review (§6 monotonic)"
MF_PROTECTED="
  - '^projects/demo/locked/.*\$'" new_sandbox
mkdir -p projects/demo/locked; echo x > projects/demo/locked/thing.md
expect_out "governance touching a manifest-added protected path routes to review" "HUMAN REVIEW REQUIRED" \
  scripts/publish --event governance --actor claude-code --message "edit locked" --no-fetch

###############################################################################
case_ "approval gate: before_dispatch (§8)"
MF_GATE_DISPATCH=precheck new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007
expect_fail_out "dispatch blocked without approval record" "before_dispatch gate 'precheck'" \
  scripts/publish demo/007 --actor claude-code --dispatch --no-fetch
printf '## APPROVAL demo/007 precheck — david — 2026-09-21\n' >> docs/activity_log/APPROVALS_LOG.md; commit_push approve
expect_out "dispatch succeeds after approval recorded" "ready → dispatched" \
  scripts/publish demo/007 --actor claude-code --dispatch --no-fetch

###############################################################################
case_ "approval gate: before_acceptance (§8)"
MF_GATE_ACCEPT=signoff new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007; dispatch demo/007; landfile demo/007 projects/demo/result.md
mkpkt projects/demo/handoff/008-reviewer.md demo/008 reviewer judgment governed none demo/007 projects/demo/review.md
ready 008 projects/demo/handoff/008-reviewer.md; create demo/008; dispatch demo/008 gpt-x; landfile demo/008 projects/demo/review.md
expect_fail_out "accept blocked without signoff approval" "before_acceptance gate 'signoff'" \
  scripts/publish demo/007 --actor claude-code --set-status accepted --no-fetch
printf '## APPROVAL demo/007 signoff — david — 2026-09-21\n' >> docs/activity_log/APPROVALS_LOG.md; commit_push approve
expect_out "accept succeeds after signoff recorded" "landed → accepted" \
  scripts/publish demo/007 --actor claude-code --set-status accepted --no-fetch

###############################################################################
case_ "approval gate: before_external_action at protected landing (§8)"
MF_GATE_EXT=prod-write new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine protected independent none projects/demo/result.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007; dispatch demo/007
echo r > projects/demo/result.md
expect_fail_out "protected landing blocked without external-action approval" "before_external_action gate 'prod-write'" \
  scripts/publish demo/007 --actor claude-code --no-fetch

###############################################################################
case_ "tier governed requires an independent review (§4)"
new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed none none projects/demo/result.md
expect_fail_out "governed producing handoff without required_reviews fails check" "requires required_reviews: independent" \
  scripts/handoff-check projects/demo/handoff/007-specialist.md --no-fetch

###############################################################################
case_ "at-most-once: a completed handoff is not re-dispatched (§10)"
new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007; dispatch demo/007; landfile demo/007 projects/demo/result.md
mkpkt projects/demo/handoff/008-reviewer.md demo/008 reviewer judgment governed none demo/007 projects/demo/review.md
ready 008 projects/demo/handoff/008-reviewer.md; create demo/008; dispatch demo/008 gpt-x; landfile demo/008 projects/demo/review.md
step "accept 007" scripts/publish demo/007 --actor claude-code --set-status accepted --no-fetch
expect_fail_out "re-dispatch of an accepted handoff refused" "requires status ready" \
  scripts/publish demo/007 --actor claude-code --dispatch --no-fetch

###############################################################################
case_ "revision & supersession (§4)"
new_sandbox
# land+accept 007
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007; dispatch demo/007; landfile demo/007 projects/demo/result.md
mkpkt projects/demo/handoff/008-reviewer.md demo/008 reviewer judgment governed none demo/007 projects/demo/review.md
ready 008 projects/demo/handoff/008-reviewer.md; create demo/008; dispatch demo/008 gpt-x; landfile demo/008 projects/demo/review.md
step "accept 007" scripts/publish demo/007 --actor claude-code --set-status accepted --no-fetch
# a revising packet may overwrite an accepted output
mkpkt projects/demo/handoff/009-specialist.md demo/009 specialist routine governed independent none projects/demo/result.md "revises: demo/007"
# fix the auto-added 'revises: none' line by removing it (keep the explicit one)
sed -i '0,/^revises: none$/{/^revises: none$/d}' projects/demo/handoff/009-specialist.md
expect_out "revises: <accepted> authorizes overwriting its output" "revises demo/007" \
  scripts/handoff-check projects/demo/handoff/009-specialist.md --no-fetch --dry-run

###############################################################################
case_ "isolation shape (§7)"
new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
sed -i 's#^isolation: open#isolation: { withhold: [prior-review], lift_when: direction-locked }#' projects/demo/handoff/007-specialist.md
expect_out "withhold with a lift_when passes" "scoped withhold with a lift event" \
  scripts/handoff-check projects/demo/handoff/007-specialist.md --no-fetch --dry-run
new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
sed -i 's#^isolation: open#isolation: { withhold: [prior-review] }#' projects/demo/handoff/007-specialist.md
expect_fail_out "withhold without a lift_when fails" "must name a lift_when" \
  scripts/handoff-check projects/demo/handoff/007-specialist.md --no-fetch --dry-run

###############################################################################
case_ "automation actor has authority: none (§2)"
new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007
expect_fail_out "automation cannot dispatch (evidence only)" "authority: none" \
  scripts/publish demo/007 --actor automation --dispatch --no-fetch

###############################################################################
case_ "micro path: compact event, no packet; protected paths refused (§12)"
new_sandbox
echo "tweak" >> projects/demo/brief.md
expect_out "micro change records an event and lands" "micro recorded @" \
  scripts/publish --micro --actor claude-code --message "fix a typo" --no-fetch
expect_out "micro event is drift-clean" "no drift" scripts/publish --drift --no-fetch
echo "# gov" >> config/roles.yaml
expect_fail_out "micro refuses a protected path" "cannot touch protected path" \
  scripts/publish --micro --actor claude-code --message "sneak governance" --no-fetch

###############################################################################
case_ "incompatible core version refused (§ pinning)"
MF_VERSION=9.0 new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
expect_fail_out "manifest pinning a different major core is refused" "incompatible core version" \
  scripts/handoff-check projects/demo/handoff/007-specialist.md --no-fetch

###############################################################################
case_ "manifest staleness is a warning, not a failure (§10)"
new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007; dispatch demo/007
# change the manifest after dispatch (add an inert comment), commit it
printf '\n# post-dispatch edit\n' >> PROJECT_MANIFEST.yaml; commit_push "manifest edit"
expect_out "handoff-check warns but passes on a stale manifest" "manifest changed since dispatch" \
  scripts/handoff-check projects/demo/handoff/007-specialist.md --no-fetch

###############################################################################
case_ "rejected push preserves work on a rescue branch (§10)"
new_sandbox
mkpkt projects/demo/handoff/007-specialist.md demo/007 specialist routine governed independent none projects/demo/result.md
ready 007 projects/demo/handoff/007-specialist.md; create demo/007; dispatch demo/007
# a second clone advances origin/trunk so the steward's next push is rejected
SECOND="$TMPROOT/second.$RANDOM"; git clone -q "$(git remote get-url origin)" "$SECOND"
( cd "$SECOND"; git config user.email t@t; git config user.name t; echo x > advanced.txt; git add -A; git commit -q -m advance; git push -q origin trunk )
echo r > projects/demo/result.md
expect_fail_out "push rejection is reported and work preserved" "preserved on" \
  scripts/publish demo/007 --actor claude-code --no-fetch
expect_ok "a rescue/ branch exists after rejection" bash -c 'git branch --list "rescue/*" | grep -q rescue'

###############################################################################
echo
printf '%s————————————————————————————————%s\n' "$C" "$N"
printf 'conformance: %s%d passed%s, %s%d failed%s  (%d cases)\n' "$G" "$PASS" "$N" "$R" "$FAIL" "$N" "$((PASS+FAIL))"
[ $FAIL -eq 0 ] || exit 1
