#!/bin/bash
# Copy the shared core files into every skill so each skill stands alone.
# --check reports drift without writing.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS=(compete-cron-builder execution-cron-builder learn-cron-builder optimization-cron-builder looper-cron-builder)
FILES=(core.md substrate-cron.md)
check=0; [[ "${1:-}" == "--check" ]] && check=1
drift=0
for skill in "${SKILLS[@]}"; do
  mkdir -p "${ROOT_DIR}/${skill}/references"
  for f in "${FILES[@]}"; do
    src="${ROOT_DIR}/core/${f}"; dst="${ROOT_DIR}/${skill}/references/${f}"
    if cmp -s "$src" "$dst"; then continue; fi
    if [[ $check -eq 1 ]]; then echo "DRIFT: ${skill}/references/${f}" >&2; drift=1; else cp "$src" "$dst"; echo "Synced ${skill}/references/${f}"; fi
  done
done
# Sync pure Lean sources from formal/b3elean into execution-cron-builder/scripts/b3elean
# so installed skills and grokbot zips run standalone when the user provides Lean 4.
B3ELEAN_SRC="${ROOT_DIR}/formal/b3elean"
B3ELEAN_DST="${ROOT_DIR}/execution-cron-builder/scripts/b3elean"
B3ELEAN_FILES=(lean-toolchain lakefile.toml lake-manifest.json B3ELean.lean B3ELean/Core.lean B3ELean/Soundness.lean B3ELean/Main.lean)
if [[ -d "$B3ELEAN_SRC" ]]; then
  for rel in "${B3ELEAN_FILES[@]}"; do
    src="${B3ELEAN_SRC}/${rel}"; dst="${B3ELEAN_DST}/${rel}"
    [[ -f "$src" ]] || continue
    if [[ -f "$dst" ]] && cmp -s "$src" "$dst"; then continue; fi
    if [[ $check -eq 1 ]]; then
      echo "DRIFT: execution-cron-builder/scripts/b3elean/${rel}" >&2; drift=1
    else
      mkdir -p "$(dirname "$dst")"; cp "$src" "$dst"
      echo "Synced execution-cron-builder/scripts/b3elean/${rel}"
    fi
  done
fi
exit $drift
