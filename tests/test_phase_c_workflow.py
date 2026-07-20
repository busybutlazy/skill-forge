import json
import unittest
from pathlib import Path

from skill_forge.repository import load_skill


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = ["plan-change", "implement-task", "verify-change", "report-change", "review-change"]
VERSIONS = {
    "plan-change": "0.1.1",
    "implement-task": "0.1.1",
    "verify-change": "0.1.1",
    "report-change": "0.1.0",
    "review-change": "0.1.0",
}
REFERENCES = {
    "plan-change": "IMPLEMENTATION_PLAN_TEMPLATE.md",
    "implement-task": "TASK_HANDOFF_CHECKLIST.md",
    "verify-change": "VERIFICATION_REPORT_TEMPLATE.md",
    "report-change": "CHANGE_REPORT_TEMPLATE.md",
    "review-change": "REVIEW_REPORT_TEMPLATE.md",
}


class PhaseCWorkflowContractTests(unittest.TestCase):
    def test_packages_validate_and_include_owned_reference(self) -> None:
        for name in SKILLS:
            with self.subTest(skill=name):
                skill = load_skill(REPO_ROOT, name)
                self.assertEqual(skill.version, VERSIONS[name])
                self.assertEqual(skill.updated_at, "2026-07-20")
                manifest = json.loads(
                    (REPO_ROOT / "canonical-skills" / "regular-skills" / name / "manifest.json")
                    .read_text(encoding="utf-8")
                )
                paths = {entry["path"] for entry in manifest["files"]}
                self.assertIn(f"references/{REFERENCES[name]}", paths)

    def test_instructions_pin_docker_only_and_stopping_handoff(self) -> None:
        for name in SKILLS:
            with self.subTest(skill=name):
                instruction = (
                    REPO_ROOT / "canonical-skills" / "regular-skills" / name / "instruction.md"
                ).read_text(encoding="utf-8")
                self.assertIn("host", instruction.lower())
                self.assertIn("container", instruction.lower())
                self.assertIn("stop", instruction.lower())
                self.assertIn("handoff", instruction.lower())

    def test_catalog_group_is_ordered_and_not_recommended(self) -> None:
        catalog = json.loads(
            (REPO_ROOT / "canonical-skills" / "catalog.json").read_text(encoding="utf-8")
        )
        group = next(group for group in catalog["groups"] if group["name"] == "Change Workflow")
        self.assertEqual(group["skills"], SKILLS)
        self.assertTrue(set(SKILLS).isdisjoint(catalog["recommended"]))

    def test_guideline_marks_phase_c_skills_available(self) -> None:
        guideline = (
            REPO_ROOT / "canonical-configs" / "agent-guideline" / "guideline.md"
        ).read_text(encoding="utf-8")
        self.assertIn("已提供的 Change Workflow skills", guideline)
        for name in SKILLS:
            self.assertIn(f"`{name}`", guideline)

    def test_delivered_bootstrap_is_not_described_as_future_roadmap(self) -> None:
        stale_phrases = ("bootstrap-project` roadmap", "Phase D `bootstrap-project`", "future `bootstrap-project`")
        for name in ("plan-change", "implement-task", "verify-change"):
            instruction = (
                REPO_ROOT / "canonical-skills" / "regular-skills" / name / "instruction.md"
            ).read_text(encoding="utf-8")
            for phrase in stale_phrases:
                self.assertNotIn(phrase, instruction)


if __name__ == "__main__":
    unittest.main()
