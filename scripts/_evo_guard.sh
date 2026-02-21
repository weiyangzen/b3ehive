#!/bin/bash
# EvoMap reliability guard: retry + cross-session event log.

set -euo pipefail

readonly EVO_WORKSPACE="${SCRIPT_DIR}/workspace"
readonly EVO_LOG_DIR="${EVO_WORKSPACE}/.evo"
readonly EVO_RECENT_EVENTS="${EVO_WORKSPACE}/RECENT_EVENTS.md"

evo_init() {
  mkdir -p "${EVO_LOG_DIR}"
  if [[ ! -f "${EVO_RECENT_EVENTS}" ]]; then
    cat > "${EVO_RECENT_EVENTS}" << 'EOF'
# RECENT_EVENTS

Rolling 24h event feed for cross-session continuity.
EOF
  fi
}

evo_log() {
  local phase="$1"
  local message="$2"
  printf -- "- [%s] [%s] %s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${phase}" "${message}" >> "${EVO_RECENT_EVENTS}"
}

run_with_retry() {
  local attempts="$1"
  shift
  local n=1
  local delay=1
  while true; do
    if "$@"; then
      return 0
    fi
    if [[ "${n}" -ge "${attempts}" ]]; then
      return 1
    fi
    sleep "${delay}"
    delay=$((delay * 2))
    n=$((n + 1))
  done
}
