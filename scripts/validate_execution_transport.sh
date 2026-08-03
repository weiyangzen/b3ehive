#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="${ROOT_DIR}/execution-cron-builder"
PLUGIN_SKILL_DIR="${ROOT_DIR}/plugins/b3ehive/skills/execution-cron-builder"

required_files=(
  "SKILL.md"
  "agents/openai.yaml"
  "references/execution-pattern.md"
  "references/gate-rules.md"
)

errors=0

error() {
  echo "ERROR: $*" >&2
  errors=$((errors + 1))
}

for relative in "${required_files[@]}"; do
  source_file="${SKILL_DIR}/${relative}"
  plugin_file="${PLUGIN_SKILL_DIR}/${relative}"
  [[ -f "$source_file" ]] || error "missing execution skill source: ${relative}"
  [[ -f "$plugin_file" ]] || error "missing plugin execution skill: ${relative}"
  if [[ -f "$source_file" && -f "$plugin_file" ]] && ! cmp -s "$source_file" "$plugin_file"; then
    error "plugin execution skill is stale: ${relative}"
  fi
done

skill_text="${SKILL_DIR}/SKILL.md"
for required in \
  'WORKER_TRANSPORT=tmux_codex_tui' \
  'APP_SERVER_WORKERS=forbidden' \
  'ordinary interactive' \
  'private writable `CODEX_HOME`' \
  'authenticated active `/goal`' \
  'claim-specific completion token' \
  'capture-pane -p -J'; do
  grep -Fq "$required" "$skill_text" || error "missing execution transport contract: ${required}"
done

grep -Eq 'tmux -S .*new-session' "$skill_text" || \
  error "execution skill lacks a task-local tmux launch template"
grep -Eq 'CODEX_HOME=.*codex-home' "$skill_text" || \
  error "execution skill lacks task-local CODEX_HOME"
grep -Eq 'codex_argv=\(codex -C "\$(WORKER_REPO|WORK_ROOT)"' "$skill_text" || \
  error "execution skill lacks an interactive Codex TUI argv"

for required in \
  'transport: tmux_codex_tui' \
  'app_server_workers: forbidden' \
  'process_isolation: one_interactive_process_tree_per_claim' \
  'state_isolation: one_writable_codex_home_per_claim' \
  'goal_completion_token: required_unique_per_claim' \
  'goal_delivery_verification: complete_composer_text_required_before_submit' \
  'goal_delivery_probe_template:' \
  'goal_submit_count: 1' \
  'duplicate_goal_submission: forbidden'; do
  grep -Fq "$required" "${ROOT_DIR}/config.yaml" || \
    error "config lacks Codex transport policy: ${required}"
done

if grep -Eq 'goal_template:.*paste-buffer.*send-keys' "${ROOT_DIR}/config.yaml"; then
  error "Codex goal template submits before delivery can be verified"
fi

grep -Eq 'goal_template:.*\{goal_completion_token\}' "${ROOT_DIR}/config.yaml" || \
  error "Codex goal template lacks a claim-specific completion token"
grep -Eq 'goal_delivery_probe_template:.*capture-pane -p -J' "${ROOT_DIR}/config.yaml" || \
  error "Codex goal delivery probe does not inspect joined composer text"

for required in \
  'one admission pump reaches exactly `N` authenticated lanes' \
  'Do not wait for the next' \
  'every intentional underfill has a specific persisted'; do
  grep -Fq "$required" "$skill_text" || \
    error "missing concurrency fill contract: ${required}"
done

# Forbidden transports may be named only in negative/hard-failure prose. Reject
# command-shaped occurrences and shared app-server config in all launch surfaces.
if grep -InE 'codex([[:space:]]+[^#]*)?[[:space:]]+(app-server|exec)([[:space:]]|$)' \
  "${ROOT_DIR}/config.yaml" || \
  grep -RInE --include='*.sh' --include='*.yaml' --include='*.yml' \
  --include='*.json' 'codex([[:space:]]+[^#]*)?[[:space:]]+(app-server|exec)([[:space:]]|$)' \
  "${ROOT_DIR}/scripts"; then
  error "repository config or scripts contain a forbidden Codex worker command"
fi

if grep -RInE --include='*.md' '^[[:space:]]*(\$[[:space:]]*)?codex[[:space:]]+(app-server|exec)([[:space:]]|$)' \
  "${SKILL_DIR}" "${ROOT_DIR}/docs" "${ROOT_DIR}/optimization-cron-builder"; then
  error "execution docs contain a positive forbidden Codex command"
fi

for forbidden in \
  'cvbackbone' \
  '/Work/Github/' \
  'Stage3IOSPathValidation' \
  'gpt-5.6-luna'; do
  if grep -RInF "$forbidden" "$SKILL_DIR"; then
    error "execution skill contains project-specific residue: ${forbidden}"
  fi
done

if [[ "$errors" -ne 0 ]]; then
  exit 1
fi

echo "Execution transport validation passed: repository-agnostic, tmux TUI only, one independent Codex process per claim."
