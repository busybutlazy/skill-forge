from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from skill_forge.claude_hooks import (
    PythonRuntime,
    claude_hooks_status,
    install_claude_hooks,
)
from skill_forge.codex_hooks import codex_hooks_status, install_codex_hooks
from skill_forge.managed_bundles import load_managed_bundle


REPO_ROOT = Path(__file__).resolve().parents[1]


class AgentHooksBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="skill-forge-agent-hooks-")
        self.project = Path(self.temp_dir.name) / "project"
        self.project.mkdir()
        (self.project / ".git").mkdir()
        self.runtime = PythonRuntime(("python3",), sys.version_info[:3])

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_canonical_bundle_loads(self) -> None:
        source = load_managed_bundle(REPO_ROOT, "agent-hooks")
        self.assertIsNotNone(source)
        self.assertEqual(source.name, "agent-hooks")
        self.assertEqual([artifact.spec.artifact_id for artifact in source.artifacts], ["safety-check"])

    def test_claude_install_is_transactional_and_up_to_date(self) -> None:
        with mock.patch("skill_forge.claude_hooks.find_python_runtime", return_value=self.runtime):
            self.assertEqual(claude_hooks_status(REPO_ROOT, self.project).status, "not_installed")
            paths = install_claude_hooks(REPO_ROOT, self.project, runtime=self.runtime)
            self.assertEqual(len(paths), 2)
            self.assertTrue((self.project / ".claude" / "hooks" / "skill-forge" / "safety_check.py").is_file())
            self.assertTrue((self.project / ".claude" / "settings.json").is_file())
            self.assertEqual(claude_hooks_status(REPO_ROOT, self.project).status, "up_to_date")

    def test_invalid_settings_preflight_prevents_bundle_write(self) -> None:
        settings = self.project / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text("{ invalid\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "refusing to modify"):
            install_claude_hooks(REPO_ROOT, self.project, runtime=self.runtime)
        self.assertFalse(
            (self.project / ".claude" / "hooks" / "skill-forge" / "safety_check.py").exists()
        )

    def test_settings_write_failure_rolls_back_bundle(self) -> None:
        with mock.patch("skill_forge.claude_hooks._write_json_atomic", side_effect=OSError("failure")):
            with self.assertRaisesRegex(OSError, "failure"):
                install_claude_hooks(REPO_ROOT, self.project, runtime=self.runtime)
        self.assertFalse(
            (self.project / ".claude" / "hooks" / "skill-forge" / "safety_check.py").exists()
        )
        self.assertFalse((self.project / ".claude" / "settings.json").exists())

    def test_installed_runner_allows_and_denies_real_payload_shapes(self) -> None:
        install_claude_hooks(REPO_ROOT, self.project, runtime=self.runtime)
        runner = self.project / ".claude" / "hooks" / "skill-forge" / "safety_check.py"
        cases = [
            ({"tool_name": "Bash", "tool_input": {"command": "git status"}}, True, None),
            ({"tool_name": "Bash", "tool_input": {"command": "git reset --hard HEAD"}}, False, "git.reset-hard"),
            ({"tool_name": "Write", "tool_input": {"file_path": str(self.project / "src/app.py"), "content": "ok"}}, True, None),
            ({"tool_name": "Write", "tool_input": {"file_path": str(self.project / ".env"), "content": "secret"}}, False, "path.protected-write"),
            ({"tool_name": "Edit", "tool_input": {"file_path": str(self.project / ".env.local"), "old_string": "a", "new_string": "b"}}, False, "path.protected-write"),
            ({"tool_name": "apply_patch", "tool_input": {"command": "*** Begin Patch\n*** Add File: .git/config\n+x\n*** End Patch"}}, False, "path.protected-write"),
        ]
        for partial_payload, allowed, rule_id in cases:
            payload = {
                "cwd": str(self.project),
                "hook_event_name": "PreToolUse",
                **partial_payload,
            }
            with self.subTest(payload=partial_payload):
                result = subprocess.run(
                    [sys.executable, str(runner)],
                    input=json.dumps(payload),
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                if allowed:
                    self.assertEqual(result.stdout, "")
                else:
                    output = json.loads(result.stdout)
                    reason = output["hookSpecificOutput"]["permissionDecisionReason"]
                    self.assertIn(rule_id, reason)

    def test_codex_install_is_transactional_and_reports_trust_review(self) -> None:
        paths = install_codex_hooks(REPO_ROOT, self.project, runtime=self.runtime)
        self.assertEqual(len(paths), 2)
        status = codex_hooks_status(REPO_ROOT, self.project)
        self.assertEqual(status.status, "up_to_date")
        self.assertTrue(status.trust_review_required)
        self.assertTrue((self.project / ".codex" / "hooks.json").is_file())

    def test_codex_disabled_feature_is_reported_inactive(self) -> None:
        install_codex_hooks(REPO_ROOT, self.project, runtime=self.runtime)
        config = self.project / ".codex" / "config.toml"
        config.write_text("[features]\nhooks = false\n", encoding="utf-8")
        self.assertEqual(codex_hooks_status(REPO_ROOT, self.project).status, "inactive")

    def test_codex_invalid_feature_config_is_reported_broken(self) -> None:
        install_codex_hooks(REPO_ROOT, self.project, runtime=self.runtime)
        config = self.project / ".codex" / "config.toml"
        config.write_text("[invalid\n", encoding="utf-8")
        self.assertEqual(codex_hooks_status(REPO_ROOT, self.project).status, "broken")

    def test_codex_settings_failure_rolls_back_bundle(self) -> None:
        with mock.patch("skill_forge.codex_hooks._write_json_atomic", side_effect=OSError("failure")):
            with self.assertRaisesRegex(OSError, "failure"):
                install_codex_hooks(REPO_ROOT, self.project, runtime=self.runtime)
        self.assertFalse(
            (self.project / ".codex" / "hooks" / "skill-forge" / "safety_check.py").exists()
        )


if __name__ == "__main__":
    unittest.main()
