#!/bin/bash
# Run b3ehive multi-layer blueprint stack validation, boundary checks, IR export, or Gantt rendering.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
case "${1:-}" in
  gantt)
    shift
    exec python3 "${ROOT_DIR}/execution-cron-builder/scripts/render_stack_gantt.py" "$@"
    ;;
  stack|boundaries|export-ir)
    exec python3 "${ROOT_DIR}/execution-cron-builder/scripts/validate_blueprint_stack.py" "$@"
    ;;
  *)
    echo "Usage: scripts/validate_stack.sh <stack|boundaries|export-ir|gantt> MANIFEST [options]" >&2
    exit 2
    ;;
esac
