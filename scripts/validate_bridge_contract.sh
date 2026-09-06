#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

skills=(
  compete-cron-builder
  execution-cron-builder
  learn-cron-builder
  optimization-cron-builder
  looper-cron-builder
)

suite_ref="${ROOT_DIR}/looper-cron-builder/references/b3ehive-bridge-contract.md"

if [[ ! -f "$suite_ref" ]]; then
  echo "ERROR: missing shared bridge contract: ${suite_ref}" >&2
  exit 1
fi

for skill in "${skills[@]}"; do
  skill_file="${ROOT_DIR}/${skill}/SKILL.md"
  if [[ ! -f "$skill_file" ]]; then
    echo "ERROR: missing skill file: ${skill_file}" >&2
    exit 1
  fi
  if [[ "$skill" != "looper-cron-builder" ]]; then
    if ! rg -q 'b3ehive-bridge-contract.md' "$skill_file"; then
      echo "ERROR: ${skill} does not reference shared bridge contract" >&2
      exit 1
    fi
  fi
  if ! rg -q 'looper_log|LooperLog' "$skill_file"; then
    echo "ERROR: ${skill} missing looper_log / LooperLog contract text" >&2
    exit 1
  fi
done

for required in \
  'State Constitution' \
  'EstimatorPolicy' \
  'Unified RouteDecision' \
  'SkillRegistry And NestedSkillCall' \
  'EvidenceLint' \
  'LooperLog Multi-Grain Object/Instrument Feedback' \
  'ParetoGate For Self-Evolution' \
  'ROI As Scheduling Signal' \
  'B3IR And Interface Modes' \
  'Anti-Bloat Output Rule' \
  'Prompt And Hook Boundary'; do
  if ! rg -q "$required" "$suite_ref"; then
    echo "ERROR: shared bridge contract missing section: ${required}" >&2
    exit 1
  fi
done

for required in \
  'TargetObject' \
  'InstrumentObject' \
  'ObjectLoop' \
  'InstrumentLoop' \
  'target_feedback' \
  'instrument_object'; do
  if ! rg -q "$required" "$suite_ref"; then
    echo "ERROR: shared bridge contract missing object/instrument looper-log term: ${required}" >&2
    exit 1
  fi
done

if ! rg -Fq 'accepted InstrumentObject change needs its own [ ] -> [_] -> [x] lifecycle' "$suite_ref"; then
  echo "ERROR: shared bridge contract missing InstrumentObject lifecycle authority rule" >&2
  exit 1
fi

if rg -n 'OperatingDelta|LessonDelta|lesson_log|lesson-derived|memory bridge' \
  "${ROOT_DIR}/SKILL.md" \
  "${ROOT_DIR}/README.md" \
  "${ROOT_DIR}/docs" \
  "${ROOT_DIR}"/*-cron-builder/SKILL.md \
  "${ROOT_DIR}"/*-cron-builder/references/*.md >/tmp/b3ehive-bridge-contract-stale-scan.log; then
  echo "ERROR: stale feedback/delta wording remains" >&2
  cat /tmp/b3ehive-bridge-contract-stale-scan.log >&2
  exit 1
fi

python3 - "$ROOT_DIR/package.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1]))
expected = [
    "compete-cron-builder",
    "execution-cron-builder",
    "learn-cron-builder",
    "optimization-cron-builder",
    "looper-cron-builder",
]
for key in ("codex", "claudeCode", "opencode", "hermes"):
    got = data[key]["skills"]
    if got != expected:
        raise SystemExit(f"{key}.skills = {got!r}, expected {expected!r}")
PY

echo "Bridge contract validation passed."
