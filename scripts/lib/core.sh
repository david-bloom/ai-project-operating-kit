#!/usr/bin/env bash
# Shared helpers for scripts/handoff-check and scripts/publish.
# Bash 3.2+ (macOS default) + git + awk + sed. No other dependencies.
#
# This is the GENERALIZED, data-driven successor to the Design Studio
# scripts/lib/studio.sh. It reads project-specific parameters (actors, roles,
# source-of-truth branch, protected paths, approval gates, limits, output
# layout) from a PROJECT MANIFEST and the config registries, and enforces
# docs/CORE_OPERATING_POLICY.md. The enumerations below (statuses, lanes,
# tiers, events, gates) ARE the policy — they are the immutable core floor and
# are not project-configurable (§6). Everything else is resolved from data.
#
# Status: DRAFT (Increment 1b). Unproven until the Increment 2 conformance
# fixtures pass. See docs/BUILD_STATUS.md.

# ---------------------------------------------------------------- core floor
# Fixed by docs/CORE_OPERATING_POLICY.md. A project may ADD protection/gates
# (monotonic, §6); it may never remove or redefine these.
# CORE_VERSION is this engine's implemented policy version. A manifest whose
# core.version has a different MAJOR is incompatible (refused at resolve).
CORE_VERSION="3.0"
CORE_STATUSES="draft ready dispatched landed accepted returned blocked superseded"
CORE_LANES="routine judgment divergence"
CORE_TIERS="micro governed protected"
CORE_EVENTS="handoff-created status-changed output-landed governance recovery"
CORE_GATES="before_dispatch before_external_action before_acceptance before_done"

# Protected-path floor: the operating system's own governance always needs
# human review, in every project (§6). Project additions extend this.
CORE_PROTECTED_FLOOR='^(docs/CORE_OPERATING_POLICY\.md|docs/architecture/.*|config/.*|scripts/.*|templates/.*|CLAUDE\.md|prompts/.*|profiles/[^/]+/(README|policy)\.md|[^/]*/?PROJECT_MANIFEST\.ya?ml)$'

# Size + staleness floor. Manifest may raise/lower via `limits:` and `stale_hours:`.
DEFAULT_LIMIT_IMAGE=512000      # 500 KB
DEFAULT_LIMIT_FILE=2097152      # 2 MB
DEFAULT_LIMIT_COMMIT=10485760   # 10 MB
DEFAULT_STALE_SECONDS=172800    # 48 h

# ---------------------------------------------------------------- portability
sha256() { if command -v sha256sum >/dev/null 2>&1; then sha256sum | cut -c1-64; else shasum -a 256 | cut -c1-64; fi; }
fsize()  { stat -c %s "$1" 2>/dev/null || stat -f %z "$1"; }
epoch_to_date() { date -u -d @"$1" +%Y-%m-%d 2>/dev/null || date -u -r "$1" +%Y-%m-%d; }
lower()  { printf '%s' "$1" | tr '[:upper:]' '[:lower:]'; }
# read lines from a command into an array (bash 3.2 has no mapfile): read_into ARR cmd args...
read_into() { local _n=$1; shift; eval "$_n=()"; local _l; while IFS= read -r _l; do eval "$_n+=(\"\$_l\")"; done < <("$@"); }

RED=$'\033[31m'; GRN=$'\033[32m'; YEL=$'\033[33m'; NC=$'\033[0m'
FAILS=0; WARNS=0
ok()   { printf '%s  ok   %s%s\n' "$GRN" "$NC" "$*"; }
fail() { printf '%s  FAIL %s%s\n' "$RED" "$NC" "$*"; FAILS=$((FAILS+1)); }
warn() { printf '%s  warn %s%s\n' "$YEL" "$NC" "$*"; WARNS=$((WARNS+1)); }
die()  { printf '%sERROR:%s %s\n' "$RED" "$NC" "$*" >&2; exit 2; }
in_list() { local x=$1; shift; for i in "$@"; do [ "$i" = "$x" ] && return 0; done; return 1; }
repo_root() { git rev-parse --show-toplevel; }

# ---------------------------------------------------------------- YAML readers
# Minimal, dependency-free readers for the specific manifest/config shapes this
# kit authors (flat front matter, one or two nested levels, block or inline
# lists). Not a general YAML parser; author manifests in the documented style.

parse_inline_list() {  # "[a, b, c]" or "[]" -> one item per line
  local v=$1; v=${v#[}; v=${v%]}
  [ -z "${v//[[:space:]]/}" ] && return 0
  printf '%s' "$v" | tr ',' '\n' | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//; s/^["'\'']//; s/["'\'']$//' | grep -v '^$' || true
}

yget() {  # file key  (key may be "top" or "top.sub") -> scalar (inline # stripped)
  local f=$1 key=$2
  case "$key" in
    *.*) awk -v top="${key%%.*}" -v subk="${key#*.}" '
           $0 ~ "^"top":[ ]*(#.*)?$" { inb=1; next }
           inb && /^[^ ]/ { inb=0 }
           inb && index($0,"  "subk":")==1 { s=$0; sub("^  "subk":[ ]*","",s); sub(/[ ]+#.*$/,"",s); print s; exit }' "$f" ;;
    *)   awk -v k="$key" '
           index($0,k":")==1 { s=$0; sub("^"k":[ ]*","",s); sub(/[ ]+#.*$/,"",s); print s; exit }' "$f" ;;
  esac
}

ytoplist() {  # file key -> list items (inline [..] on the key line, or block "  - item")
  local f=$1 k=$2 inline
  inline=$(awk -v k="$k" 'index($0,k":")==1 { s=$0; sub("^"k":[ ]*","",s); sub(/[ ]+#.*$/,"",s); print s; exit }' "$f")
  case "$inline" in
    \[*\]) parse_inline_list "$inline"; return 0 ;;
  esac
  awk -v k="$k" '
    index($0,k":")==1 && $0 ~ ("^"k":[ ]*(#.*)?$") { inl=1; next }
    inl && $0 ~ /^  - / { s=$0; sub(/^  - /,"",s); sub(/[ ]+#.*$/,"",s); gsub(/^["'\'']|["'\'']$/,"",s); if(s!="") print s; next }
    inl && /^[^ ]/ { inl=0 }' "$f"
}

# ---------------------------------------------------------------- manifest resolve
# resolve_manifest [path] -> sets the globals the scripts operate on. Fails with
# a clear message if no manifest (the scripts are project-scoped by design).
MANIFEST=""
resolve_manifest() {
  MANIFEST=${1:-${MANIFEST:-PROJECT_MANIFEST.yaml}}
  [ -f "$MANIFEST" ] || die "no project manifest at '$MANIFEST' (set \$MANIFEST or pass one); these scripts run inside a project that adopts the core (docs/CORE_OPERATING_POLICY.md §11)"

  PROJECT=$(yget "$MANIFEST" project);                 [ -n "$PROJECT" ] || die "manifest: project is required"
  POLICY_VERSION=$(yget "$MANIFEST" core.version);      [ -n "$POLICY_VERSION" ] || POLICY_VERSION="unspecified"
  # version compatibility (§ core/profile pinning): same MAJOR as this engine
  if [ "$POLICY_VERSION" != unspecified ] && [ "${POLICY_VERSION%%.*}" != "${CORE_VERSION%%.*}" ]; then
    die "incompatible core version: manifest pins core $POLICY_VERSION but this engine implements $CORE_VERSION (different major)"
  fi
  SOT_BRANCH=$(yget "$MANIFEST" source_of_truth.branch);[ -n "$SOT_BRANCH" ] || SOT_BRANCH=main
  SOT_REPO=$(yget "$MANIFEST" source_of_truth.repo)
  OWNER=$(yget "$MANIFEST" owner)
  ORCH=$(yget "$MANIFEST" orchestrator)
  STEWARD=$(yget "$MANIFEST" steward)
  DEFAULT_TIER=$(yget "$MANIFEST" defaults.tier);       [ -n "$DEFAULT_TIER" ] || DEFAULT_TIER=governed
  DEFAULT_ISOLATION=$(yget "$MANIFEST" defaults.isolation); [ -n "$DEFAULT_ISOLATION" ] || DEFAULT_ISOLATION=open

  # layout: one knob (paths.projects_root, default "projects")
  PROJECTS_ROOT=$(yget "$MANIFEST" paths.projects_root); [ -n "$PROJECTS_ROOT" ] || PROJECTS_ROOT=projects

  # limits (manifest may override the floor)
  local li lf lc sh
  li=$(yget "$MANIFEST" limits.image);  LIMIT_IMAGE=${li:-$DEFAULT_LIMIT_IMAGE}
  lf=$(yget "$MANIFEST" limits.file);   LIMIT_FILE=${lf:-$DEFAULT_LIMIT_FILE}
  lc=$(yget "$MANIFEST" limits.commit); LIMIT_COMMIT=${lc:-$DEFAULT_LIMIT_COMMIT}
  sh=$(yget "$MANIFEST" stale_hours);   STALE_SECONDS=$(( ${sh:-48} * 3600 ))

  # actors: names from the surface rows (deduped)
  ACTORS=$(mf_actors "$MANIFEST" | awk '{print $1}' | sort -u | tr '\n' ' ')
  [ -n "${ACTORS// /}" ] || die "manifest: at least one actor surface is required"

  # roles: core registry (config/roles.yaml) + any active profile role registries
  ROLES=$(core_roles)
  local prof
  for prof in $(mf_profiles "$MANIFEST"); do
    [ -f "profiles/$prof/roles.yaml" ] && ROLES="$ROLES $(awk 'f&&/^  [a-z-]+:/{s=$1;sub(/:$/,"",s);print s} /^roles:/{f=1}' "profiles/$prof/roles.yaml")"
  done

  # protected paths: core floor + manifest additions (monotonic, §6)
  declare -g -a PROTECTED_ADD=(); read_into PROTECTED_ADD ytoplist "$MANIFEST" protected_paths
}

core_roles() {  # keys under `roles:` in config/roles.yaml
  local f=config/roles.yaml
  [ -f "$f" ] && awk 'f&&/^  [a-z_-]+:/{s=$1;sub(/:$/,"",s);print s} /^roles:/{f=1}' "$f" | tr '\n' ' ' \
    || echo "owner orchestrator specialist reviewer steward"
}

mf_actors() {  # file -> "actor surface delivery authority" per surface row (authority defaults 'full')
  awk '
    /^actors:/ { inb=1; next }
    inb && /^[^ -]/ { inb=0 }
    inb && /^  - / {
      a=""; s=""; d=""; au="full"
      if (match($0,/actor:[ ]*[A-Za-z0-9._-]+/))    { t=substr($0,RSTART,RLENGTH); sub(/actor:[ ]*/,"",t);    a=t }
      if (match($0,/surface:[ ]*[A-Za-z0-9._-]+/))  { t=substr($0,RSTART,RLENGTH); sub(/surface:[ ]*/,"",t);  s=t }
      if (match($0,/delivery:[ ]*[A-Za-z0-9._-]+/)) { t=substr($0,RSTART,RLENGTH); sub(/delivery:[ ]*/,"",t); d=t }
      if (match($0,/authority:[ ]*[A-Za-z0-9._-]+/)){ t=substr($0,RSTART,RLENGTH); sub(/authority:[ ]*/,"",t);au=t }
      if (a!="") print a, s, d, au
    }' "$1"
}

# actor_authority <actor> -> "none" if EVERY surface of the actor is authority:none,
# else "full". An authority:none actor produces evidence only (§2): it cannot set
# lifecycle state (dispatch/accept/return) or approve/decide.
actor_authority() {
  local a=$1 anyfull=0 seen=0 au
  while read -r au; do seen=1; [ "$au" != none ] && anyfull=1; done < <(mf_actors "$MANIFEST" | awk -v a="$a" '$1==a {print $4}')
  [ $seen = 1 ] && [ $anyfull = 0 ] && { echo none; return; }; echo full
}

mf_profiles() {  # file -> profile names (2-indent keys under `profiles:`)
  awk '
    /^profiles:/ { inb=1; next }
    inb && /^[^ #]/ { inb=0 }
    inb && /^  [a-z][a-z0-9_-]*:/ { s=$1; sub(/:$/,"",s); print s }' "$1"
}

delivery_for() {  # actor surface -> airlock|branch|publisher ("" if not found)
  mf_actors "$MANIFEST" | awk -v a="$1" -v s="$2" '$1==a && ($2==s || s=="") {print $3; exit}'
}

# Approval records live in docs/activity_log/APPROVALS_LOG.md, one block each:
#   ## APPROVAL <handoff-id> <gate> — <approver> — <date>
# has_approval <handoff-id> <gate> -> 0 if a matching approval is recorded
has_approval() {
  local log=docs/activity_log/APPROVALS_LOG.md
  [ -f "$log" ] || return 1
  grep -qiE "^## APPROVAL[[:space:]]+$1[[:space:]]+$2([[:space:]]|\$)" "$log"
}

# ---------------------------------------------------------------- header parsing
hdr_present() { [ "$(head -n1 "$1")" = "---" ]; }

hdr_get() {  # file key -> scalar value (inline "# comment" stripped)
  awk -v k="$2" '
    NR==1 { if ($0!="---") exit; next }
    $0=="---" { exit }
    index($0, k":")==1 { s=$0; sub("^"k":[ ]*","",s); sub(/[ ]+#.*$/,"",s); print s; exit }' "$1"
}

hdr_list() {  # file key -> list items, one per line
  awk -v k="$2" '
    NR==1 { if ($0!="---") exit; next }
    $0=="---" { exit }
    inl && $0 ~ /^  - / { s=$0; sub(/^  - /,"",s); sub(/[ ]+#.*$/,"",s); if (s!="") print s; next }
    { inl=0 } index($0, k":")==1 && $0 ~ ("^"k":[ ]*(#.*)?$") { inl=1 }' "$1"
}

hdr_set() {  # file key value -> rewrite scalar in front matter (insert before closing --- if absent)
  local f=$1 k=$2 v=$3
  awk -v k="$k" -v v="$v" '
    BEGIN{fm=0;done=0}
    NR==1 { print; fm=1; next }
    fm==1 && $0=="---" { if(!done){ print k": "v; done=1 } fm=2; print; next }
    fm==1 && index($0,k":")==1 { print k": "v; done=1; next }
    { print }' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
}

body_frozen() {  # file -> body after front matter, up to (excluding) "## Amendments"
  awk '
    NR==1 { if ($0!="---") { print; } fm=1; next }
    fm==1 && $0=="---" { fm=2; next }
    fm==2 && $0=="## Amendments" { exit }
    fm==2 { print }' "$1"
}

frozen_hash() {  # file -> sha256 over role/lane/tier/isolation/inputs/outputs + frozen body (§4)
  { echo "role=$(hdr_get "$1" role)"; echo "lane=$(hdr_get "$1" lane)"; echo "tier=$(hdr_get "$1" tier)"
    echo "isolation=$(hdr_get "$1" isolation)"
    echo "inputs:"; hdr_list "$1" inputs; echo "outputs:"; hdr_list "$1" outputs
    echo "body:"; body_frozen "$1"; } | sha256
}

# manifest_hash -> canonical hash of the resolved manifest + referenced profile configs (§4)
manifest_hash() {
  { cat "$MANIFEST"; local prof
    for prof in $(mf_profiles "$MANIFEST"); do
      [ -f "profiles/$prof/profile.yaml" ] && { echo "=== profile:$prof ==="; cat "profiles/$prof/profile.yaml"; }
    done; } | sha256
}

# instructions_hash -> hash of the compact participant instructions generated at
# dispatch (role, inputs, outputs, resolved isolation, delivery, protection set).
# A stand-in for a full generated instructions doc; the fixtures may tighten it.
participant_instructions() {  # packet -> text
  local pkt=$1
  echo "role=$(hdr_get "$pkt" role)"
  echo "lane=$(hdr_get "$pkt" lane)  tier=$(hdr_get "$pkt" tier)"
  echo "isolation=$(hdr_get "$pkt" isolation)"
  echo "delivery=$(delivery_for "$(hdr_get "$pkt" actor)" "$(hdr_get "$pkt" surface)")"
  echo "inputs:"; hdr_list "$pkt" inputs
  echo "outputs:"; hdr_list "$pkt" outputs
  echo "protection:"; effective_protection
}
instructions_hash() { participant_instructions "$1" | sha256; }

# effective_protection -> the combined protected-path regex (floor + additions)
effective_protection() {
  echo "$CORE_PROTECTED_FLOOR"
  local p; for p in "${PROTECTED_ADD[@]}"; do [ -n "$p" ] && echo "$p"; done
}
# is_protected_path <path> -> 0 if it matches the floor or any manifest addition
is_protected_path() {
  local c=$1 p
  [[ "$c" =~ $CORE_PROTECTED_FLOOR ]] && return 0
  for p in "${PROTECTED_ADD[@]}"; do [ -n "$p" ] && [[ "$c" =~ $p ]] && return 0; done
  return 1
}

# ---------------------------------------------------------------- id / path helpers
packet_from_id() {  # "<slug>/<NNN>" -> path (must be exactly one match)
  local slug=${1%%/*} nnn=${1##*/} m
  m=$(ls "$PROJECTS_ROOT/$slug/handoff/$nnn"-*.md 2>/dev/null | grep -v README || true)
  [ "$(printf '%s\n' "$m" | grep -c .)" -eq 1 ] || return 1
  printf '%s' "$m"
}

path_parts() {  # packet path -> sets SLUG NNN FROLE
  local p=$1 base
  case "$p" in "$PROJECTS_ROOT"/*/handoff/*.md) ;; *) return 1;; esac
  SLUG=${p#"$PROJECTS_ROOT"/}; SLUG=${SLUG%%/*}
  base=$(basename "$p" .md)
  NNN=${base%%-*}; FROLE=${base#*-}
  [[ "$NNN" =~ ^[0-9]{3}$ ]] || return 1
}

# review linkage: a landed/accepted review handoff pointing back at <id> (§4)
has_landed_review() {  # <handoff-id> -> 0 if an independent review has landed
  local id=$1 slug=${1%%/*} p st
  for p in $(ls "$PROJECTS_ROOT/$slug/handoff/"[0-9][0-9][0-9]-*.md 2>/dev/null); do
    hdr_present "$p" || continue
    [ "$(hdr_get "$p" review_of)" = "$id" ] || continue
    st=$(hdr_get "$p" status); in_list "$st" landed accepted && return 0
  done
  return 1
}

# ---------------------------------------------------------------- source-of-truth ref
sot() { echo "origin/$SOT_BRANCH"; }
on_sot()   { git cat-file -e "origin/$SOT_BRANCH:$1" 2>/dev/null; }
sot_sha()  { git rev-parse --short=7 "origin/$SOT_BRANCH"; }
fetch_sot(){ [ "${NO_FETCH:-0}" = "1" ] || git fetch --quiet origin "$SOT_BRANCH" || die "cannot fetch origin $SOT_BRANCH"; }

# Path references in a packet body that look like repo paths.
body_path_refs() {
  body_frozen "$1" | grep -oE '(projects|docs|config|prompts|scripts|templates|profiles)/[A-Za-z0-9_./<>*-]+' \
    | sed -E 's/[.,;:)]+$//' | grep -vE '[<>*]' | grep -vE '/$' | sort -u
}

# Derived next action for a handoff row in the state file
next_action_for() {  # status actor role -> text
  case "$1" in
    draft)      echo "orchestrator: finish packet, run handoff-check";;
    ready)      echo "orchestrator: dispatch (publish --dispatch)";;
    dispatched) echo "$2 as $3: produce declared outputs, then publish";;
    landed)     echo "orchestrator: accept or return";;
    returned)   echo "orchestrator: write superseding handoff";;
    blocked)    echo "see reason in packet; owner decides";;
    accepted|superseded) echo "-";;
    *)          echo "?";;
  esac
}
