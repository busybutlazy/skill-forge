from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from skill_forge.claude_hooks import (
    PythonRuntime,
    claude_hook_settings_status,
    find_python_runtime,
    install_claude_hook_settings,
)


class ClaudeHookSettingsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="skill-forge-claude-hooks-")
        self.project = Path(self.temp_dir.name)
        self.runtime = PythonRuntime(("python3",), (3, 11, 0))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_runtime_accepts_311_and_newer_without_upper_bound(self) -> None:
        for version in ("3.11.0", "3.12.9", "3.99.1"):
            with self.subTest(version=version):
                def run(*args, **kwargs):
                    return subprocess.CompletedProcess(args[0], 0, stdout=f"{version}\n", stderr="")

                runtime = find_python_runtime(candidates=(("python3",),), run=run)
                self.assertIsNotNone(runtime)
                self.assertEqual(runtime.version, tuple(map(int, version.split("."))))

    def test_runtime_rejects_old_or_missing_python(self) -> None:
        def old_python(*args, **kwargs):
            return subprocess.CompletedProcess(args[0], 0, stdout="3.10.14\n", stderr="")

        self.assertIsNone(find_python_runtime(candidates=(("python3",),), run=old_python))

        def missing_python(*args, **kwargs):
            raise FileNotFoundError

        self.assertIsNone(find_python_runtime(candidates=(("python3",),), run=missing_python))

    def test_install_adds_owned_group_and_preserves_unrelated_settings(self) -> None:
        path = self.project / ".claude" / "settings.json"
        path.parent.mkdir(parents=True)
        unrelated_group = {
            "matcher": "Write",
            "hooks": [{"type": "command", "command": "echo user-hook"}],
        }
        path.write_text(
            json.dumps({"custom": True, "hooks": {"PreToolUse": [unrelated_group]}}) + "\n",
            encoding="utf-8",
        )
        self.assertEqual(claude_hook_settings_status(self.project).status, "not_installed")
        install_claude_hook_settings(self.project, runtime=self.runtime)
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(payload["custom"])
        self.assertEqual(payload["hooks"]["PreToolUse"][0], unrelated_group)
        self.assertEqual(claude_hook_settings_status(self.project).status, "up_to_date")

    def test_reinstall_is_idempotent(self) -> None:
        path = install_claude_hook_settings(self.project, runtime=self.runtime)
        first = path.read_bytes()
        install_claude_hook_settings(self.project, runtime=self.runtime)
        self.assertEqual(path.read_bytes(), first)

    def test_drift_requires_force_and_replaces_only_owned_group(self) -> None:
        path = install_claude_hook_settings(self.project, runtime=self.runtime)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["hooks"]["PreToolUse"][0]["hooks"][0]["timeout"] = 999
        unrelated = {"matcher": "Read", "hooks": [{"type": "command", "command": "echo keep"}]}
        payload["hooks"]["PreToolUse"].append(unrelated)
        path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        self.assertEqual(claude_hook_settings_status(self.project).status, "drift")
        with self.assertRaisesRegex(ValueError, "--force"):
            install_claude_hook_settings(self.project, runtime=self.runtime)
        install_claude_hook_settings(
            self.project,
            runtime=self.runtime,
            force=True,
            confirm=lambda _: True,
        )
        updated = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn(unrelated, updated["hooks"]["PreToolUse"])
        self.assertEqual(claude_hook_settings_status(self.project).status, "up_to_date")

    def test_force_repair_preserves_user_handler_in_same_group(self) -> None:
        path = install_claude_hook_settings(self.project, runtime=self.runtime)
        payload = json.loads(path.read_text(encoding="utf-8"))
        owned_group = payload["hooks"]["PreToolUse"][0]
        user_handler = {"type": "command", "command": "echo keep-me"}
        owned_group["hooks"].append(user_handler)
        path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

        install_claude_hook_settings(
            self.project,
            runtime=self.runtime,
            force=True,
            confirm=lambda _: True,
        )
        updated = json.loads(path.read_text(encoding="utf-8"))
        all_handlers = [
            handler
            for group in updated["hooks"]["PreToolUse"]
            for handler in group["hooks"]
        ]
        self.assertIn(user_handler, all_handlers)
        self.assertEqual(claude_hook_settings_status(self.project).status, "up_to_date")

    def test_invalid_or_symlink_settings_are_never_modified(self) -> None:
        path = self.project / ".claude" / "settings.json"
        path.parent.mkdir(parents=True)
        path.write_text("{ invalid\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "refusing to modify"):
            install_claude_hook_settings(self.project, runtime=self.runtime, force=True)
        self.assertEqual(path.read_text(encoding="utf-8"), "{ invalid\n")

        path.unlink()
        user_file = self.project / "user-settings.json"
        user_file.write_text("{}\n", encoding="utf-8")
        path.symlink_to(user_file)
        with self.assertRaisesRegex(ValueError, "refusing to modify"):
            install_claude_hook_settings(self.project, runtime=self.runtime, force=True)
        self.assertTrue(path.is_symlink())
        self.assertEqual(user_file.read_text(encoding="utf-8"), "{}\n")

    def test_requires_supported_runtime_before_writing(self) -> None:
        with mock.patch("skill_forge.claude_hooks.find_python_runtime", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "Python 3.11 or newer"):
                install_claude_hook_settings(self.project, runtime=None)

        windows_runtime = PythonRuntime(("py", "-3"), (3, 12, 0))
        with self.assertRaisesRegex(RuntimeError, "Windows launcher support is pending"):
            install_claude_hook_settings(self.project, runtime=windows_runtime)
        self.assertFalse((self.project / ".claude" / "settings.json").exists())


if __name__ == "__main__":
    unittest.main()
