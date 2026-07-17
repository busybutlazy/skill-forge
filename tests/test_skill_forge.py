from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skill_forge.agent_memory import (
    config_file_path,
    config_status,
    install_config,
    load_agent_memory,
    load_all_config_items,
    load_config_item,
    memory_file_path,
)
from skill_forge.catalog import CatalogConfig, CatalogGroup, group_skill_names, load_catalog
from skill_forge.install import list_installed
from skill_forge.menu import _pad, _visible_len
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
        self.assertIn("install-my-skill", public_skills)
        self.assertNotIn("create-skill", public_skills)
        self.assertIn("create-skill", maintainer_skills)
        self.assertIn("finalize-skill", maintainer_skills)
        self.assertIn("import-plugin-skill", maintainer_skills)
        self.assertIn("install-manager-skill", maintainer_skills)
        self.assertIn("update-skill", maintainer_skills)

    def test_install_skill_has_shared_tag(self) -> None:
        skill = load_skill(REPO_ROOT, "install-my-skill")
        self.assertEqual(skill.scope, "public")
        self.assertIn("shared", skill.tags)

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

        # Pipeline roles must be present
        self.assertIn("skillkeeper", import_instruction)
        self.assertIn("imitator", import_instruction)
        self.assertIn("reviewer", import_instruction)
        self.assertIn("skill-review-packet", import_instruction)
        # Key artifacts produced by each role
        self.assertIn("skillkeeper-initial.md", import_instruction)
        self.assertIn("source-inventory.md", import_instruction)
        self.assertIn("reviewer-report.md", import_instruction)
        self.assertIn("skillkeeper-final.md", import_instruction)
        self.assertIn("skill-review-packet.md", import_instruction)
        self.assertIn("change-request.md", import_instruction)
        self.assertIn("draft-review.md", import_instruction)
        # Human review gate before promote
        self.assertIn("使用者明確表示 draft 不再需要修改", import_instruction)
        # Promote destination includes manager-skills path
        self.assertIn("`canonical-skills/manager-skills/<skill-name>/`", import_instruction)
        # Post-promote requirements
        self.assertIn("至少做一個 Codex target smoke test", import_instruction)
        self.assertIn("只有在上述步驟都成功後，才刪除", import_instruction)

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


class CliTestCase(unittest.TestCase):
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


class WorkflowTests(CliTestCase):
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
        self.assertIn("VALID install-my-skill", result.stdout)
        self.assertIn("VALID update-skill", result.stdout)

    def test_catalog_json_lists_public_skills_for_target(self) -> None:
        result = self.run_cli("catalog", "--target", "claude", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        skills = json.loads(result.stdout)
        names = [s["name"] for s in skills]
        self.assertIn("commit", names)
        self.assertIn("install-my-skill", names)
        # maintainer-only skills must not appear in public catalog
        self.assertNotIn("create-skill", names)
        for entry in skills:
            self.assertIn("name", entry)
            self.assertIn("version", entry)
            self.assertIn("description", entry)
            self.assertIn("scope", entry)
            self.assertIn("tags", entry)

    def test_catalog_scope_all_includes_maintainer_skills(self) -> None:
        result = self.run_cli("catalog", "--target", "codex", "--scope", "all", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        skills = json.loads(result.stdout)
        names = [s["name"] for s in skills]
        self.assertIn("commit", names)
        self.assertIn("create-skill", names)

    def test_catalog_tabular_output_contains_skill_names(self) -> None:
        result = self.run_cli("catalog", "--target", "claude")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("commit", result.stdout)
        self.assertIn("install-my-skill", result.stdout)

    def test_wrapper_no_interactive_flag_stripped_from_help_text(self) -> None:
        wrapper = REPO_ROOT / "skill-manager"
        self.assertTrue(wrapper.is_file())
        content = wrapper.read_text(encoding="utf-8")
        self.assertIn("--no-interactive", content)
        self.assertIn("_NON_INTERACTIVE", content)
        self.assertIn("-T", content)

    def test_ps1_wrapper_no_interactive_support(self) -> None:
        launcher = REPO_ROOT / "skill-manager.ps1"
        content = launcher.read_text(encoding="utf-8")
        self.assertIn("IsNonInteractive", content)
        self.assertIn("--no-interactive", content)
        self.assertIn("-T", content)

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
                input_text="1\n\n2\n2\n\n8\n",
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
                input_text="1\n\n2\na\n\n8\n",
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
                input_text="1\n\n8\n",
                extra_env={
                    "SKILL_FORGE_PROJECT_HOST_DIR": "/host/project",
                },
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            clean_output = self.strip_ansi(result.stdout)
            self.assertIn("Project /host/project", clean_output)
            self.assertNotIn(".skill-forge-output", clean_output)


class CatalogTests(unittest.TestCase):
    def test_load_catalog_from_repo(self) -> None:
        catalog = load_catalog(REPO_ROOT)
        self.assertTrue(catalog.groups)
        self.assertIn("install-my-skill", catalog.recommended)
        self.assertTrue(catalog.highlight_keywords)

    def test_load_catalog_missing_file_returns_empty_config(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            catalog = load_catalog(Path(tmp_dir))
            self.assertEqual(catalog.groups, [])
            self.assertEqual(catalog.recommended, [])
            self.assertEqual(catalog.highlight_keywords, [])

    def test_load_catalog_invalid_json_returns_empty_config(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            root = Path(tmp_dir)
            (root / "canonical-skills").mkdir()
            (root / "canonical-skills" / "catalog.json").write_text("{not json", encoding="utf-8")
            catalog = load_catalog(root)
            self.assertEqual(catalog.groups, [])

    def test_group_skill_names_orders_and_dedupes(self) -> None:
        catalog = CatalogConfig(
            groups=[
                CatalogGroup(name="Git", skills=["commit", "create-pr", "missing-skill"]),
                CatalogGroup(name="Docs", skills=["dto-organizer"]),
            ],
            recommended=["commit", "unknown-skill"],
        )
        names = ["commit", "create-pr", "dto-organizer", "task-plan"]
        sections = group_skill_names(names, catalog, recommended_label="Rec", others_label="Rest")
        self.assertEqual(
            sections,
            [
                ("Rec", ["commit"]),
                ("Git", ["create-pr"]),
                ("Docs", ["dto-organizer"]),
                ("Rest", ["task-plan"]),
            ],
        )

    def test_group_skill_names_without_catalog_falls_back_to_others(self) -> None:
        sections = group_skill_names(["a", "b"], CatalogConfig())
        self.assertEqual(sections, [("Others", ["a", "b"])])

    def test_pad_ignores_ansi_escape_codes(self) -> None:
        colored = "\033[36m\033[1mcommit\033[0m"
        self.assertEqual(_visible_len(colored), len("commit"))
        self.assertEqual(_visible_len(_pad(colored, 10)) , 10)


class AgentMemoryTests(unittest.TestCase):
    def test_load_agent_memory_source(self) -> None:
        source = load_agent_memory(REPO_ROOT)
        self.assertIsNotNone(source)
        assert source is not None
        self.assertTrue(source.version)
        self.assertTrue(source.body.endswith("\n"))

    def test_memory_install_and_status_lifecycle(self) -> None:
        source = load_agent_memory(REPO_ROOT)
        assert source is not None
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            # Not installed yet.
            self.assertIsNone(config_status(source, project_root, "claude"))

            path = install_config(source, project_root, "claude")
            self.assertEqual(path, project_root / "CLAUDE.md")
            self.assertIn("skill-forge:agent-memory", path.read_text(encoding="utf-8"))

            status = config_status(source, project_root, "claude")
            assert status is not None
            self.assertEqual(status.status, "up_to_date")
            self.assertTrue(status.managed)

            # Local edits are detected as drift.
            path.write_text(path.read_text(encoding="utf-8").replace("# Agent", "# Edited"), encoding="utf-8")
            status = config_status(source, project_root, "claude")
            assert status is not None
            self.assertEqual(status.status, "drift")

            # Drift refuses plain install and requires force + confirm.
            with self.assertRaises(ValueError):
                install_config(source, project_root, "claude")
            install_config(source, project_root, "claude", force=True, confirm=lambda _: True)
            status = config_status(source, project_root, "claude")
            assert status is not None
            self.assertEqual(status.status, "up_to_date")

            # Appending after the marker is still drift, not unmanaged.
            with path.open("a", encoding="utf-8") as handle:
                handle.write("my extra note\n")
            status = config_status(source, project_root, "claude")
            assert status is not None
            self.assertEqual(status.status, "drift")

    def test_memory_version_bump_reports_update_available(self) -> None:
        import dataclasses

        source = load_agent_memory(REPO_ROOT)
        assert source is not None
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            install_config(source, project_root, "codex")
            newer = dataclasses.replace(source, version="99.0.0")
            status = config_status(newer, project_root, "codex")
            assert status is not None
            self.assertEqual(status.status, "update_available")
            # update_available overwrites without force.
            install_config(newer, project_root, "codex")
            status = config_status(newer, project_root, "codex")
            assert status is not None
            self.assertEqual(status.status, "up_to_date")

    def test_memory_refuses_unmanaged_file(self) -> None:
        source = load_agent_memory(REPO_ROOT)
        assert source is not None
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            existing = memory_file_path(project_root, "claude")
            existing.write_text("# My own CLAUDE.md\n", encoding="utf-8")

            status = config_status(source, project_root, "claude")
            assert status is not None
            self.assertEqual(status.status, "unmanaged")
            with self.assertRaises(ValueError):
                install_config(source, project_root, "claude", force=True, confirm=lambda _: True)
            self.assertEqual(existing.read_text(encoding="utf-8"), "# My own CLAUDE.md\n")


class MemoryCliTests(CliTestCase):
    def test_memory_cli_status_and_install(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            status = self.run_cli(
                "memory", "status", "--target", "codex", "--project", str(project_root), "--json"
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            payload = json.loads(status.stdout)
            self.assertEqual(payload["status"], "not_installed")

            installed = self.run_cli(
                "memory", "install", "--target", "codex", "--project", str(project_root)
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)
            self.assertTrue((project_root / "AGENTS.md").is_file())

            status = self.run_cli(
                "memory", "status", "--target", "codex", "--project", str(project_root), "--json"
            )
            payload = json.loads(status.stdout)
            self.assertEqual(payload["status"], "up_to_date")


class GuidelineConfigTests(unittest.TestCase):
    def test_load_all_config_items_includes_both_items(self) -> None:
        sources = load_all_config_items(REPO_ROOT)
        names = [source.name for source in sources]
        self.assertIn("agent-memory", names)
        self.assertIn("agent-guideline", names)

    def test_load_config_item_rejects_unknown_name(self) -> None:
        with self.assertRaises(ValueError):
            load_config_item(REPO_ROOT, "no-such-item")

    def test_guideline_install_and_status_lifecycle(self) -> None:
        source = load_config_item(REPO_ROOT, "agent-guideline")
        assert source is not None
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            # Not installed yet; install creates the docs/ parent directory.
            self.assertIsNone(config_status(source, project_root, "claude"))
            path = install_config(source, project_root, "claude")
            self.assertEqual(path, project_root / "docs" / "agent-guideline.md")
            self.assertIn("skill-forge:agent-guideline", path.read_text(encoding="utf-8"))

            status = config_status(source, project_root, "claude")
            assert status is not None
            self.assertEqual(status.status, "up_to_date")
            self.assertTrue(status.managed)

            # Local edits are detected as drift.
            with path.open("a", encoding="utf-8") as handle:
                handle.write("my extra note\n")
            status = config_status(source, project_root, "claude")
            assert status is not None
            self.assertEqual(status.status, "drift")

            # Drift refuses plain install and requires force + confirm.
            with self.assertRaises(ValueError):
                install_config(source, project_root, "claude")
            install_config(source, project_root, "claude", force=True, confirm=lambda _: True)
            status = config_status(source, project_root, "claude")
            assert status is not None
            self.assertEqual(status.status, "up_to_date")

    def test_guideline_version_bump_reports_update_available(self) -> None:
        import dataclasses

        source = load_config_item(REPO_ROOT, "agent-guideline")
        assert source is not None
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            install_config(source, project_root, "codex")
            newer = dataclasses.replace(source, version="99.0.0")
            status = config_status(newer, project_root, "codex")
            assert status is not None
            self.assertEqual(status.status, "update_available")
            # update_available overwrites without force.
            install_config(newer, project_root, "codex")
            status = config_status(newer, project_root, "codex")
            assert status is not None
            self.assertEqual(status.status, "up_to_date")

    def test_guideline_refuses_unmanaged_file(self) -> None:
        source = load_config_item(REPO_ROOT, "agent-guideline")
        assert source is not None
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            existing = config_file_path(source, project_root, "codex")
            existing.parent.mkdir(parents=True)
            existing.write_text("# My own guideline\n", encoding="utf-8")

            status = config_status(source, project_root, "codex")
            assert status is not None
            self.assertEqual(status.status, "unmanaged")
            with self.assertRaises(ValueError):
                install_config(source, project_root, "codex", force=True, confirm=lambda _: True)
            self.assertEqual(existing.read_text(encoding="utf-8"), "# My own guideline\n")


class GuidelineCliTests(CliTestCase):
    def test_guideline_status_covers_all_items(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            status = self.run_cli(
                "guideline", "status", "--target", "codex", "--project", str(project_root), "--json"
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            payloads = json.loads(status.stdout)
            names = {payload["name"] for payload in payloads}
            self.assertIn("agent-memory", names)
            self.assertIn("agent-guideline", names)
            self.assertIn("agent-hooks", names)
            for payload in payloads:
                self.assertEqual(payload["status"], "not_installed")

            plain = self.run_cli(
                "guideline", "status", "--target", "codex", "--project", str(project_root)
            )
            self.assertEqual(plain.returncode, 0, plain.stderr)
            lines = plain.stdout.strip().splitlines()
            self.assertEqual(len(lines), len(payloads))
            for line in lines:
                self.assertIn("not_installed", line)

    def test_guideline_install_all_items(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            installed = self.run_cli(
                "guideline", "install", "--target", "codex", "--project", str(project_root)
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)
            self.assertTrue((project_root / "AGENTS.md").is_file())
            self.assertTrue((project_root / "docs" / "agent-guideline.md").is_file())
            self.assertTrue((project_root / ".codex" / "hooks.json").is_file())

            status = self.run_cli(
                "guideline", "status", "--target", "codex", "--project", str(project_root), "--json"
            )
            payloads = json.loads(status.stdout)
            for payload in payloads:
                self.assertEqual(payload["status"], "up_to_date")

    def test_guideline_agent_hooks_filter_installs_bundle_and_reports_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            (project_root / ".git").mkdir()

            result = self.run_cli(
                "guideline", "install", "--item", "agent-hooks",
                "--target", "codex", "--project", str(project_root),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project_root / ".codex" / "hooks.json").is_file())
            self.assertTrue(
                (project_root / ".codex" / "hooks" / "skill-forge" / "safety_check.py").is_file()
            )
            self.assertFalse((project_root / "AGENTS.md").exists())

            status = self.run_cli(
                "guideline", "status", "--item", "agent-hooks", "--json",
                "--target", "codex", "--project", str(project_root),
            )
            payload = json.loads(status.stdout)[0]
            self.assertEqual(payload["status"], "up_to_date")
            self.assertEqual(payload["artifacts"][0]["id"], "safety-check")

    def test_guideline_agent_hooks_failure_does_not_abort_other_items(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            hooks = project_root / ".codex" / "hooks.json"
            hooks.parent.mkdir(parents=True)
            hooks.write_text("{ invalid\n", encoding="utf-8")

            result = self.run_cli(
                "guideline", "install", "--target", "codex", "--project", str(project_root)
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("agent-hooks:", result.stderr)
            self.assertTrue((project_root / "AGENTS.md").is_file())
            self.assertTrue((project_root / "docs" / "agent-guideline.md").is_file())
            self.assertEqual(hooks.read_text(encoding="utf-8"), "{ invalid\n")

    def test_guideline_item_filter_installs_single_item(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            installed = self.run_cli(
                "guideline", "install", "--item", "agent-guideline",
                "--target", "codex", "--project", str(project_root),
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)
            self.assertTrue((project_root / "docs" / "agent-guideline.md").is_file())
            self.assertFalse((project_root / "AGENTS.md").exists())

            status = self.run_cli(
                "guideline", "status", "--item", "agent-guideline",
                "--target", "codex", "--project", str(project_root), "--json",
            )
            payloads = json.loads(status.stdout)
            self.assertEqual(len(payloads), 1)
            self.assertEqual(payloads[0]["name"], "agent-guideline")
            self.assertEqual(payloads[0]["status"], "up_to_date")

    def test_guideline_unknown_item_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            result = self.run_cli(
                "guideline", "status", "--item", "no-such-item",
                "--target", "codex", "--project", str(project_root),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown config item: no-such-item", result.stderr)

    def test_guideline_install_continues_after_item_failure(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            unmanaged = project_root / "AGENTS.md"
            unmanaged.write_text("# My own AGENTS.md\n", encoding="utf-8")

            result = self.run_cli(
                "guideline", "install", "--target", "codex", "--project", str(project_root)
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("agent-memory:", result.stderr)
            self.assertIn("refusing to overwrite", result.stderr)
            # The unmanaged file is untouched, the other item still installs.
            self.assertEqual(unmanaged.read_text(encoding="utf-8"), "# My own AGENTS.md\n")
            self.assertTrue((project_root / "docs" / "agent-guideline.md").is_file())

    def test_guideline_install_continues_after_item_oserror(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            (project_root / "docs").write_text("blocks guideline directory\n", encoding="utf-8")

            result = self.run_cli(
                "guideline", "install", "--target", "codex", "--project", str(project_root)
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("agent-guideline:", result.stderr)
            self.assertTrue((project_root / "AGENTS.md").is_file())
            self.assertEqual(
                (project_root / "docs").read_text(encoding="utf-8"),
                "blocks guideline directory\n",
            )

    def test_memory_alias_produces_identical_marker(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            memory_project = Path(tmp_dir) / "memory-project"
            memory_project.mkdir()
            guideline_project = Path(tmp_dir) / "guideline-project"
            guideline_project.mkdir()

            via_memory = self.run_cli(
                "memory", "install", "--target", "codex", "--project", str(memory_project)
            )
            self.assertEqual(via_memory.returncode, 0, via_memory.stderr)
            via_guideline = self.run_cli(
                "guideline", "install", "--item", "agent-memory",
                "--target", "codex", "--project", str(guideline_project),
            )
            self.assertEqual(via_guideline.returncode, 0, via_guideline.stderr)

            memory_content = (memory_project / "AGENTS.md").read_text(encoding="utf-8")
            guideline_content = (guideline_project / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(memory_content, guideline_content)
            self.assertRegex(
                memory_content,
                r"<!-- skill-forge:agent-memory version=\S+ sha256=[0-9a-f]{64} -->\n$",
            )


class MenuOnboardingTests(CliTestCase):
    def test_onboarding_installs_baseline_for_claude(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            result = self.run_cli(
                "menu",
                "--project",
                str(project_root),
                input_text="2\n\n8\n",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            clean_output = self.strip_ansi(result.stdout)
            self.assertIn("Recommended baseline for this target:", clean_output)
            self.assertTrue((project_root / ".claude" / "settings.local.json").is_file())
            statuses = list_installed(REPO_ROOT, project_root, "claude")
            names = {status.name for status in statuses}
            self.assertIn("install-my-skill", names)

    def test_onboarding_can_be_declined(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            result = self.run_cli(
                "menu",
                "--project",
                str(project_root),
                input_text="2\nn\n8\n",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((project_root / ".claude" / "settings.local.json").exists())
            self.assertEqual(list_installed(REPO_ROOT, project_root, "claude"), [])

    def test_install_menu_shows_groups_without_configs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            result = self.run_cli(
                "menu",
                "--project",
                str(project_root),
                input_text="1\nn\n2\nq\n\n8\n",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            clean_output = self.strip_ansi(result.stdout)
            self.assertIn("★ Recommended", clean_output)
            self.assertIn("Install / Update project guideline", clean_output)
            # Config items now live in the dedicated guideline menu, not the skill install list.
            skill_menu = clean_output.split("Select skills to install or refresh:", 1)[1]
            self.assertNotIn("agent-memory", skill_menu)
            self.assertNotIn("Configs", skill_menu)

    def test_menu_guideline_installs_all_config_items(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            result = self.run_cli(
                "menu",
                "--project",
                str(project_root),
                input_text="1\nn\n3\na\n\n8\n",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            clean_output = self.strip_ansi(result.stdout)
            self.assertIn("Select guideline items to install or refresh:", clean_output)
            memory_path = project_root / "AGENTS.md"
            guideline_path = project_root / "docs" / "agent-guideline.md"
            self.assertTrue(memory_path.is_file(), clean_output)
            self.assertTrue(guideline_path.is_file(), clean_output)
            self.assertIn("skill-forge:agent-memory", memory_path.read_text(encoding="utf-8"))
            self.assertIn("skill-forge:agent-guideline", guideline_path.read_text(encoding="utf-8"))

    def test_menu_guideline_number_selects_matching_item(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            result = self.run_cli(
                "menu",
                "--project",
                str(project_root),
                input_text="1\nn\n3\n2\n\n8\n",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((project_root / "AGENTS.md").exists())
            guideline_path = project_root / "docs" / "agent-guideline.md"
            self.assertTrue(guideline_path.is_file(), self.strip_ansi(result.stdout))
            self.assertIn("skill-forge:agent-guideline", guideline_path.read_text(encoding="utf-8"))

    def test_menu_guideline_number_selects_agent_hooks_bundle(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()
            (project_root / ".git").mkdir()

            result = self.run_cli(
                "menu",
                "--project",
                str(project_root),
                input_text="1\nn\n3\n3\n\n8\n",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((project_root / ".codex" / "hooks.json").is_file())
            self.assertFalse((project_root / "AGENTS.md").exists())
            self.assertFalse((project_root / "docs" / "agent-guideline.md").exists())

    def test_status_menu_lists_guideline_items_even_when_not_installed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            project_root = Path(tmp_dir) / "project"
            project_root.mkdir()

            result = self.run_cli(
                "menu",
                "--project",
                str(project_root),
                input_text="1\nn\n1\n\n8\n",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            clean_output = self.strip_ansi(result.stdout)
            self.assertIn("No installed skills found for target codex.", clean_output)
            self.assertIn("Guideline", clean_output)
            self.assertIn("agent-memory", clean_output)
            self.assertIn("agent-guideline", clean_output)
            self.assertIn("agent-hooks", clean_output)
            self.assertIn("not installed", clean_output)


if __name__ == "__main__":
    unittest.main()
