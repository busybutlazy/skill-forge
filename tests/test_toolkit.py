from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skill_toolkit.install import list_installed
from skill_toolkit.repository import (
    load_all_skills,
    load_skill,
    validate_skill_dir,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class ValidationTests(unittest.TestCase):
    def test_all_canonical_skills_validate(self) -> None:
        for skill in load_all_skills(REPO_ROOT):
            result = validate_skill_dir(skill.root)
            self.assertTrue(result.valid, f"{skill.name}: {result.issues}")

    def test_dto_skill_has_examples_asset_projection(self) -> None:
        skill = load_skill(REPO_ROOT, "dto-organizer")
        self.assertIn("examples", skill.asset_dirs)


class WorkflowTests(unittest.TestCase):
    def run_cli(
        self,
        *args: str,
        cwd: Path | None = None,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "skill_toolkit",
                "--repo-root",
                str(REPO_ROOT),
                *args,
            ],
            cwd=str(cwd or REPO_ROOT),
            env=env,
            text=True,
            input=input_text,
            capture_output=True,
            check=False,
        )

    def test_validate_command(self) -> None:
        result = self.run_cli("validate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("VALID commit", result.stdout)
        self.assertIn("VALID create-pr", result.stdout)
        self.assertIn("VALID dto-organizer", result.stdout)

    def test_codex_install_update_list_json_and_remove_workflow(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="skill-toolkit-test-"
        ) as tmp_dir:
            temp_root = Path(tmp_dir)
            render_root = temp_root / "rendered"
            project_root = temp_root / "project"
            project_root.mkdir()

            rendered = self.run_cli(
                "render",
                "commit",
                "--target",
                "codex",
                "--output",
                str(render_root),
            )
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            rendered_skill = (
                render_root
                / ".agents"
                / "skills"
                / "commit"
                / "SKILL.md"
            )
            self.assertTrue(rendered_skill.is_file())

            installed = self.run_cli(
                "install",
                "commit",
                "--target",
                "codex",
                "--project",
                str(project_root),
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)
            installed_dir = project_root / ".agents" / "skills" / "commit"
            metadata_path = installed_dir / "metadata.json"
            skill_path = installed_dir / "SKILL.md"
            self.assertTrue(metadata_path.is_file())

            listed_json = self.run_cli(
                "list",
                "--target",
                "codex",
                "--project",
                str(project_root),
                "--json",
            )
            self.assertEqual(listed_json.returncode, 0, listed_json.stderr)
            statuses = json.loads(listed_json.stdout)
            self.assertEqual(statuses[0]["status"], "up_to_date")
            self.assertTrue(statuses[0]["managed"])

            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["version"] = "0.0.1"
            metadata_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            statuses = list_installed(REPO_ROOT, project_root, "codex")
            self.assertEqual(statuses[0].status, "update_available")

            reinstalled = self.run_cli(
                "install",
                "commit",
                "--target",
                "codex",
                "--project",
                str(project_root),
            )
            self.assertEqual(reinstalled.returncode, 0, reinstalled.stderr)
            statuses = list_installed(REPO_ROOT, project_root, "codex")
            self.assertEqual(statuses[0].status, "up_to_date")

            updated = self.run_cli(
                "update",
                "commit",
                "--target",
                "codex",
                "--project",
                str(project_root),
            )
            self.assertEqual(updated.returncode, 0, updated.stderr)
            statuses = list_installed(REPO_ROOT, project_root, "codex")
            self.assertEqual(statuses[0].status, "up_to_date")

            skill_path.write_text(
                skill_path.read_text(encoding="utf-8") + "\nmanual drift\n",
                encoding="utf-8",
            )
            statuses = list_installed(REPO_ROOT, project_root, "codex")
            self.assertEqual(statuses[0].status, "drift")

            rejected_install = self.run_cli(
                "install",
                "commit",
                "--target",
                "codex",
                "--project",
                str(project_root),
            )
            self.assertEqual(rejected_install.returncode, 1)
            self.assertIn("rerun install with --force", rejected_install.stderr)

            rejected = self.run_cli(
                "update",
                "commit",
                "--target",
                "codex",
                "--project",
                str(project_root),
            )
            self.assertEqual(rejected.returncode, 1)
            self.assertIn("rerun update with --force", rejected.stderr)

            forced_install = self.run_cli(
                "install",
                "commit",
                "--target",
                "codex",
                "--project",
                str(project_root),
                "--force",
                input_text="yes\n",
            )
            self.assertEqual(forced_install.returncode, 0, forced_install.stderr)
            statuses = list_installed(REPO_ROOT, project_root, "codex")
            self.assertEqual(statuses[0].status, "up_to_date")

            forced = self.run_cli(
                "update",
                "commit",
                "--target",
                "codex",
                "--project",
                str(project_root),
                "--force",
                input_text="yes\n",
            )
            self.assertEqual(forced.returncode, 0, forced.stderr)
            statuses = list_installed(REPO_ROOT, project_root, "codex")
            self.assertEqual(statuses[0].status, "up_to_date")

            skill_path.unlink()
            statuses = list_installed(REPO_ROOT, project_root, "codex")
            self.assertEqual(statuses[0].status, "broken")
            self.assertTrue(statuses[0].managed)

            repaired_install = self.run_cli(
                "install",
                "commit",
                "--target",
                "codex",
                "--project",
                str(project_root),
                input_text="yes\n",
            )
            self.assertEqual(repaired_install.returncode, 0, repaired_install.stderr)
            statuses = list_installed(REPO_ROOT, project_root, "codex")
            self.assertEqual(statuses[0].status, "up_to_date")

            removed = self.run_cli(
                "remove",
                "commit",
                "--target",
                "codex",
                "--project",
                str(project_root),
            )
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(installed_dir.exists())

    def test_unmanaged_codex_install_is_detected_and_not_overwritten_or_removed(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="skill-toolkit-test-"
        ) as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            unmanaged_dir = (
                project_root / ".agents" / "skills" / "commit"
            )
            unmanaged_dir.mkdir(parents=True)
            (unmanaged_dir / "SKILL.md").write_text(
                "manual\n",
                encoding="utf-8",
            )
            (unmanaged_dir / "metadata.json").write_text(
                json.dumps(
                    {
                        "name": "commit",
                        "version": "1.0.0",
                        "rendered_from": "somewhere-else/commit",
                        "source_package_sha256": "foreign",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            statuses = list_installed(REPO_ROOT, project_root, "codex")
            self.assertEqual(statuses[0].name, "commit")
            self.assertEqual(statuses[0].status, "unmanaged")
            self.assertFalse(statuses[0].managed)

            rejected_install = self.run_cli(
                "install",
                "commit",
                "--target",
                "codex",
                "--project",
                str(project_root),
            )
            self.assertEqual(rejected_install.returncode, 1)
            self.assertIn("is unmanaged; refusing to overwrite it", rejected_install.stderr)

            removed = self.run_cli(
                "remove",
                "commit",
                "--target",
                "codex",
                "--project",
                str(project_root),
            )
            self.assertEqual(removed.returncode, 1)
            self.assertIn("refusing to remove it", removed.stderr)

    def test_claude_install_broken_update_and_unmanaged_workflow(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="skill-toolkit-test-"
        ) as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            installed = self.run_cli(
                "install",
                "dto-organizer",
                "--target",
                "claude",
                "--project",
                str(project_root),
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)

            listed = self.run_cli(
                "list",
                "--target",
                "claude",
                "--project",
                str(project_root),
            )
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn("dto-organizer\tup_to_date\t", listed.stdout)

            agent_path = (
                project_root / ".claude" / "agents" / "dto-organizer.md"
            )
            content = agent_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            agent_path.write_text(
                "\n".join(lines[3:]) + "\n",
                encoding="utf-8",
            )

            statuses = list_installed(REPO_ROOT, project_root, "claude")
            self.assertEqual(statuses[0].status, "broken")
            self.assertTrue(statuses[0].managed)

            repaired = self.run_cli(
                "update",
                "dto-organizer",
                "--target",
                "claude",
                "--project",
                str(project_root),
                input_text="yes\n",
            )
            self.assertEqual(repaired.returncode, 0, repaired.stderr)
            statuses = list_installed(REPO_ROOT, project_root, "claude")
            self.assertEqual(statuses[0].status, "up_to_date")

            manual_agent = (
                project_root / ".claude" / "agents" / "commit.md"
            )
            manual_agent.parent.mkdir(parents=True, exist_ok=True)
            manual_agent.write_text(
                "---\nname: commit\n---\nmanual\n",
                encoding="utf-8",
            )

            listed_json = self.run_cli(
                "list",
                "--target",
                "claude",
                "--project",
                str(project_root),
                "--json",
            )
            self.assertEqual(listed_json.returncode, 0, listed_json.stderr)
            statuses_json = json.loads(listed_json.stdout)
            manual_status = next(
                item
                for item in statuses_json
                if item["name"] == "commit"
            )
            self.assertEqual(manual_status["status"], "unmanaged")
            self.assertFalse(manual_status["managed"])

            rejected_install = self.run_cli(
                "install",
                "commit",
                "--target",
                "claude",
                "--project",
                str(project_root),
            )
            self.assertEqual(rejected_install.returncode, 1)
            self.assertIn("is unmanaged; refusing to overwrite it", rejected_install.stderr)

            removed = self.run_cli(
                "remove",
                "dto-organizer",
                "--target",
                "claude",
                "--project",
                str(project_root),
            )
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(agent_path.exists())

    def test_menu_installs_and_lists_codex_skill(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-toolkit-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            output_root = Path(tmp_dir) / "output"
            project_root.mkdir()
            output_root.mkdir()

            result = self.run_cli(
                "menu",
                "--project",
                str(project_root),
                "--output",
                str(output_root),
                input_text="1\n2\n1\n1\n7\n",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Installed commit", result.stdout)
            self.assertIn("Target: codex", result.stdout)
            statuses = list_installed(REPO_ROOT, project_root, "codex")
            self.assertEqual(statuses[0].name, "commit")
            self.assertEqual(statuses[0].status, "up_to_date")


if __name__ == "__main__":
    unittest.main()
