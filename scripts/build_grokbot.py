#!/usr/bin/env python3
"""Build the grokbot skill set from the five base skills.

Each base skill becomes `grokbot/skills/grokbot-<skill>/` plus a reproducible
`grokbot/grokbot-<skill>-skill.zip`. Grokbot installs a zip with
`unzip grokbot-<skill>-skill.zip -d ~/.claude/skills/`.

The build inserts `core/grokbot-gate.md` after the SKILL.md title, swaps the
Agent Runner section of `references/substrate-cron.md` for
`core/grokbot-runtime.md`, and drops every adapter and transport for another
host. --check reports drift without writing.
"""
import hashlib
import io
import os
import pathlib
import re
import shutil
import stat
import sys
import zipfile

ROOT = pathlib.Path(os.environ.get("B3EHIVE_ROOT") or pathlib.Path(__file__).resolve().parents[1])
SKILLS = ["compete-cron-builder", "execution-cron-builder", "learn-cron-builder",
          "optimization-cron-builder", "looper-cron-builder"]
PREFIX = "grokbot-"
OUT = ROOT / "grokbot"
RUNTIME = "claude --dangerously-skip-permissions"
DESCRIPTION_PREFIX = f"Grokbot only. Subagents run only as {RUNTIME}. "
DROP = {"agents/openai.yaml", "agents/cursor.yaml", "references/transport-codex-tui.md"}
SKIP_NAMES = {".DS_Store", ".b3ehive-version"}
ZIP_TIME = (1980, 1, 1, 0, 0, 0)
# Exact edits for body lines that point at a dropped file.
EDITS = {
    "execution-cron-builder": [
        ("Codex workers follow `references/transport-codex-tui.md` in full. Other runners\n"
         "follow `references/substrate-cron.md`.",
         "Workers run under the grokbot runtime in the gate above and follow\n"
         "`references/substrate-cron.md`."),
        ("- `references/transport-codex-tui.md`: Codex worker transport\n", ""),
    ],
}


def replace_once(text, old, new, where):
    if text.count(old) != 1:
        sys.exit(f"ERROR: {where}: expected one match for {old[:60]!r}")
    return text.replace(old, new, 1)


def build_skill_md(skill, text, version):
    name = PREFIX + skill
    gate = (ROOT / "core" / "grokbot-gate.md").read_text(encoding="utf-8")
    gate = gate.replace("{base}", skill).replace("{name}", name).replace("{version}", version)
    where = f"{skill}/SKILL.md"
    text = replace_once(text, f"\nname: {skill}\n", f"\nname: {name}\n", where)
    text = replace_once(text, "\ndescription: ", "\ndescription: " + DESCRIPTION_PREFIX, where)
    title = re.search(r"^# (.+)\n\n", text, flags=re.M)
    if not title:
        sys.exit(f"ERROR: {where}: no '# Title' line")
    text = (text[:title.start()] + f"# {title.group(1)} (grokbot)\n\n" + gate + "\n"
            + text[title.end():])
    for old, new in EDITS.get(skill, []):
        text = replace_once(text, old, new, where)
    return text


def build_substrate(text):
    runtime = (ROOT / "core" / "grokbot-runtime.md").read_text(encoding="utf-8")
    m = re.search(r"^## Agent Runner\n.*?(?=^## )", text, flags=re.M | re.S)
    if not m:
        sys.exit("ERROR: core/substrate-cron.md: no '## Agent Runner' section")
    return text[:m.start()] + runtime + text[m.end():]


def build_adapter(skill, text):
    text = text.replace(f"${skill}", f"${PREFIX}{skill}")
    text = re.sub(r'display_name: "([^"]+)"', r'display_name: "Grokbot \1"', text)
    return re.sub(r"Grok Build(?: --always-approve)? workers", f"{RUNTIME} subagents", text)


def files_for(skill, version):
    """Return {relative path: (bytes, mode)} for one grokbot skill."""
    src = ROOT / skill
    out = {}
    for path in sorted(src.rglob("*")):
        rel = path.relative_to(src).as_posix()
        if not path.is_file() or path.name in SKIP_NAMES or rel in DROP \
                or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        mode = 0o755 if path.stat().st_mode & stat.S_IXUSR else 0o644
        data = path.read_text(encoding="utf-8") if path.suffix in (".md", ".yaml", ".py", ".tsv") else None
        if rel == "SKILL.md":
            data = build_skill_md(skill, data, version)
        elif rel == "references/substrate-cron.md":
            data = build_substrate(data)
        elif rel.startswith("agents/"):
            data = build_adapter(skill, data)
        out[rel] = (data.encode("utf-8") if data is not None else path.read_bytes(), mode)
    return out


def digest(files):
    """Same digest as `bin/b3ehive doctor` and `scripts/install_skills.sh`."""
    paths = sorted(f"./{rel}".encode() for rel in files)
    listing = b"".join(hashlib.sha256(files[p.decode()[2:]][0]).hexdigest().encode() + b"  " + p + b"\n"
                       for p in paths)
    return hashlib.sha256(listing).hexdigest()[:16]


def build_zip(name, files, version):
    stamp = f"version={version}\nskill={name}\ndigest={digest(files)}\n".encode()
    entries = {**files, ".b3ehive-version": (stamp, 0o644)}
    dirs = {f"{name}/"}
    for rel in entries:
        parts = rel.split("/")[:-1]
        dirs |= {f"{name}/" + "/".join(parts[:i + 1]) + "/" for i in range(len(parts))}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in sorted(dirs):
            info = zipfile.ZipInfo(d, ZIP_TIME)
            info.external_attr = (0o40755 << 16) | 0x10
            zf.writestr(info, b"")
        for rel in sorted(entries):
            data, mode = entries[rel]
            info = zipfile.ZipInfo(f"{name}/{rel}", ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100000 | mode) << 16
            zf.writestr(info, data)
    return buf.getvalue()


def on_disk(d):
    out = {}
    if d.is_dir():
        for path in sorted(d.rglob("*")):
            if path.is_file() and path.name not in SKIP_NAMES and "__pycache__" not in path.parts:
                mode = 0o755 if path.stat().st_mode & stat.S_IXUSR else 0o644
                out[path.relative_to(d).as_posix()] = (path.read_bytes(), mode)
    return out


def main(argv):
    check = "--check" in argv
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    drift = 0
    names = []
    for skill in SKILLS:
        name = PREFIX + skill
        names.append(name)
        files = files_for(skill, version)
        dst = OUT / "skills" / name
        archive = OUT / f"{name}-skill.zip"
        blob = build_zip(name, files, version)
        if check:
            if on_disk(dst) != files:
                print(f"DRIFT: grokbot/skills/{name}", file=sys.stderr); drift = 1
            if not archive.is_file() or archive.read_bytes() != blob:
                print(f"DRIFT: grokbot/{archive.name}", file=sys.stderr); drift = 1
            continue
        shutil.rmtree(dst, ignore_errors=True)
        for rel, (data, mode) in files.items():
            path = dst / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            path.chmod(mode)
        archive.write_bytes(blob)
        print(f"Built grokbot/{archive.name}")
    if check:
        known = {f"{n}-skill.zip" for n in names}
        for extra in sorted(OUT.glob("*-skill.zip")):
            if extra.name not in known:
                print(f"DRIFT: grokbot/{extra.name} has no base skill", file=sys.stderr); drift = 1
        for extra in sorted((OUT / "skills").glob("*")) if (OUT / "skills").is_dir() else []:
            if extra.name not in names:
                print(f"DRIFT: grokbot/skills/{extra.name} has no base skill", file=sys.stderr); drift = 1
        if drift:
            print("ERROR: grokbot skill set is stale; run scripts/build_grokbot.py", file=sys.stderr)
    return drift


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
