# Learn Route Policy

Route choice is contractual. Record decisions in `Docs/learn/route_decision.md`.

Minimum fields:

```text
learn_mode
source_kind
target_kind
selected_route
model_class
budget_reason
risk_reason
validator_reason
fallback_route
```

## Defaults

```text
understand:
  high_reasoning for complex code
  standard for small/simple files

transform:
  high_reasoning for code/API/schema/runtime transformations
  standard for mechanical tool asset conversion

translate:
  cheap_translation or uncommon_translation by default
  high_reasoning only when risk or validators require it
```

Translation tasks often work well with cheaper or uncommon routes, including
35B-class or A3B-class models, when validators are strong and the domain is not
high-stakes.

## Escalation

Escalate route when:

- legal, medical, security, or financial meaning is high-stakes
- source contains code-heavy technical semantics
- glossary conflicts are detected
- section parity fails repeatedly
- transform validators fail repeatedly with plausible model error
- the human explicitly requests a high-reasoning route

## Translate Validators

Translate mode must preserve:

- headings and anchors
- links
- code blocks
- tables
- admonitions
- glossary decisions
- source section coverage
- technical meaning change ledger
