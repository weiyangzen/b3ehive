#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

looper="${ROOT_DIR}/looper-cron-builder/SKILL.md"
bridge_ref="${ROOT_DIR}/looper-cron-builder/references/bridge-control.md"
suite_ref="${ROOT_DIR}/looper-cron-builder/references/b3ehive-bridge-contract.md"

if [[ ! -f "$looper" ]]; then
  echo "ERROR: missing looper skill" >&2
  exit 1
fi

if [[ ! -f "$bridge_ref" ]]; then
  echo "ERROR: missing looper bridge-control reference" >&2
  exit 1
fi

if [[ ! -f "$suite_ref" ]]; then
  echo "ERROR: missing shared b3ehive bridge contract reference" >&2
  exit 1
fi

for required in \
  'BridgeSurface' \
  'BridgeSignal' \
  'BridgeDelta' \
  'SideEffectGate' \
  'OperatorSignal' \
  'NestedRunLedger' \
  'ParentLeaseRef' \
  'EvidenceLedger' \
  'LooperLog' \
  'looper_log' \
  'TargetObject' \
  'InstrumentObject' \
  'ObjectLoop' \
  'InstrumentLoop' \
  'target_feedback' \
  'instrument_object' \
  'EstimatorPolicy' \
  'RouteDecision' \
  'EvidenceLint' \
  'ParetoGate' \
  'bridge_level' \
  'master-only acceptance'; do
  if ! rg -q "$required" "$looper" "$bridge_ref" "$suite_ref"; then
    echo "ERROR: looper upgrade missing required protocol text: ${required}" >&2
    exit 1
  fi
done

if ! rg -Fq 'accepted InstrumentObject change needs its own [ ] -> [_] -> [x] lifecycle' "$suite_ref"; then
  echo "ERROR: looper upgrade missing InstrumentObject lifecycle authority rule" >&2
  exit 1
fi

for bridge_level in context handoff memory artifact blueprint strategy metric identity; do
  if ! rg -q "$bridge_level" "$bridge_ref"; then
    echo "ERROR: bridge-control missing bridge level: ${bridge_level}" >&2
    exit 1
  fi
done

for runtime_file in \
  bridge_surfaces.yaml \
  bridge_signals.yaml \
  bridge_delta_ledger.jsonl \
  evidence_ledger.jsonl \
  operator_signals.jsonl \
  side_effect_decisions.jsonl \
  nested_run_ledger.jsonl \
  looper_log.jsonl; do
  if ! rg -q "$runtime_file" "$looper" "$bridge_ref" "$suite_ref"; then
    echo "ERROR: looper upgrade missing runtime file: ${runtime_file}" >&2
    exit 1
  fi
done

for skill in compete-cron-builder execution-cron-builder learn-cron-builder optimization-cron-builder; do
  if ! rg -q 'b3ehive-bridge-contract.md' "${ROOT_DIR}/${skill}/SKILL.md"; then
    echo "ERROR: ${skill} missing shared bridge contract reference" >&2
    exit 1
  fi
  if ! rg -q 'ParentLeaseRef' "${ROOT_DIR}/${skill}"; then
    echo "ERROR: ${skill} missing ParentLeaseRef looper embedding rule" >&2
    exit 1
  fi
  if ! rg -q 'TargetObject' "${ROOT_DIR}/${skill}/SKILL.md" || ! rg -q 'InstrumentObject' "${ROOT_DIR}/${skill}/SKILL.md"; then
    echo "ERROR: ${skill} missing TargetObject / InstrumentObject looper_log obligation" >&2
    exit 1
  fi
  if ! rg -q 'cannot write `?\[x\]' "${ROOT_DIR}/${skill}" && ! rg -q 'never write `?\[x\]' "${ROOT_DIR}/${skill}"; then
    echo "ERROR: ${skill} missing nested no-direct-[x] rule" >&2
    exit 1
  fi
done

if rg -n 'OperatingDelta|LessonDelta|lesson_log|lesson-derived|memory bridge' \
  "${ROOT_DIR}/SKILL.md" \
  "${ROOT_DIR}"/*-cron-builder/SKILL.md \
  "${ROOT_DIR}/looper-cron-builder/references/b3ehive-bridge-contract.md" \
  "${ROOT_DIR}/looper-cron-builder/references/bridge-control.md" >/tmp/b3ehive-looper-stale-scan.log; then
  echo "ERROR: stale feedback/delta wording remains in active bridge surfaces" >&2
  cat /tmp/b3ehive-looper-stale-scan.log >&2
  exit 1
fi

if rg -n 'six portable|six skill|The Six|六大 Skill' \
  "${ROOT_DIR}/README.md" \
  "${ROOT_DIR}/SKILL.md" \
  "${ROOT_DIR}/docs" >/tmp/b3ehive-looper-six-scan.log; then
  echo "ERROR: stale six-skill language remains" >&2
  cat /tmp/b3ehive-looper-six-scan.log >&2
  exit 1
fi

active_count="$(python3 - <<'PY' "${ROOT_DIR}/package.json"
import json, sys
data = json.load(open(sys.argv[1]))
skills = data["codex"]["skills"]
print(len(skills))
PY
)"

if [[ "$active_count" != "5" ]]; then
  echo "ERROR: package codex skills count is ${active_count}, expected 5" >&2
  exit 1
fi

echo "Looper upgrade validation passed."
