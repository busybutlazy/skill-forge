import json
import tempfile
import unittest
from pathlib import Path

from skill_forge.install import install_skill, list_installed
from skill_forge.repository import load_skill


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "canonical-skills" / "regular-skills" / "bootstrap-project"
REFERENCES = {
    "references/BOOTSTRAP_PLAN_TEMPLATE.md",
    "references/DOCKER_BASELINE_CHECKLIST.md",
    "references/PYTHON_PROFILE.md",
    "references/NODE_PROFILE.md",
    "references/AGENT_RULES_TEMPLATE.md",
    "references/CHANGE_ARTIFACT_TEMPLATES.md",
}


class PhaseDBootstrapContractTests(unittest.TestCase):
    def test_package_validates_and_manifest_includes_every_reference(self) -> None:
        skill = load_skill(REPO_ROOT, "bootstrap-project")
        self.assertEqual(skill.version, "0.1.0")
        self.assertEqual(skill.updated_at, "2026-07-20")
        manifest = json.loads((SKILL_DIR / "manifest.json").read_text(encoding="utf-8"))
        paths = {entry["path"] for entry in manifest["files"]}
        self.assertTrue(REFERENCES.issubset(paths))

    def test_instruction_requires_explicit_approval_before_writes(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        discovery = instruction.index("## D1 — Read-Only Discovery")
        approval = instruction.index("## D2 — Bootstrap Plan and Mandatory Approval Pause")
        writes = instruction.index("## D3 — Minimum Approved Infrastructure")
        self.assertLess(discovery, approval)
        self.assertLess(approval, writes)
        self.assertIn("Do not create or modify infrastructure until a human explicitly approves", instruction)
        self.assertIn("Material deviations require a revised plan and new approval", instruction)

    def test_instruction_pins_docker_only_and_existing_infrastructure_refusal(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        self.assertIn("There is no host fallback", instruction)
        self.assertIn("never overwrite it automatically", instruction)
        self.assertIn("Docker unavailable", instruction)
        self.assertIn("Agents, humans, and CI will use the same approved container entrypoint", instruction)

    def test_runtime_matrix_is_evidence_driven(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        for profile in ("Python", "Node/TypeScript", "Generic/unknown", "Existing container workflow"):
            self.assertIn(profile, instruction)
        python_profile = (SKILL_DIR / "references" / "PYTHON_PROFILE.md").read_text(encoding="utf-8")
        node_profile = (SKILL_DIR / "references" / "NODE_PROFILE.md").read_text(encoding="utf-8")
        self.assertIn("only from existing manifest/lock evidence", python_profile)
        self.assertIn("Multiple/conflicting lockfiles", node_profile)
        self.assertIn("Do not invent scripts", node_profile)

    def test_both_targets_install_every_reference_idempotently(self) -> None:
        for target, relative_root in (
            ("codex", Path(".agents/skills/bootstrap-project")),
            ("claude", Path(".claude/skills/bootstrap-project")),
        ):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp_dir:
                project = Path(tmp_dir)
                first = install_skill(REPO_ROOT, project, "bootstrap-project", target)
                second = install_skill(REPO_ROOT, project, "bootstrap-project", target)
                self.assertEqual(first, project / relative_root)
                self.assertEqual(second, first)
                for rel_path in REFERENCES:
                    self.assertEqual(
                        (first / rel_path).read_bytes(),
                        (SKILL_DIR / rel_path).read_bytes(),
                    )
                status = next(
                    item
                    for item in list_installed(REPO_ROOT, project, target)
                    if item.name == "bootstrap-project"
                )
                self.assertEqual(status.status, "up_to_date")
                self.assertEqual(status.source_package_sha256, load_skill(REPO_ROOT, "bootstrap-project").package_sha256)

    def test_catalog_and_guideline_mark_bootstrap_available_not_recommended(self) -> None:
        catalog = json.loads((REPO_ROOT / "canonical-skills" / "catalog.json").read_text(encoding="utf-8"))
        change_index = next(i for i, group in enumerate(catalog["groups"]) if group["name"] == "Change Workflow")
        bootstrap_index = next(i for i, group in enumerate(catalog["groups"]) if group["name"] == "Project Bootstrap")
        self.assertEqual(bootstrap_index, change_index + 1)
        self.assertEqual(catalog["groups"][bootstrap_index]["skills"], ["bootstrap-project"])
        self.assertNotIn("bootstrap-project", catalog["recommended"])

        guideline = (REPO_ROOT / "canonical-configs" / "agent-guideline" / "guideline.md").read_text(encoding="utf-8")
        self.assertIn("`bootstrap-project` 是新專案缺少容器入口時唯一受規範允許的架設路徑", guideline)
        self.assertNotIn("Phase D roadmap；目前不可用", guideline)


if __name__ == "__main__":
    unittest.main()
