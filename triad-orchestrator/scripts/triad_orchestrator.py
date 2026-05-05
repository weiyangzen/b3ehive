#!/usr/bin/env python3
import argparse
import concurrent.futures
import datetime as dt
import pathlib
import re
import subprocess
import sys

RUNS = [
    {"id": "run_a", "agent_id": "run_a", "label": "Agent A"},
    {"id": "run_b", "agent_id": "run_b", "label": "Agent B"},
    {"id": "run_c", "agent_id": "run_c", "label": "Agent C"},
]


def read_text(path):
    try:
        return pathlib.Path(path).read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def write_text(path, text):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text((text or "").strip() + "\n", encoding="utf-8")


def run_paths(root, run_id):
    implementation_dir = pathlib.Path(root) / run_id / "implementation"
    return {
        "implementation_dir": implementation_dir,
        "result": implementation_dir / "result.md",
        "failure": implementation_dir / "failure.md",
        "verification": implementation_dir / "verification.md",
        "critique_round_1": implementation_dir / "critique_round_1.md",
        "update_round_1": implementation_dir / "update_round_1.md",
        "critique_round_2": implementation_dir / "critique_round_2.md",
        "final_repair": implementation_dir / "final_repair.md",
    }


def build_plan(task, output):
    output = pathlib.Path(output)
    return {
        "task": task.strip(),
        "output": output,
        "runs": [{**run, "paths": run_paths(output, run["id"])} for run in RUNS],
    }


def peer_blocks(runs):
    blocks = []
    for run in runs:
        text = read_text(run["paths"]["update_round_1"]) or read_text(run["paths"]["result"])
        blocks.append(f"## {run['label']} ({run['id']})\n{text or '(empty)'}")
    return "\n\n".join(blocks)


def build_prompt(stage, plan, run, peer_runs=None, verifier_report="", critiques="", previous_text="", best_run_id=""):
    peer_runs = peer_runs or []
    header = "\n".join(
        [
            f"You are {run['label']} in a three-agent tournament workflow.",
            "Be concrete, testable, and blunt. Avoid vague process narration.",
            f"Original task: {plan['task']}",
        ]
    )
    if stage == "implementation":
        return "\n\n".join(
            [
                header,
                "Stage: first implementation.",
                f"Write as if your result will be stored at {run['id']}/implementation/result.md.",
                "Include implementation details, validation steps, risks, and next actions.",
            ]
        )
    if stage == "critique_round_1":
        return "\n\n".join(
            [
                header,
                "Stage: first cross-critique.",
                "Critique the other two runs sharply. Focus on correctness, missing tests, maintainability, and integration risk.",
                f"Verifier report:\n{verifier_report or '(empty)'}",
                f"Peer outputs:\n{peer_blocks(peer_runs) or '(empty)'}",
            ]
        )
    if stage == "update_round_1":
        return "\n\n".join(
            [
                header,
                "Stage: update after critiques.",
                "Produce a full updated result, not just a reply to comments.",
                f"Previous result:\n{previous_text or '(empty)'}",
                f"Critiques received:\n{critiques or '(empty)'}",
            ]
        )
    if stage == "critique_round_2":
        return "\n\n".join(
            [
                header,
                "Stage: second critique and best-run vote.",
                "Critique the updated peer outputs and end with best_run_id: run_a/run_b/run_c.",
                f"Peer updated outputs:\n{peer_blocks(peer_runs) or '(empty)'}",
            ]
        )
    if stage == "final_repair":
        return "\n\n".join(
            [
                header,
                "Stage: final repair assignment.",
                f"Selected best run: {best_run_id or '(unknown)'}",
                "Summarize found issues and the repair work you are responsible for.",
                f"Your updated result:\n{previous_text or '(empty)'}",
                f"Second-round critiques:\n{critiques or '(empty)'}",
            ]
        )
    raise ValueError(f"unknown stage: {stage}")


def build_verifier_prompt(plan):
    outputs = []
    for run in plan["runs"]:
        text = read_text(run["paths"]["result"]) or read_text(run["paths"]["failure"])
        outputs.append(f"## {run['label']} ({run['id']})\n{text or '(empty)'}")
    return "\n\n".join(
        [
            "You are the initial verifier for a three-agent workflow.",
            "Check run_a/run_b/run_c for non-empty output, task alignment, blockers, warnings, and likely tests.",
            f"Original task: {plan['task']}",
            "Three outputs:\n" + "\n\n".join(outputs),
        ]
    )


def parse_best_run_id(text):
    match = re.search(r"\b(run_[abc])\b", text or "", flags=re.I)
    return match.group(1).lower() if match else ""


def select_best(texts):
    counts = {run["id"]: 0 for run in RUNS}
    for text in texts:
        best = parse_best_run_id(text)
        if best in counts:
            counts[best] += 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def run_agent(args, *, agent_id, run_id, stage, prompt, output_file):
    prompt_file = pathlib.Path(args.output) / "_prompts" / f"{run_id}_{stage}.md"
    write_text(prompt_file, prompt)
    if args.runner == "mock":
        if stage == "critique_round_2":
            return f"{run_id} {stage} mock output\nbest_run_id: run_a"
        return f"{run_id} {stage} mock output"
    if args.runner != "command":
        raise ValueError(f"unsupported runner: {args.runner}")
    if not args.command:
        raise ValueError("--command is required when --runner command")
    command = args.command.format(
        agent_id=agent_id,
        run_id=run_id,
        stage=stage,
        prompt_file=str(prompt_file),
        output_file=str(output_file),
    )
    completed = subprocess.run(
        command,
        shell=True,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output = completed.stdout.strip()
    if completed.stderr.strip():
        output = (output + "\n\nSTDERR:\n" + completed.stderr.strip()).strip()
    if completed.returncode != 0:
        raise RuntimeError(output or f"command failed with exit code {completed.returncode}")
    return output


def orchestrate(args):
    output = pathlib.Path(args.output or f"triad-runs/{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}")
    args.output = str(output)
    plan = build_plan(args.task, output)
    for run in plan["runs"]:
        run["paths"]["implementation_dir"].mkdir(parents=True, exist_ok=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {}
        for run in plan["runs"]:
            prompt = build_prompt("implementation", plan, run)
            futures[executor.submit(run_agent, args, agent_id=run["agent_id"], run_id=run["id"], stage="implementation", prompt=prompt, output_file=run["paths"]["result"])] = run
        for future in concurrent.futures.as_completed(futures):
            run = futures[future]
            try:
                write_text(run["paths"]["result"], future.result())
            except Exception as exc:
                write_text(run["paths"]["failure"], str(exc))

    if all(read_text(run["paths"]["failure"]) and not read_text(run["paths"]["result"]) for run in plan["runs"]):
        write_text(output / "summary.md", "# Triad Orchestration Failed\n\nAll three implementation agents failed.")
        raise RuntimeError("all three implementation agents failed")

    verifier_report = run_agent(
        args,
        agent_id=args.verifier_agent,
        run_id="verifier",
        stage="verification",
        prompt=build_verifier_prompt(plan),
        output_file=output / "verification.md",
    )
    write_text(output / "verification.md", verifier_report)
    for run in plan["runs"]:
        write_text(run["paths"]["verification"], verifier_report)

    critiques_1 = {}
    for run in plan["runs"]:
        peers = [peer for peer in plan["runs"] if peer["id"] != run["id"]]
        text = run_agent(args, agent_id=run["agent_id"], run_id=run["id"], stage="critique_round_1", prompt=build_prompt("critique_round_1", plan, run, peers, verifier_report), output_file=run["paths"]["critique_round_1"])
        critiques_1[run["id"]] = text
        write_text(run["paths"]["critique_round_1"], text)

    for run in plan["runs"]:
        received = "\n\n".join(text for run_id, text in critiques_1.items() if run_id != run["id"])
        text = run_agent(args, agent_id=run["agent_id"], run_id=run["id"], stage="update_round_1", prompt=build_prompt("update_round_1", plan, run, critiques=received, previous_text=read_text(run["paths"]["result"])), output_file=run["paths"]["update_round_1"])
        write_text(run["paths"]["update_round_1"], text)

    critiques_2 = {}
    for run in plan["runs"]:
        peers = [peer for peer in plan["runs"] if peer["id"] != run["id"]]
        text = run_agent(args, agent_id=run["agent_id"], run_id=run["id"], stage="critique_round_2", prompt=build_prompt("critique_round_2", plan, run, peers), output_file=run["paths"]["critique_round_2"])
        critiques_2[run["id"]] = text
        write_text(run["paths"]["critique_round_2"], text)

    best = select_best(critique for critique in critiques_2.values())
    write_text(output / "best_run.txt", best)

    for run in plan["runs"]:
        text = run_agent(args, agent_id=run["agent_id"], run_id=run["id"], stage="final_repair", prompt=build_prompt("final_repair", plan, run, previous_text=read_text(run["paths"]["update_round_1"]), critiques="\n\n".join(critiques_2.values()), best_run_id=best), output_file=run["paths"]["final_repair"])
        write_text(run["paths"]["final_repair"], text)

    final_repairs = ["# Final Repair Assignments", "", f"Best run: {best}", ""]
    for run in plan["runs"]:
        final_repairs.extend([f"## {run['id']}", read_text(run["paths"]["final_repair"]) or "(empty)", ""])
    write_text(output / "final_repairs.md", "\n".join(final_repairs))
    write_text(output / "summary.md", f"# Triad Orchestration Summary\n\nTask: {plan['task']}\nBest run: {best}\nOutput: {output}")
    return output, best


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a three-agent orchestration workflow.")
    parser.add_argument("--task", required=True)
    parser.add_argument("--output", default="")
    parser.add_argument("--runner", choices=["mock", "command"], default="mock")
    parser.add_argument("--command", default="")
    parser.add_argument("--verifier-agent", default="verifier")
    args = parser.parse_args(argv)
    output, best = orchestrate(args)
    print(f"Triad orchestration complete")
    print(f"Best run: {best}")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
