#!/bin/bash
# Phase 3: Objective scoring

set -euo pipefail

echo "🐝 Phase 3: Objective scoring..."

for agent in a b c; do
    echo "  Agent ${agent^^} scoring..."
    touch "workspace/run_${agent}/SCORECARD.md"
done

echo "✅ Phase 3 complete"
