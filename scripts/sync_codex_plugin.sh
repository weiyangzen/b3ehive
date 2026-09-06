#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGIN_SKILLS_DIR="${ROOT_DIR}/plugins/b3ehive/skills"

SKILLS=(
  compete-cron-builder
  execution-cron-builder
  learn-cron-builder
  optimization-cron-builder
  looper-cron-builder
)

mkdir -p "$PLUGIN_SKILLS_DIR"

for skill in "${SKILLS[@]}"; do
  src="${ROOT_DIR}/${skill}"
  dst="${PLUGIN_SKILLS_DIR}/${skill}"
  if [[ ! -f "${src}/SKILL.md" ]]; then
    echo "Missing skill source: ${src}/SKILL.md" >&2
    exit 1
  fi
  rm -rf "$dst"
  cp -a "$src" "$dst"
  echo "Synced ${skill}"
done

echo "Codex plugin skills synced: ${PLUGIN_SKILLS_DIR}"
