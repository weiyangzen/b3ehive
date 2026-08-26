#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SKILLS=(
  compete-cron-builder
  execution-cron-builder
  learn-cron-builder
  optimization-cron-builder
  looper-cron-builder
)

errors=0

for skill in "${SKILLS[@]}"; do
  skill_file="${ROOT_DIR}/${skill}/SKILL.md"
  if [[ ! -f "$skill_file" ]]; then
    echo "ERROR: missing ${skill_file}" >&2
    ((errors++))
    continue
  fi

  if ! sed -n '1,6p' "$skill_file" | grep -qx -- '---'; then
    echo "ERROR: ${skill_file} missing YAML frontmatter fence" >&2
    ((errors++))
  fi

  if ! sed -n '1,8p' "$skill_file" | grep -q "^name: ${skill}$"; then
    echo "ERROR: ${skill_file} missing matching name frontmatter" >&2
    ((errors++))
  fi

  if ! sed -n '1,8p' "$skill_file" | grep -q '^description: '; then
    echo "ERROR: ${skill_file} missing description frontmatter" >&2
    ((errors++))
  fi
done

for required in docs/agent-platforms.md scripts/install_skills.sh; do
  if [[ ! -f "${ROOT_DIR}/${required}" ]]; then
    echo "ERROR: missing ${required}" >&2
    ((errors++))
  fi
done

"${ROOT_DIR}/scripts/install_skills.sh" --target all --scope project --project-dir /tmp/b3ehive-skill-check --dry-run >/dev/null
"${ROOT_DIR}/scripts/validate_execution_transport.sh"

if [[ "$errors" -gt 0 ]]; then
  exit 1
fi

echo "Agent platform validation passed for Codex, Claude Code, Cursor, Grok Build, opencode, OpenClaw, and Hermes."
