#!/usr/bin/env python3
"""Render read-only same-name *_Gantt.md companions for a b3ehive blueprint stack.

Never parsed back as authority (Law 1). Replaces each Gantt atomically.
"""
import argparse
import json
import pathlib
import sys
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import validate_blueprint_stack as vbs


def render_one(doc: dict) -> str:
    bpid = doc["blueprint_id"]
    items = doc["items"]
    done = sum(1 for it in items if it["mark"] == "x")
    sub = sum(1 for it in items if it["mark"] == "_")
    opened = sum(1 for it in items if it["mark"] == " ")
    gantt_rel = doc["entry"].get("gantt") or doc["meta"].get("same_name_gantt") or vbs.expected_gantt(doc["rel_path"])
    title = pathlib.PurePosixPath(gantt_rel).stem.replace("_Gantt", "")

    lines = [
        f"# {title} — Read-Only Gantt Projection",
        "",
        f"> **READ-ONLY PROJECTION** generated from `{doc['rel_path']}` (`blueprint_id: {bpid}`, `sha256: {doc['sha256'][:16]}`).",
        "> Do not edit manually or parse back as authority (b3ehive Law 1).",
        "",
        f"- Items: **{len(items)}** | Accepted `[x]`: **{done}** | Submitted `[_]`: **{sub}** | Open `[ ]`: **{opened}**",
        "",
        "| Layer | Mark | ID | Title | Budget | Depends On | Oracle |",
        "|:---:|:---:|:---:|---|:---:|---|---|",
    ]
    by_layer = defaultdict(list)
    for it in items:
        by_layer[it["fields"].get("layer", "L?")].append(it)
    for layer in sorted(by_layer):
        for it in by_layer[layer]:
            f = it["fields"]
            deps = f.get("depends_on", "—")
            lines.append(
                f"| `{layer}` | `[{it['mark']}]` | `{it['id']}` | {it['title']} | `{f.get('budget', '')}` | `{deps}` | `{f.get('oracle', '')}` |"
            )

    lines += ["", "```mermaid", "flowchart LR"]
    for it in items:
        nid = it["id"].replace("-", "_").replace(".", "_")
        lines.append(f'    {nid}["{it["id"]} [{it["mark"]}]"]')
    for it in items:
        nid = it["id"].replace("-", "_").replace(".", "_")
        for dep in vbs.parse_list(it["fields"].get("depends_on", "")):
            if "#" not in dep:
                did = dep.replace("-", "_").replace(".", "_")
                lines.append(f"    {did} --> {nid}")
    lines += ["```", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("manifest", help="Path to blueprint_stack.json")
    p.add_argument("--repo-root", help="Repository root (default: manifest directory)")
    p.add_argument("--check", action="store_true", help="Exit non-zero if any Gantt is missing or stale")
    args = p.parse_args(argv)

    mp = pathlib.Path(args.manifest).resolve()
    if not mp.is_file():
        print(f"ERROR: manifest not found: {mp}", file=sys.stderr)
        return 2
    repo_root = pathlib.Path(args.repo_root).resolve() if args.repo_root else mp.parent
    data = vbs.load_stack(mp, repo_root)
    if data["errors"]:
        for e in data["errors"]:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    stale, count = 0, 0
    for doc in data["parsed"]:
        gantt_cfg = doc["entry"].get("gantt") or doc["meta"].get("same_name_gantt")
        if gantt_cfg and "/" not in gantt_cfg:
            out_path = (repo_root / doc["rel_path"]).parent / gantt_cfg
        elif gantt_cfg:
            out_path = repo_root / gantt_cfg
        else:
            out_path = repo_root / vbs.expected_gantt(doc["rel_path"])

        rendered = render_one(doc)
        if args.check:
            if not out_path.is_file() or out_path.read_text(encoding="utf-8") != rendered:
                print(f"STALE: {out_path}", file=sys.stderr)
                stale += 1
        else:
            tmp = out_path.with_suffix(out_path.suffix + ".tmp")
            tmp.write_text(rendered, encoding="utf-8")
            tmp.replace(out_path)
            count += 1

    if args.check:
        if stale:
            return 1
        print(f"All {len(data['parsed'])} read-only Gantt projections are fresh.")
        return 0
    print(f"Rendered {count} read-only *_Gantt.md projection(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
