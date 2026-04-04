from __future__ import annotations

import subprocess
from pathlib import Path

from .install import install_skill, list_installed, remove_skill, update_skill
from .repository import SUPPORTED_TARGETS, load_all_skills


class InteractiveMenu:
    def __init__(self, repo_root: Path, project_dir: Path, output_dir: Path, *, shell_rc: Path | None = None) -> None:
        self.repo_root = repo_root
        self.project_dir = project_dir
        self.output_dir = output_dir
        self.shell_rc = shell_rc
        self.target = "codex"

    def run(self) -> int:
        self.target = self._choose_target(initial=True)
        while True:
            self._print_summary()
            choice = self._prompt_choice(
                "Choose an action:",
                [
                    "Check installed skill status",
                    "Install a skill",
                    "Update a skill",
                    "Remove a skill",
                    "Switch target",
                    "Open expert terminal",
                    "Exit",
                ],
            )
            if choice == 1:
                self._show_statuses()
            elif choice == 2:
                self._install_skill()
            elif choice == 3:
                self._update_skill()
            elif choice == 4:
                self._remove_skill()
            elif choice == 5:
                self.target = self._choose_target(initial=False)
            elif choice == 6:
                self._open_expert_terminal()
            else:
                print("Exiting skill manager.")
                return 0

    def _statuses(self):
        return list_installed(self.repo_root, self.project_dir, self.target)

    def _print_summary(self) -> None:
        statuses = self._statuses()
        counts: dict[str, int] = {}
        for item in statuses:
            counts[item.status] = counts.get(item.status, 0) + 1
        parts = [f"{status}={counts[status]}" for status in sorted(counts)]
        summary = ", ".join(parts) if parts else "no installed skills"
        print()
        print(f"Target: {self.target}")
        print(f"Project: {self.project_dir}")
        print(f"Output: {self.output_dir}")
        print(f"Status summary: {summary}")
        print()

    def _show_statuses(self) -> None:
        statuses = self._statuses()
        print()
        if not statuses:
            print(f"No installed skills found for target {self.target}.")
            return
        print("Installed skills:")
        for item in statuses:
            details = f" ({item.details})" if item.details else ""
            version = item.version or "-"
            print(f"- {item.name}: {item.status} [{version}]{details}")

    def _install_skill(self) -> None:
        skill_names = [skill.name for skill in load_all_skills(self.repo_root, target_filter={self.target})]
        if not skill_names:
            print("No canonical skills available.")
            return
        choice = self._prompt_choice("Select a skill to install:", skill_names)
        skill_name = skill_names[choice - 1]
        try:
            path = install_skill(
                self.repo_root,
                self.project_dir,
                skill_name,
                self.target,
                force=False,
                confirm=self._confirm_yes_no,
            )
        except ValueError as exc:
            message = str(exc)
            if "rerun install with --force" in message:
                if self._confirm_yes_no(f"{message}. Force overwrite? [y/N]: "):
                    path = install_skill(
                        self.repo_root,
                        self.project_dir,
                        skill_name,
                        self.target,
                        force=True,
                        confirm=self._confirm_yes_no,
                    )
                else:
                    print("Install skipped.")
                    return
            else:
                print(message)
                return
        except RuntimeError as exc:
            print(str(exc))
            return
        print(f"Installed {skill_name} to {path}")

    def _update_skill(self) -> None:
        statuses = [item for item in self._statuses() if item.managed and item.status != "up_to_date"]
        if not statuses:
            print(f"No managed skills need action for target {self.target}.")
            return
        labels = [f"{item.name} ({item.status})" for item in statuses]
        choice = self._prompt_choice("Select a skill to update or repair:", labels)
        status = statuses[choice - 1]
        try:
            path = update_skill(
                self.repo_root,
                self.project_dir,
                status.name,
                self.target,
                force=False,
                confirm=self._confirm_yes_no,
            )
        except ValueError as exc:
            message = str(exc)
            if "rerun update with --force" in message:
                if self._confirm_yes_no(f"{message}. Force overwrite? [y/N]: "):
                    path = update_skill(
                        self.repo_root,
                        self.project_dir,
                        status.name,
                        self.target,
                        force=True,
                        confirm=self._confirm_yes_no,
                    )
                else:
                    print("Update skipped.")
                    return
            else:
                print(message)
                return
        except RuntimeError as exc:
            print(str(exc))
            return
        print(f"Updated {status.name} at {path}")

    def _remove_skill(self) -> None:
        statuses = self._statuses()
        if not statuses:
            print(f"No installed skills found for target {self.target}.")
            return
        labels = [f"{item.name} ({item.status})" for item in statuses]
        choice = self._prompt_choice("Select a skill to remove:", labels)
        status = statuses[choice - 1]
        if not self._confirm_yes_no(f"Remove {status.name} from target {self.target}? [y/N]: "):
            print("Remove skipped.")
            return
        try:
            path = remove_skill(self.repo_root, self.project_dir, status.name, self.target)
        except (ValueError, FileNotFoundError) as exc:
            print(str(exc))
            return
        print(f"Removed {status.name} from {path}")

    def _choose_target(self, *, initial: bool) -> str:
        title = "Select target:" if initial else "Switch target:"
        choice = self._prompt_choice(title, list(SUPPORTED_TARGETS))
        return SUPPORTED_TARGETS[choice - 1]

    def _open_expert_terminal(self) -> None:
        if self.shell_rc is None:
            print("Expert terminal is not available in this environment.")
            return
        print("Opening expert terminal. Exit the shell to return to the menu.")
        subprocess.run(["bash", "--noprofile", "--rcfile", str(self.shell_rc)], check=False)

    def _prompt_choice(self, title: str, options: list[str]) -> int:
        while True:
            print()
            print(title)
            for index, label in enumerate(options, start=1):
                print(f"{index}. {label}")
            raw = input("> ").strip()
            if raw.isdigit():
                choice = int(raw)
                if 1 <= choice <= len(options):
                    return choice
            print("Enter one of the numbered options.")

    def _confirm_yes_no(self, prompt: str) -> bool:
        response = input(prompt).strip().lower()
        return response in {"y", "yes"}


def run_menu(repo_root: Path, project_dir: Path, output_dir: Path, *, shell_rc: Path | None = None) -> int:
    manager = InteractiveMenu(repo_root, project_dir, output_dir, shell_rc=shell_rc)
    return manager.run()
