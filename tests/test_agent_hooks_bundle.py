from __future__ import annotations

import json
import os
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
from skill_forge.hook_policy import HookRequest, evaluate_hook_request
from skill_forge.managed_bundles import load_managed_bundle


REPO_ROOT = Path(__file__).resolve().parents[1]


class AgentHooksBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="skill-forge-agent-hooks-")
        self.project = Path(self.temp_dir.name) / "project"
        self.project.mkdir()
        (self.project / ".git").mkdir()
        (self.project / ".git" / "HEAD").write_text("ref: refs/heads/feature/test\n")
        self.runtime = PythonRuntime(("python3",), sys.version_info[:3])

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_canonical_bundle_loads(self) -> None:
        source = load_managed_bundle(REPO_ROOT, "agent-hooks")
        self.assertIsNotNone(source)
        self.assertEqual(source.name, "agent-hooks")
        self.assertEqual(source.version, "0.3.0")
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
            ({"tool_name": "NotebookEdit", "tool_input": {"notebook_path": str(self.project / ".env.notebook")}}, False, "path.protected-write"),
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

    def test_internal_policy_and_standalone_runner_share_decision_fixtures(self) -> None:
        install_claude_hooks(REPO_ROOT, self.project, runtime=self.runtime)
        runner = self.project / ".claude" / "hooks" / "skill-forge" / "safety_check.py"
        cases = (
            ("git status", None),
            ("git reset --hard HEAD", "git.reset-hard"),
            ("git clean -fd", "git.clean-force"),
            ("git push --force origin main", "git.force-push"),
            ("rm -rf .", "shell.broad-recursive-delete"),
            ("rm -rf *", "shell.unresolved-recursive-delete"),
            ("rm -rf ./*", "shell.unresolved-recursive-delete"),
            ("rm -rf build/*.tmp", "shell.unresolved-recursive-delete"),
            ("rm -rf $DIR/*", "shell.unresolved-recursive-delete"),
            ("rm -rf build/cache", None),
            ("pip install requests", "dependency.host-install"),
            ("pip3.12 install requests", "dependency.host-install"),
            ("pip --quiet install requests", "dependency.host-install"),
            ("python3 -m pip install requests", "dependency.host-install"),
            ("uv sync", "dependency.host-install"),
            ("uv pip install requests", "dependency.host-install"),
            ("poetry add requests", "dependency.host-install"),
            ("npm ci", "dependency.host-install"),
            ("npm --prefix app install", "dependency.host-install"),
            ("pnpm install", "dependency.host-install"),
            ("yarn", "dependency.host-install"),
            ("docker run image pip install requests", None),
            ("docker compose run app npm ci", None),
            ("make setup", None),
        )
        for command, expected_rule in cases:
            with self.subTest(command=command):
                internal = evaluate_hook_request(
                    HookRequest("Bash", command, self.project, self.project)
                )
                internal_rule = None if internal.allowed else internal.rule_id
                payload = {
                    "cwd": str(self.project),
                    "hook_event_name": "PreToolUse",
                    "tool_name": "Bash",
                    "tool_input": {"command": command},
                }
                result = subprocess.run(
                    [sys.executable, str(runner)],
                    input=json.dumps(payload),
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                runner_rule = None
                if result.stdout:
                    reason = json.loads(result.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
                    runner_rule = reason.split("]", 1)[0].removeprefix("[")
                self.assertEqual(internal_rule, expected_rule)
                self.assertEqual(runner_rule, expected_rule)

    def test_runner_and_policy_block_commit_only_on_protected_branch(self) -> None:
        install_claude_hooks(REPO_ROOT, self.project, runtime=self.runtime)
        runner = self.project / ".claude" / "hooks" / "skill-forge" / "safety_check.py"
        for branch, expected_rule in (("main", "git.protected-branch-commit"), ("master", "git.protected-branch-commit"), ("feature/work", None)):
            with self.subTest(branch=branch):
                (self.project / ".git" / "HEAD").write_text(f"ref: refs/heads/{branch}\n")
                internal = evaluate_hook_request(HookRequest("Bash", "git commit -m test", self.project, self.project))
                internal_rule = None if internal.allowed else internal.rule_id
                result = subprocess.run(
                    [sys.executable, str(runner)],
                    input=json.dumps({"cwd": str(self.project), "tool_name": "Bash", "tool_input": {"command": "git commit -m test"}}),
                    text=True,
                    capture_output=True,
                    check=False,
                )
                runner_rule = None
                if result.stdout:
                    reason = json.loads(result.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
                    runner_rule = reason.split("]", 1)[0].removeprefix("[")
                self.assertEqual(internal_rule, expected_rule)
                self.assertEqual(runner_rule, expected_rule)

    def test_runner_uses_declared_project_root_when_git_is_absent(self) -> None:
        non_git = Path(self.temp_dir.name) / "non-git"
        nested = non_git / "src"
        nested.mkdir(parents=True)
        runner = REPO_ROOT / "canonical-configs" / "agent-hooks" / "hooks" / "safety_check.py"
        result = subprocess.run(
            [sys.executable, str(runner)],
            input=json.dumps({"cwd": str(nested), "tool_name": "Write", "tool_input": {"file_path": str(non_git / ".env")}}),
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(non_git)},
        )
        reason = json.loads(result.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn("path.protected-write", reason)

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
