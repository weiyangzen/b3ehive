#!/bin/bash
# Every repository check. Fails on the first broken gate.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

for tool in python3 shasum cmp; do
  command -v "$tool" >/dev/null || { echo "ERROR: missing dependency: ${tool}" >&2; exit 2; }
done

scripts/sync_core.sh --check
scripts/sync_loop.sh --check
for skill in compete-cron-builder execution-cron-builder learn-cron-builder optimization-cron-builder looper-cron-builder; do
  diff -rq -x __pycache__ "$skill" "plugins/b3ehive/skills/$skill" >/dev/null || {
    echo "ERROR: plugin copy of ${skill} is stale; run scripts/sync_codex_plugin.sh" >&2; exit 1; }
done
python3 scripts/build_grokbot.py --check
python3 scripts/lint_skills.py
python3 -m unittest discover -s tests -q
bash scripts/validate_compete_three_way.sh
bash scripts/validate_agent_platforms.sh
python3 -m json.tool evals/scenarios.json >/dev/null
for f in bin/b3ehive scripts/*.sh; do bash -n "$f"; done
echo "All b3ehive checks passed."
