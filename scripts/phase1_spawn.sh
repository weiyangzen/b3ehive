#!/bin/bash
# Phase 1: Spawn 3 agents

set -euo pipefail

readonly TASK="${1:-}"

if [[ -z "$TASK" ]]; then
    echo "Usage: phase1_spawn.sh \"Task\""
    exit 1
fi

echo "🐝 Phase 1: Spawning 3 agents..."
echo "Task: $TASK"

# Create workspace
mkdir -p workspace/{run_a,run_b,run_c}

# Spawn agents (simulated)
for agent in a b c; do
    echo "  Agent ${agent^^} spawned"
    mkdir -p "workspace/run_${agent}/implementation"
    touch "workspace/run_${agent}/Checklist.md"
    touch "workspace/run_${agent}/SUMMARY.md"
done

echo "✅ Phase 1 complete"
