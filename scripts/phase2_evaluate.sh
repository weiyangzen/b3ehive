#!/bin/bash
# Phase 2: Cross-evaluation

set -euo pipefail

echo "🐝 Phase 2: Cross-evaluation..."

for from in a b c; do
    for to in a b c; do
        [[ "$from" == "$to" ]] && continue
        echo "  Agent ${from^^} evaluating Agent ${to^^}"
        mkdir -p "workspace/run_${from}/evaluation"
        touch "workspace/run_${from}/evaluation/EVALUATION_${from}_TO_${to}.md"
    done
done

echo "✅ Phase 2 complete"
