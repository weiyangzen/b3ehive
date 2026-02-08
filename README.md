# b3ehive 🐝

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> "Fake it until make it" - Feynman-style Triple-Agent Competitive Collaboration

## Quick Install

```bash
# Clone to OpenClaw skills directory
git clone https://github.com/weiyangzen/b3ehive.git ~/.openclaw/skills/b3ehive

# Or install via OpenClaw CLI
openclaw skills install https://github.com/weiyangzen/b3ehive.git
```

## Usage

```bash
# Run b3ehive with your task
b3ehive "Implement a rate limiter with token bucket algorithm"

# Or via OpenClaw
openclaw skills run b3ehive --task "Your coding task here"
```

## How It Works

1. **Phase 1: Parallel Implementation**
   - Agent A (Focus: Simplicity)
   - Agent B (Focus: Speed)
   - Agent C (Focus: Robustness)

2. **Phase 2: Cross-Evaluation**
   - Each agent evaluates the other two
   - Objective metrics: code simplicity, speed, stability, corner cases

3. **Phase 3: Objective Self-Scoring**
   - Fair self-assessment
   - Peer comparison

4. **Phase 4: Final Delivery**
   - Best solution selected
   - Full comparison report

## Documentation

- [SKILL.md](SKILL.md) - Full technical specification
- [config.yaml](config.yaml) - Configuration options

## License

MIT © Weiyang ([@weiyangzen](https://github.com/weiyangzen))
