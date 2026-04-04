from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skill_toolkit.install import list_installed
from skill_toolkit.repository import load_all_skills, load_skill, validate_skill_dir


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
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        return subprocess.run(
            [sys.executable, "-m", "skill_toolkit", "--repo-root", str(REPO_ROOT), *args],
            cwd=str(cwd or REPO_ROOT),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_validate_command(self) -> None:
        result = self.run_cli("validate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("VALID commit", result.stdout)
        self.assertIn("VALID create-pr", result.stdout)
        self.assertIn("VALID dto-organizer", result.stdout)

    def test_render_install_list_remove_codex(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-toolkit-test-") as tmp_dir:
            temp_root = Path(tmp_dir)
            render_root = temp_root / "rendered"
            project_root = temp_root / "project"
            project_root.mkdir()

            rendered = self.run_cli("render", "commit", "--target", "codex", "--output", str(render_root))
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            rendered_skill = render_root / ".agents" / "skills" / "commit" / "SKILL.md"
            self.assertTrue(rendered_skill.is_file())

            installed = self.run_cli("install", "commit", "--target", "codex", "--project", str(project_root))
            self.assertEqual(installed.returncode, 0, installed.stderr)
            metadata_path = project_root / ".agents" / "skills" / "commit" / "metadata.json"
            self.assertTrue(metadata_path.is_file())

            listed = self.run_cli("list", "--target", "codex", "--project", str(project_root))
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn("\tup_to_date\t", listed.stdout)

            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["source_package_sha256"] = "drifted"
            metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            statuses = list_installed(REPO_ROOT, project_root, "codex")
            self.assertEqual(statuses[0].status, "drift")

            removed = self.run_cli("remove", "commit", "--target", "codex", "--project", str(project_root))
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse((project_root / ".agents" / "skills" / "commit").exists())

    def test_render_install_list_remove_claude(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-toolkit-test-") as tmp_dir:
            temp_root = Path(tmp_dir)
            render_root = temp_root / "rendered"
            project_root = temp_root / "project"
            project_root.mkdir()

            rendered = self.run_cli("render", "dto-organizer", "--target", "claude", "--output", str(render_root))
            self.assertEqual(rendered.returncode, 0, rendered.stderr)
            rendered_file = render_root / ".claude" / "agents" / "dto-organizer.md"
            rendered_assets = render_root / ".claude" / "agents" / "dto-organizer.assets" / "examples" / "DTO_2026-04-02.md"
            self.assertTrue(rendered_file.is_file())
            self.assertTrue(rendered_assets.is_file())

            installed = self.run_cli("install", "dto-organizer", "--target", "claude", "--project", str(project_root))
            self.assertEqual(installed.returncode, 0, installed.stderr)

            listed = self.run_cli("list", "--target", "claude", "--project", str(project_root))
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn("dto-organizer\tup_to_date\t", listed.stdout)

            removed = self.run_cli("remove", "dto-organizer", "--target", "claude", "--project", str(project_root))
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse((project_root / ".claude" / "agents" / "dto-organizer.md").exists())


if __name__ == "__main__":
    unittest.main()
