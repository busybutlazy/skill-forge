import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skill_forge.install import list_installed
from skill_forge.repository import load_skill, resolve_skill_install_set


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "canonical-skills" / "regular-skills" / "deliver-roadmap-phase"
DEPENDENCIES = [
    "plan-change", "implement-task", "run-approved-change",
    "verify-change", "report-change", "review-change",
]


class RoadmapPhaseDeliveryTests(unittest.TestCase):
    def test_facade_contract_is_one_phase_and_preserves_authority_gates(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        for required in (
            "one approved Roadmap Phase", "PHASE_EXECUTION_PLAN.md",
            "one Phase Delivery Packet approval gate", "dependency order",
            "genuinely separate `review-change`", "Human Phase Acceptance",
            "Never commit, push, merge, release, or deploy implicitly",
        ):
            self.assertIn(required, instruction)
        self.assertIn("multiple phases", instruction)
        self.assertIn("Do not advance the Roadmap state", instruction)

    def test_package_declares_complete_atomic_workflow_bundle(self) -> None:
        skill = load_skill(REPO_ROOT, "deliver-roadmap-phase")
        self.assertEqual(skill.version, "0.2.0")
        self.assertEqual(skill.skill_dependencies, DEPENDENCIES)
        resolved = resolve_skill_install_set(
            REPO_ROOT, [skill.name], "codex", allowed_scopes={"public"}
        )
        self.assertEqual([item.name for item in resolved], [*DEPENDENCIES, skill.name])

    def test_catalog_exposes_facade_separately_from_atomic_skills(self) -> None:
        catalog = json.loads((REPO_ROOT / "canonical-skills" / "catalog.json").read_text(encoding="utf-8"))
        roadmap = next(group for group in catalog["groups"] if group["name"] == "Project Lifecycle")
        workflow = next(group for group in catalog["groups"] if group["name"] == "Change Workflow")
        self.assertEqual(
            roadmap["skills"],
            ["grill-with-docs", "define-project", "bootstrap-project", "deliver-roadmap-phase"],
        )
        self.assertEqual(workflow["skills"], DEPENDENCIES)
        self.assertNotIn("deliver-roadmap-phase", catalog["recommended"])

    def test_phase_decision_gates_block_planning_when_due(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        for required in (
            "Read every gate before planning",
            "cannot enter\nplanning when any decision required before Phase start remains unresolved",
            "route to `grill-with-docs`",
            "Decision Gates in `changes/<phase-run-id>/PHASE_REQUEST.md`",
        ):
            self.assertIn(required, instruction)

    def test_cli_installs_bundle_for_both_targets_idempotently(self) -> None:
        for target in ("codex", "claude"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp_dir:
                command = [
                    sys.executable, "-m", "skill_forge", "--repo-root", str(REPO_ROOT),
                    "install", "deliver-roadmap-phase", "--target", target,
                    "--project", tmp_dir, "--yes",
                ]
                env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src"))
                first = subprocess.run(command, cwd=REPO_ROOT, env=env, text=True, capture_output=True)
                second = subprocess.run(command, cwd=REPO_ROOT, env=env, text=True, capture_output=True)
                self.assertEqual(first.returncode, 0, first.stderr)
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertIn("Installing dependency bundle", first.stderr)
                statuses = {item.name: item.status for item in list_installed(REPO_ROOT, Path(tmp_dir), target)}
                expected = [*DEPENDENCIES, "deliver-roadmap-phase"]
                self.assertEqual({name: statuses[name] for name in expected}, {name: "up_to_date" for name in expected})


if __name__ == "__main__":
    unittest.main()
