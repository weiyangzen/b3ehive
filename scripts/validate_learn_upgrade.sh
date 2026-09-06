#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

required_skills=(
  compete-cron-builder
  execution-cron-builder
  learn-cron-builder
  optimization-cron-builder
  looper-cron-builder
)

removed_skills=(
  debate-cron-builder
  debating-cron-builder
  research-cron-builder
  migration-cron-builder
)

for skill in "${required_skills[@]}"; do
  if [[ ! -f "${ROOT_DIR}/${skill}/SKILL.md" ]]; then
    echo "ERROR: missing active skill ${skill}" >&2
    exit 1
  fi
done

for skill in "${removed_skills[@]}"; do
  if [[ -e "${ROOT_DIR}/${skill}" ]]; then
    echo "ERROR: removed skill still exists: ${skill}" >&2
    exit 1
  fi
done

if rg -n 'research-cron-builder|migration-cron-builder' \
  "${ROOT_DIR}/package.json" \
  "${ROOT_DIR}/scripts/validate_agent_platforms.sh" \
  "${ROOT_DIR}/docs/agent-platforms.md" \
  "${ROOT_DIR}/README.md" \
  "${ROOT_DIR}/SKILL.md" >/tmp/b3ehive-learn-active-scan.log; then
  echo "ERROR: removed skill appears in active package/platform surfaces" >&2
  cat /tmp/b3ehive-learn-active-scan.log >&2
  exit 1
fi

for skill in "${removed_skills[@]}"; do
  if ! rg -q "${skill}" "${ROOT_DIR}/scripts/install_skills.sh"; then
    echo "ERROR: installer does not remove deprecated ${skill}" >&2
    exit 1
  fi
done

learn="${ROOT_DIR}/learn-cron-builder/SKILL.md"
for required in \
  'learn_mode=understand' \
  'learn_mode=transform' \
  'learn_mode=translate' \
  'source_manifest.tsv' \
  'one-to-one' \
  'subset' \
  'route_policy' \
  'Workers may only advance' \
  'master lane is the only actor'; do
  if ! rg -q "$required" "$learn"; then
    echo "ERROR: learn skill missing required contract text: ${required}" >&2
    exit 1
  fi
done

for reference in learn-pattern.md coverage-contract.md route-policy.md; do
  if [[ ! -f "${ROOT_DIR}/learn-cron-builder/references/${reference}" ]]; then
    echo "ERROR: missing learn reference ${reference}" >&2
    exit 1
  fi
done

echo "Learn upgrade validation passed."
