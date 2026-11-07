import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ["compete-cron-builder", "execution-cron-builder", "learn-cron-builder",
          "optimization-cron-builder", "looper-cron-builder"]
RUNNER = "claude -p --dangerously-skip-permissions"


def build(root, *args):
    env = {**os.environ, "B3EHIVE_ROOT": str(root)}
    return subprocess.run([sys.executable, str(ROOT / "scripts" / "build_grokbot.py"), *args],
                          env=env, capture_output=True, text=True)


class GrokbotTests(unittest.TestCase):
    def test_repository_is_current(self):
        result = build(ROOT, "--check")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_every_skill_has_gate_and_runtime(self):
        for skill in SKILLS:
            text = (ROOT / "grokbot" / "skills" / f"grokbot-{skill}" / "SKILL.md").read_text()
            self.assertIn(f"name: grokbot-{skill}\n", text)
            self.assertIn("Only grokbot loads this skill.", text)
            self.assertIn(f"unzip grokbot-{skill}-skill.zip -d ~/.claude/skills/", text)
            self.assertIn("Every subagent call uses only `claude --dangerously-skip-permissions`", text)
            self.assertIn(RUNNER, text)
            self.assertLess(text.index("## Grokbot Gate"), text.index("core v2"))

    def test_zip_unpacks_into_one_named_directory(self):
        for skill in SKILLS:
            name = f"grokbot-{skill}"
            with zipfile.ZipFile(ROOT / "grokbot" / f"{name}-skill.zip") as zf:
                tops = {n.split("/")[0] for n in zf.namelist()}
                self.assertEqual(tops, {name})
                self.assertIn(f"{name}/SKILL.md", zf.namelist())
                self.assertIn(f"{name}/.b3ehive-version", zf.namelist())
                skill_md = zf.read(f"{name}/SKILL.md").decode()
                self.assertEqual(skill_md, (ROOT / "grokbot" / "skills" / name / "SKILL.md").read_text())

    def test_substrate_names_only_claude(self):
        other = re.compile(r"codex -C|grok --always-approve|run_cursor_agent|opencode run|hermes chat|--permission-mode")
        for skill in SKILLS:
            text = (ROOT / "grokbot" / "skills" / f"grokbot-{skill}" / "references" / "substrate-cron.md").read_text()
            self.assertIsNone(other.search(text))
            self.assertIn(RUNNER, text)
            self.assertIn("## Guard Tick Budget", text)

    def test_other_host_files_dropped(self):
        for skill in SKILLS:
            d = ROOT / "grokbot" / "skills" / f"grokbot-{skill}"
            self.assertFalse((d / "agents" / "openai.yaml").exists())
            self.assertFalse((d / "agents" / "cursor.yaml").exists())
            self.assertFalse((d / "references" / "transport-codex-tui.md").exists())
        self.assertNotIn("transport-codex-tui",
                         (ROOT / "grokbot" / "skills" / "grokbot-execution-cron-builder" / "SKILL.md").read_text())

    def test_build_is_reproducible(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        for d in SKILLS + ["core"]:
            shutil.copytree(ROOT / d, tmp / d)
        shutil.copy(ROOT / "VERSION", tmp / "VERSION")
        self.assertEqual(build(tmp).returncode, 0)
        for skill in SKILLS:
            name = f"grokbot-{skill}-skill.zip"
            self.assertEqual((tmp / "grokbot" / name).read_bytes(), (ROOT / "grokbot" / name).read_bytes())

    def test_base_edit_shows_drift(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        for d in SKILLS + ["core", "grokbot"]:
            shutil.copytree(ROOT / d, tmp / d)
        shutil.copy(ROOT / "VERSION", tmp / "VERSION")
        sk = tmp / "looper-cron-builder" / "SKILL.md"
        sk.write_text(sk.read_text() + "\nchanged\n")
        result = build(tmp, "--check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DRIFT: grokbot/skills/grokbot-looper-cron-builder", result.stderr)


if __name__ == "__main__":
    unittest.main()
