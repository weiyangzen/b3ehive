#!/usr/bin/env python3
"""Minimal validator and IR exporter for multi-layer b3ehive blueprint stacks.

Subcommands:
  stack       Check global acyclicity, local layer order, prefix-aware path
              non-interference (dag_ordered or strict_disjoint), transitive [x]
              closure, leaf/platform edge boundaries, and mandatory deps.
  boundaries  Check stack invariants plus Rule-of-Two capability duplication
              and source-level zero sibling / zero reverse imports.
  export-ir   Emit deterministic JSON IR (+ topo_witness) for formal verifiers.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import sys
from collections import defaultdict, deque

VALID_ROLES = ("master", "platform", "leaf")
VALID_MARKS = (" ", "_", "x")
ITEM_RE = re.compile(r"^- \[(.)\] \[([A-Za-z0-9._-]+)\] (.+)$")
FIELD_RE = re.compile(r"^  - ([a-z_]+): (.+)$")
DEFAULT_EXTS = (".py", ".go", ".rs", ".ts", ".js", ".cs", ".cpp", ".c", ".h", ".java", ".kt", ".swift")
DEFAULT_IGNORE = (".git", "node_modules", "__pycache__", "target", "dist", "build")


def norm_path(raw: str) -> str:
    p = raw.strip().replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return re.sub(r"/+", "/", p).rstrip("/")


def expected_gantt(bp_path: str) -> str:
    p = pathlib.PurePosixPath(bp_path.replace("\\", "/"))
    stem = p.stem[:-9] + "Gantt" if p.stem.endswith("Blueprint") else p.stem + "_Gantt"
    parent = "" if str(p.parent) == "." else str(p.parent) + "/"
    return f"{parent}{stem}{p.suffix}"


def parse_list(raw: str) -> list:
    s = raw.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    return [tok.strip() for tok in s.split(",") if tok.strip()]


def parse_blueprint(path: pathlib.Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    meta = {}
    ym = re.search(r"```yaml\n(.*?)\n```", raw, re.S)
    if ym:
        for line in ym.group(1).splitlines():
            s = line.strip()
            if s and not s.startswith("#") and ":" in s:
                k, _, v = s.partition(":")
                meta[k.strip()] = v.strip().strip("'\"")
    items, cur = [], None
    for line in raw.splitlines():
        im = ITEM_RE.match(line)
        if im:
            if cur is not None:
                items.append(cur)
            cur = {"mark": im.group(1), "id": im.group(2), "title": im.group(3).strip(), "fields": {}}
        elif cur is not None:
            fm = FIELD_RE.match(line)
            if fm:
                cur["fields"][fm.group(1)] = fm.group(2).strip()
            elif line.startswith("#"):
                items.append(cur)
                cur = None
    if cur is not None:
        items.append(cur)
    return {
        "raw": raw,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "meta": meta,
        "items": items,
    }


def load_stack(manifest_path: pathlib.Path, repo_root: pathlib.Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    layers = manifest.get("layers", [])
    layer_rank = {name: i for i, name in enumerate(layers)}
    loc_cap = int(manifest.get("default_budget_loc_cap", 5000))
    path_policy = manifest.get("owned_paths_policy", "dag_ordered")
    if path_policy not in ("dag_ordered", "strict_disjoint"):
        errors.append(f"invalid owned_paths_policy '{path_policy}'")
        path_policy = "dag_ordered"

    bp_by_id, parsed = {}, []
    for entry in manifest.get("blueprints", []):
        bpid, role, rel = entry.get("blueprint_id", ""), entry.get("role", ""), entry.get("path", "")
        if not bpid or bpid in bp_by_id:
            errors.append(f"missing or duplicate blueprint_id '{bpid}'")
            continue
        if role not in VALID_ROLES:
            errors.append(f"{bpid}: invalid role '{role}'")
        fp = repo_root / rel
        if not fp.is_file():
            errors.append(f"{bpid}: missing file '{rel}'")
            continue
        doc = parse_blueprint(fp)
        doc.update({"blueprint_id": bpid, "role": role, "rel_path": rel.replace("\\", "/"), "entry": entry})
        if doc["meta"].get("blueprint_id") and doc["meta"]["blueprint_id"] != bpid:
            errors.append(f"{bpid}: YAML blueprint_id mismatch")
        gantt = entry.get("gantt") or doc["meta"].get("same_name_gantt")
        if gantt:
            want = expected_gantt(doc["rel_path"])
            got = gantt.replace("\\", "/")
            if "/" not in got:
                want = pathlib.PurePosixPath(want).name
            if got != want:
                errors.append(f"{bpid}: same-name Gantt '{got}' != '{want}'")
        bp_by_id[bpid] = doc
        parsed.append(doc)
    if not parsed:
        errors.append("stack manifest defines no valid blueprints")

    all_nodes, global_ids, owned_records = {}, {}, []
    for doc in parsed:
        bpid = doc["blueprint_id"]
        pat_str = doc["entry"].get("stable_id_pattern") or doc["meta"].get("stable_id_pattern")
        pat = re.compile(pat_str) if pat_str else None
        for it in doc["items"]:
            iid, f = it["id"], it["fields"]
            if it["mark"] not in VALID_MARKS:
                errors.append(f"{bpid}#{iid}: invalid state mark '[{it['mark']}]'")
            if pat and not pat.match(iid):
                errors.append(f"{bpid}#{iid}: violates stable_id_pattern '{pat_str}'")
            if iid in global_ids:
                errors.append(f"{bpid}#{iid}: duplicate global item ID (also in {global_ids[iid]})")
            global_ids[iid] = bpid
            all_nodes[(bpid, iid)] = (doc, it)
            for req in ("oracle", "owned_paths"):
                if not f.get(req):
                    errors.append(f"{bpid}#{iid}: missing required field '{req}'")
            if layers and f.get("layer", "") not in layer_rank:
                errors.append(f"{bpid}#{iid}: missing or unknown layer '{f.get('layer', '')}'")
            if f.get("budget"):
                bm = re.match(r"^loc<(\d+)$", f["budget"])
                if not bm or int(bm.group(1)) > loc_cap:
                    errors.append(f"{bpid}#{iid}: invalid or >loc<{loc_cap} budget '{f['budget']}'")
            for p in parse_list(f.get("owned_paths", "")):
                np = norm_path(p)
                if not np:
                    continue
                if np.startswith("/") or np == ".." or np.startswith("../") or "/../" in np:
                    errors.append(f"{bpid}#{iid}: owned_paths must be repo-relative: '{p}'")
                else:
                    owned_records.append((np, bpid, iid))

    adj, indeg, edges, bp_cross_deps = defaultdict(list), {n: 0 for n in all_nodes}, [], defaultdict(set)
    for (bpid, iid), (doc, it) in all_nodes.items():
        src_role, src_layer = doc["role"], it["fields"].get("layer", "")
        is_harvest = it["fields"].get("harvest", "").lower() == "true"
        for dep in parse_list(it["fields"].get("depends_on", "")):
            if "#" in dep:
                ref_bp, ref_id = dep.split("#", 1)
                target = (ref_bp, ref_id)
                if target not in all_nodes:
                    errors.append(f"{bpid}#{iid}: broken cross-blueprint dependency '{dep}'")
                    continue
                bp_cross_deps[bpid].add(dep)
                dep_role = all_nodes[target][0]["role"]
                if src_role == "leaf" and dep_role == "leaf" and bpid != ref_bp:
                    errors.append(f"{bpid}#{iid}: forbidden leaf-to-leaf dependency '{dep}'")
                if src_role == "platform" and dep_role == "leaf" and not is_harvest:
                    errors.append(f"{bpid}#{iid}: forbidden platform-to-leaf dependency '{dep}' (requires harvest: true)")
                kind = "harvest" if is_harvest and dep_role == "leaf" else "cross"
            else:
                target = (bpid, dep)
                if target not in all_nodes:
                    errors.append(f"{bpid}#{iid}: missing local dependency '{dep}'")
                    continue
                dep_layer = all_nodes[target][1]["fields"].get("layer", "")
                if layers and src_layer in layer_rank and dep_layer in layer_rank and layer_rank[dep_layer] > layer_rank[src_layer]:
                    errors.append(f"{bpid}#{iid}: local layer inversion ({dep_layer} > {src_layer})")
                kind = "local"
            dep_it = all_nodes[target][1]
            if it["mark"] == "x" and dep_it["mark"] != "x":
                errors.append(f"{bpid}#{iid}: accepted [x] depends on unaccepted '{dep}' ([{dep_it['mark']}])")
            adj[target].append((bpid, iid))
            indeg[(bpid, iid)] += 1
            edges.append((target, (bpid, iid), kind))

    mand_deps = manifest.get("mandatory_leaf_deps", [])
    mand_refs = manifest.get("mandatory_leaf_refs", [])
    for doc in parsed:
        if doc["role"] != "leaf":
            continue
        bpid = doc["blueprint_id"]
        for mdep in mand_deps:
            if mdep not in bp_cross_deps[bpid]:
                errors.append(f"{bpid}: missing mandatory leaf dependency '{mdep}'")
        for mref in mand_refs:
            if mref not in doc["raw"]:
                errors.append(f"{bpid}: missing mandatory leaf reference '{mref}'")

    # Kahn topological sort (deterministic witness for Lean / CI).
    q = deque(sorted(n for n, d in indeg.items() if d == 0))
    indeg_work, topo = dict(indeg), []
    while q:
        u = q.popleft()
        topo.append(u)
        for v in sorted(adj[u]):
            indeg_work[v] -= 1
            if indeg_work[v] == 0:
                q.append(v)
    acyclic = len(topo) == len(all_nodes)
    if not acyclic:
        stuck = sorted(f"{b}#{i}" for (b, i), d in indeg_work.items() if d > 0)
        errors.append(f"global cross-blueprint DAG cycle involving {len(stuck)} node(s): {', '.join(stuck[:10])}")

    # O(N log N) segment-trie prefix overlap check.
    ancestors = None
    if path_policy == "dag_ordered" and acyclic:
        idx = {n: i for i, n in enumerate(topo)}
        mask = {n: 0 for n in topo}
        for u in topo:
            reach = mask[u] | (1 << idx[u])
            for v in adj[u]:
                mask[v] |= reach
        ancestors = (idx, mask)

    def ordered(a, b) -> bool:
        if not ancestors:
            return False
        idx, mask = ancestors
        return bool((mask[b] & (1 << idx[a])) or (mask[a] & (1 << idx[b])))

    active = []
    for np, bpid, iid in sorted(owned_records, key=lambda r: (tuple(r[0].split("/")), r[1], r[2])):
        segs = tuple(np.split("/"))
        while active and active[-1][0] != segs[: len(active[-1][0])]:
            active.pop()
        for _, prev_p, prev_bp, prev_id in active:
            if (prev_bp, prev_id) == (bpid, iid):
                continue
            if path_policy == "dag_ordered" and ordered((prev_bp, prev_id), (bpid, iid)):
                continue
            label = "concurrent owned_paths overlap" if path_policy == "dag_ordered" else "owned_paths overlap"
            errors.append(f"{label}: {prev_bp}#{prev_id} ('{prev_p}') overlaps {bpid}#{iid} ('{np}')")
        active.append((segs, np, bpid, iid))

    return {
        "manifest": manifest,
        "parsed": parsed,
        "all_nodes": all_nodes,
        "edges": edges,
        "topo": topo if acyclic else [],
        "errors": errors,
    }


def check_boundaries(stack_data: dict, repo_root: pathlib.Path) -> list:
    errors = []
    manifest = stack_data["manifest"]
    promoted = set(manifest.get("promoted_capabilities", []))
    leaf_caps = defaultdict(set)
    for (bpid, _), (doc, it) in stack_data["all_nodes"].items():
        caps = parse_list(it["fields"].get("capability", ""))
        if doc["role"] == "platform":
            promoted.update(caps)
        elif doc["role"] == "leaf":
            for c in caps:
                leaf_caps[c].add(bpid)
    for cap, owners in sorted(leaf_caps.items()):
        if len(owners) >= 2 and cap not in promoted:
            errors.append(
                f"Rule-of-Two: capability '{cap}' claimed by leaves {sorted(owners)} without a platform item or promoted_capabilities entry"
            )

    b = manifest.get("boundaries", {})
    platform_root = norm_path(b.get("platform_root", ""))
    leaf_roots = {k: norm_path(v) for k, v in b.get("leaf_roots", {}).items() if norm_path(v)}
    exts = tuple(b.get("code_extensions", DEFAULT_EXTS))
    ignore = set(b.get("ignore_dirs", DEFAULT_IGNORE))

    def scan_dir(base: pathlib.Path, forbidden: list, kind: str):
        if not base.is_dir():
            return
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in ignore and not os.path.islink(os.path.join(root, d))]
            for fn in files:
                if not fn.endswith(exts):
                    continue
                fp = pathlib.Path(root) / fn
                txt = fp.read_text(encoding="utf-8", errors="ignore")
                for label, token in forbidden:
                    if token in txt:
                        errors.append(f"{kind}: '{fp.relative_to(repo_root).as_posix()}' references '{label}' ('{token}')")

    for lid, lrel in sorted(leaf_roots.items()):
        siblings = [(oid, orel) for oid, orel in sorted(leaf_roots.items()) if oid != lid]
        scan_dir(repo_root / lrel, siblings, "sibling leakage")
    if platform_root and leaf_roots:
        scan_dir(repo_root / platform_root, sorted(leaf_roots.items()), "reverse dependency")
    return errors


def build_ir(stack_data: dict) -> dict:
    m = stack_data["manifest"]
    nodes = []
    for bpid, iid in sorted(stack_data["all_nodes"]):
        doc, it = stack_data["all_nodes"][(bpid, iid)]
        f = it["fields"]
        bm = re.match(r"^loc<(\d+)$", f.get("budget", ""))
        nodes.append(
            {
                "blueprint_id": bpid,
                "item_id": iid,
                "role": doc["role"],
                "state": {" ": "open", "_": "submitted", "x": "accepted"}.get(it["mark"], "unknown"),
                "layer": f.get("layer", ""),
                "budget_loc": int(bm.group(1)) if bm else None,
                "has_oracle": bool(f.get("oracle")),
                "harvest": f.get("harvest", "").lower() == "true",
                "owned_paths": [norm_path(p).split("/") for p in parse_list(f.get("owned_paths", "")) if norm_path(p)],
                "capabilities": parse_list(f.get("capability", "")),
            }
        )
    edges = sorted(
        [{"from": f"{u[0]}#{u[1]}", "to": f"{v[0]}#{v[1]}", "kind": k} for u, v, k in stack_data["edges"]],
        key=lambda e: (e["from"], e["to"], e["kind"]),
    )
    return {
        "schema_version": "b3ehive-stack-ir/v1",
        "stack_id": m.get("stack_id", ""),
        "owned_paths_policy": m.get("owned_paths_policy", "dag_ordered"),
        "default_budget_loc_cap": int(m.get("default_budget_loc_cap", 5000)),
        "layers": m.get("layers", []),
        "mandatory_leaf_deps": m.get("mandatory_leaf_deps", []),
        "promoted_capabilities": sorted(m.get("promoted_capabilities", [])),
        "blueprints": [
            {"blueprint_id": d["blueprint_id"], "role": d["role"], "path": d["rel_path"], "sha256": d["sha256"]}
            for d in sorted(stack_data["parsed"], key=lambda x: x["blueprint_id"])
        ],
        "nodes": nodes,
        "edges": edges,
        "topo_witness": [f"{b}#{i}" for b, i in stack_data["topo"]],
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("stack", "boundaries", "export-ir"):
        sp = sub.add_parser(name)
        sp.add_argument("manifest", help="Path to blueprint_stack.json")
        sp.add_argument("--repo-root", help="Repository root (default: manifest directory)")
        if name == "export-ir":
            sp.add_argument("-o", "--output", help="Output JSON path (default: stdout)")

    args = p.parse_args(argv)
    mp = pathlib.Path(args.manifest).resolve()
    if not mp.is_file():
        print(f"ERROR: manifest not found: {mp}", file=sys.stderr)
        return 2
    repo_root = pathlib.Path(args.repo_root).resolve() if args.repo_root else mp.parent
    data = load_stack(mp, repo_root)

    errs = list(data["errors"])
    if args.cmd == "boundaries":
        errs.extend(check_boundaries(data, repo_root))
    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.cmd == "export-ir":
        payload = json.dumps(build_ir(data), indent=2, sort_keys=True) + "\n"
        if args.output:
            pathlib.Path(args.output).write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        return 0

    print(
        f"{args.cmd.title()} validation passed: {len(data['parsed'])} blueprints, "
        f"{len(data['all_nodes'])} items, {len(data['edges'])} edges."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
