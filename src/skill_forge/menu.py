from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .install import install_skill, list_installed, remove_skill, update_skill
from .models import CanonicalSkill, InstalledStatus
from .repository import SUPPORTED_TARGETS, load_all_skills

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
CLEAR_SCREEN = "\033[2J\033[H"


def _color(text: str, *styles: str) -> str:
    return f"{''.join(styles)}{text}{RESET}"


def _status_style(status: str) -> tuple[str, ...]:
    if status == "up_to_date":
        return (GREEN, BOLD)
    if status == "update_available":
        return (YELLOW, BOLD)
    if status == "drift":
        return (YELLOW,)
    if status == "broken":
        return (RED, BOLD)
    if status == "unmanaged":
        return (BLUE,)
    return (DIM,)


class InteractiveMenu:
    def __init__(self, repo_root: Path, project_dir: Path, *, shell_rc: Path | None = None) -> None:
        self.repo_root = repo_root
        self.project_dir = project_dir
        self.shell_rc = shell_rc
        self.target = "codex"
        self.project_display_dir = Path(os.environ.get("SKILL_FORGE_PROJECT_HOST_DIR", str(project_dir)))

    def run(self) -> int:
        self.target = self._choose_target(initial=True)
        while True:
            self._clear_screen()
            self._print_header()
            choice = self._prompt_choice(
                "Choose an action:",
                [
                    "Check installed skill status",
                    "Install / Update skills",
                    "Update / Repair skills",
                    "Remove installed skills",
                    "Switch target",
                    "Open expert terminal",
                    "Exit",
                ],
            )
            if choice == 1:
                self._show_statuses()
                self._pause()
            elif choice == 2:
                self._install_skill()
                self._pause()
            elif choice == 3:
                self._update_skill()
                self._pause()
            elif choice == 4:
                self._remove_skill()
                self._pause()
            elif choice == 5:
                self.target = self._choose_target(initial=False)
            elif choice == 6:
                self._open_expert_terminal()
                self._pause()
            else:
                self._clear_screen()
                print("Exiting skill manager.")
                return 0

    def _clear_screen(self) -> None:
        print(CLEAR_SCREEN, end="")

    def _statuses(self):
        return list_installed(self.repo_root, self.project_dir, self.target)

    def _canonical_skills(self) -> list[CanonicalSkill]:
        return load_all_skills(self.repo_root, target_filter={self.target}, scopes={"public"})

    def _canonical_index(self) -> dict[str, CanonicalSkill]:
        return {skill.name: skill for skill in self._canonical_skills()}

    def _print_header(self) -> None:
        statuses = self._statuses()
        counts: dict[str, int] = {}
        for item in statuses:
            counts[item.status] = counts.get(item.status, 0) + 1
        parts = [self._render_status_badge(status, counts[status]) for status in sorted(counts)]
        summary = ", ".join(parts) if parts else "no installed skills"
        width = 62
        print()
        print(_color("╔" + "═" * width + "╗", CYAN))
        print(_color("║", CYAN) + _color("skill-forge Manager".center(width), BOLD) + _color("║", CYAN))
        print(_color("╠" + "═" * width + "╣", CYAN))
        print(_color("║", CYAN) + f" Target : {self.target:<{width - 10}}" + _color("║", CYAN))
        print(_color("║", CYAN) + f" Skills : {len(self._canonical_skills()):<{width - 10}}" + _color("║", CYAN))
        print(_color("╚" + "═" * width + "╝", CYAN))
        print(_color("Project", DIM) + f" {self.project_display_dir}")
        print(_color("Status ", DIM) + f" {summary}")
        print()

    def _render_status_badge(self, status: str, count: int | None = None) -> str:
        label = status if count is None else f"{status}={count}"
        return _color(label, *_status_style(status))

    def _render_skill_line(self, skill: CanonicalSkill, *, installed: InstalledStatus | None = None) -> str:
        source_version = _color(f"v{skill.version}", DIM)
        tags = " ".join(_color(f"#{tag}", BLUE) for tag in skill.tags[:3]) if skill.tags else _color("#untagged", DIM)
        if installed is None:
            badge = _color("not installed", DIM)
            version_note = ""
        else:
            badge = self._render_status_badge(installed.status)
            installed_version = installed.version or "unknown"
            version_note = f" {_color(f'local v{installed_version}', DIM)}"
            if installed.status == "update_available":
                version_note += f" {_color('→', DIM)} {_color(f'v{skill.version} available', YELLOW)}"
            elif installed.status == "up_to_date":
                version_note += f" {_color('✓ current', GREEN)}"
        return f"{skill.name:<16} {source_version:<18} {badge}{version_note}\n  {skill.description}\n  {tags}"

    def _show_statuses(self) -> None:
        self._clear_screen()
        self._print_header()
        statuses = self._statuses()
        sources = self._canonical_index()
        if not statuses:
            print(_color(f"No installed skills found for target {self.target}.", YELLOW))
            return
        print(_color(f"Installed skills for {self.target}:", BOLD))
        for item in statuses:
            source = sources.get(item.name)
            if source is not None:
                print(self._render_skill_line(source, installed=item))
            else:
                badge = self._render_status_badge(item.status)
                version = item.version or "unknown"
                details = f" {item.details}" if item.details else ""
                print(f"{item.name:<16} {_color(f'local v{version}', DIM)} {badge}{details}")
            if item.details:
                print(f"  {_color(item.details, DIM)}")
            print()

    def _parse_multi_select(self, raw: str, options: list[str]) -> list[int] | None:
        value = raw.strip().lower()
        if not value or value == "q":
            return None
        if value == "a":
            return list(range(len(options)))

        selections: list[int] = []
        seen: set[int] = set()
        for chunk in raw.split(","):
            token = chunk.strip()
            if not token:
                continue
            if not token.isdigit():
                print(_color(f"Invalid selection: {token}", RED))
                continue
            choice = int(token)
            if not (1 <= choice <= len(options)):
                print(_color(f"Invalid selection: {token}", RED))
                continue
            index = choice - 1
            if index not in seen:
                seen.add(index)
                selections.append(index)
        return selections or None

    def _prompt_multi_choice(self, title: str, labels: list[str], *, allow_all: bool = False) -> list[int] | None:
        self._clear_screen()
        self._print_header()
        print()
        print(title)
        for index, label in enumerate(labels, start=1):
            print(f"  {_color(f'[{index}]', BOLD)} {label}")
        prompt = "Enter numbers"
        if allow_all:
            prompt += ", 'a' for all"
        prompt += ", or 'q' to cancel:"
        print()
        print(prompt)
        return self._parse_multi_select(input("> "), labels)

    def _install_skill(self) -> None:
        skills = self._canonical_skills()
        if not skills:
            print(_color("No canonical skills available.", YELLOW))
            return
        statuses = {item.name: item for item in self._statuses()}
        labels = []
        for skill in skills:
            labels.append(self._render_skill_line(skill, installed=statuses.get(skill.name)))
        selections = self._prompt_multi_choice(
            "Select skills to install or refresh:",
            labels,
            allow_all=True,
        )
        if not selections:
            print(_color("Install cancelled.", DIM))
            return

        selected_skills = [skills[index] for index in selections]
        self._clear_screen()
        self._print_header()
        print()
        print(_color("Will install/update:", BOLD))
        for skill in selected_skills:
            current = statuses.get(skill.name)
            if current is None:
                print(f"  • {skill.name} {_color(f'v{skill.version}', GREEN)} {_color('(new)', DIM)}")
                continue
            current_version = current.version or "unknown"
            print(
                f"  • {skill.name} {_color(f'local v{current_version}', DIM)} "
                f"{_color('→', DIM)} {_color(f'v{skill.version}', GREEN)} "
                f"{self._render_status_badge(current.status)}"
            )

        successes: list[str] = []
        for skill in selected_skills:
            outcome = self._run_install(skill.name)
            if outcome:
                successes.append(skill.name)

        if successes:
            print()
            print(_color(f"Installed/updated {len(successes)} skill(s): {', '.join(successes)}", GREEN, BOLD))

    def _update_skill(self) -> None:
        statuses = [item for item in self._statuses() if item.managed and item.status != "up_to_date"]
        if not statuses:
            print(_color(f"No managed skills need action for target {self.target}.", YELLOW))
            return
        sources = self._canonical_index()
        labels = [
            self._render_skill_line(sources[item.name], installed=item) if item.name in sources else f"{item.name} {item.status}"
            for item in statuses
        ]
        selections = self._prompt_multi_choice(
            "Select managed skills to update or repair:",
            labels,
            allow_all=True,
        )
        if not selections:
            print(_color("Update cancelled.", DIM))
            return

        self._clear_screen()
        self._print_header()
        successes: list[str] = []
        for index in selections:
            status = statuses[index]
            if self._run_update(status.name):
                successes.append(status.name)

        if successes:
            print()
            print(_color(f"Updated/repaired {len(successes)} skill(s): {', '.join(successes)}", GREEN, BOLD))

    def _remove_skill(self) -> None:
        statuses = self._statuses()
        if not statuses:
            print(_color(f"No installed skills found for target {self.target}.", YELLOW))
            return
        sources = self._canonical_index()
        labels = [
            self._render_skill_line(sources[item.name], installed=item) if item.name in sources else f"{item.name} {item.status}"
            for item in statuses
        ]
        selections = self._prompt_multi_choice(
            "Select installed skills to remove:",
            labels,
        )
        if not selections:
            print(_color("Remove cancelled.", DIM))
            return

        selected = [statuses[index] for index in selections]
        self._clear_screen()
        self._print_header()
        print()
        print(_color("Will remove:", BOLD))
        for status in selected:
            print(f"  • {status.name} {self._render_status_badge(status.status)}")
        if not self._confirm_yes_no(f"Remove {len(selected)} skill(s) from target {self.target}? [y/N]: "):
            print(_color("Remove skipped.", DIM))
            return

        successes: list[str] = []
        for status in selected:
            try:
                path = remove_skill(self.repo_root, self.project_dir, status.name, self.target)
            except (ValueError, FileNotFoundError) as exc:
                print(_color(str(exc), RED))
                continue
            print(_color(f"Removed {status.name} from {path}", GREEN))
            successes.append(status.name)

        if successes:
            print()
            print(_color(f"Removed {len(successes)} skill(s): {', '.join(successes)}", GREEN, BOLD))

    def _run_install(self, skill_name: str) -> bool:
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
                    return self._run_install_forced(skill_name)
                print(_color(f"Skipped {skill_name}.", DIM))
                return False
            print(_color(message, RED))
            return False
        except RuntimeError as exc:
            print(_color(str(exc), RED))
            return False
        print(_color(f"Installed {skill_name} to {path}", GREEN))
        return True

    def _run_install_forced(self, skill_name: str) -> bool:
        try:
            path = install_skill(
                self.repo_root,
                self.project_dir,
                skill_name,
                self.target,
                force=True,
                confirm=self._confirm_yes_no,
            )
        except (RuntimeError, ValueError) as exc:
            print(_color(str(exc), RED))
            return False
        print(_color(f"Installed {skill_name} to {path}", GREEN))
        return True

    def _run_update(self, skill_name: str) -> bool:
        try:
            path = update_skill(
                self.repo_root,
                self.project_dir,
                skill_name,
                self.target,
                force=False,
                confirm=self._confirm_yes_no,
            )
        except ValueError as exc:
            message = str(exc)
            if "rerun update with --force" in message:
                if self._confirm_yes_no(f"{message}. Force overwrite? [y/N]: "):
                    return self._run_update_forced(skill_name)
                print(_color(f"Skipped {skill_name}.", DIM))
                return False
            print(_color(message, RED))
            return False
        except RuntimeError as exc:
            print(_color(str(exc), RED))
            return False
        print(_color(f"Updated {skill_name} at {path}", GREEN))
        return True

    def _run_update_forced(self, skill_name: str) -> bool:
        try:
            path = update_skill(
                self.repo_root,
                self.project_dir,
                skill_name,
                self.target,
                force=True,
                confirm=self._confirm_yes_no,
            )
        except (RuntimeError, ValueError) as exc:
            print(_color(str(exc), RED))
            return False
        print(_color(f"Updated {skill_name} at {path}", GREEN))
        return True

    def _choose_target(self, *, initial: bool) -> str:
        title = "Select target:" if initial else "Switch target:"
        choice = self._prompt_choice(title, list(SUPPORTED_TARGETS))
        return SUPPORTED_TARGETS[choice - 1]

    def _open_expert_terminal(self) -> None:
        if self.shell_rc is None:
            print(_color("Expert terminal is not available in this environment.", YELLOW))
            return
        self._clear_screen()
        print(_color("Opening expert terminal. Exit the shell to return to the menu.", CYAN))
        subprocess.run(["bash", "--noprofile", "--rcfile", str(self.shell_rc)], check=False)

    def _prompt_choice(self, title: str, options: list[str]) -> int:
        while True:
            print()
            print(_color(title, BOLD))
            for index, label in enumerate(options, start=1):
                print(f"  {_color(f'[{index}]', BOLD)} {label}")
            raw = input("> ").strip()
            if raw.isdigit():
                choice = int(raw)
                if 1 <= choice <= len(options):
                    return choice
            print(_color("Enter one of the numbered options.", RED))

    def _confirm_yes_no(self, prompt: str) -> bool:
        response = input(prompt).strip().lower()
        return response in {"y", "yes"}

    def _pause(self) -> None:
        input(_color("Press Enter to continue...", DIM))


def run_menu(repo_root: Path, project_dir: Path, *, shell_rc: Path | None = None) -> int:
    manager = InteractiveMenu(repo_root, project_dir, shell_rc=shell_rc)
    return manager.run()
