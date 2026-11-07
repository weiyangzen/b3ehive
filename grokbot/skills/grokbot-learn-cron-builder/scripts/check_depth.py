#!/usr/bin/env python3
"""Check learn notes against a learn_depth level (what, how, why).

how: a `## How` section whose bullets each cite evidence.
why: a `## Why` section whose `###` entries each carry driver, alternatives,
tradeoff, significance, and level (V with a citation, or I).
A depth map (TSV: glob<TAB>depth) overrides the default per path.
"""
import argparse
import fnmatch
import pathlib
import re
import sys

LEVELS = {"what": 0, "how": 1, "why": 2}
NOTE_SUFFIXES = ("_learn.md", "_rationale.md")
FIELDS = ("driver", "alternatives", "tradeoff", "significance", "level")


def sections(text):
    parts, current = {}, None
    for line in text.splitlines():
        m = re.match(r"^## (\S.*?)\s*$", line)
        if m:
            current = m.group(1).strip().lower()
            parts[current] = []
        elif current:
            parts[current].append(line)
    return parts


def check_how(lines):
    errs = []
    bullets = [l for l in lines if re.match(r"^\s*-\s+\S", l)]
    if not bullets:
        errs.append("How has no principles")
    for b in bullets:
        if not re.search(r"evidence:\s*\S", b):
            errs.append(f"How line lacks evidence: {b.strip()[:60]}")
    return errs


def check_why(lines):
    errs, entries, current = [], [], None
    for line in lines:
        m = re.match(r"^###\s+(.+)$", line)
        if m:
            current = {"title": m.group(1).strip(), "fields": {}}
            entries.append(current)
            continue
        f = re.match(r"^\s*-\s*(driver|alternatives|tradeoff|significance|level)\s*:\s*(.*)$", line, re.I)
        if f and current is not None:
            current["fields"][f.group(1).lower()] = f.group(2).strip()
    if not entries:
        errs.append("Why has no decision entries")
    for e in entries:
        for field in FIELDS:
            if not e["fields"].get(field):
                errs.append(f"Why '{e['title'][:40]}' lacks {field}")
        level = e["fields"].get("level", "")
        if level and not re.match(r"^[VI]\b", level):
            errs.append(f"Why '{e['title'][:40]}' level must start with V or I")
        if level.startswith("V") and not re.search(r"[`(]", level):
            errs.append(f"Why '{e['title'][:40]}' level V needs a citation")
    return errs


def load_map(path):
    rules = []
    if path:
        for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                glob, depth = line.split("\t")[:2]
                rules.append((glob.strip(), depth.strip()))
    return rules


def depth_for(rel, default, rules):
    depth = default
    for glob, d in rules:
        if fnmatch.fnmatch(rel, glob):
            depth = d
    return depth


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--depth", choices=LEVELS, default="what")
    p.add_argument("--map", help="TSV of glob<TAB>depth, matched against paths relative to each root")
    p.add_argument("roots", nargs="+")
    args = p.parse_args(argv)
    rules = load_map(args.map)
    errors, checked = [], 0
    for root in map(pathlib.Path, args.roots):
        files = [root] if root.is_file() else sorted(f for f in root.rglob("*.md") if f.name.endswith(NOTE_SUFFIXES))
        for f in files:
            rel = str(f.relative_to(root)) if root.is_dir() else f.name
            depth = depth_for(rel, args.depth, rules)
            if depth not in LEVELS:
                errors.append(f"{rel}: unknown depth {depth}")
                continue
            checked += 1
            parts = sections(f.read_text(encoding="utf-8"))
            if LEVELS[depth] >= 1:
                for name in ("what", "how"):
                    if name not in parts:
                        errors.append(f"{f}: missing '## {name.title()}' for depth {depth}")
                if "how" in parts:
                    errors += [f"{f}: {e}" for e in check_how(parts["how"])]
            if LEVELS[depth] >= 2:
                if "why" not in parts:
                    errors.append(f"{f}: missing '## Why' for depth why")
                else:
                    errors += [f"{f}: {e}" for e in check_why(parts["why"])]
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    if not errors:
        print(f"Depth check passed for {checked} note(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
