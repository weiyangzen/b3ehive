#!/bin/bash
# Runtime reliability guard: retry + cross-session event log.

set -euo pipefail

readonly RUNTIME_WORKSPACE="${SCRIPT_DIR}/workspace"
readonly RUNTIME_LOG_DIR="${RUNTIME_WORKSPACE}/.runtime"
readonly RUNTIME_RECENT_EVENTS="${RUNTIME_WORKSPACE}/RECENT_EVENTS.md"

runtime_init() {
  mkdir -p "${RUNTIME_LOG_DIR}"
  if [[ ! -f "${RUNTIME_RECENT_EVENTS}" ]]; then
    cat > "${RUNTIME_RECENT_EVENTS}" << 'EOF'
# RECENT_EVENTS

Rolling 24h event feed for cross-session continuity.
EOF
  fi
}

runtime_log() {
  local phase="$1"
  local message="$2"
  printf -- "- [%s] [%s] %s\n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${phase}" "${message}" >> "${RUNTIME_RECENT_EVENTS}"
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
