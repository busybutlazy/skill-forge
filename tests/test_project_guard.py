from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from skill_forge.project_guard import (  # noqa: E402
    UnsafeProjectDir,
    check_project_dir,
    host_project_dir,
    project_dir_warnings,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
WRAPPER = REPO_ROOT / "skill-manager"


class CheckProjectDirTests(unittest.TestCase):
    def test_accepts_a_normal_project_dir(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            check_project_dir(Path(tmp_dir) / "project")

    def test_rejects_filesystem_root(self) -> None:
        with self.assertRaises(UnsafeProjectDir) as caught:
            check_project_dir(Path("/"))
        self.assertIn("filesystem root", str(caught.exception))

    def test_rejects_home_dir(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            with unittest.mock.patch.dict(os.environ, {"HOME": tmp_dir}, clear=False):
                with self.assertRaises(UnsafeProjectDir) as caught:
                    check_project_dir(Path(tmp_dir))
        self.assertIn("home directory", str(caught.exception))

    def test_validates_the_host_dir_when_running_in_the_container(self) -> None:
        """/workspace/project never looks unsafe; the mounted host dir might."""
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            env = {"HOME": tmp_dir, "SKILL_FORGE_PROJECT_HOST_DIR": tmp_dir}
            with unittest.mock.patch.dict(os.environ, env, clear=False):
                self.assertEqual(host_project_dir(Path("/workspace/project")), Path(tmp_dir))
                with self.assertRaises(UnsafeProjectDir):
                    check_project_dir(Path("/workspace/project"))


class ProjectDirWarningTests(unittest.TestCase):
    def test_warns_when_not_a_git_repository(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            warnings = project_dir_warnings(Path(tmp_dir))
        self.assertEqual(len(warnings), 1)
        self.assertIn("not a git repository", warnings[0])

    def test_silent_for_a_git_repository(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            (Path(tmp_dir) / ".git").mkdir()
            self.assertEqual(project_dir_warnings(Path(tmp_dir)), [])


class CliGuardTests(unittest.TestCase):
    def run_cli(self, *args: str, extra_env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        env.update(extra_env)
        return subprocess.run(
            [sys.executable, "-m", "skill_forge", "--repo-root", str(REPO_ROOT), *args],
            cwd=str(REPO_ROOT),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_warns_on_a_non_git_project_when_installing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            result = self.run_cli(
                "guideline",
                "status",
                "--target",
                "claude",
                "--project",
                tmp_dir,
                extra_env={},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            # status is read-only, so the note stays out of the way
            self.assertNotIn("not a git repository", result.stderr)

    def test_home_dir_is_rejected_before_anything_is_written(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            result = self.run_cli(
                "list",
                "--target",
                "claude",
                "--project",
                tmp_dir,
                extra_env={"HOME": tmp_dir},
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("home directory", result.stderr)
            # The startup security check must not have created settings for it.
            self.assertFalse((Path(tmp_dir) / ".claude").exists())


@unittest.skipUnless(WRAPPER.is_file(), "wrapper script is missing")
class WrapperGuardTests(unittest.TestCase):
    def run_wrapper(self, cwd: str, home: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["HOME"] = home
        return subprocess.run(
            ["sh", str(WRAPPER), "--no-interactive", "list"],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_home_dir_is_rejected_before_docker_starts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            result = self.run_wrapper(cwd=tmp_dir, home=tmp_dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("home directory", result.stderr)
        self.assertNotIn("runtime image", result.stdout)

    def test_filesystem_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-forge-test-") as tmp_dir:
            result = self.run_wrapper(cwd="/", home=tmp_dir)
        self.assertEqual(result.returncode, 1)
        self.assertIn("filesystem root", result.stderr)


if __name__ == "__main__":
    unittest.main()
