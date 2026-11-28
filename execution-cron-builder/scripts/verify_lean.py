#!/usr/bin/env python3
"""Lean 4 formal verifier and anti-gaming oracle runner for b3ehive (b3lean).

Subcommands:
  stack       Export stack IR and certify via `b3lean check` (and optional `--cert`
              kernel certificate + axiom audit).
  oracle      Verify a blueprint item's `oracle: lean:<Module>.<Theorem>` with
              `lake build`, external `leanchecker`, strict `#print axioms`
              allowlist, and optional read-only Spec-dir protection.
  self-check  Build `formal/b3lean`, run `leanchecker`, and audit all theorems.
"""
import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
SELF_THEOREMS = [
    "B3Lean.topo_acyclic_sound",
    "B3Lean.dag_ordered_noninterference",
    "B3Lean.checkBoundaries_sound",
    "B3Lean.checkTransitiveAccepted_sound",
    "B3Lean.checkRuleOfTwo_sound",
    "B3Lean.master_only_acceptance",
    "B3Lean.occam_no_gain_for_single_leaf",
    "B3Lean.occam_factoring_strict_saving",
    "B3Lean.major_revision_non_regression",
    "B3Lean.checkStack_sound",
]


def find_b3lean_dir(explicit: str = None) -> pathlib.Path:
    if explicit:
        return pathlib.Path(explicit).resolve()
    env = os.environ.get("B3EHIVE_LEAN_DIR")
    if env:
        return pathlib.Path(env).resolve()
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "formal" / "b3lean"
        if (cand / "lakefile.toml").is_file():
            return cand
    return pathlib.Path.cwd() / "formal" / "b3lean"


def run_cmd(cmd, cwd=None, stdin_text=None):
    return subprocess.run(cmd, cwd=cwd, input=stdin_text, capture_output=True, text=True)


def parse_axioms(output: str, expected_names: list) -> list:
    """Return error list if any theorem is missing or uses disallowed axioms."""
    errors = []
    found = {}
    for line in output.splitlines():
        m_none = re.match(r"^'([^']+)' does not depend on any axioms$", line.strip())
        if m_none:
            found[m_none.group(1)] = set()
            continue
        m_ax = re.match(r"^'([^']+)' depends on axioms:\s*\[([^\]]*)\]$", line.strip())
        if m_ax:
            axs = {a.strip() for a in m_ax.group(2).split(",") if a.strip()}
            found[m_ax.group(1)] = axs
    for name in expected_names:
        if name not in found:
            errors.append(f"axiom audit missing output for '{name}'")
            continue
        disallowed = sorted(found[name] - ALLOWED_AXIOMS)
        if disallowed:
            errors.append(f"'{name}' uses disallowed axiom(s): {', '.join(disallowed)}")
    return errors


def ensure_b3lean_built(b3lean_dir: pathlib.Path) -> pathlib.Path:
    if not shutil.which("lake"):
        raise RuntimeError("lake not found in PATH; install Lean 4 (elan) or set B3_FORMAL_VERIFIER=off")
    exe = b3lean_dir / ".lake" / "build" / "bin" / "b3lean"
    if not exe.is_file():
        res = run_cmd(["lake", "build"], cwd=b3lean_dir)
        if res.returncode != 0:
            raise RuntimeError(f"lake build failed:\n{res.stdout}\n{res.stderr}")
    return exe


def cmd_self_check(args) -> int:
    b3lean_dir = find_b3lean_dir(args.b3lean_dir)
    if not (b3lean_dir / "lakefile.toml").is_file():
        print(f"ERROR: formal/b3lean not found at {b3lean_dir}", file=sys.stderr)
        return 2
    res = run_cmd(["lake", "build"], cwd=b3lean_dir)
    if res.returncode != 0:
        print(res.stdout + res.stderr, file=sys.stderr)
        return 1
    for mod in ("B3Lean.Core", "B3Lean.Soundness"):
        chk = run_cmd(["lake", "env", "leanchecker", mod], cwd=b3lean_dir)
        if chk.returncode != 0:
            print(f"ERROR: leanchecker failed on {mod}:\n{chk.stdout}{chk.stderr}", file=sys.stderr)
            return 1
    snippet = "import B3Lean.Soundness\n" + "\n".join(f"#print axioms {t}" for t in SELF_THEOREMS) + "\n"
    aud = run_cmd(["lake", "env", "lean", "--stdin"], cwd=b3lean_dir, stdin_text=snippet)
    if aud.returncode != 0:
        print(f"ERROR: axiom audit failed:\n{aud.stdout}{aud.stderr}", file=sys.stderr)
        return 1
    errs = parse_axioms(aud.stdout, SELF_THEOREMS)
    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"b3lean self-check passed: lake build, leanchecker, and {len(SELF_THEOREMS)} theorems clean.")
    return 0


def cmd_stack(args) -> int:
    b3lean_dir = find_b3lean_dir(args.b3lean_dir)
    try:
        exe = ensure_b3lean_built(b3lean_dir)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    validator = pathlib.Path(__file__).resolve().parent / "validate_blueprint_stack.py"
    with tempfile.TemporaryDirectory() as td:
        ir_path = pathlib.Path(td) / "stack_ir.json"
        exp_cmd = [sys.executable, str(validator), "export-ir", args.manifest, "-o", str(ir_path)]
        if args.repo_root:
            exp_cmd.extend(["--repo-root", args.repo_root])
        exp = run_cmd(exp_cmd)
        if exp.returncode != 0:
            print(exp.stderr or exp.stdout, file=sys.stderr)
            return exp.returncode

        chk = run_cmd([str(exe), "check", str(ir_path)])
        if chk.returncode != 0:
            print(chk.stderr or chk.stdout, file=sys.stderr)
            return chk.returncode

        if args.cert:
            cert_path = pathlib.Path(td) / "StackCert.lean"
            gen = run_cmd([str(exe), "cert", str(ir_path), "-o", str(cert_path)])
            if gen.returncode != 0:
                print(gen.stderr or gen.stdout, file=sys.stderr)
                return gen.returncode
            kchk = run_cmd(["lake", "env", "lean", "-DwarningAsError=true", str(cert_path)], cwd=b3lean_dir)
            if kchk.returncode != 0:
                print(f"ERROR: kernel cert failed:\n{kchk.stdout}{kchk.stderr}", file=sys.stderr)
                return 1
            errs = parse_axioms(kchk.stdout, ["cert_stack_certified"])
            if errs:
                for e in errs:
                    print(f"ERROR: {e}", file=sys.stderr)
                return 1
            print(chk.stdout.strip() + " + kernel cert verified (clean axioms).")
        else:
            print(chk.stdout.strip())
    return 0


def cmd_oracle(args) -> int:
    target = args.target
    if target.startswith("lean:"):
        target = target[5:]
    if ":" in target:
        module, const_name = target.split(":", 1)
    elif "." in target:
        module, _ = target.rsplit(".", 1)
        const_name = target
    else:
        print(f"ERROR: oracle target must be <Module>.<Theorem> or <Module>:<Theorem>, got '{args.target}'", file=sys.stderr)
        return 2
    proj = pathlib.Path(args.project).resolve()
    if not proj.is_dir():
        print(f"ERROR: Lean project dir not found: {proj}", file=sys.stderr)
        return 2

    # Optional read-only Spec directory guard against worker tampering.
    if args.spec_dir and args.changed_paths:
        spec_norm = pathlib.PurePosixPath(args.spec_dir.replace("\\", "/")).as_posix().rstrip("/")
        for cp in args.changed_paths:
            cp_norm = pathlib.PurePosixPath(cp.replace("\\", "/")).as_posix().lstrip("./")
            if cp_norm == spec_norm or cp_norm.startswith(spec_norm + "/"):
                print(f"ERROR: worker modified read-only spec path '{cp}' under '{spec_norm}'", file=sys.stderr)
                return 1

    bld = run_cmd(["lake", "build", module], cwd=proj)
    if bld.returncode != 0:
        print(f"ERROR: lake build {module} failed:\n{bld.stdout}{bld.stderr}", file=sys.stderr)
        return 1

    lchk = run_cmd(["lake", "env", "leanchecker", module], cwd=proj)
    if lchk.returncode != 0:
        print(f"ERROR: leanchecker failed on {module}:\n{lchk.stdout}{lchk.stderr}", file=sys.stderr)
        return 1

    snippet = f"import {module}\n#print axioms {const_name}\n"
    aud = run_cmd(["lake", "env", "lean", "-DwarningAsError=true", "--stdin"], cwd=proj, stdin_text=snippet)
    if aud.returncode != 0:
        print(f"ERROR: axiom audit failed for {const_name}:\n{aud.stdout}{aud.stderr}", file=sys.stderr)
        return 1

    errs = parse_axioms(aud.stdout, [const_name])
    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"Lean oracle passed: {const_name} (leanchecker + strict axiom allowlist).")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_self = sub.add_parser("self-check")
    sp_self.add_argument("--b3lean-dir", help="Path to formal/b3lean")

    sp_stack = sub.add_parser("stack")
    sp_stack.add_argument("manifest", help="Path to blueprint_stack.json")
    sp_stack.add_argument("--repo-root", help="Repository root")
    sp_stack.add_argument("--cert", action="store_true", help="Emit and kernel-check StackCert.lean")
    sp_stack.add_argument("--b3lean-dir", help="Path to formal/b3lean")

    sp_oracle = sub.add_parser("oracle")
    sp_oracle.add_argument("target", help="Target theorem as [lean:]<Module>.<Theorem>")
    sp_oracle.add_argument("--project", required=True, help="Lean Lake project directory")
    sp_oracle.add_argument("--spec-dir", help="Read-only spec directory forbidden in worker diffs")
    sp_oracle.add_argument("--changed-path", dest="changed_paths", action="append", default=[], help="Worker-modified path")

    args = p.parse_args(argv)
    if args.cmd == "self-check":
        return cmd_self_check(args)
    if args.cmd == "stack":
        return cmd_stack(args)
    if args.cmd == "oracle":
        return cmd_oracle(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
