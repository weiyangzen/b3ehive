#!/usr/bin/env python3
"""Run a bounded b3ehive proposal competition and keep its ledger.

The script runs stages, records receipts, measures candidates with an optional
oracle, tallies votes, and merges findings. The calling agent decides the
question type, counts, oracle, and routes; the script never guesses them.
"""
import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

QUESTION_TYPES = ("precision", "coverage", "audit", "repair", "blueprint", "execution_choice")
UNION_TYPES = {"coverage", "audit"}
SHAPES = ("lanes", "three_way_challenge")
THREE_WAY_IDS = ["run_a", "run_b", "run_c"]
SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
FINDING_RE = re.compile(r"^\s*FINDING:\s*(.+)$", re.M)
VOTE_RE = re.compile(r"^\s*selected_candidate_id\s*:\s*([A-Za-z0-9_-]+)\s*$", re.M | re.I)
REVIEW_RE = re.compile(r"^\s*selected\s*:\s*([A-Z])\s*$", re.M)
SCORE_RE = re.compile(r"^\s*SCORE:\s*(-?[0-9]+(?:\.[0-9]+)?(?:[eE][-+]?[0-9]+)?)\s*$", re.M)
REGRESSED_RE = re.compile(r"^\s*REGRESSED:\s*(.+)$", re.M)
SUSPECT_RE = re.compile(r"^\s*SUSPECT:\s*(.+)$", re.M)
OBSERVED_RE = re.compile(r"^\s*OBSERVED_ONLY\b", re.M)


def read_text(path):
    try:
        return pathlib.Path(path).read_text(encoding="utf-8").strip()
    except (FileNotFoundError, IsADirectoryError):
        return ""


def write_text(path, text):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text((text or "").strip() + "\n", encoding="utf-8")


def write_json(path, data):
    write_text(path, json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))


def sha256(text):
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def truncate(text, max_bytes):
    data = (text or "").encode("utf-8", errors="replace")
    if max_bytes <= 0 or len(data) <= max_bytes:
        return text or ""
    return f"[output truncated to last {max_bytes} bytes]\n" + data[-max_bytes:].decode("utf-8", errors="replace")


def require_free_space(path, min_free_gb):
    if min_free_gb <= 0:
        return
    path = pathlib.Path(path)
    probe = path if path.exists() else path.parent
    while not probe.exists():
        probe = probe.parent
    free_gb = shutil.disk_usage(probe).free // (1024 ** 3)
    if free_gb < min_free_gb:
        raise RuntimeError(f"only {free_gb}GiB free at {probe}; need at least {min_free_gb}GiB")


# ---------------------------------------------------------------- planning

def candidate_paths(root, cid, layout):
    root = pathlib.Path(root)
    if layout == "old_three_way":
        d = root / cid / "implementation"
        names = {"result": "result.md", "verification": "verification.md",
                 "peer_review_round_1": "critique_round_1.md", "revision_round_1": "update_round_1.md",
                 "peer_review_round_2": "critique_round_2.md", "repair_synthesis": "final_repair.md"}
    else:
        d = root / cid
        names = {"result": "result.md", "verification": "verification.md",
                 "peer_review_round_1": "peer_review_round_1.md", "revision_round_1": "revision_round_1.md",
                 "peer_review_round_2": "peer_review_round_2.md", "repair_synthesis": "repair_synthesis.md"}
    paths = {key: d / name for key, name in names.items()}
    paths["dir"] = d
    paths["receipts"] = d / "receipts.jsonl"
    return paths


def build_plan(args):
    if args.shape == "three_way_challenge":
        ids, rounds, choose = THREE_WAY_IDS, 1, 1
    else:
        if args.proposal_count < 1:
            raise SystemExit("--proposal-count must be at least 1")
        ids = [f"proposal_{i:03d}" for i in range(1, args.proposal_count + 1)]
        rounds = args.rounds
        choose = args.choose_count
    union = args.question_type in UNION_TYPES or choose == "all-valid"
    if not union:
        choose = int(choose)
        if choose < 1:
            raise SystemExit("--choose-count must be at least 1 or all-valid")
    if args.handoff_mode == "looper_attempt" and not args.parent_lease_ref:
        raise SystemExit("--handoff-mode looper_attempt requires --parent-lease-ref")
    return {
        "competition_id": f"COMP-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "task": args.task.strip(),
        "question_type": args.question_type,
        "shape": args.shape,
        "selection": "union" if union else "rank",
        "choose_count": "all_valid" if union else choose,
        "rounds": rounds,
        "layout": args.artifact_layout,
        "candidates": [{"id": cid, "paths": candidate_paths(args.output, cid, args.artifact_layout), "failed": None}
                       for cid in ids],
    }


# ---------------------------------------------------------------- prompts

def header(plan, cand):
    return "\n".join([
        f"You are candidate {cand['id']} in a {plan['shape']} competition.",
        f"Question type: {plan['question_type']}.",
        f"Task: {plan['task']}",
        f"Write only inside {cand['paths']['dir']}.",
        "Be concrete and testable. Report facts, not forecasts.",
    ])


def finding_rule(plan):
    if plan["selection"] != "union":
        return ""
    return ("Report each finding on its own line as "
            "`FINDING: <location> | <claim> | <reproduction> | <severity>`; "
            "a finding without a reproduction is dropped.")


def current_text(cand):
    p = cand["paths"]
    return read_text(p["revision_round_1"]) or read_text(p["result"])


def peer_block(peers, key):
    return "\n\n".join(f"## {c['id']}\n{read_text(c['paths'][key]) or read_text(c['paths']['result']) or '(empty)'}"
                       for c in peers)


def stage_prompt(stage, plan, cand, peers, received=""):
    h = header(plan, cand)
    if stage == "proposal":
        return f"{h}\n\nStage: proposal. Return the result, its validation commands, risks, and next actions. {finding_rule(plan)}"
    if stage == "peer_review_round_1":
        return f"{h}\n\nStage: peer review. Critique correctness, missing tests, and integration risk.\n\n{peer_block(peers, 'result')}"
    if stage == "revision_round_1":
        return (f"{h}\n\nStage: revision. Return a full revised result. {finding_rule(plan)}\n\n"
                f"Your result:\n{read_text(cand['paths']['result'])}\n\nReviews received:\n{received or '(none)'}")
    if stage == "peer_review_round_2":
        return (f"{h}\n\nStage: second review and vote. Critique the revised peers, then end with one line "
                f"`selected_candidate_id: <id>` naming a peer. Votes for yourself are void.\n\n"
                f"{peer_block(peers, 'revision_round_1')}")
    if stage == "repair_synthesis":
        return (f"{h}\n\nStage: repair synthesis. Selected: {received}. List the issues found and the repairs "
                f"you own.\n\nYour result:\n{current_text(cand)}")
    raise ValueError(stage)


# ---------------------------------------------------------------- running

def run_command(template, values, max_mb, env=None):
    command = template.format(**values)
    done = subprocess.run(command, shell=True, text=True, capture_output=True,
                          env={**os.environ, **(env or {})})
    out = truncate(done.stdout.strip(), max_mb * 1024 * 1024)
    err = truncate(done.stderr.strip(), max_mb * 1024 * 1024)
    return done.returncode, out, err, command


def mock_output(plan, cand, stage, peers):
    ids = [c["id"] for c in plan["candidates"]]
    n = ids.index(cand["id"])
    text = f"{cand['id']} {stage} mock output"
    if stage in ("proposal", "revision_round_1") and plan["selection"] == "union":
        text += (f"\nFINDING: src/api.py:10 | missing input validation | pytest tests/test_api.py::test_bad_input | high"
                 f"\nFINDING: src/api.py:{20 + n} | unchecked error path {n} | pytest tests/test_api.py::test_err_{n} | medium")
    if stage == "peer_review_round_2" and peers:
        text += f"\nselected_candidate_id: {ids[(n + 1) % len(ids)]}"
    return text


def run_stage(args, plan, stage, out_key, cands, prompt_for):
    def one(cand):
        peers = [c for c in plan["candidates"] if c["id"] != cand["id"] and not c["failed"]]
        prompt = prompt_for(cand, peers)
        prompt_file = pathlib.Path(args.output) / "_prompts" / f"{cand['id']}_{stage}.md"
        write_text(prompt_file, prompt)
        out_file = cand["paths"][out_key]
        if args.runner == "mock":
            return cand, 0, mock_output(plan, cand, stage, peers), "", "mock"
        values = {"agent_id": cand["id"], "run_id": cand["id"], "candidate_id": cand["id"], "stage": stage,
                  "prompt_file": str(prompt_file), "output_file": str(out_file),
                  "candidate_dir": str(cand["paths"]["dir"]), "competition_id": plan["competition_id"],
                  "question_type": plan["question_type"], "selection_mode": plan["selection"]}
        code, out, err, cmd = run_command(args.command, values, args.max_output_mb)
        return cand, code, out, err, cmd

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(args.budget_workers, len(cands)))) as pool:
        for cand, code, out, err, cmd in pool.map(one, cands):
            receipt = {"stage": stage, "argv": cmd, "exit_code": code, "stdout_sha256": sha256(out),
                       "at": dt.datetime.now().isoformat(timespec="seconds")}
            with cand["paths"]["receipts"].open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(receipt) + "\n")
            if code != 0 or not out.strip():
                cand["failed"] = stage
                write_text(cand["paths"]["dir"] / f"failure_{stage}.md",
                           f"exit {code}\n\n{out}\n\nSTDERR:\n{err}".strip())
            else:
                write_text(cand["paths"][out_key], out)


def failed_text(plan):
    items = [c["id"] + "@" + c["failed"] for c in plan["candidates"] if c["failed"]]
    return ", ".join(items) or "none"


def live(plan):
    return [c for c in plan["candidates"] if not c["failed"]]


# ---------------------------------------------------------------- selection

def measure(args, plan, cand):
    """Run the oracle `--oracle-runs` times; every run must pass. Score is the worst run.

    `REGRESSED: <target>` lines mark a guard-set regression and fail the candidate.
    `OBSERVED_ONLY` marks evidence below declared fidelity: kept, never ranked.
    `SUSPECT: <reason>` records an integrity suspicion without disqualifying.
    """
    scores, passed, runs = [], True, []
    regressed, suspected, observed_only = [], [], False
    for run_index in range(args.oracle_runs):
        values = {"candidate_id": cand["id"], "candidate_dir": str(cand["paths"]["dir"]),
                  "result_file": str(cand["paths"]["revision_round_1"] if read_text(cand["paths"]["revision_round_1"])
                                     else cand["paths"]["result"]),
                  "run_index": run_index, "competition_id": plan["competition_id"]}
        env = {"B3_ORACLE_RUN": str(run_index),
               "B3_ORACLE_SEED": str(int(sha256(f"{plan['competition_id']}:{run_index}")[:8], 16))}
        code, out, err, cmd = run_command(args.oracle_command, values, args.max_output_mb, env)
        found = SCORE_RE.findall(out)
        runs.append({"run": run_index, "exit_code": code, "score": float(found[-1]) if found else None,
                     "stdout_sha256": sha256(out), "argv": cmd})
        regressed += REGRESSED_RE.findall(out)
        suspected += SUSPECT_RE.findall(out)
        observed_only = observed_only or bool(OBSERVED_RE.search(out))
        passed = passed and code == 0
        if found:
            scores.append(float(found[-1]))
    passed = passed and not regressed
    worst = None
    if scores:
        worst = min(scores) if args.oracle_direction == "max" else max(scores)
    return {"passed": passed, "score": worst, "runs": runs, "regressed": sorted(set(regressed)),
            "suspected": sorted(set(suspected)), "observed_only": observed_only}


def blind_review(args, plan, cands):
    ordered = sorted(cands, key=lambda c: sha256(plan["competition_id"] + c["id"]))
    letters = {chr(ord("A") + i): c["id"] for i, c in enumerate(ordered)}
    blocks = "\n\n".join(f"## {letter}\n{current_text(next(c for c in cands if c['id'] == cid))}"
                         for letter, cid in letters.items())
    prompt = (f"You did not write any candidate. Judge them blind for this task:\n{plan['task']}\n\n"
              f"Read the work, not its claims. End with one line `selected: <letter>`.\n\n{blocks}")
    prompt_file = pathlib.Path(args.output) / "_prompts" / "blind_review.md"
    write_text(prompt_file, prompt)
    code, out, _, _ = run_command(args.review_command, {"prompt_file": str(prompt_file),
                                                        "competition_id": plan["competition_id"]},
                                  args.max_output_mb)
    write_text(pathlib.Path(args.output) / "blind_review.md", out)
    found = REVIEW_RE.findall(out) if code == 0 else []
    return letters.get(found[-1]) if found else None


def tally_votes(plan):
    votes, void = {c["id"]: 0 for c in plan["candidates"]}, []
    for voter in plan["candidates"]:
        text = read_text(voter["paths"]["peer_review_round_2"])
        found = VOTE_RE.findall(text)
        if not found:
            continue
        choice = found[-1].lower()
        if choice == voter["id"] or choice not in votes:
            void.append({"voter": voter["id"], "choice": choice})
            continue
        votes[choice] += 1
    return votes, void


def rank(args, plan, cands):
    oracle = {c["id"]: measure(args, plan, c) for c in cands} if args.oracle_command else {}
    eligible = [c for c in cands if not oracle or (oracle[c["id"]]["passed"] and not oracle[c["id"]]["observed_only"])]
    observed = [c["id"] for c in cands if oracle and oracle[c["id"]]["observed_only"]]
    review_pick = blind_review(args, plan, eligible) if args.review_command and len(eligible) > 1 else None
    votes, void = tally_votes(plan)

    def key(c):
        score = (oracle.get(c["id"]) or {}).get("score")
        if score is None:
            oracle_key = 0.0
        else:
            oracle_key = -score if args.oracle_direction == "max" else score
        return (oracle_key, 0 if c["id"] == review_pick else 1, -votes.get(c["id"], 0), c["id"])

    ordered = sorted(eligible, key=key)
    return ordered[: plan["choose_count"]], {"oracle": oracle, "review_pick": review_pick,
                                             "votes": votes, "void_votes": void,
                                             "observed_only": observed,
                                             "suspected": {c["id"]: oracle[c["id"]]["suspected"]
                                                           for c in cands if oracle and oracle[c["id"]]["suspected"]}}


def norm(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def union(plan, cands):
    merged, dropped = {}, []
    for c in cands:
        for raw in FINDING_RE.findall(current_text(c)):
            parts = [p.strip() for p in raw.split("|")]
            if len(parts) < 3 or not parts[2]:
                dropped.append({"candidate": c["id"], "finding": raw, "reason": "no reproduction"})
                continue
            location, claim, repro = parts[:3]
            severity = parts[3].lower() if len(parts) > 3 and parts[3] else "medium"
            k = (norm(location), norm(claim))
            entry = merged.setdefault(k, {"location": location, "claim": claim, "reproduction": repro,
                                          "severity": severity, "sources": []})
            entry["sources"].append(c["id"])
            if SEVERITY_RANK.get(severity, 9) < SEVERITY_RANK.get(entry["severity"], 9):
                entry["severity"] = severity
    findings = list(merged.values())
    if plan["question_type"] == "audit":
        findings.sort(key=lambda f: (SEVERITY_RANK.get(f["severity"], 9), f["location"]))
    contributors = sorted({s for f in findings for s in f["sources"]}) or [c["id"] for c in cands]
    return findings, dropped, contributors


# ---------------------------------------------------------------- main flow

def write_manifest(args, plan, selection=None, extra=None):
    write_json(pathlib.Path(args.output) / "compete_manifest.json", {
        "schema_version": "b3ehive.compete.v2",
        "competition_id": plan["competition_id"],
        "task": plan["task"],
        "question_type": plan["question_type"],
        "competition_shape": plan["shape"],
        "selection_mode": plan["selection"],
        "artifact_layout": plan["layout"],
        "choose_count": plan["choose_count"],
        "rounds": plan["rounds"],
        "candidate_ids": [c["id"] for c in plan["candidates"]],
        "failed": {c["id"]: c["failed"] for c in plan["candidates"] if c["failed"]},
        "oracle": {"command": args.oracle_command or None, "runs": args.oracle_runs,
                   "direction": args.oracle_direction},
        "blind_review": bool(args.review_command),
        "selected_ids": selection or [],
        "handoff": {"mode": args.handoff_mode, "source_item_id": args.source_item_id or None,
                    "source_loop_id": args.source_loop_id or None,
                    "parent_lease_ref": args.parent_lease_ref or None, "state": "[_]"},
        **(extra or {}),
    })


def orchestrate(args):
    out = pathlib.Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    require_free_space(out, args.min_free_gb)
    plan = build_plan(args)
    for c in plan["candidates"]:
        c["paths"]["dir"].mkdir(parents=True, exist_ok=True)
    decide = [f"DECIDE question_type={plan['question_type']} because {args.why or 'caller supplied'}",
              f"DECIDE shape={plan['shape']} candidates={len(plan['candidates'])} choose={plan['choose_count']} rounds={plan['rounds']}",
              f"DECIDE oracle={'command' if args.oracle_command else 'none'} runs={args.oracle_runs} review={'blind' if args.review_command else 'none'}"]
    write_text(out / "decisions.log", "\n".join(decide))
    write_text(out / "classification.md",
               f"# Classification\n\nQuestion type: {plan['question_type']}\nCompetition shape: {plan['shape']}\n"
               f"Selection mode: {plan['selection']}")
    write_manifest(args, plan)

    run_stage(args, plan, "proposal", "result", plan["candidates"],
              lambda c, peers: stage_prompt("proposal", plan, c, peers))
    if not live(plan):
        write_text(out / "summary.md", "# Compete Failed\n\nNo candidate produced a valid proposal.")
        write_manifest(args, plan)
        raise RuntimeError("no valid candidate proposals")

    for c in plan["candidates"]:
        write_text(c["paths"]["verification"], "Measured by the oracle at selection." if args.oracle_command
                   else "No oracle supplied; selection uses blind review and votes.")
    write_text(out / "verification.md", read_text(plan["candidates"][0]["paths"]["verification"]))

    if plan["rounds"] >= 1:
        run_stage(args, plan, "peer_review_round_1", "peer_review_round_1", live(plan),
                  lambda c, peers: stage_prompt("peer_review_round_1", plan, c, peers))
        reviews = {c["id"]: read_text(c["paths"]["peer_review_round_1"]) for c in plan["candidates"]}
        run_stage(args, plan, "revision_round_1", "revision_round_1", live(plan),
                  lambda c, peers: stage_prompt("revision_round_1", plan, c, peers,
                                                "\n\n".join(t for i, t in reviews.items() if i != c["id"] and t)))
        if plan["selection"] == "rank":
            run_stage(args, plan, "peer_review_round_2", "peer_review_round_2", live(plan),
                      lambda c, peers: stage_prompt("peer_review_round_2", plan, c, peers))
    if not live(plan):
        write_text(out / "summary.md", "# Compete Failed\n\nEvery candidate failed a later stage.")
        write_manifest(args, plan)
        raise RuntimeError("no candidate survived the review stages")

    extra = {}
    if plan["selection"] == "union":
        findings, dropped, selected_ids = union(plan, live(plan))
        lines = [f"- [{f['severity']}] {f['location']}: {f['claim']} (repro: `{f['reproduction']}`; "
                 f"from {', '.join(f['sources'])})" for f in findings]
        write_text(out / "synthesis.md", "# Coverage Union\n\n" + ("\n".join(lines) or "No findings."))
        write_json(out / "findings.json", {"findings": findings, "dropped": dropped})
        extra = {"findings": len(findings), "dropped_findings": len(dropped)}
    else:
        chosen, evidence = rank(args, plan, live(plan))
        selected_ids = [c["id"] for c in chosen]
        write_json(out / "selection_evidence.json", evidence)
        extra = {"review_pick": evidence["review_pick"], "votes": evidence["votes"],
                 "void_votes": evidence["void_votes"], "observed_only": evidence["observed_only"],
                 "suspected": evidence["suspected"]}
        if not selected_ids:
            write_text(out / "summary.md", "# Compete Failed\n\nNo candidate passed the oracle.")
            write_manifest(args, plan, [], extra)
            raise RuntimeError("no candidate passed the oracle")
        write_text(out / "synthesis.md", "# Selection\n\n" + "\n".join(f"- {i}" for i in selected_ids))

    write_json(out / "selected.json", {"selected_ids": selected_ids})
    write_json(out / "rejected.json", {"rejected_ids": [c["id"] for c in plan["candidates"]
                                                        if c["id"] not in selected_ids]})
    write_text(out / "best_run.txt", selected_ids[0])

    run_stage(args, plan, "repair_synthesis", "repair_synthesis", live(plan),
              lambda c, peers: stage_prompt("repair_synthesis", plan, c, peers, ", ".join(selected_ids)))
    write_text(out / "final_repairs.md", "# Final Repair Assignments\n\n" + "\n\n".join(
        f"## {c['id']}\n{read_text(c['paths']['repair_synthesis']) or '(none)'}" for c in plan["candidates"]))
    write_text(out / "summary.md",
               f"# Compete Summary\n\nTask: {plan['task']}\nQuestion type: {plan['question_type']}\n"
               f"Shape: {plan['shape']}\nSelected: {', '.join(selected_ids)}\n"
               f"Failed: {failed_text(plan)}\n"
               f"State: [_] (the master accepts)")
    write_manifest(args, plan, selected_ids, extra)
    return out, selected_ids


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Run a bounded b3ehive proposal competition.")
    p.add_argument("--task", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--question-type", required=True, choices=QUESTION_TYPES,
                   help="Decided by the calling agent; the script never infers it.")
    p.add_argument("--why", default="", help="Reason recorded in the DECIDE line.")
    p.add_argument("--shape", choices=SHAPES, default="lanes")
    p.add_argument("--competition-shape", dest="shape", choices=SHAPES, help=argparse.SUPPRESS)
    p.add_argument("--proposal-count", type=int, default=3)
    p.add_argument("--choose-count", default="1", help="Integer or all-valid.")
    p.add_argument("--rounds", type=int, choices=(0, 1), default=1)
    p.add_argument("--budget-workers", type=int, default=3)
    p.add_argument("--artifact-layout", choices=("native", "old_three_way"), default="native")
    p.add_argument("--runner", choices=("mock", "command"), default="command")
    p.add_argument("--command", default=os.environ.get("B3EHIVE_AGENT_RUNNER", ""))
    p.add_argument("--oracle-command", default="")
    p.add_argument("--oracle-runs", type=int, default=1)
    p.add_argument("--oracle-direction", choices=("max", "min"), default="max")
    p.add_argument("--review-command", default="")
    p.add_argument("--max-output-mb", type=int, default=20)
    p.add_argument("--min-free-gb", type=int, default=int(os.environ.get("MIN_FREE_GB", "5")))
    p.add_argument("--handoff-mode", choices=("standalone", "execution_embed", "looper_attempt"), default="standalone")
    p.add_argument("--source-item-id", default="")
    p.add_argument("--source-loop-id", default="")
    p.add_argument("--parent-lease-ref", default="")
    args = p.parse_args(argv)
    if args.runner == "command" and not args.command:
        p.error("--runner command needs --command or B3EHIVE_AGENT_RUNNER; use --runner mock for a dry run")
    if args.oracle_runs < 1:
        p.error("--oracle-runs must be at least 1")
    return args


def main(argv=None):
    args = parse_args(argv)
    try:
        out, selected = orchestrate(args)
    except RuntimeError as exc:
        print(f"Compete failed: {exc}", file=sys.stderr)
        return 3
    print(f"Selected: {', '.join(selected)}")
    print(f"Output: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
