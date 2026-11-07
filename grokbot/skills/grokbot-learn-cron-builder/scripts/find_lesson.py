#!/usr/bin/env python3
"""Bounded lookup over a lesson and incident ledger (canon/lessons.tsv).

search  : rank rows by query terms; return at most --limit summaries (id, kind, trigger).
show    : return one full row by id.
activate: exit 0 only if the id appears in the results for a use-site query.
check   : validate required fields per kind.
"""
import argparse
import csv
import json
import math
import pathlib
import re
import sys
from collections import Counter

FIELDS = ["id", "kind", "trigger", "evidence", "cause", "action", "validation",
          "stop", "limits", "governs", "applied", "helpful"]
REQUIRED = {
    "lesson": ["trigger", "action", "validation", "stop", "evidence"],
    "incident": ["trigger", "evidence", "cause", "action"],
}
APPLIED = {"", "applied", "not_applied", "refuted"}
HELPFUL = {"", "helpful", "harmful", "neutral", "unknown"}
TOKEN = re.compile(r"[A-Za-z0-9_./:-]+")


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def tokens(text):
    return [t.lower() for t in TOKEN.findall(text or "")]


def search(rows, query, limit):
    terms = tokens(query)
    if not terms:
        return []
    docs = [tokens(" ".join(r.get(f, "") for f in ("id", "trigger", "cause", "governs"))) for r in rows]
    df = Counter(t for d in docs for t in set(d))
    n, avg = len(docs), (sum(map(len, docs)) / max(1, len(docs)))
    scored = []
    for row, doc in zip(rows, docs):
        tf = Counter(doc)
        score = 0.0
        for t in terms:
            if t not in tf:
                continue
            idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
            score += idf * tf[t] * 2.2 / (tf[t] + 1.2 * (0.25 + 0.75 * len(doc) / avg))
        if row.get("id", "").lower() in terms:
            score += 100.0
        if score > 0:
            scored.append((score, row))
    scored.sort(key=lambda x: (-x[0], x[1].get("id", "")))
    return [{"id": r["id"], "kind": r.get("kind", ""), "trigger": r.get("trigger", "")[:160],
             "score": round(s, 3)} for s, r in scored[:limit]]


def check(rows):
    errors, seen = [], set()
    for i, r in enumerate(rows, 2):
        rid = r.get("id", "")
        if not rid:
            errors.append(f"line {i}: missing id")
            continue
        if rid in seen:
            errors.append(f"{rid}: duplicate id")
        seen.add(rid)
        kind = r.get("kind", "")
        if kind not in REQUIRED:
            errors.append(f"{rid}: kind must be lesson or incident")
            continue
        for f in REQUIRED[kind]:
            if not (r.get(f) or "").strip():
                errors.append(f"{rid}: {kind} needs {f}")
        if (r.get("applied") or "") not in APPLIED:
            errors.append(f"{rid}: applied must be one of {sorted(APPLIED - {''})}")
        if (r.get("helpful") or "") not in HELPFUL:
            errors.append(f"{rid}: helpful must be one of {sorted(HELPFUL - {''})}")
        if r.get("helpful") in {"helpful", "harmful"} and r.get("applied") != "applied":
            errors.append(f"{rid}: helpful/harmful needs applied=applied")
    return errors


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--ledger", default="canon/lessons.tsv")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--limit", type=int, default=20)
    sh = sub.add_parser("show"); sh.add_argument("id")
    a = sub.add_parser("activate"); a.add_argument("id"); a.add_argument("query"); a.add_argument("--limit", type=int, default=20)
    sub.add_parser("check")
    args = p.parse_args(argv)
    path = pathlib.Path(args.ledger)
    if not path.is_file():
        print(json.dumps({"error": f"ledger not found: {path}"}))
        return 2
    rows = load(path)
    if args.cmd == "search":
        print(json.dumps({"results": search(rows, args.query, min(args.limit, 20))}, ensure_ascii=False))
        return 0
    if args.cmd == "show":
        row = next((r for r in rows if r.get("id") == args.id), None)
        print(json.dumps(row or {"error": f"no row {args.id}"}, ensure_ascii=False))
        return 0 if row else 1
    if args.cmd == "activate":
        ids = [r["id"] for r in search(rows, args.query, args.limit)]
        hit = args.id in ids
        print(json.dumps({"id": args.id, "query": args.query, "activated": hit}))
        return 0 if hit else 1
    errors = check(rows)
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    if not errors:
        print(f"Ledger check passed for {len(rows)} row(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
