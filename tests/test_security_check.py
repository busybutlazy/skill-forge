from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from skill_forge.security_check import (
    SECURITY_DEFAULTS,
    init_security_settings,
    remove_obsolete_security_settings,
)


class SecuritySettingsMigrationTests(unittest.TestCase):
    def test_new_defaults_do_not_include_managed_hooks_only(self) -> None:
        self.assertNotIn("allowManagedHooksOnly", SECURITY_DEFAULTS)
        with tempfile.TemporaryDirectory(prefix="skill-forge-security-") as tmp_dir:
            project = Path(tmp_dir)
            path = init_security_settings(project)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertNotIn("allowManagedHooksOnly", payload)

    def test_removes_only_obsolete_key_and_preserves_other_settings(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-security-") as tmp_dir:
            project = Path(tmp_dir)
            path = project / ".claude" / "settings.local.json"
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "allowManagedHooksOnly": True,
                        "permissions": {"allow": ["Bash(git status)"]},
                        "custom": {"keep": True},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            removed = remove_obsolete_security_settings(project)
            self.assertEqual(removed, ["allowManagedHooksOnly"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload,
                {
                    "permissions": {"allow": ["Bash(git status)"]},
                    "custom": {"keep": True},
                },
            )

    def test_invalid_json_is_not_rewritten(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-security-") as tmp_dir:
            project = Path(tmp_dir)
            path = project / ".claude" / "settings.local.json"
            path.parent.mkdir(parents=True)
            path.write_text("{ invalid\n", encoding="utf-8")
            self.assertEqual(remove_obsolete_security_settings(project), [])
            self.assertEqual(path.read_text(encoding="utf-8"), "{ invalid\n")

    def test_atomic_write_failure_preserves_original(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-security-") as tmp_dir:
            project = Path(tmp_dir)
            path = project / ".claude" / "settings.local.json"
            path.parent.mkdir(parents=True)
            original = '{"allowManagedHooksOnly": true, "keep": true}\n'
            path.write_text(original, encoding="utf-8")
            with mock.patch("skill_forge.security_check.os.replace", side_effect=OSError("failure")):
                with self.assertRaisesRegex(OSError, "failure"):
                    remove_obsolete_security_settings(project)
            self.assertEqual(path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
