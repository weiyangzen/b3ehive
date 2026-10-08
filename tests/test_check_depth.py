import contextlib
import io
import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "learn-cron-builder" / "scripts"))
import check_depth as cd  # noqa: E402

GOOD = """# src/ledger.py

## What
Appends rows to the run ledger.

## How
- Single writer per ledger — evidence: `src/ledger.py:41`

## Why
### Single writer per ledger
- driver: concurrent appends corrupted rows (commit `a1b2c3d`)
- alternatives: file locks per append — worse: slower and fails on network disks
- tradeoff: writes queue behind one process
- significance: recovery replays a single ordered log
- level: V (commit `a1b2c3d`)
"""


class DepthTests(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())

    def note(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def run_check(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            code = cd.main([*args, str(self.root)])
        return code, err.getvalue()

    def test_complete_note_passes_why(self):
        self.note("src/ledger.py_learn.md", GOOD)
        self.assertEqual(self.run_check("--depth", "why")[0], 0)

    def test_what_depth_ignores_missing_sections(self):
        self.note("a.py_learn.md", "# a.py\n\nPurpose only.\n")
        self.assertEqual(self.run_check("--depth", "what")[0], 0)

    def test_how_requires_evidence(self):
        self.note("a.py_learn.md", "## What\nx\n\n## How\n- Keeps things clean\n")
        code, err = self.run_check("--depth", "how")
        self.assertEqual(code, 1)
        self.assertIn("lacks evidence", err)

    def test_why_requires_all_fields(self):
        self.note("a.py_learn.md", GOOD.replace("- tradeoff: writes queue behind one process\n", ""))
        code, err = self.run_check("--depth", "why")
        self.assertEqual(code, 1)
        self.assertIn("lacks tradeoff", err)

    def test_verified_level_needs_citation(self):
        self.note("a.py_learn.md", GOOD.replace("- level: V (commit `a1b2c3d`)", "- level: V"))
        code, err = self.run_check("--depth", "why")
        self.assertEqual(code, 1)
        self.assertIn("needs a citation", err)

    def test_inferred_level_passes(self):
        self.note("a.py_learn.md", GOOD.replace("- level: V (commit `a1b2c3d`)", "- level: I (likely to keep replay simple)"))
        self.assertEqual(self.run_check("--depth", "why")[0], 0)

    def test_depth_map_raises_depth_for_core_only(self):
        self.note("core/a.py_learn.md", GOOD)
        self.note("util/b.py_learn.md", "# b.py\nshort\n")
        depth_map = self.root.parent / f"{self.root.name}_map.tsv"
        depth_map.write_text("core/*\twhy\n")
        self.assertEqual(self.run_check("--depth", "what", "--map", str(depth_map))[0], 0)
        self.note("core/c.py_learn.md", "# c.py\nshort\n")
        self.assertEqual(self.run_check("--depth", "what", "--map", str(depth_map))[0], 1)


if __name__ == "__main__":
    unittest.main()
