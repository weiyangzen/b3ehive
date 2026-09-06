#!/usr/bin/env python3
import argparse
import concurrent.futures
import datetime as dt
import json
import pathlib
import re
import shutil
import subprocess

QUESTION_TYPES = {
    "auto",
    "precision",
    "coverage",
    "audit",
    "blueprint",
    "seo",
    "execution_choice",
    "repair",
}

COMPETITION_SHAPES = {
    "auto",
    "three_way_challenge",
    "parallel_proposals",
    "coverage_sweep",
    "repair_search",
    "top_k_synthesis",
}

SELECTION_MODES = {
    "auto",
    "best_one",
    "top_k",
    "coverage_union",
    "risk_union",
    "vote_then_tiebreak",
    "repair_queue",
}

OLD_THREE_WAY_IDS = ["run_a", "run_b", "run_c"]


def read_text(path):
    try:
        return pathlib.Path(path).read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def write_text(path, text):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text((text or "").strip() + "\n", encoding="utf-8")


def write_json(path, data):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def truncate_text(text, max_bytes):
    if max_bytes <= 0:
        return text or ""
    data = (text or "").encode("utf-8", errors="replace")
    if len(data) <= max_bytes:
        return text or ""
    marker = f"[output truncated to last {max_bytes} bytes]\n"
    tail = data[-max_bytes:]
    return marker + tail.decode("utf-8", errors="replace")


def ensure_output_budget(output, max_mb):
    if max_mb <= 0:
        return
    output = pathlib.Path(output)
    if not output.exists():
        return
    max_bytes = max_mb * 1024 * 1024
    for path in output.rglob("*"):
        if not path.is_file():
            continue
        try:
            if path.stat().st_size <= max_bytes:
                continue
            data = path.read_bytes()[-max_bytes:]
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_bytes(f"[file truncated to last {max_bytes} bytes]\n".encode("utf-8") + data)
            tmp.replace(path)
        except OSError:
            continue


def require_free_space(path, min_free_gb):
    if min_free_gb <= 0:
        return
    usage = shutil.disk_usage(path)
    free_gb = usage.free // (1024**3)
    if free_gb < min_free_gb:
        raise RuntimeError(f"only {free_gb}GiB free at {path}; need at least {min_free_gb}GiB")


def classify_question(task, requested):
    if requested != "auto":
        return requested
    task_l = task.lower()
    if any(word in task_l for word in ["security", "performance", "coverage", "audit", "release", "no omissions"]):
        return "audit" if "audit" in task_l or "release" in task_l else "coverage"
    if any(word in task_l for word in ["repair", "failure", "failed", "fix", "lint", "test failed", "merge conflict"]):
        return "repair"
    if any(word in task_l for word in ["blueprint", "plan", "strategy", "architecture", "prototype"]):
        return "blueprint"
    if "seo" in task_l:
        return "seo"
    if any(word in task_l for word in ["choose", "best", "root cause", "correct"]):
        return "precision"
    return "precision"


def resolve_shape(question_type, requested):
    if requested != "auto":
        return requested
    if question_type == "coverage":
        return "coverage_sweep"
    if question_type == "audit":
        return "coverage_sweep"
    if question_type == "repair":
        return "repair_search"
    if question_type in {"blueprint", "seo"}:
        return "top_k_synthesis"
    return "parallel_proposals"


def resolve_selection(question_type, shape, requested):
    if requested != "auto":
        return requested
    if shape == "three_way_challenge":
        return "vote_then_tiebreak"
    if question_type == "coverage":
        return "coverage_union"
    if question_type == "audit":
        return "risk_union"
    if question_type == "repair":
        return "repair_queue"
    if question_type in {"blueprint", "seo"}:
        return "top_k"
    return "best_one"


def auto_proposal_count(question_type, shape, budget_workers):
    budget_workers = max(1, budget_workers)
    if shape == "three_way_challenge":
        return 3
    if question_type in {"precision", "repair"}:
        return min(budget_workers, 4)
    if question_type in {"blueprint", "seo"}:
        return min(budget_workers, 5)
    return budget_workers


def resolve_count(value, default):
    if value == "auto":
        return default
    return max(1, int(value))


def resolve_choose_count(value, question_type, shape, selection_mode, proposal_count):
    if value == "all-valid":
        return "all_valid"
    if value != "auto":
        return max(1, min(int(value), proposal_count))
    if shape == "three_way_challenge":
        return 1
    if selection_mode in {"coverage_union", "risk_union"} or question_type in {"coverage", "audit"}:
        return "all_valid"
    if selection_mode == "top_k":
        return min(proposal_count, 3)
    if selection_mode == "repair_queue":
        return min(proposal_count, 2)
    return 1


def candidate_paths(root, candidate_id, artifact_layout):
    root = pathlib.Path(root)
    if artifact_layout == "old_three_way":
        implementation_dir = root / candidate_id / "implementation"
        return {
            "implementation_dir": implementation_dir,
            "result": implementation_dir / "result.md",
            "failure": implementation_dir / "failure.md",
            "verification": implementation_dir / "verification.md",
            "peer_review_round_1": implementation_dir / "critique_round_1.md",
            "revision_round_1": implementation_dir / "update_round_1.md",
            "peer_review_round_2": implementation_dir / "critique_round_2.md",
            "repair_synthesis": implementation_dir / "final_repair.md",
        }
    candidate_dir = root / candidate_id
    return {
        "implementation_dir": candidate_dir / "implementation",
        "result": candidate_dir / "result.md",
        "failure": candidate_dir / "failure.md",
        "verification": candidate_dir / "verification.md",
        "peer_review_round_1": candidate_dir / "peer_review_round_1.md",
        "revision_round_1": candidate_dir / "revision_round_1.md",
        "peer_review_round_2": candidate_dir / "peer_review_round_2.md",
        "repair_synthesis": candidate_dir / "repair_synthesis.md",
    }


def build_candidates(output, shape, proposal_count, artifact_layout):
    if shape == "three_way_challenge":
        ids = OLD_THREE_WAY_IDS
    else:
        ids = [f"proposal_{idx:03d}" for idx in range(1, proposal_count + 1)]
    return [
        {
            "id": candidate_id,
            "agent_id": candidate_id,
            "label": f"Candidate {candidate_id}",
            "paths": candidate_paths(output, candidate_id, artifact_layout),
        }
        for candidate_id in ids
    ]


def peer_blocks(candidates, preferred_file):
    blocks = []
    for candidate in candidates:
        text = read_text(candidate["paths"].get(preferred_file, "")) or read_text(candidate["paths"]["result"])
        blocks.append(f"## {candidate['label']} ({candidate['id']})\n{text or '(empty)'}")
    return "\n\n".join(blocks)


def build_candidate_prompt(stage, plan, candidate, peer_candidates=None, verifier_report="", critiques="", previous_text="", selected_id=""):
    peer_candidates = peer_candidates or []
    header = "\n".join(
        [
            f"You are candidate {candidate['id']} in a {plan['competition_shape']} competition.",
            "Be concrete, testable, and blunt. Avoid vague process narration.",
            f"Question type: {plan['question_type']}",
            f"Selection mode: {plan['selection_mode']}",
            f"Original task: {plan['task']}",
            f"Writable output directory: {candidate['paths']['implementation_dir']}",
            "Do not write outside your candidate output directory.",
        ]
    )
    if stage == "proposal":
        return "\n\n".join(
            [
                header,
                "Stage: proposal.",
                "Return implementation details, validation steps, risks, and next actions.",
            ]
        )
    if stage == "peer_review_round_1":
        return "\n\n".join(
            [
                header,
                "Stage: first peer review.",
                "Critique the other candidates sharply. Focus on correctness, missing tests, maintainability, and integration risk.",
                f"Verifier report:\n{verifier_report or '(empty)'}",
                f"Peer outputs:\n{peer_blocks(peer_candidates, 'result') or '(empty)'}",
            ]
        )
    if stage == "revision_round_1":
        return "\n\n".join(
            [
                header,
                "Stage: revision after peer reviews.",
                "Produce a full revised result, not just a reply to comments.",
                f"Previous result:\n{previous_text or '(empty)'}",
                f"Reviews received:\n{critiques or '(empty)'}",
            ]
        )
    if stage == "peer_review_round_2":
        return "\n\n".join(
            [
                header,
                "Stage: second peer review and selection vote.",
                "Critique the revised peer outputs and end with selected_candidate_id: <candidate id>.",
                f"Peer revised outputs:\n{peer_blocks(peer_candidates, 'revision_round_1') or '(empty)'}",
            ]
        )
    if stage == "repair_synthesis":
        return "\n\n".join(
            [
                header,
                "Stage: final repair synthesis.",
                f"Selected candidate: {selected_id or '(unknown)'}",
                "Summarize found issues and the repair work you are responsible for.",
                f"Your revised result:\n{previous_text or '(empty)'}",
                f"Second-round reviews:\n{critiques or '(empty)'}",
            ]
        )
    raise ValueError(f"unknown candidate stage: {stage}")


def build_verifier_prompt(plan):
    outputs = []
    for candidate in plan["candidates"]:
        text = read_text(candidate["paths"]["result"]) or read_text(candidate["paths"]["failure"])
        outputs.append(f"## {candidate['label']} ({candidate['id']})\n{text or '(empty)'}")
    return "\n\n".join(
        [
            "You are the initial verifier for a proposal competition.",
            "Check candidates for non-empty output, task alignment, blockers, warnings, and likely validation steps.",
            f"Question type: {plan['question_type']}",
            f"Original task: {plan['task']}",
            "Candidate outputs:\n" + "\n\n".join(outputs),
        ]
    )


def parse_candidate_id(text, candidate_ids):
    for pattern in [
        r"selected_candidate_id\s*:\s*([A-Za-z0-9_-]+)",
        r"best_run_id\s*:\s*([A-Za-z0-9_-]+)",
        r"\b(run_[abc])\b",
        r"\b(proposal_\d{3})\b",
    ]:
        match = re.search(pattern, text or "", flags=re.I)
        if match:
            candidate_id = match.group(1).lower()
            if candidate_id in candidate_ids:
                return candidate_id
    return ""


def select_candidates(selection_mode, choose_count, candidates, review_texts):
    candidate_ids = [candidate["id"] for candidate in candidates if read_text(candidate["paths"]["result"])]
    if not candidate_ids:
        return []
    if choose_count == "all_valid" or selection_mode in {"coverage_union", "risk_union"}:
        return candidate_ids
    if selection_mode == "vote_then_tiebreak":
        counts = {candidate_id: 0 for candidate_id in candidate_ids}
        for text in review_texts:
            selected = parse_candidate_id(text, candidate_ids)
            if selected in counts:
                counts[selected] += 1
        return [sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]]
    count = choose_count if isinstance(choose_count, int) else 1
    return candidate_ids[:count]


def run_agent(args, plan, *, agent_id, candidate_id, stage, prompt, output_file):
    prompt_file = pathlib.Path(args.output) / "_prompts" / f"{candidate_id}_{stage}.md"
    write_text(prompt_file, prompt)
    if args.runner == "mock":
        if stage == "peer_review_round_2":
            return f"{candidate_id} {stage} mock output\nselected_candidate_id: {plan['candidates'][0]['id']}"
        return f"{candidate_id} {stage} mock output"
    if args.runner != "command":
        raise ValueError(f"unsupported runner: {args.runner}")
    if not args.command:
        raise ValueError("--command is required when --runner command")
    command = args.command.format(
        agent_id=agent_id,
        run_id=candidate_id,
        candidate_id=candidate_id,
        stage=stage,
        prompt_file=str(prompt_file),
        output_file=str(output_file),
        competition_id=plan["competition_id"],
        question_type=plan["question_type"],
        selection_mode=plan["selection_mode"],
    )
    completed = subprocess.run(
        command,
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    max_bytes = args.max_output_mb * 1024 * 1024
    output = truncate_text(completed.stdout.strip(), max_bytes)
    stderr = truncate_text(completed.stderr.strip(), max_bytes)
    if stderr:
        output = (output + "\n\nSTDERR:\n" + stderr).strip()
    if completed.returncode != 0:
        raise RuntimeError(output or f"command failed with exit code {completed.returncode}")
    return output


def write_initial_manifest(output, plan, args):
    manifest = {
        "schema_version": "b3ehive.compete.v1",
        "competition_id": plan["competition_id"],
        "task": plan["task"],
        "question_type": plan["question_type"],
        "competition_shape": plan["competition_shape"],
        "selection_mode": plan["selection_mode"],
        "artifact_layout": plan["artifact_layout"],
        "budget": {
            "workers": args.budget_workers,
            "proposal_count": len(plan["candidates"]),
            "choose_count": plan["choose_count"],
            "max_output_mb": args.max_output_mb,
        },
        "candidate_ids": [candidate["id"] for candidate in plan["candidates"]],
        "stages": [
            "proposal",
            "initial_verification",
            "peer_review_round_1",
            "revision_round_1",
            "peer_review_round_2",
            "selection_vote",
            "repair_synthesis",
        ],
        "failure_policy": {
            "parallel_settled": True,
            "fail_only_if_no_valid_candidate": True,
        },
        "selection": {
            "selected_ids": [],
            "tie_break": "stable_candidate_id",
        },
        "handoff": {
            "mode": args.handoff_mode,
            "source_blueprint_item_id": args.source_item_id or None,
            "source_loop_id": args.source_loop_id or None,
            "may_mark_x": False,
        },
    }
    write_json(pathlib.Path(output) / "compete_manifest.json", manifest)
    return manifest


def update_manifest_selection(output, selected_ids):
    manifest_path = pathlib.Path(output) / "compete_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["selection"]["selected_ids"] = selected_ids
    write_json(manifest_path, manifest)


def build_plan(args):
    question_type = classify_question(args.task, args.question_type)
    shape = resolve_shape(question_type, args.competition_shape)
    selection_mode = resolve_selection(question_type, shape, args.selection_mode)
    proposal_default = auto_proposal_count(question_type, shape, args.budget_workers)
    proposal_count = resolve_count(args.proposal_count, proposal_default)
    if shape == "three_way_challenge":
        proposal_count = 3
    choose_count = resolve_choose_count(args.choose_count, question_type, shape, selection_mode, proposal_count)
    candidates = build_candidates(args.output, shape, proposal_count, args.artifact_layout)
    return {
        "competition_id": f"COMP-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "task": args.task.strip(),
        "question_type": question_type,
        "competition_shape": shape,
        "selection_mode": selection_mode,
        "artifact_layout": args.artifact_layout,
        "choose_count": choose_count,
        "candidates": candidates,
    }


def orchestrate(args):
    output = pathlib.Path(args.output or f"competition-runs/{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}")
    args.output = str(output)
    require_free_space(output.parent if output.parent != pathlib.Path("") else pathlib.Path("."), args.min_free_gb)
    plan = build_plan(args)
    for candidate in plan["candidates"]:
        candidate["paths"]["implementation_dir"].mkdir(parents=True, exist_ok=True)

    write_initial_manifest(output, plan, args)
    write_text(output / "classification.md", f"# Classification\n\nQuestion type: {plan['question_type']}\nCompetition shape: {plan['competition_shape']}\nSelection mode: {plan['selection_mode']}")

    max_workers = max(1, min(args.budget_workers, len(plan["candidates"])))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for candidate in plan["candidates"]:
            prompt = build_candidate_prompt("proposal", plan, candidate)
            futures[
                executor.submit(
                    run_agent,
                    args,
                    plan,
                    agent_id=candidate["agent_id"],
                    candidate_id=candidate["id"],
                    stage="proposal",
                    prompt=prompt,
                    output_file=candidate["paths"]["result"],
                )
            ] = candidate
        for future in concurrent.futures.as_completed(futures):
            candidate = futures[future]
            try:
                write_text(candidate["paths"]["result"], future.result())
            except Exception as exc:
                write_text(candidate["paths"]["failure"], str(exc))
        ensure_output_budget(output, args.max_output_mb)

    if all(read_text(candidate["paths"]["failure"]) and not read_text(candidate["paths"]["result"]) for candidate in plan["candidates"]):
        write_text(output / "summary.md", "# Compete Cron Failed\n\nNo valid candidate proposals were produced.")
        raise RuntimeError("no valid candidate proposals were produced")

    verifier_report = run_agent(
        args,
        plan,
        agent_id=args.verifier_agent,
        candidate_id="verifier",
        stage="initial_verification",
        prompt=build_verifier_prompt(plan),
        output_file=output / "verification.md",
    )
    write_text(output / "verification.md", verifier_report)
    for candidate in plan["candidates"]:
        write_text(candidate["paths"]["verification"], verifier_report)

    reviews_1 = {}
    for candidate in plan["candidates"]:
        peers = [peer for peer in plan["candidates"] if peer["id"] != candidate["id"]]
        text = run_agent(
            args,
            plan,
            agent_id=candidate["agent_id"],
            candidate_id=candidate["id"],
            stage="peer_review_round_1",
            prompt=build_candidate_prompt("peer_review_round_1", plan, candidate, peers, verifier_report),
            output_file=candidate["paths"]["peer_review_round_1"],
        )
        reviews_1[candidate["id"]] = text
        write_text(candidate["paths"]["peer_review_round_1"], text)

    for candidate in plan["candidates"]:
        received = "\n\n".join(text for candidate_id, text in reviews_1.items() if candidate_id != candidate["id"])
        text = run_agent(
            args,
            plan,
            agent_id=candidate["agent_id"],
            candidate_id=candidate["id"],
            stage="revision_round_1",
            prompt=build_candidate_prompt(
                "revision_round_1",
                plan,
                candidate,
                critiques=received,
                previous_text=read_text(candidate["paths"]["result"]),
            ),
            output_file=candidate["paths"]["revision_round_1"],
        )
        write_text(candidate["paths"]["revision_round_1"], text)

    reviews_2 = {}
    for candidate in plan["candidates"]:
        peers = [peer for peer in plan["candidates"] if peer["id"] != candidate["id"]]
        text = run_agent(
            args,
            plan,
            agent_id=candidate["agent_id"],
            candidate_id=candidate["id"],
            stage="peer_review_round_2",
            prompt=build_candidate_prompt("peer_review_round_2", plan, candidate, peers),
            output_file=candidate["paths"]["peer_review_round_2"],
        )
        reviews_2[candidate["id"]] = text
        write_text(candidate["paths"]["peer_review_round_2"], text)

    selected = select_candidates(plan["selection_mode"], plan["choose_count"], plan["candidates"], reviews_2.values())
    if not selected:
        raise RuntimeError("selection produced no candidates")
    update_manifest_selection(output, selected)
    write_json(output / "selected.json", {"selected_ids": selected})
    rejected = [candidate["id"] for candidate in plan["candidates"] if candidate["id"] not in selected]
    write_json(output / "rejected.json", {"rejected_ids": rejected})
    write_text(output / "best_run.txt", selected[0])

    for candidate in plan["candidates"]:
        text = run_agent(
            args,
            plan,
            agent_id=candidate["agent_id"],
            candidate_id=candidate["id"],
            stage="repair_synthesis",
            prompt=build_candidate_prompt(
                "repair_synthesis",
                plan,
                candidate,
                previous_text=read_text(candidate["paths"]["revision_round_1"]),
                critiques="\n\n".join(reviews_2.values()),
                selected_id=selected[0],
            ),
            output_file=candidate["paths"]["repair_synthesis"],
        )
        write_text(candidate["paths"]["repair_synthesis"], text)

    repairs = ["# Final Repair Assignments", "", f"Selected candidate: {selected[0]}", ""]
    for candidate in plan["candidates"]:
        repairs.extend([f"## {candidate['id']}", read_text(candidate["paths"]["repair_synthesis"]) or "(empty)", ""])
    write_text(output / "final_repairs.md", "\n".join(repairs))

    if plan["selection_mode"] in {"coverage_union", "risk_union"} or plan["choose_count"] == "all_valid":
        synthesis_title = "Coverage Union"
        synthesis_body = "\n\n".join(
            f"## {candidate['id']}\n{read_text(candidate['paths']['revision_round_1']) or read_text(candidate['paths']['result'])}"
            for candidate in plan["candidates"]
            if candidate["id"] in selected
        )
    else:
        synthesis_title = "Synthesis"
        synthesis_body = f"Selected candidate: {selected[0]}"
    write_text(output / "synthesis.md", f"# {synthesis_title}\n\n{synthesis_body}")
    write_text(
        output / "summary.md",
        f"# Compete Cron Summary\n\nTask: {plan['task']}\nQuestion type: {plan['question_type']}\nCompetition shape: {plan['competition_shape']}\nSelected: {', '.join(selected)}\nOutput: {output}",
    )
    ensure_output_budget(output, args.max_output_mb)
    return output, selected


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a bounded b3ehive proposal competition.")
    parser.add_argument("--task", required=True)
    parser.add_argument("--output", default="")
    parser.add_argument("--budget-workers", type=int, default=3)
    parser.add_argument("--proposal-count", default="auto")
    parser.add_argument("--choose-count", default="auto")
    parser.add_argument("--question-type", choices=sorted(QUESTION_TYPES), default="auto")
    parser.add_argument("--competition-shape", choices=sorted(COMPETITION_SHAPES), default="auto")
    parser.add_argument("--selection-mode", choices=sorted(SELECTION_MODES), default="auto")
    parser.add_argument("--artifact-layout", choices=["native", "old_three_way"], default="native")
    parser.add_argument("--runner", choices=["mock", "command"], default="mock")
    parser.add_argument("--command", default="")
    parser.add_argument("--verifier-agent", default="verifier")
    parser.add_argument("--max-output-mb", type=int, default=20)
    parser.add_argument("--min-free-gb", type=int, default=30)
    parser.add_argument("--handoff-mode", choices=["standalone", "execution_embed", "looper_attempt"], default="standalone")
    parser.add_argument("--source-item-id", default="")
    parser.add_argument("--source-loop-id", default="")
    args = parser.parse_args(argv)
    output, selected = orchestrate(args)
    print("Compete cron complete")
    print(f"Selected: {', '.join(selected)}")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
