from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skill_forge.hook_policy import HookRequest, evaluate_hook_request


class HookPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(prefix="skill-forge-hook-policy-")
        self.project_root = Path(self.temp_dir.name) / "project"
        self.project_root.mkdir()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def evaluate(self, tool_name: str, command: str, *, cwd: Path | None = None):
        return evaluate_hook_request(
            HookRequest(
                tool_name=tool_name,
                command=command,
                cwd=cwd or self.project_root,
                project_root=self.project_root,
            )
        )

    def evaluate_write(self, tool_name: str, file_path: str):
        return evaluate_hook_request(
            HookRequest(
                tool_name=tool_name,
                command="",
                cwd=self.project_root,
                project_root=self.project_root,
                file_path=file_path,
            )
        )

    def test_blocks_dangerous_git_commands_in_chains(self) -> None:
        cases = {
            "git reset --hard HEAD": "git.reset-hard",
            "git clean -fd": "git.clean-force",
            "git clean --force --directories": "git.clean-force",
            "git push origin main --force": "git.force-push",
            "FOO=bar git status && git push -f origin main": "git.force-push",
            "git status\ngit reset --hard HEAD": "git.reset-hard",
            "git -C /tmp reset --hard HEAD": "git.reset-hard",
            "sh -c 'git push --force origin main'": "git.force-push",
        }
        for command, rule_id in cases.items():
            with self.subTest(command=command):
                decision = self.evaluate("Bash", command)
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.rule_id, rule_id)

    def test_allows_non_destructive_git_commands(self) -> None:
        for command in ("git status", "git diff --check", "git reset --soft HEAD~1", "git clean -nfd", "git push origin main"):
            with self.subTest(command=command):
                self.assertTrue(self.evaluate("Bash", command).allowed)

    def test_blocks_broad_recursive_deletes_but_allows_scoped_temp_cleanup(self) -> None:
        blocked = (
            "rm -rf /",
            "rm -rf .",
            "rm --recursive --force $HOME",
            f"rm -rf {self.project_root}",
        )
        for command in blocked:
            with self.subTest(command=command):
                decision = self.evaluate("Bash", command)
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.rule_id, "shell.broad-recursive-delete")
        self.assertTrue(self.evaluate("Bash", "rm -rf /tmp/build-output").allowed)
        self.assertTrue(self.evaluate("Bash", "rm -r build-output").allowed)

    def test_blocks_recursive_forced_delete_with_unresolved_globs(self) -> None:
        for command in (
            "rm -rf *",
            "rm -rf ./*",
            "rm -rf ../*",
            "rm -rf build/*.tmp",
            "rm -rf $DIR/*",
            "rm --recursive --force 'cache/[0-9]*'",
            "rm -rf output/?",
        ):
            with self.subTest(command=command):
                decision = self.evaluate("Bash", command)
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.rule_id, "shell.unresolved-recursive-delete")

        self.assertTrue(self.evaluate("Bash", "rm -rf build/cache").allowed)
        self.assertTrue(self.evaluate("Bash", "rm -f build/*.tmp").allowed)

    def test_malformed_shell_is_denied(self) -> None:
        decision = self.evaluate("Bash", "printf 'unterminated")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.rule_id, "shell.malformed")

    def test_blocks_apply_patch_for_protected_paths(self) -> None:
        paths = (
            ".env",
            ".env.production",
            "secrets/token.txt",
            "config/credentials.json",
            ".git/config",
            ".claude/hooks/check.py",
            ".codex/hooks/check.py",
            "nested/../.env.local",
        )
        for path in paths:
            patch = f"*** Begin Patch\n*** Add File: {path}\n+value\n*** End Patch"
            with self.subTest(path=path):
                decision = self.evaluate("apply_patch", patch)
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.rule_id, "path.protected-write")

    def test_allows_apply_patch_for_normal_source_and_docs(self) -> None:
        patch = """*** Begin Patch
*** Update File: src/app.py
@@
-old
+new
*** Add File: docs/guide.md
+guide
*** End Patch"""
        self.assertTrue(self.evaluate("apply_patch", patch).allowed)

    def test_edit_and_write_protect_paths_from_claude_payloads(self) -> None:
        for tool_name in ("Edit", "Write"):
            with self.subTest(tool_name=tool_name):
                denied = self.evaluate_write(tool_name, str(self.project_root / ".env"))
                self.assertFalse(denied.allowed)
                self.assertEqual(denied.rule_id, "path.protected-write")
                self.assertTrue(
                    self.evaluate_write(tool_name, str(self.project_root / "src" / "app.py")).allowed
                )

    def test_file_write_without_path_is_denied(self) -> None:
        request = HookRequest(
            tool_name="Write",
            command="",
            cwd=self.project_root,
            project_root=self.project_root,
        )
        decision = evaluate_hook_request(request)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.rule_id, "write.malformed")

    def test_malformed_nonempty_patch_is_denied(self) -> None:
        decision = self.evaluate("apply_patch", "not an apply_patch payload")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.rule_id, "patch.malformed")

    def test_unsupported_tools_are_allowed(self) -> None:
        self.assertTrue(self.evaluate("Read", "/project/.env").allowed)


if __name__ == "__main__":
    unittest.main()
