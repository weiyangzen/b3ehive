#!/bin/bash
# Phase 1: Parallel Implementation with PCTF compliance

set -euo pipefail

readonly TASK="${1:-}"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly WORKSPACE="${SCRIPT_DIR}/workspace"

# Assertion: Task must be provided
if [[ -z "$TASK" ]]; then
    echo "ERROR: Usage: phase1_spawn.sh \"Task description\""
    exit 1
fi

echo "🐝 Phase 1: Spawning 3 agents..."
echo "Task: $TASK"

# Create workspace directories
mkdir -p "${WORKSPACE}/run_a" "${WORKSPACE}/run_b" "${WORKSPACE}/run_c"

# Agent configuration with PCTF-compliant prompts
declare -A AGENT_FOCUS=(
    [a]="Simplicity and elegance - minimal lines, clean abstractions"
    [b]="Performance and speed - optimized algorithms, minimal overhead"
    [c]="Robustness and completeness - exhaustive error handling, all corner cases"
)

# Spawn each agent
for agent in a b c; do
    echo "  Spawning Agent ${agent^^}..."
    
    agent_dir="${WORKSPACE}/run_${agent}"
    mkdir -p "${agent_dir}/implementation"
    mkdir -p "${agent_dir}/evaluation"
    
    # PCTF-compliant prompt
    cat > "${agent_dir}/PROMPT.md" << EOF
# Agent ${agent^^} - Implementation Task

## Role
Expert Software Engineer

## Focus
${AGENT_FOCUS[$agent]}

## Task
${TASK}

## Constraints (MUST FOLLOW)
1. Complete runnable code in implementation/ directory
2. Create Checklist.md with ALL items checked before completion
3. Create SUMMARY.md explaining your unique approach and competitive advantages
4. Your approach MUST differ from Agents B and C
5. Code must pass linter and all tests

## Linter Rules
- Code must compile/run without errors
- All tests must pass
- No TODO comments left
- All functions documented
- Maximum cyclomatic complexity: 10

## Output Files
- implementation/main.* (main code)
- implementation/tests.* (comprehensive tests)
- Checklist.md (all checked)
- SUMMARY.md (competitive analysis)

## Success Criteria
ASSERT: implementation/ exists and contains runnable code
ASSERT: Checklist.md has no unchecked items
ASSERT: SUMMARY.md explains why your approach is superior
EOF

    # Create Checklist template
    cat > "${agent_dir}/Checklist.md" << 'EOF'
# Implementation Checklist

## Core Implementation
- [ ] Main algorithm implemented
- [ ] Helper functions created
- [ ] Error handling added
- [ ] Resource cleanup implemented
- [ ] Edge cases handled

## Testing
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Edge case tests included
- [ ] All tests passing

## Documentation
- [ ] Code comments added
- [ ] Function documentation complete
- [ ] Usage examples provided

## Quality
- [ ] Code reviewed for clarity
- [ ] No TODOs or FIXMEs remaining
- [ ] Linter passes
- [ ] Ready for evaluation
EOF

    # Create SUMMARY template
    cat > "${agent_dir}/SUMMARY.md" << EOF
# Agent ${agent^^} Summary

## Focus
${AGENT_FOCUS[$agent]}

## Approach
[Describe your unique approach]

## Key Design Decisions
1. [Decision 1]
2. [Decision 2]
3. [Decision 3]

## Competitive Advantages
- [Advantage 1]
- [Advantage 2]
- [Advantage 3]

## Metrics
- Lines of code: [X]
- Time complexity: [O(X)]
- Space complexity: [O(X)]
- Test coverage: [X%]

## Self-Assessment
[How you believe your solution compares]
EOF

    echo "  Agent ${agent^^} spawned successfully"
done

# Linter: Verify all agents have required structure
echo "  Running linter checks..."
for agent in a b c; do
    agent_dir="${WORKSPACE}/run_${agent}"
    
    # Assertion: Required files exist
    if [[ ! -f "${agent_dir}/PROMPT.md" ]]; then
        echo "ERROR: Agent ${agent} PROMPT.md missing"
        exit 1
    fi
    
    if [[ ! -f "${agent_dir}/Checklist.md" ]]; then
        echo "ERROR: Agent ${agent} Checklist.md missing"
        exit 1
    fi
    
    if [[ ! -f "${agent_dir}/SUMMARY.md" ]]; then
        echo "ERROR: Agent ${agent} SUMMARY.md missing"
        exit 1
    fi
done

echo "✅ Phase 1 complete: 3 agents spawned and validated"
