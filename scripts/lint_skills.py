#!/usr/bin/env python3
"""Structure and lexicon lint for the five b3ehive skills.

Checks behavior-relevant structure, not vocabulary presence:
- frontmatter parses, name matches the directory, description fits
- SKILL.md stays within its line and token budget
- references stay one level deep and exist
- shared core and loop copies match their sources
- skill bodies declare the core and loop versions they bind
- v2-authored text pairs no verb with a forbidden subject
- skill bodies never restate a core or loop sentence
- grokbot builds carry the load gate and name only the claude runtime
"""
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(os.environ.get("B3EHIVE_ROOT") or pathlib.Path(__file__).resolve().parents[1])
SKILLS = ["compete-cron-builder", "execution-cron-builder", "learn-cron-builder",
          "optimization-cron-builder", "looper-cron-builder"]
MAX_LINES = 300
MAX_TOKENS = 3500          # chars / 4; Claude Code re-attaches only 5,000 tokens per skill after compaction
MAX_DESCRIPTION = 400
CORE_VERSION, LOOP_VERSION = "core v2", "loop v2"
GROKBOT_RUNNER = "claude -p --dangerously-skip-permissions"
GROKBOT_GATE = ["## Grokbot Gate", "Only grokbot loads this skill.", "-d ~/.claude/skills/",
                "Every subagent call uses only `claude --dangerously-skip-permissions`", GROKBOT_RUNNER]
OTHER_RUNNERS = re.compile(r"codex -C|codex exec|grok --always-approve|run_cursor_agent|opencode run"
                           r"|openclaw .*agent --local|hermes chat|--permission-mode")

# Verbs bound to fixed subjects by the core lexicon.
FORBIDDEN = [
    (r"\b(workers?|candidates?|nested runs?|reviewers?|oracles?|loops?|looper)\s+(accepts?|rejects?)\b", "only the master accepts or rejects"),
    (r"\b(workers?|candidates?|nested runs?)\s+(judges?|leases?|retires?)\b", "workers submit; reviewers judge; looper leases"),
    (r"\b(master|masters)\s+(claims?|submits?)\b", "the master accepts, it does not claim or submit"),
    (r"\b(workers?|candidates?)\s+(writes?|marks?)\s+`?\[x\]", "only the master accepts"),
]

errors = []


def err(msg):
    errors.append(msg)


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        err(f"{path}: frontmatter must open on line 1")
        return {}
    block = text.split("---", 2)[1]
    try:
        import yaml  # optional: strict parse when available
        data = yaml.safe_load(block) or {}
    except ImportError:
        data = {}
        for line in block.strip().splitlines():
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip()
            if key.strip() == "description" and ": " in value:
                err(f"{path}: unquoted ': ' inside description breaks strict YAML parsers")
    except Exception as exc:  # yaml.YAMLError
        err(f"{path}: frontmatter is not valid YAML: {str(exc).splitlines()[0]}")
        return {}
    return data


def sentences(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    units, buf = [], []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", "|")):
            units.append(" ".join(buf)); buf = []
            continue
        item = re.match(r"^(?:[-*]|\d+\.)\s+(.*)$", s)
        if item:
            units.append(" ".join(buf)); buf = [item.group(1)]
        else:
            buf.append(s)
    units.append(" ".join(buf))
    out = []
    for unit in units:
        for s in re.split(r"(?<=[.!?])\s+", unit):
            s = s.strip().lower()
            if len(s.split()) >= 8:
                out.append(s)
    return out


def lint_grokbot():
    for skill in SKILLS:
        name = "grokbot-" + skill
        d = ROOT / "grokbot" / "skills" / name
        sk = d / "SKILL.md"
        if not sk.is_file():
            err(f"{name}: missing SKILL.md; run scripts/build_grokbot.py")
            continue
        text = sk.read_text(encoding="utf-8")
        fm = frontmatter(sk)
        if fm.get("name") != name:
            err(f"{name}: frontmatter name must be {name}")
        desc = str(fm.get("description", ""))
        if not desc.startswith("Grokbot only.") or len(desc) > MAX_DESCRIPTION:
            err(f"{name}: description must start with 'Grokbot only.' and fit {MAX_DESCRIPTION} chars (has {len(desc)})")
        if len(text) // 4 > MAX_TOKENS or text.count("\n") + 1 > MAX_LINES:
            err(f"{name}: SKILL.md exceeds the line or token budget")
        for needle in GROKBOT_GATE:
            if needle not in text:
                err(f"{name}: grokbot gate lacks '{needle}'")
        for ref in sorted(set(re.findall(r"`((?:references/[\w.-]+|loop)\.md)`", text))):
            if not (d / ref).is_file():
                err(f"{name}: SKILL.md cites missing {ref}")
        sub = d / "references" / "substrate-cron.md"
        m = OTHER_RUNNERS.search(sub.read_text(encoding="utf-8")) if sub.is_file() else None
        if not sub.is_file() or m:
            err(f"{name}: references/substrate-cron.md must name only the claude runtime ({m.group(0) if m else 'missing'})")
        for extra in ("agents/openai.yaml", "agents/cursor.yaml", "references/transport-codex-tui.md"):
            if (d / extra).exists():
                err(f"{name}: {extra} belongs to another host")


def main():
    core_src = ROOT / "core" / "core.md"
    sub_src = ROOT / "core" / "substrate-cron.md"
    loop_src = ROOT / "looper-cron-builder" / "loop.md"
    for p in (core_src, sub_src, loop_src):
        if not p.is_file():
            err(f"missing shared source {p.relative_to(ROOT)}")
    shared = set()
    for p in (core_src, loop_src):
        if p.is_file():
            shared |= set(sentences(p.read_text(encoding="utf-8")))

    for skill in SKILLS:
        d = ROOT / skill
        sk = d / "SKILL.md"
        if not sk.is_file():
            err(f"{skill}: missing SKILL.md")
            continue
        text = sk.read_text(encoding="utf-8")
        fm = frontmatter(sk)
        if fm.get("name") != skill:
            err(f"{skill}: frontmatter name must be {skill}")
        desc = str(fm.get("description", ""))
        if not desc or len(desc) > MAX_DESCRIPTION:
            err(f"{skill}: description must be 1-{MAX_DESCRIPTION} chars (has {len(desc)})")
        lines = text.count("\n") + 1
        tokens = len(text) // 4
        if lines > MAX_LINES:
            err(f"{skill}: SKILL.md has {lines} lines (max {MAX_LINES})")
        if tokens > MAX_TOKENS:
            err(f"{skill}: SKILL.md is ~{tokens} tokens (max {MAX_TOKENS})")
        if CORE_VERSION not in text or (LOOP_VERSION not in text):
            err(f"{skill}: SKILL.md must declare '{CORE_VERSION}' and '{LOOP_VERSION}'")

        for ref in sorted(set(re.findall(r"`((?:references/[\w.-]+|loop)\.md)`", text))):
            if ref == "SKILL.md":
                continue
            if not (d / ref).is_file():
                err(f"{skill}: SKILL.md cites missing {ref}")
        for md in [sk, *sorted((d / "references").glob("*.md"))]:
            if re.search(r"\]\(\.\./|`\.\./", md.read_text(encoding="utf-8")):
                err(f"{md.relative_to(ROOT)}: references must stay inside the skill (no ../)")

        refs = d / "references"
        for name, src in (("core.md", core_src), ("substrate-cron.md", sub_src)):
            copy = refs / name
            if not copy.is_file() or copy.read_bytes() != src.read_bytes():
                err(f"{skill}: references/{name} differs from core/{name}; run scripts/sync_core.sh")
        if skill != "looper-cron-builder":
            copy = refs / "loop.md"
            if not copy.is_file() or copy.read_bytes() != loop_src.read_bytes():
                err(f"{skill}: references/loop.md differs from looper-cron-builder/loop.md; run scripts/sync_loop.sh")

        body = text.split("---", 2)[2] if text.startswith("---") else text
        for pattern, why in FORBIDDEN:
            for m in re.finditer(pattern, body, flags=re.I):
                err(f"{skill}: lexicon violation '{m.group(0)}' ({why})")
        for s in sentences(body):
            if s in shared:
                err(f"{skill}: restates a core/loop sentence: '{s[:70]}...'")

    if (ROOT / "grokbot").is_dir():
        lint_grokbot()

    for p in (core_src, loop_src, ROOT / "core" / "grokbot-gate.md"):
        if p.is_file():
            body = p.read_text(encoding="utf-8")
            for pattern, why in FORBIDDEN:
                for m in re.finditer(pattern, body, flags=re.I):
                    err(f"{p.relative_to(ROOT)}: lexicon violation '{m.group(0)}' ({why})")

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print("Skill lint passed: frontmatter, budgets, one-level references, synced core and loop, lexicon, no restatement, grokbot gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
