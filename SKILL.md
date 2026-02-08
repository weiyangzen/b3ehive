# b3ehive Skill

## Overview

Feynman-style Triple-Agent Competitive Collaboration System.

Three isolated agents implement the same functionality, evaluate each other, and compete to produce the optimal solution.

## Philosophy

> "Fake it until make it" - Richard Feynman

Three agents independently "fake" understanding by implementing solutions, then through rigorous evaluation, collectively "make" the best solution.

## System Architecture

```
User Task
    │
    ├──→ Agent A (Simplicity) ──┐
    ├──→ Agent B (Speed) ───────┼──→ Cross-Evaluation ──→ Scoring ──→ Best Solution
    └──→ Agent C (Robustness) ──┘
```

## Four Phases

### Phase 1: Parallel Implementation
Three agents implement with different focuses:
- **Agent A**: Simplicity and elegance
- **Agent B**: Performance and speed  
- **Agent C**: Robustness and completeness

### Phase 2: Cross-Evaluation
Each agent evaluates others on:
- Code simplicity (20%)
- Execution speed (25%)
- Stability (25%)
- Corner case coverage (20%)
- Maintainability (10%)

### Phase 3: Objective Self-Scoring
Fair self-assessment and peer comparison.

### Phase 4: Final Delivery
Optimal solution based on competitive evaluation.

## Installation

```bash
git clone https://github.com/weiyangzen/b3ehive.git ~/.openclaw/skills/b3ehive
```

## Usage

```bash
b3ehive "Implement HTTP retry with exponential backoff"
```

## Configuration

Edit `config.yaml`:

```yaml
b3ehive:
  agents:
    count: 3
    model: openai-proxy/gpt-5.3-codex
    thinking: high
  evaluation:
    dimensions:
      simplicity: 20
      speed: 25
      stability: 25
      corner_cases: 20
      maintainability: 10
```

## License

MIT
