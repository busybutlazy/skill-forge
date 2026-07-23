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
SKILLS_ROOT = REPO_ROOT / "canonical-skills" / "regular-skills"
DEPENDENCIES = ["grilling", "domain-modeling"]
UPSTREAM_COMMIT = "ed37663cc5fbef691ddfecd080dff42f7e7e350d"


class DecisionMethodTests(unittest.TestCase):
    def test_grill_with_docs_declares_and_resolves_dependencies(self) -> None:
        skill = load_skill(REPO_ROOT, "grill-with-docs")
        self.assertEqual(skill.skill_dependencies, DEPENDENCIES)
        resolved = resolve_skill_install_set(
            REPO_ROOT, [skill.name], "codex", allowed_scopes={"public"}
        )
        self.assertEqual([item.name for item in resolved], [*DEPENDENCIES, skill.name])

    def test_catalog_exposes_entrypoint_but_not_internal_methods(self) -> None:
        catalog = json.loads(
            (REPO_ROOT / "canonical-skills" / "catalog.json").read_text(encoding="utf-8")
        )
        group = next(item for item in catalog["groups"] if item["name"] == "Start a Project")
        self.assertEqual(
            group["skills"],
            ["grill-with-docs", "define-project", "bootstrap-project", "deliver-roadmap-phase"],
        )
        grouped = {name for item in catalog["groups"] for name in item["skills"]}
        self.assertNotIn("grilling", grouped)
        self.assertNotIn("domain-modeling", grouped)

    def test_readiness_summary_and_blocking_gate_are_required(self) -> None:
        instruction = (SKILLS_ROOT / "grill-with-docs" / "instruction.md").read_text(
            encoding="utf-8"
        )
        for heading in (
            "## Resolved Decisions",
            "## Intentionally Deferred Decisions",
            "## Blocking Open Decisions",
            "## Conflicts or Assumptions Found",
            "## Updated Artifacts",
            "## Recommended Next Workflow",
        ):
            self.assertIn(heading, instruction)
        self.assertIn("Only when `Blocking Open Decisions: None`", instruction)
        self.assertIn("Ready for define-project", instruction)

    def test_authority_adapter_survives_render_for_both_targets(self) -> None:
        required = {
            "grilling": "| Modify production code, dependencies, migrations, runtime, or deployment | Denied |",
            "domain-modeling": "| Modify production code, dependencies, migrations, runtime, or deployment | Denied |",
            "grill-with-docs": "| Write production code, dependencies, migrations, runtime, deployment, or implementation tasks | Denied |",
        }
        for target in ("codex", "claude"):
            for skill, marker in required.items():
                with self.subTest(target=target, skill=skill), tempfile.TemporaryDirectory() as tmp:
                    result = subprocess.run(
                        [
                            sys.executable, "-m", "skill_forge", "--repo-root", str(REPO_ROOT),
                            "render", skill, "--target", target, "--output", tmp,
                        ],
                        cwd=REPO_ROOT,
                        env=dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src")),
                        text=True,
                        capture_output=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    rendered = (Path(result.stdout.strip()) / "SKILL.md").read_text(
                        encoding="utf-8"
                    )
                    self.assertIn(marker, rendered)

    def test_entrypoint_invocation_gates_and_internal_method_visibility(self) -> None:
        claude_expectations = {
            "grill-with-docs": "disable-model-invocation: true",
            "grilling": "user-invocable: false",
            "domain-modeling": "user-invocable: false",
        }
        for skill, marker in claude_expectations.items():
            with self.subTest(target="claude", skill=skill), tempfile.TemporaryDirectory() as tmp:
                result = subprocess.run(
                    [
                        sys.executable, "-m", "skill_forge", "--repo-root", str(REPO_ROOT),
                        "render", skill, "--target", "claude", "--output", tmp,
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
                self.assertIn(marker, rendered)

        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable, "-m", "skill_forge", "--repo-root", str(REPO_ROOT),
                    "render", "grill-with-docs", "--target", "codex", "--output", tmp,
                ],
                cwd=REPO_ROOT,
                env=dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src")),
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            agent_config = (
                Path(result.stdout.strip()) / "agents" / "openai.yaml"
            ).read_text(encoding="utf-8")
            self.assertIn("allow_implicit_invocation: false", agent_config)

    def test_final_catalog_does_not_leave_define_project_route_dangling(self) -> None:
        entrypoint = load_skill(REPO_ROOT, "grill-with-docs")
        self.assertIn("define-project", entrypoint.instruction)
        target = load_skill(REPO_ROOT, "define-project")
        self.assertEqual(target.scope, "public")

    def test_upstream_provenance_is_discoverable(self) -> None:
        notice = (REPO_ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        for name in ("grilling", "domain-modeling", "grill-with-docs"):
            package = json.loads((SKILLS_ROOT / name / "package.json").read_text(encoding="utf-8"))
            provenance = package["provenance"]
            self.assertEqual(provenance["commit"], UPSTREAM_COMMIT)
            self.assertEqual(provenance["license"], "MIT")
            self.assertIn(name, notice)
        self.assertIn(UPSTREAM_COMMIT, notice)
        self.assertIn("Copyright (c) 2026 Matt Pocock", notice)

    def test_install_bundle_for_both_targets(self) -> None:
        for target in ("codex", "claude"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                result = subprocess.run(
                    [
                        sys.executable, "-m", "skill_forge", "--repo-root", str(REPO_ROOT),
                        "install", "grill-with-docs", "--target", target,
                        "--project", tmp, "--yes",
                    ],
                    cwd=REPO_ROOT,
                    env=dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src")),
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                statuses = {
                    item.name: item.status
                    for item in list_installed(REPO_ROOT, Path(tmp), target)
                }
                expected = [*DEPENDENCIES, "grill-with-docs"]
                self.assertEqual(
                    {name: statuses[name] for name in expected},
                    {name: "up_to_date" for name in expected},
                )

    def test_repair_and_remove_do_not_leave_dependency_manifest_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src"))
            base = [
                sys.executable, "-m", "skill_forge", "--repo-root", str(REPO_ROOT)
            ]
            install = subprocess.run(
                [
                    *base, "install", "grill-with-docs", "--target", "codex",
                    "--project", tmp, "--yes",
                ],
                cwd=REPO_ROOT, env=env, text=True, capture_output=True,
            )
            self.assertEqual(install.returncode, 0, install.stderr)

            installed_instruction = (
                Path(tmp) / ".agents" / "skills" / "grill-with-docs" / "SKILL.md"
            )
            installed_instruction.write_text(
                installed_instruction.read_text(encoding="utf-8") + "\nlocal drift\n",
                encoding="utf-8",
            )
            repair = subprocess.run(
                [
                    *base, "install", "grill-with-docs", "--target", "codex",
                    "--project", tmp, "--force", "--yes",
                ],
                cwd=REPO_ROOT, env=env, text=True, capture_output=True,
            )
            self.assertEqual(repair.returncode, 0, repair.stderr)

            remove = subprocess.run(
                [
                    *base, "remove", "grill-with-docs", "--target", "codex",
                    "--project", tmp,
                ],
                cwd=REPO_ROOT, env=env, text=True, capture_output=True,
            )
            self.assertEqual(remove.returncode, 0, remove.stderr)
            statuses = {
                item.name: item.status
                for item in list_installed(REPO_ROOT, Path(tmp), "codex")
            }
            self.assertEqual(
                {name: statuses[name] for name in DEPENDENCIES},
                {name: "up_to_date" for name in DEPENDENCIES},
            )
            self.assertNotIn("grill-with-docs", statuses)

    def test_relative_reference_links_exist(self) -> None:
        instruction = SKILLS_ROOT / "domain-modeling" / "instruction.md"
        for relative in (
            "references/CONTEXT-FORMAT.md",
            "references/ADR-FORMAT.md",
        ):
            self.assertTrue((instruction.parent / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
