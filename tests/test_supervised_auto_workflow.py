import json
import tempfile
import unittest
from pathlib import Path

from skill_forge.install import install_skill, list_installed
from skill_forge.repository import load_skill


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "canonical-skills" / "regular-skills" / "run-approved-change"


class SupervisedAutoWorkflowTests(unittest.TestCase):
    def test_plan_contract_requires_explicit_execution_policy(self) -> None:
        instruction = (
            REPO_ROOT / "canonical-skills" / "regular-skills" / "plan-change" / "instruction.md"
        ).read_text(encoding="utf-8")
        template = (
            REPO_ROOT
            / "canonical-skills"
            / "regular-skills"
            / "plan-change"
            / "references"
            / "IMPLEMENTATION_PLAN_TEMPLATE.md"
        ).read_text(encoding="utf-8")
        self.assertIn("the human must approve the mode explicitly", instruction)
        self.assertIn("## Execution Policy", template)
        self.assertIn("Risk level: low / medium / high / extreme", template)
        self.assertIn("Automation mode: one-task-at-a-time / supervised-auto", template)
        self.assertIn("Material plan changes invalidate approval", template)

    def test_auto_skill_has_narrow_admission_and_stopping_boundary(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        for required in (
            "low or medium",
            "Automation mode: supervised-auto",
            "auto-approved task IDs",
            "TASK_LOG.md",
            "evidence-only verification phase",
            "Do not switch back into implementation",
            "separate `review-change` session",
            "commit, push, merge, release",
        ):
            self.assertIn(required, instruction)
        self.assertIn("High/extreme risk", instruction)
        self.assertIn("use `implement-task` instead", instruction)

    def test_strict_implement_task_contract_is_preserved(self) -> None:
        instruction = (
            REPO_ROOT / "canonical-skills" / "regular-skills" / "implement-task" / "instruction.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Execute exactly one named task", instruction)
        self.assertIn("do not begin another task", instruction)

    def test_memory_guideline_and_catalog_agree_on_modes(self) -> None:
        memory = (REPO_ROOT / "canonical-configs" / "agent-memory" / "memory.md").read_text(encoding="utf-8")
        guideline = (
            REPO_ROOT / "canonical-configs" / "agent-guideline" / "guideline.md"
        ).read_text(encoding="utf-8")
        catalog = json.loads((REPO_ROOT / "canonical-skills" / "catalog.json").read_text(encoding="utf-8"))
        self.assertIn("預設一次一個 Task", memory)
        self.assertIn("低／中風險", memory)
        self.assertIn("完整驗證失敗", memory)
        self.assertIn("`one-task-at-a-time`", guideline)
        self.assertIn("`supervised-auto`", guideline)
        self.assertIn("完整驗證階段不得切回實作", guideline)
        group = next(group for group in catalog["groups"] if group["name"] == "Change Workflow")
        self.assertEqual(
            group["skills"],
            ["plan-change", "implement-task", "run-approved-change", "verify-change", "report-change", "review-change"],
        )
        self.assertNotIn("run-approved-change", catalog["recommended"])

    def test_both_targets_install_checklist_idempotently(self) -> None:
        source = load_skill(REPO_ROOT, "run-approved-change")
        self.assertEqual(source.version, "0.1.0")
        for target, relative_root in (
            ("codex", Path(".agents/skills/run-approved-change")),
            ("claude", Path(".claude/skills/run-approved-change")),
        ):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp_dir:
                project = Path(tmp_dir)
                first = install_skill(REPO_ROOT, project, source.name, target)
                second = install_skill(REPO_ROOT, project, source.name, target)
                self.assertEqual(first, project / relative_root)
                self.assertEqual(second, first)
                self.assertEqual(
                    (first / "references" / "AUTO_EXECUTION_CHECKLIST.md").read_bytes(),
                    (SKILL_DIR / "references" / "AUTO_EXECUTION_CHECKLIST.md").read_bytes(),
                )
                status = next(item for item in list_installed(REPO_ROOT, project, target) if item.name == source.name)
                self.assertEqual(status.status, "up_to_date")


if __name__ == "__main__":
    unittest.main()
