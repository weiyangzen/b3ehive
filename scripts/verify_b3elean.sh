#!/bin/bash
# Run b3elean (Lean 4.34.0) formal verification for b3ehive blueprint stacks or Lean oracles.
# Users bring their own Lean 4 environment (elan + leanprover/lean4:v4.34.0).
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if ! command -v lake >/dev/null || ! command -v lean >/dev/null; then
  cat >&2 <<'MSG'
ERROR: Lean 4 toolchain (`lean` / `lake`) not found in PATH.
Install elan (https://github.com/leanprover/elan) and the pinned toolchain:
  elan toolchain install leanprover/lean4:v4.34.0
Or skip Lean verification with: B3_FORMAL_VERIFIER=off
MSG
  exit 2
fi
exec python3 "${ROOT_DIR}/execution-cron-builder/scripts/verify_lean.py" "$@"
