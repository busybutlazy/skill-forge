from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from skill_forge.managed_bundles import (
    install_managed_bundle,
    load_managed_bundle,
    managed_bundle_status,
)


class ManagedBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="skill-forge-bundle-")
        self.root = Path(self.temp_dir.name)
        self.repo_root = self.root / "repo"
        self.project_root = self.root / "project"
        self.bundle_root = self.repo_root / "canonical-configs" / "test-hooks"
        (self.bundle_root / "hooks").mkdir(parents=True)
        self.project_root.mkdir()
        (self.bundle_root / "hooks" / "check.py").write_text("print('check')\n", encoding="utf-8")
        (self.bundle_root / "hooks" / "audit.py").write_text("print('audit')\n", encoding="utf-8")
        self.write_config()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_config(self, **overrides: object) -> None:
        config: dict[str, object] = {
            "schema_version": 1,
            "name": "test-hooks",
            "version": "1.0.0",
            "description": "test bundle",
            "updated_at": "2026-07-17",
            "artifacts": [
                {
                    "id": "safety-check",
                    "source": "hooks/check.py",
                    "targets": {
                        "codex": ".codex/hooks/check.py",
                        "claude": ".claude/hooks/check.py",
                    },
                    "comment_prefix": "#",
                    "executable": True,
                },
                {
                    "id": "audit-log",
                    "source": "hooks/audit.py",
                    "targets": {
                        "codex": ".codex/hooks/audit.py",
                        "claude": ".claude/hooks/audit.py",
                    },
                    "comment_prefix": "#",
                },
            ],
        }
        config.update(overrides)
        (self.bundle_root / "config.json").write_text(
            json.dumps(config, indent=2) + "\n",
            encoding="utf-8",
        )

    def load(self):
        source = load_managed_bundle(self.repo_root, "test-hooks")
        self.assertIsNotNone(source)
        return source

    def test_install_and_status_lifecycle_for_both_targets(self) -> None:
        for target in ("codex", "claude"):
            with self.subTest(target=target):
                project = self.project_root / target
                project.mkdir()
                source = self.load()
                self.assertEqual(managed_bundle_status(source, project, target).status, "not_installed")
                paths = install_managed_bundle(source, project, target)
                self.assertEqual(len(paths), 2)
                self.assertEqual(managed_bundle_status(source, project, target).status, "up_to_date")
                for path in paths:
                    self.assertIn(b"# skill-forge:test-hooks/", path.read_bytes())
                self.assertEqual(paths[0].stat().st_mode & 0o777, 0o755)
                self.assertEqual(paths[1].stat().st_mode & 0o777, 0o644)

    def test_partial_managed_bundle_is_broken_and_repaired(self) -> None:
        source = self.load()
        paths = install_managed_bundle(source, self.project_root, "codex")
        paths[1].unlink()
        status = managed_bundle_status(source, self.project_root, "codex")
        self.assertEqual(status.status, "broken")
        install_managed_bundle(source, self.project_root, "codex")
        self.assertEqual(managed_bundle_status(source, self.project_root, "codex").status, "up_to_date")

    def test_missing_executable_mode_is_broken_and_repaired(self) -> None:
        source = self.load()
        paths = install_managed_bundle(source, self.project_root, "codex")
        paths[0].chmod(0o644)
        self.assertEqual(managed_bundle_status(source, self.project_root, "codex").status, "broken")
        install_managed_bundle(source, self.project_root, "codex")
        self.assertEqual(paths[0].stat().st_mode & 0o777, 0o755)

    def test_unmanaged_artifact_refuses_entire_bundle_without_writes(self) -> None:
        source = self.load()
        unmanaged = self.project_root / ".codex" / "hooks" / "audit.py"
        unmanaged.parent.mkdir(parents=True)
        unmanaged.write_text("user owned\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unmanaged artifact"):
            install_managed_bundle(source, self.project_root, "codex", force=True, confirm=lambda _: True)
        self.assertEqual(unmanaged.read_text(encoding="utf-8"), "user owned\n")
        self.assertFalse((self.project_root / ".codex" / "hooks" / "check.py").exists())

    def test_drift_requires_force_and_confirmation(self) -> None:
        source = self.load()
        paths = install_managed_bundle(source, self.project_root, "codex")
        paths[0].write_text(paths[0].read_text(encoding="utf-8") + "# local edit\n", encoding="utf-8")
        self.assertEqual(managed_bundle_status(source, self.project_root, "codex").status, "drift")
        with self.assertRaisesRegex(ValueError, "--force"):
            install_managed_bundle(source, self.project_root, "codex")
        with self.assertRaisesRegex(RuntimeError, "aborted"):
            install_managed_bundle(source, self.project_root, "codex", force=True, confirm=lambda _: False)
        install_managed_bundle(source, self.project_root, "codex", force=True, confirm=lambda _: True)
        self.assertEqual(managed_bundle_status(source, self.project_root, "codex").status, "up_to_date")

    def test_version_bump_is_update_available(self) -> None:
        source = self.load()
        install_managed_bundle(source, self.project_root, "codex")
        self.write_config(version="2.0.0")
        newer = self.load()
        self.assertEqual(managed_bundle_status(newer, self.project_root, "codex").status, "update_available")
        install_managed_bundle(newer, self.project_root, "codex")
        self.assertEqual(managed_bundle_status(newer, self.project_root, "codex").status, "up_to_date")

    def test_write_failure_rolls_back_all_artifacts(self) -> None:
        source = self.load()
        original_atomic_write = __import__(
            "skill_forge.managed_bundles", fromlist=["_atomic_write"]
        )._atomic_write
        calls = 0

        def fail_second_write(path: Path, content: bytes, mode: int) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated failure")
            original_atomic_write(path, content, mode)

        with mock.patch("skill_forge.managed_bundles._atomic_write", side_effect=fail_second_write):
            with self.assertRaisesRegex(OSError, "simulated failure"):
                install_managed_bundle(source, self.project_root, "codex")
        self.assertFalse((self.project_root / ".codex" / "hooks" / "check.py").exists())
        self.assertFalse((self.project_root / ".codex" / "hooks" / "audit.py").exists())

    def test_rejects_unsafe_source_and_target_paths(self) -> None:
        unsafe_artifacts = [
            {
                "id": "escape",
                "source": "../outside.py",
                "targets": {"codex": ".codex/hooks/check.py"},
                "comment_prefix": "#",
            },
            {
                "id": "escape",
                "source": "hooks/check.py",
                "targets": {"codex": "../outside.py"},
                "comment_prefix": "#",
            },
        ]
        for artifact in unsafe_artifacts:
            with self.subTest(artifact=artifact):
                self.write_config(artifacts=[artifact])
                with self.assertRaisesRegex(ValueError, "path must stay within"):
                    load_managed_bundle(self.repo_root, "test-hooks")

    def test_rejects_duplicate_target_paths(self) -> None:
        artifacts = [
            {
                "id": artifact_id,
                "source": source,
                "targets": {"codex": ".codex/hooks/same.py"},
                "comment_prefix": "#",
            }
            for artifact_id, source in (("first", "hooks/check.py"), ("second", "hooks/audit.py"))
        ]
        self.write_config(artifacts=artifacts)
        with self.assertRaisesRegex(ValueError, "duplicate target path"):
            load_managed_bundle(self.repo_root, "test-hooks")

    def test_symlink_target_is_unmanaged_and_refused(self) -> None:
        source = self.load()
        user_file = self.root / "user-check.py"
        user_file.write_text("user owned\n", encoding="utf-8")
        target = self.project_root / ".codex" / "hooks" / "check.py"
        target.parent.mkdir(parents=True)
        target.symlink_to(user_file)
        status = managed_bundle_status(source, self.project_root, "codex")
        self.assertEqual(status.status, "unmanaged")
        with self.assertRaisesRegex(ValueError, "unmanaged artifact"):
            install_managed_bundle(source, self.project_root, "codex", force=True, confirm=lambda _: True)
        self.assertTrue(target.is_symlink())
        self.assertEqual(user_file.read_text(encoding="utf-8"), "user owned\n")


if __name__ == "__main__":
    unittest.main()
