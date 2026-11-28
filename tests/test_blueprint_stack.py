import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "execution-cron-builder" / "scripts" / "validate_blueprint_stack.py"


def run_v(*args):
    return subprocess.run([sys.executable, str(VALIDATOR), *args], capture_output=True, text=True)


def make_fixture(tmp: pathlib.Path) -> pathlib.Path:
    for d in ("docs/blueprints/leaves", "platform/contracts", "platform/core", "leaves/alpha/src", "leaves/beta/src"):
        (tmp / d).mkdir(parents=True)
    (tmp / "platform/core/lib.py").write_text("V = 1\n", encoding="utf-8")
    (tmp / "leaves/alpha/src/main.py").write_text("from platform.core import lib\n", encoding="utf-8")
    (tmp / "leaves/beta/src/main.py").write_text("from platform.core import lib\n", encoding="utf-8")

    (tmp / "docs/blueprints/00_Master_Blueprint.md").write_text(
        """# Master
```yaml
blueprint_id: top
same_name_gantt: 00_Master_Gantt.md
stable_id_pattern: '^TOP-[0-9]{3}$'
```
- [x] [TOP-001] Freeze contracts
  - owned_paths: docs/spec.md
  - oracle: verify/TOP-001.sh
  - budget: loc<2500
  - layer: L0
- [ ] [TOP-100] Close Wave 1
  - depends_on: [TOP-001, alpha#LA-001, beta#LB-001]
  - owned_paths: verify/TOP-100.sh
  - oracle: verify/TOP-100.sh
  - budget: loc<2000
  - layer: L2
""",
        encoding="utf-8",
    )
    (tmp / "docs/blueprints/01_Platform_Blueprint.md").write_text(
        """# Platform
```yaml
blueprint_id: plt
same_name_gantt: 01_Platform_Gantt.md
stable_id_pattern: '^PLT-[0-9]{3}$'
```
- [x] [PLT-001] Core contracts
  - depends_on: [top#TOP-001]
  - owned_paths: platform/contracts/
  - oracle: verify/PLT-001.sh
  - budget: loc<3000
  - layer: L0
  - capability: contracts.envelope
- [ ] [PLT-100] Harvest shared lib
  - depends_on: [PLT-001, alpha#LA-001]
  - owned_paths: platform/core/
  - oracle: verify/PLT-100.sh
  - budget: loc<3000
  - layer: L1
  - harvest: true
""",
        encoding="utf-8",
    )
    (tmp / "docs/blueprints/leaves/Alpha_Blueprint.md").write_text(
        """# Alpha
```yaml
blueprint_id: alpha
same_name_gantt: Alpha_Gantt.md
stable_id_pattern: '^LA-[0-9]{3}$'
```
- [x] [LA-001] Alpha core
  - depends_on: [plt#PLT-001]
  - owned_paths: leaves/alpha/src/
  - oracle: verify/LA-001.sh
  - budget: loc<3500
  - layer: L1
  - capability: alpha.loop
""",
        encoding="utf-8",
    )
    (tmp / "docs/blueprints/leaves/Beta_Blueprint.md").write_text(
        """# Beta
```yaml
blueprint_id: beta
same_name_gantt: Beta_Gantt.md
stable_id_pattern: '^LB-[0-9]{3}$'
```
- [ ] [LB-001] Beta core
  - depends_on: [plt#PLT-001]
  - owned_paths: leaves/beta/src/
  - oracle: verify/LB-001.sh
  - budget: loc<3500
  - layer: L1
  - capability: beta.batch
""",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "b3ehive-blueprint-stack/v1",
        "stack_id": "fixture",
        "owned_paths_policy": "dag_ordered",
        "default_budget_loc_cap": 5000,
        "layers": ["L0", "L1", "L2"],
        "blueprints": [
            {"blueprint_id": "top", "role": "master", "path": "docs/blueprints/00_Master_Blueprint.md"},
            {"blueprint_id": "plt", "role": "platform", "path": "docs/blueprints/01_Platform_Blueprint.md"},
            {"blueprint_id": "alpha", "role": "leaf", "path": "docs/blueprints/leaves/Alpha_Blueprint.md"},
            {"blueprint_id": "beta", "role": "leaf", "path": "docs/blueprints/leaves/Beta_Blueprint.md"},
        ],
        "mandatory_leaf_deps": ["plt#PLT-001"],
        "boundaries": {
            "platform_root": "platform",
            "leaf_roots": {"alpha": "leaves/alpha", "beta": "leaves/beta"},
            "code_extensions": [".py"],
        },
    }
    mp = tmp / "blueprint_stack.json"
    mp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return mp


class BlueprintStackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.manifest = make_fixture(self.tmp)

    def test_valid_stack_and_boundaries_pass(self):
        self.assertEqual(run_v("stack", str(self.manifest), "--repo-root", str(self.tmp)).returncode, 0)
        self.assertEqual(run_v("boundaries", str(self.manifest), "--repo-root", str(self.tmp)).returncode, 0)

    def test_rejects_leaf_to_leaf_and_untagged_platform_to_leaf(self):
        beta = self.tmp / "docs/blueprints/leaves/Beta_Blueprint.md"
        beta.write_text(beta.read_text().replace("[plt#PLT-001]", "[plt#PLT-001, alpha#LA-001]"))
        plt = self.tmp / "docs/blueprints/01_Platform_Blueprint.md"
        plt.write_text(plt.read_text().replace("  - harvest: true\n", ""))
        r = run_v("stack", str(self.manifest), "--repo-root", str(self.tmp))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("forbidden leaf-to-leaf", r.stderr)
        self.assertIn("forbidden platform-to-leaf", r.stderr)

    def test_rejects_global_cycle_and_transitive_acceptance_violation(self):
        alpha = self.tmp / "docs/blueprints/leaves/Alpha_Blueprint.md"
        alpha.write_text(alpha.read_text().replace("[plt#PLT-001]", "[plt#PLT-001, plt#PLT-100]"))
        r = run_v("stack", str(self.manifest), "--repo-root", str(self.tmp))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("global cross-blueprint DAG cycle", r.stderr)
        self.assertIn("accepted [x] depends on unaccepted", r.stderr)

    def test_dag_ordered_allows_ancestor_overlap_rejects_concurrent_overlap(self):
        alpha = self.tmp / "docs/blueprints/leaves/Alpha_Blueprint.md"
        alpha.write_text(
            alpha.read_text()
            + "- [ ] [LA-002] Refine\n  - depends_on: [LA-001]\n  - owned_paths: leaves/alpha/src/main.py\n"
            + "  - oracle: verify/LA-002.sh\n  - budget: loc<2000\n  - layer: L2\n"
        )
        self.assertEqual(run_v("stack", str(self.manifest), "--repo-root", str(self.tmp)).returncode, 0)
        alpha.write_text(
            alpha.read_text()
            + "- [ ] [LA-003] Race\n  - depends_on: [LA-001]\n  - owned_paths: leaves/alpha/src/main.py\n"
            + "  - oracle: verify/LA-003.sh\n  - budget: loc<2000\n  - layer: L2\n"
        )
        r = run_v("stack", str(self.manifest), "--repo-root", str(self.tmp))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("concurrent owned_paths overlap", r.stderr)

    def test_strict_disjoint_rejects_cross_blueprint_prefix_overlap(self):
        m = json.loads(self.manifest.read_text())
        m["owned_paths_policy"] = "strict_disjoint"
        self.manifest.write_text(json.dumps(m))
        beta = self.tmp / "docs/blueprints/leaves/Beta_Blueprint.md"
        beta.write_text(beta.read_text().replace("leaves/beta/src/", "platform/contracts/leak.py"))
        r = run_v("stack", str(self.manifest), "--repo-root", str(self.tmp))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("owned_paths overlap", r.stderr)

    def test_boundaries_rejects_rule_of_two_and_source_leaks(self):
        beta = self.tmp / "docs/blueprints/leaves/Beta_Blueprint.md"
        beta.write_text(beta.read_text().replace("beta.batch", "alpha.loop"))
        (self.tmp / "leaves/alpha/src/main.py").write_text("# leaves/beta/src/main.py\n")
        (self.tmp / "platform/core/lib.py").write_text("# leaves/alpha/src/main.py\n")
        r = run_v("boundaries", str(self.manifest), "--repo-root", str(self.tmp))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("Rule-of-Two", r.stderr)
        self.assertIn("sibling leakage", r.stderr)
        self.assertIn("reverse dependency", r.stderr)

    def test_export_ir_deterministic_and_cli_parity(self):
        out = self.tmp / "ir.json"
        r = run_v("export-ir", str(self.manifest), "--repo-root", str(self.tmp), "-o", str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        ir = json.loads(out.read_text())
        self.assertEqual(ir["schema_version"], "b3ehive-stack-ir/v1")
        self.assertEqual(len(ir["topo_witness"]), 6)
        self.assertLess(ir["topo_witness"].index("top#TOP-001"), ir["topo_witness"].index("plt#PLT-001"))
        cli = subprocess.run(
            [str(ROOT / "bin/b3ehive"), "validate", "export-ir", str(self.manifest), "--repo-root", str(self.tmp)],
            capture_output=True, text=True,
        )
        self.assertEqual(cli.returncode, 0, cli.stderr)
        self.assertEqual(cli.stdout, out.read_text())


if __name__ == "__main__":
    unittest.main()
