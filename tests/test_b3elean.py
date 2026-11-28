import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERIFY_LEAN = ROOT / "execution-cron-builder" / "scripts" / "verify_lean.py"
VALIDATOR = ROOT / "execution-cron-builder" / "scripts" / "validate_blueprint_stack.py"
B3ELEAN_DIR = ROOT / "formal" / "b3elean"
HAS_LEAN = bool(shutil.which("lake") and shutil.which("lean"))

sys.path.insert(0, str(ROOT / "tests"))
from test_blueprint_stack import make_fixture


def run_vl(*args):
    return subprocess.run([sys.executable, str(VERIFY_LEAN), *args], capture_output=True, text=True)


@unittest.skipUnless(HAS_LEAN, "Lean 4 (lake/lean) not installed")
class B3ELeanTests(unittest.TestCase):
    def test_self_check_builds_and_audits_clean_axioms(self):
        r = run_vl("self-check", "--b3elean-dir", str(B3ELEAN_DIR))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("self-check passed", r.stdout)

    def test_standalone_bundled_skill_copy_runs_via_cache(self):
        bundled = ROOT / "execution-cron-builder" / "scripts" / "b3elean"
        self.assertTrue((bundled / "lakefile.toml").is_file(), "bundled b3elean must be synced into skill")
        r = run_vl("self-check", "--b3elean-dir", str(bundled))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # Ensure installed skill dir stays clean (no .lake created inside skill copy).
        self.assertFalse((bundled / ".lake").exists())

    def test_stack_native_and_kernel_cert_pass(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        manifest = make_fixture(tmp)
        r = run_vl("stack", str(manifest), "--repo-root", str(tmp), "--cert", "--b3elean-dir", str(B3ELEAN_DIR))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("b3elean CERTIFIED", r.stdout)
        self.assertIn("kernel cert verified", r.stdout)

    def test_b3elean_rejects_corrupted_ir_invariants(self):
        tmp = pathlib.Path(tempfile.mkdtemp())
        manifest = make_fixture(tmp)
        ir_path = tmp / "ir.json"
        exp = subprocess.run(
            [sys.executable, str(VALIDATOR), "export-ir", str(manifest), "--repo-root", str(tmp), "-o", str(ir_path)],
            capture_output=True, text=True,
        )
        self.assertEqual(exp.returncode, 0, exp.stderr)
        exe = B3ELEAN_DIR / ".lake" / "build" / "bin" / "b3elean"
        self.assertTrue(exe.is_file(), "b3elean binary should exist after self-check")

        # Tamper 1: inject leaf-to-leaf edge -> boundary_clean must fail.
        ir = json.loads(ir_path.read_text())
        ir["edges"].append({"from": "alpha#LA-001", "to": "beta#LB-001", "kind": "cross"})
        bad1 = tmp / "bad1.json"
        bad1.write_text(json.dumps(ir))
        r1 = subprocess.run([str(exe), "check", str(bad1)], capture_output=True, text=True)
        self.assertNotEqual(r1.returncode, 0)
        self.assertIn("boundary_clean", r1.stderr)

        # Tamper 2: inject concurrent overlapping owned_paths between alpha & beta -> paths_non_interfering must fail.
        ir2 = json.loads(ir_path.read_text())
        for n in ir2["nodes"]:
            if n["item_id"] == "LB-001":
                n["owned_paths"] = [["leaves", "alpha", "src", "main.py"]]
        bad2 = tmp / "bad2.json"
        bad2.write_text(json.dumps(ir2))
        r2 = subprocess.run([str(exe), "check", str(bad2)], capture_output=True, text=True)
        self.assertNotEqual(r2.returncode, 0)
        self.assertIn("paths_non_interfering", r2.stderr)

    def test_oracle_anti_gaming_guards(self):
        proj = pathlib.Path(tempfile.mkdtemp())
        (proj / "lean-toolchain").write_text("leanprover/lean4:v4.34.0\n", encoding="utf-8")
        (proj / "lakefile.toml").write_text(
            'name = "demo"\nversion = "0.1.0"\ndefaultTargets = ["Demo"]\n\n[[lean_lib]]\nname = "Demo"\n',
            encoding="utf-8",
        )
        (proj / "Demo").mkdir()
        (proj / "Demo.lean").write_text(
            "import Demo.Good\nimport Demo.CheatSorry\nimport Demo.CheatAxiom\nimport Demo.CheatNative\n",
            encoding="utf-8",
        )
        (proj / "Demo" / "Good.lean").write_text(
            "namespace Demo.Good\ntheorem ok (a b : Nat) : a + b = b + a := Nat.add_comm a b\nend Demo.Good\n",
            encoding="utf-8",
        )
        (proj / "Demo" / "CheatSorry.lean").write_text(
            "namespace Demo.CheatSorry\ntheorem bad_sorry : 1 = 2 := by sorry\nend Demo.CheatSorry\n",
            encoding="utf-8",
        )
        (proj / "Demo" / "CheatAxiom.lean").write_text(
            "namespace Demo.CheatAxiom\naxiom magic : 1 = 2\ntheorem bad_axiom : 1 = 2 := magic\nend Demo.CheatAxiom\n",
            encoding="utf-8",
        )
        (proj / "Demo" / "CheatNative.lean").write_text(
            "namespace Demo.CheatNative\ntheorem bad_native : (2 + 2 == 4) = true := by native_decide\nend Demo.CheatNative\n",
            encoding="utf-8",
        )

        # Good proof passes.
        ok = run_vl("oracle", "lean:Demo.Good.ok", "--project", str(proj), "--spec-dir", "Specs", "--changed-path", "Demo/Good.lean")
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)

        # Spec tampering rejected before even trusting proof.
        tamper = run_vl("oracle", "lean:Demo.Good.ok", "--project", str(proj), "--spec-dir", "Specs", "--changed-path", "Specs/Mandate.lean")
        self.assertNotEqual(tamper.returncode, 0)
        self.assertIn("read-only spec path", tamper.stderr)

        # sorry rejected.
        r_sorry = run_vl("oracle", "lean:Demo.CheatSorry.bad_sorry", "--project", str(proj))
        self.assertNotEqual(r_sorry.returncode, 0)
        self.assertIn("sorryAx", r_sorry.stderr)

        # custom axiom rejected.
        r_ax = run_vl("oracle", "lean:Demo.CheatAxiom.bad_axiom", "--project", str(proj))
        self.assertNotEqual(r_ax.returncode, 0)
        self.assertIn("Demo.CheatAxiom.magic", r_ax.stderr)

        # native_decide rejected.
        r_nat = run_vl("oracle", "lean:Demo.CheatNative.bad_native", "--project", str(proj))
        self.assertNotEqual(r_nat.returncode, 0)
        self.assertTrue(
            "native_decide" in r_nat.stderr or "Lean.ofReduceBool" in r_nat.stderr or "Lean.trustCompiler" in r_nat.stderr,
            r_nat.stderr,
        )


if __name__ == "__main__":
    unittest.main()
