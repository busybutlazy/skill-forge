import json
import unittest
from pathlib import Path

from skill_forge.repository import load_skill


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "canonical-skills" / "regular-skills"


class ProjectLifecycleRoutingTests(unittest.TestCase):
    def test_ambiguous_new_project_routes_to_grill_with_docs(self) -> None:
        guideline = (
            REPO_ROOT / "canonical-configs" / "agent-guideline" / "guideline.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "New or ambiguous project | `grill-with-docs` → `define-project`",
            guideline,
        )
        self.assertIn("模糊或有重大未決策：`grill-with-docs`", guideline)
        self.assertIn(
            "並非所有專案都必須先執行 `grill-with-docs`",
            guideline,
        )

    def test_resolved_and_approved_projects_route_to_correct_entrypoints(self) -> None:
        guideline = (
            REPO_ROOT / "canonical-configs" / "agent-guideline" / "guideline.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "決策已完整但尚未形成正式專案文件：`define-project`",
            guideline,
        )
        self.assertIn(
            "已有人類批准的 Project Definition，但缺開發基線：`bootstrap-project`",
            guideline,
        )
        self.assertIn(
            "已批准 Roadmap 且準備交付一個明確 Phase：`deliver-roadmap-phase`",
            guideline,
        )

    def test_plan_change_stops_for_load_bearing_ambiguity(self) -> None:
        instruction = (SKILLS_ROOT / "plan-change" / "instruction.md").read_text(
            encoding="utf-8"
        )
        for marker in (
            "## Decision Readiness Gate",
            "load-bearing product",
            "stop and route to `grill-with-docs`",
            "Do not resolve them by assumption",
        ):
            self.assertIn(marker, instruction)

    def test_bootstrap_requires_approved_definition_for_greenfield_only(self) -> None:
        instruction = (
            SKILLS_ROOT / "bootstrap-project" / "instruction.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "## Project Readiness Gate",
            "an approval-ready Project Definition exists",
            "a human has explicitly approved that Project Definition",
            "Never invent architecture or product decisions",
            "An existing project that only lacks an engineering baseline",
        ):
            self.assertIn(marker, instruction)

    def test_phase_requires_approved_outcome_and_resolved_blockers(self) -> None:
        instruction = (
            SKILLS_ROOT / "deliver-roadmap-phase" / "instruction.md"
        ).read_text(encoding="utf-8")
        for marker in (
            "## Phase Readiness Gate",
            "approved observable outcome, scope, acceptance criteria",
            "undecided external",
            "stop and route to `grill-with-docs`",
            "Do not conduct a full",
        ):
            self.assertIn(marker, instruction)

    def test_catalog_shows_ordered_project_start_path_without_internal_methods(self) -> None:
        catalog = json.loads(
            (REPO_ROOT / "canonical-skills" / "catalog.json").read_text(encoding="utf-8")
        )
        group = next(item for item in catalog["groups"] if item["name"] == "Start a Project")
        self.assertEqual(
            group["skills"],
            [
                "grill-with-docs",
                "define-project",
                "bootstrap-project",
                "deliver-roadmap-phase",
            ],
        )
        self.assertNotIn("grilling", group["skills"])
        self.assertNotIn("domain-modeling", group["skills"])

    def test_updated_skills_keep_existing_authority_semantics(self) -> None:
        for name in ("plan-change", "bootstrap-project", "deliver-roadmap-phase"):
            self.assertEqual(load_skill(REPO_ROOT, name).scope, "public")


if __name__ == "__main__":
    unittest.main()
