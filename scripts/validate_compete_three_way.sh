#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${TMPDIR:-/tmp}/b3ehive-compete-three-way-check"

rm -rf "$OUT_DIR"

python3 "${ROOT_DIR}/compete-cron-builder/scripts/compete_cron_builder.py" \
  --task "Validate old three-way artifact coverage" \
  --output "$OUT_DIR" \
  --budget-workers 3 \
  --competition-shape three_way_challenge \
  --artifact-layout old_three_way \
  --runner mock \
  --min-free-gb 0 >/tmp/b3ehive-compete-three-way-check.log

required_top=(
  compete_manifest.json
  classification.md
  verification.md
  best_run.txt
  final_repairs.md
  summary.md
  selected.json
  rejected.json
  synthesis.md
)

for file in "${required_top[@]}"; do
  if [[ ! -f "${OUT_DIR}/${file}" ]]; then
    echo "ERROR: missing ${file}" >&2
    exit 1
  fi
done

best="$(cat "${OUT_DIR}/best_run.txt")"
case "$best" in
  run_a|run_b|run_c) ;;
  *)
    echo "ERROR: best_run.txt contains invalid candidate: ${best}" >&2
    exit 1
    ;;
esac

for candidate in run_a run_b run_c; do
  impl="${OUT_DIR}/${candidate}/implementation"
  for file in result.md verification.md critique_round_1.md update_round_1.md critique_round_2.md final_repair.md; do
    if [[ ! -f "${impl}/${file}" ]]; then
      echo "ERROR: missing ${candidate}/implementation/${file}" >&2
      exit 1
    fi
  done
done

python3 - "$OUT_DIR" <<'PY'
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
manifest = json.loads((out / "compete_manifest.json").read_text())
selected = json.loads((out / "selected.json").read_text())["selected_ids"]
best = (out / "best_run.txt").read_text().strip()

assert manifest["competition_shape"] == "three_way_challenge"
assert manifest["artifact_layout"] == "old_three_way"
assert manifest["selection_mode"] == "vote_then_tiebreak"
assert manifest["candidate_ids"] == ["run_a", "run_b", "run_c"]
assert manifest["handoff"]["may_mark_x"] is False
assert selected == [best]
PY

echo "Compete three-way artifact validation passed."
