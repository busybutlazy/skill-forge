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
            "Decision Readiness Summary, or equivalent evidence",
            "DECISION_READINESS_EVIDENCE.md",
            "Admission fails when readiness evidence is missing",
            "do not infer an answer",
            "do not turn a recommendation into an approved decision",
            "stop and route to `grill-with-docs`",
        ):
            self.assertIn(required, instruction)

    def test_equivalent_evidence_has_complete_scope_freshness_and_conflict_gates(self) -> None:
        evidence = (
            SKILL_DIR / "references" / "DECISION_READINESS_EVIDENCE.md"
        ).read_text(encoding="utf-8")
        for required in (
            "complete Decision Inventory",
            "decision ownership and dependencies",
            "implementation-owned defaults",
            "## Scope",
            "## Freshness",
            "## Conflict",
            "Uncovered areas are not implicitly ready",
            "routes to `grill-with-docs`",
        ):
            self.assertIn(required, evidence)

    def test_outputs_define_spec_roadmap_contracts_and_approval_packet(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        for required in (
            "`docs/SPEC.md`",
            "`docs/CONTRACTS.md`",
            "`docs/ROADMAP.md`",
            "Project Approval Packet",
            "PROJECT_DEFINITION_FORMAT.md",
        ):
            self.assertIn(required, instruction)
        definition_format = (
            SKILL_DIR / "references" / "PROJECT_DEFINITION_FORMAT.md"
        ).read_text(encoding="utf-8")
        for required in (
            "## Walking Skeleton",
            "### Observable Outcome",
            "### Acceptance Criteria",
            "### Decision Gates",
            "- Required Before:",
            "- Owner:",
            "- Current Status:",
        ):
            self.assertIn(required, definition_format)
        template = (
            SKILL_DIR / "references" / "PROJECT_APPROVAL_PACKET_TEMPLATE.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Approval Requested", template)
        self.assertIn("Blocking Open Decisions", template)
        self.assertIn("decision owner", template)
        self.assertIn("Roadmap Decision Gate or other blocking trigger", template)

    def test_contracts_are_conditional_and_not_implementation_details(self) -> None:
        definition_format = (
            SKILL_DIR / "references" / "PROJECT_DEFINITION_FORMAT.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "Create this file only when the project has an Externally Observable Contract",
            definition_format,
        )
        self.assertIn(
            "Internal implementation details are not contracts",
            definition_format,
        )

    def test_admission_and_roadmap_preserve_safe_deferral_contract(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        for required in (
            "safe-deferral rationale",
            "named owner",
            "explicit blocking trigger",
            "Map every deferred decision",
            "Each Decision Gate names the owner, required timing, and current status",
        ):
            self.assertIn(required, instruction)

    def test_walking_skeleton_and_phases_are_observable_vertical_outcomes(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        for required in (
            "Walking Skeleton: executable",
            "primary system boundaries",
            "A structural scaffold does not qualify",
            "prefer an independently acceptable Vertical Slice",
            "qualifying enabling Phase",
            "independently verifiable capability",
            "cannot be safely folded into the first dependent slice",
        ):
            self.assertIn(required, instruction)

    def test_authority_is_definition_only_and_requires_human_approval(self) -> None:
        instruction = (SKILL_DIR / "instruction.md").read_text(encoding="utf-8")
        for required in (
            "| Write production code or runtime implementation | Denied |",
            "| Add dependencies, run migrations, or establish deployment | Denied |",
            "| Approve the project or start `bootstrap-project` | Denied |",
            "explicit Human Project Approval",
        ):
            self.assertIn(required, instruction)

    def test_catalog_places_define_project_after_grilling_entrypoint(self) -> None:
        catalog = json.loads(
            (REPO_ROOT / "canonical-skills" / "catalog.json").read_text(encoding="utf-8")
        )
        group = next(item for item in catalog["groups"] if item["name"] == "Project Lifecycle")
        self.assertEqual(
            group["skills"],
            ["grill-with-docs", "define-project", "bootstrap-project", "deliver-roadmap-phase"],
        )
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
                self.assertIn(
                    "| Write production code or runtime implementation | Denied |",
                    rendered,
                )
                self.assertIn("Stop and wait for explicit human project approval", rendered)
                self.assertIn("stop and route to `grill-with-docs`", rendered)
                rendered_format = (
                    Path(result.stdout.strip())
                    / "references"
                    / "PROJECT_DEFINITION_FORMAT.md"
                ).read_text(encoding="utf-8")
                self.assertIn("### Decision Gates", rendered_format)
                rendered_evidence = (
                    Path(result.stdout.strip())
                    / "references"
                    / "DECISION_READINESS_EVIDENCE.md"
                ).read_text(encoding="utf-8")
                self.assertIn("## Freshness", rendered_evidence)

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
