import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skill_forge.repository import load_skill


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "canonical-skills" / "regular-skills" / "define-project"


class DefineProjectTests(unittest.TestCase):
    def test_admission_requires_decision_readiness_and_routes_blockers(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        for required in (
            "Decision Readiness Summary or equivalent evidence",
            "If decision-readiness evidence is missing",
            "do not infer an answer",
            "do not turn a recommendation into an approved decision",
            "stop and route to `grill-with-docs`",
        ):
            self.assertIn(required, instruction)

    def test_outputs_define_spec_roadmap_contracts_and_approval_packet(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        for required in (
            "`docs/SPEC.md`",
            "`docs/CONTRACTS.md`",
            "`docs/ROADMAP.md`",
            "Project Approval Packet",
            "## Walking Skeleton",
            "### Observable Outcome",
            "### Acceptance Criteria",
        ):
            self.assertIn(required, instruction)
        template = (
            SKILL_DIR / "references" / "PROJECT_APPROVAL_PACKET_TEMPLATE.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Approval Requested", template)
        self.assertIn("Blocking Open Decisions", template)

    def test_contracts_are_conditional_and_not_implementation_details(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        self.assertIn(
            "Create this only when the project has an externally observable contract",
            instruction,
        )
        self.assertIn(
            "Do not describe internal implementation details as contracts",
            instruction,
        )

    def test_walking_skeleton_and_phases_are_observable_vertical_outcomes(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        for required in (
            "genuinely executable",
            "principal system boundaries",
            "A blank scaffold does not qualify",
            "vertical outcome slice rather than a horizontal technical layer",
            "independently acceptable",
        ):
            self.assertIn(required, instruction)

    def test_authority_is_definition_only_and_requires_human_approval(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        for required in (
            "project-definition artifacts only",
            "must not write production code",
            "add dependencies",
            "run migrations",
            "approve the project",
            "start `bootstrap-project`",
            "explicit human project approval",
        ):
            self.assertIn(required, instruction)

    def test_catalog_places_define_project_after_grilling_entrypoint(self) -> None:
        catalog = json.loads(
            (REPO_ROOT / "canonical-skills" / "catalog.json").read_text(encoding="utf-8")
        )
        group = next(
            item for item in catalog["groups"]
            if item["name"] == "Project Definition / Decision Making"
        )
        self.assertEqual(group["skills"], ["grill-with-docs", "define-project"])
        self.assertNotIn("define-project", catalog["recommended"])

    def test_package_is_public_without_implementation_dependencies(self) -> None:
        skill = load_skill(REPO_ROOT, "define-project")
        self.assertEqual(skill.scope, "public")
        self.assertEqual(skill.skill_dependencies, [])
        self.assertIn("entrypoint", skill.tags)

    def test_authority_and_approval_contract_survive_both_renderers(self) -> None:
        for target in ("codex", "claude"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                result = subprocess.run(
                    [
                        sys.executable, "-m", "skill_forge", "--repo-root", str(REPO_ROOT),
                        "render", "define-project", "--target", target, "--output", tmp,
                    ],
                    cwd=REPO_ROOT,
                    env=dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src")),
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                rendered = (
                    Path(result.stdout.strip()) / "SKILL.md"
                ).read_text(encoding="utf-8")
                self.assertIn("must not write production code", rendered)
                self.assertIn("Stop and wait for explicit human project approval", rendered)
                self.assertIn("stop and route to `grill-with-docs`", rendered)

                if target == "codex":
                    agent_config = (
                        Path(result.stdout.strip()) / "agents" / "openai.yaml"
                    ).read_text(encoding="utf-8")
                    self.assertIn("allow_implicit_invocation: false", agent_config)
                else:
                    self.assertIn("disable-model-invocation: true", rendered)
                    self.assertFalse(
                        (Path(result.stdout.strip()) / "agents" / "openai.yaml").exists()
                    )


if __name__ == "__main__":
    unittest.main()
