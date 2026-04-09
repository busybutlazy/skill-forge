from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skill_forge.install import list_installed
from skill_forge.package_ops import refresh_skill_metadata
from skill_forge.repository import (
    load_all_skills,
    load_skill,
    validate_skill_dir,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


class ValidationTests(unittest.TestCase):
    def test_windows_powershell_launcher_exists(self) -> None:
        launcher = REPO_ROOT / "skill-manager.ps1"
        content = launcher.read_text(encoding="utf-8")
        self.assertTrue(launcher.is_file())
        self.assertIn('docker compose', content)
        self.assertIn('$HOME\\skill-forge\\skill-manager.ps1', content)
        self.assertIn('/workspace/project', content)

    def test_all_canonical_skills_validate(self) -> None:
        for skill in load_all_skills(REPO_ROOT):
            result = validate_skill_dir(skill.root)
            self.assertTrue(result.valid, f"{skill.name}: {result.issues}")

    def test_scope_filtering_distinguishes_public_and_maintainer_skills(self) -> None:
        public_skills = {skill.name for skill in load_all_skills(REPO_ROOT, scopes={"public"})}
        maintainer_skills = {skill.name for skill in load_all_skills(REPO_ROOT, scopes={"maintainer"})}
        self.assertIn("commit", public_skills)
        self.assertNotIn("create-skill", public_skills)
        self.assertIn("create-skill", maintainer_skills)
        self.assertIn("finalize-skill", maintainer_skills)
        self.assertIn("import-plugin-skill", maintainer_skills)
        self.assertIn("install-manager-skill", maintainer_skills)
        self.assertIn("update-skill", maintainer_skills)

    def test_dto_skill_has_examples_asset_projection(self) -> None:
        skill = load_skill(REPO_ROOT, "dto-organizer")
        self.assertIn("examples", skill.asset_dirs)

    def test_shared_tag_marks_regular_skill_for_manager_catalog(self) -> None:
        skill = load_skill(REPO_ROOT, "commit")
        self.assertEqual(skill.scope, "public")
        self.assertIn("shared", skill.tags)

    def test_manager_skill_instructions_reference_finalize_handoff(self) -> None:
        create_instruction = (
            REPO_ROOT / "canonical-skills" / "manager-skills" / "create-skill" / "instruction.md"
        ).read_text(encoding="utf-8")
        update_instruction = (
            REPO_ROOT / "canonical-skills" / "manager-skills" / "update-skill" / "instruction.md"
        ).read_text(encoding="utf-8")
        install_instruction = (
            REPO_ROOT / "canonical-skills" / "manager-skills" / "install-manager-skill" / "instruction.md"
        ).read_text(encoding="utf-8")

        self.assertIn("finalize-skill", create_instruction)
        self.assertIn("若使用者回答 `yes`", create_instruction)
        self.assertIn("若使用者回答 `no`", create_instruction)
        self.assertIn("finalize-skill", update_instruction)
        self.assertIn("若使用者回答 `yes`", update_instruction)
        self.assertIn("若使用者回答 `no`", update_instruction)
        self.assertIn("只同步已經 finalize 完成的 canonical skills", install_instruction)

    def test_import_plugin_skill_instruction_covers_review_promotion_and_cleanup(self) -> None:
        import_instruction = (
            REPO_ROOT / "canonical-skills" / "manager-skills" / "import-plugin-skill" / "instruction.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Skill 類型判定", import_instruction)
        self.assertIn("Trigger 邊界分析", import_instruction)
        self.assertIn("Permission model 分析", import_instruction)
        self.assertIn("Failure mode 分析", import_instruction)
        self.assertIn("Canonicalization 建議", import_instruction)
        self.assertIn("Maintenance cost", import_instruction)
        self.assertIn("`review-report.md` 必須使用繁體中文撰寫", import_instruction)
        self.assertIn("先把這些內容交給使用者審查", import_instruction)
        self.assertIn("應依照 `update-skill` 的修改原則處理 staged draft", import_instruction)
        self.assertIn("change-request.md", import_instruction)
        self.assertIn("draft-review.md", import_instruction)
        self.assertIn("reviewer 只做差異審查，不自行重寫整份 draft", import_instruction)
        self.assertIn("reviewer verdict：`pass` 或 `revise`", import_instruction)
        self.assertIn("`pass` 前，不可進入 promote 問題", import_instruction)
        self.assertIn("使用者明確表示 draft 不再需要修改", import_instruction)
        self.assertIn("最新 `draft-review.md` verdict 必須是 `pass`", import_instruction)
        self.assertIn("`canonical-skills/manager-skills/<skill-name>/`", import_instruction)
        self.assertIn("至少做一個 Codex target smoke test", import_instruction)
        self.assertIn("只有在這些步驟全部成功後，才刪除", import_instruction)

    def test_refresh_skill_metadata_rebuilds_manifest_and_package_hash(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-refresh-") as tmp_dir:
            temp_root = Path(tmp_dir)
            skill_root = temp_root / "canonical-skills" / "regular-skills" / "demo"
            (skill_root / "targets").mkdir(parents=True)
            (skill_root / "instruction.md").write_text("demo\n", encoding="utf-8")
            (skill_root / "targets" / "codex.frontmatter.json").write_text(
                json.dumps({"name": "demo", "description": "demo"}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (skill_root / "targets" / "claude.frontmatter.json").write_text(
                json.dumps({"name": "demo", "description": "demo"}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            (skill_root / "package.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "identity": {
                            "name": "demo",
                            "version": "1.0.0",
                            "description": "demo",
                            "updated_at": "2026-04-01",
                            "tags": ["demo"],
                        },
                        "distribution": {"scope": "public"},
                        "content": {"instruction_file": "instruction.md"},
                        "targets": {
                            "codex": {
                                "frontmatter_file": "targets/codex.frontmatter.json",
                                "install_path": ".agents/skills/{name}/",
                            },
                            "claude": {
                                "frontmatter_file": "targets/claude.frontmatter.json",
                                "install_path": ".claude/skills/{name}/",
                            },
                        },
                        "integrity": {
                            "manifest_file": "manifest.json",
                            "package_sha256": "stale",
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (skill_root / "manifest.json").write_text(
                json.dumps({"files": [], "package_sha256": "stale"}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            result = refresh_skill_metadata(temp_root, "demo", version="1.0.1", updated_at="2026-04-04")
            manifest = json.loads((skill_root / "manifest.json").read_text(encoding="utf-8"))
            package_data = json.loads((skill_root / "package.json").read_text(encoding="utf-8"))

            self.assertEqual(result.skill, "demo")
            self.assertEqual(package_data["identity"]["version"], "1.0.1")
            self.assertEqual(package_data["identity"]["updated_at"], "2026-04-04")
            self.assertEqual(package_data["integrity"]["package_sha256"], manifest["package_sha256"])
            self.assertEqual(
                [entry["path"] for entry in manifest["files"]],
                ["instruction.md", "targets/claude.frontmatter.json", "targets/codex.frontmatter.json"],
            )


class WorkflowTests(unittest.TestCase):
    def strip_ansi(self, text: str) -> str:
        return ANSI_ESCAPE_RE.sub("", text)

    def run_cli(
        self,
        *args: str,
        cwd: Path | None = None,
        input_text: str | None = None,
        extra_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "skill_forge",
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
        self.assertIn("VALID create-skill", result.stdout)
        self.assertIn("VALID dto-organizer", result.stdout)
        self.assertIn("VALID finalize-skill", result.stdout)
        self.assertIn("VALID import-plugin-skill", result.stdout)
        self.assertIn("VALID install-manager-skill", result.stdout)
        self.assertIn("VALID update-skill", result.stdout)

    def test_codex_install_update_list_json_and_remove_workflow(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="skill-forge-test-"
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
            prefix="skill-forge-test-"
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

    def test_public_install_rejects_maintainer_scoped_skill(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            installed = self.run_cli(
                "install",
                "create-skill",
                "--target",
                "codex",
                "--project",
                str(project_root),
            )
            self.assertEqual(installed.returncode, 1)
            self.assertIn("allowed scopes: public", installed.stderr)

    def test_sync_maintainer_force_adopts_existing_unmanaged_codex_skill(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            unmanaged_dir = project_root / ".agents" / "skills" / "create-skill"
            unmanaged_dir.mkdir(parents=True)
            (unmanaged_dir / "SKILL.md").write_text("manual\n", encoding="utf-8")

            synced = self.run_cli(
                "sync-maintainer",
                "create-skill",
                "--project",
                str(project_root),
                "--target",
                "codex",
                "--force",
            )
            self.assertEqual(synced.returncode, 0, synced.stderr)
            metadata_path = unmanaged_dir / "metadata.json"
            self.assertTrue(metadata_path.is_file())
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["rendered_from"], "canonical-skills/manager-skills/create-skill")

            resynced = self.run_cli(
                "sync-maintainer",
                "create-skill",
                "--project",
                str(project_root),
                "--target",
                "codex",
            )
            self.assertEqual(resynced.returncode, 0, resynced.stderr)

            listed = self.run_cli(
                "list",
                "--target",
                "codex",
                "--project",
                str(project_root),
                "--scope",
                "all",
                "--json",
            )
            self.assertEqual(listed.returncode, 0, listed.stderr)
            statuses = json.loads(listed.stdout)
            self.assertEqual(statuses[0]["status"], "up_to_date")

    def test_sync_manager_catalog_installs_manager_and_shared_skills_for_all_targets(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            synced = self.run_cli(
                "sync-manager-catalog",
                "create-skill",
                "commit",
                "--project",
                str(project_root),
                "--target",
                "all",
            )
            self.assertEqual(synced.returncode, 0, synced.stderr)

            codex_manager_metadata = project_root / ".agents" / "skills" / "create-skill" / "metadata.json"
            codex_shared_metadata = project_root / ".agents" / "skills" / "commit" / "metadata.json"
            claude_manager_agent = project_root / ".claude" / "skills" / "create-skill" / "SKILL.md"
            claude_shared_agent = project_root / ".claude" / "skills" / "commit" / "SKILL.md"

            self.assertTrue(codex_manager_metadata.is_file())
            self.assertTrue(codex_shared_metadata.is_file())
            self.assertTrue(claude_manager_agent.is_file())
            self.assertTrue(claude_shared_agent.is_file())

            manager_metadata = json.loads(codex_manager_metadata.read_text(encoding="utf-8"))
            shared_metadata = json.loads(codex_shared_metadata.read_text(encoding="utf-8"))
            self.assertEqual(manager_metadata["rendered_from"], "canonical-skills/manager-skills/create-skill")
            self.assertEqual(shared_metadata["rendered_from"], "canonical-skills/regular-skills/commit")

    def test_sync_manager_catalog_rejects_regular_skill_without_shared_tag(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            synced = self.run_cli(
                "sync-manager-catalog",
                "dto-organizer",
                "--project",
                str(project_root),
                "--target",
                "codex",
            )
            self.assertEqual(synced.returncode, 1)
            self.assertIn("is not available in the manager catalog", synced.stderr)

    def test_claude_install_broken_update_and_unmanaged_workflow(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="skill-forge-test-"
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

            skill_dir = project_root / ".claude" / "skills" / "dto-organizer"
            agent_path = skill_dir / "SKILL.md"
            metadata_path = skill_dir / "metadata.json"
            self.assertTrue(metadata_path.is_file())
            content = agent_path.read_text(encoding="utf-8")
            self.assertNotIn("<!-- skill-forge:", content)
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(metadata["name"], "dto-organizer")

            agent_path.write_text(content.replace("---\n", "", 1), encoding="utf-8")

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

            manual_skill_dir = project_root / ".claude" / "skills" / "commit"
            manual_skill_dir.mkdir(parents=True, exist_ok=True)
            manual_agent = manual_skill_dir / "SKILL.md"
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
            self.assertEqual(manual_status["status"], "broken")
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
            self.assertFalse(skill_dir.exists())

    def test_menu_installs_and_lists_codex_skill(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            result = self.run_cli(
                "menu",
                "--project",
                str(project_root),
                input_text="1\n2\n1\n\n7\n",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            clean_output = self.strip_ansi(result.stdout)
            self.assertIn("skill-forge Manager", clean_output)
            self.assertIn("Installed commit", clean_output)
            self.assertIn("Select skills to install or refresh:", clean_output)
            self.assertIn("Press Enter to continue...", clean_output)
            statuses = list_installed(REPO_ROOT, project_root, "codex")
            self.assertEqual(statuses[0].name, "commit")
            self.assertEqual(statuses[0].status, "up_to_date")

    def test_menu_can_batch_install_skills(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            result = self.run_cli(
                "menu",
                "--project",
                str(project_root),
                input_text="1\n2\na\n\n7\n",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            statuses = list_installed(REPO_ROOT, project_root, "codex")
            installed_names = [status.name for status in statuses]
            expected_names = [
                skill.name for skill in load_all_skills(REPO_ROOT, target_filter={"codex"}, scopes={"public"})
            ]
            self.assertEqual(installed_names, expected_names)

    def test_menu_prefers_host_project_path_in_header_when_present(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            result = self.run_cli(
                "menu",
                "--project",
                str(project_root),
                input_text="1\n7\n",
                extra_env={
                    "SKILL_FORGE_PROJECT_HOST_DIR": "/host/project",
                },
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            clean_output = self.strip_ansi(result.stdout)
            self.assertIn("Project /host/project", clean_output)
            self.assertNotIn(".skill-forge-output", clean_output)


if __name__ == "__main__":
    unittest.main()
