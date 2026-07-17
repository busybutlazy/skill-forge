from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skill_forge.claude_hooks import PythonRuntime
from skill_forge.codex_hooks import (
    codex_feature_status,
    codex_hook_settings_status,
    install_codex_hook_settings,
)


class CodexHookSettingsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="skill-forge-codex-hooks-")
        self.project = Path(self.temp_dir.name)
        self.runtime = PythonRuntime(("python3",), (3, 11, 0))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_install_preserves_unrelated_settings_and_is_idempotent(self) -> None:
        path = self.project / ".codex" / "hooks.json"
        path.parent.mkdir(parents=True)
        unrelated = {"matcher": "Read", "hooks": [{"type": "command", "command": "echo keep"}]}
        path.write_text(json.dumps({"custom": True, "hooks": {"PreToolUse": [unrelated]}}) + "\n")

        install_codex_hook_settings(self.project, runtime=self.runtime)
        first = path.read_bytes()
        payload = json.loads(first)
        self.assertTrue(payload["custom"])
        self.assertEqual(payload["hooks"]["PreToolUse"][0], unrelated)
        self.assertEqual(codex_hook_settings_status(self.project).status, "up_to_date")
        install_codex_hook_settings(self.project, runtime=self.runtime)
        self.assertEqual(path.read_bytes(), first)

    def test_drift_requires_confirmation_and_preserves_same_group_user_handler(self) -> None:
        path = install_codex_hook_settings(self.project, runtime=self.runtime)
        payload = json.loads(path.read_text())
        payload["hooks"]["PreToolUse"][0]["hooks"][0]["timeout"] = 99
        user_handler = {"type": "command", "command": "echo keep"}
        payload["hooks"]["PreToolUse"][0]["hooks"].append(user_handler)
        path.write_text(json.dumps(payload) + "\n")

        self.assertEqual(codex_hook_settings_status(self.project).status, "drift")
        with self.assertRaisesRegex(ValueError, "--force"):
            install_codex_hook_settings(self.project, runtime=self.runtime)
        install_codex_hook_settings(
            self.project, runtime=self.runtime, force=True, confirm=lambda _: True
        )
        handlers = [
            handler
            for group in json.loads(path.read_text())["hooks"]["PreToolUse"]
            for handler in group["hooks"]
        ]
        self.assertIn(user_handler, handlers)

    def test_invalid_and_symlink_hooks_are_never_modified(self) -> None:
        path = self.project / ".codex" / "hooks.json"
        path.parent.mkdir(parents=True)
        path.write_text("{ invalid\n")
        with self.assertRaisesRegex(ValueError, "refusing to modify"):
            install_codex_hook_settings(self.project, runtime=self.runtime, force=True)
        path.unlink()
        target = self.project / "user.json"
        target.write_text("{}\n")
        path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "refusing to modify"):
            install_codex_hook_settings(self.project, runtime=self.runtime, force=True)
        self.assertEqual(target.read_text(), "{}\n")

    def test_feature_status_reports_disabled_and_invalid_config(self) -> None:
        config = self.project / ".codex" / "config.toml"
        config.parent.mkdir(parents=True)
        config.write_text("[features]\nhooks = false\n")
        self.assertFalse(codex_feature_status(self.project).enabled)
        config.write_text("[invalid\n")
        self.assertIsNone(codex_feature_status(self.project).enabled)

    def test_windows_runtime_is_not_silently_accepted(self) -> None:
        runtime = PythonRuntime(("py", "-3"), (3, 12, 0))
        with self.assertRaisesRegex(RuntimeError, "Windows launcher support is pending"):
            install_codex_hook_settings(self.project, runtime=runtime)


if __name__ == "__main__":
    unittest.main()
