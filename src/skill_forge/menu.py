from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from .agent_memory import (
    ConfigItemSource,
    config_status,
    install_config,
    load_all_config_items,
)
from .catalog import group_skill_names, load_catalog
from .install import install_skill, list_installed, remove_skill, target_root, update_skill
from .models import CanonicalSkill, InstalledStatus
from .repository import SUPPORTED_TARGETS, load_all_skills
from .security_check import (
    check_security_settings,
    format_applied_report,
    format_created_report,
    init_security_settings,
    merge_security_defaults,
)

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
ORANGE = "\033[38;5;208m"
CLEAR_SCREEN = "\033[2J\033[H"

BASELINE_SKILL = "install-my-skill"
RECOMMENDED_LABEL = "★ Recommended"
GUIDELINE_LABEL = "Guideline"

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

# Section labels are visual grouping only; a skill's canonical name column width.
_NAME_WIDTH = 20
_VERSION_WIDTH = 10


def _color(text: str, *styles: str) -> str:
    return f"{''.join(styles)}{text}{RESET}"


def _visible_len(text: str) -> int:
    return len(_ANSI_RE.sub("", text))


def _pad(text: str, width: int) -> str:
    return text + " " * max(width - _visible_len(text), 0)


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
        self._onboarding_notice: str | None = None
        self._catalog = load_catalog(repo_root)
        keywords = sorted(self._catalog.highlight_keywords, key=len, reverse=True)
        self._highlight_re = (
            re.compile(r"\b(?:" + "|".join(re.escape(keyword) for keyword in keywords) + r")\b", re.IGNORECASE)
            if keywords
            else None
        )

    def run(self) -> int:
        self.target = self._choose_target(initial=True)
        self._run_onboarding()
        while True:
            self._clear_screen()
            self._print_header()
            choice = self._prompt_choice(
                "Choose an action:",
                [
                    "Check installed skill status",
                    "Install / Update skills",
                    "Install / Update project guideline",
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
                self._guideline_menu()
                self._pause()
            elif choice == 4:
                self._update_skill()
                self._pause()
            elif choice == 5:
                self._remove_skill()
                self._pause()
            elif choice == 6:
                self.target = self._choose_target(initial=False)
                self._run_onboarding()
            elif choice == 7:
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
        if self._onboarding_notice is not None:
            print(self._onboarding_notice)
            print()

    def _render_status_badge(self, status: str, count: int | None = None) -> str:
        label = status if count is None else f"{status}={count}"
        return _color(label, *_status_style(status))

    def _highlight(self, text: str) -> str:
        if self._highlight_re is None:
            return text
        return self._highlight_re.sub(lambda match: _color(match.group(0), ORANGE, BOLD), text)

    def _render_skill_name(self, name: str) -> str:
        rendered = _color(name, CYAN, BOLD)
        if name in self._catalog.recommended:
            rendered = _color("★ ", YELLOW) + rendered
        return rendered

    def _render_skill_line(self, skill: CanonicalSkill, *, installed: InstalledStatus | None = None) -> str:
        name = self._render_skill_name(skill.name)
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
        description = self._highlight(skill.description)
        return (
            f"{_pad(name, _NAME_WIDTH)} {_pad(source_version, _VERSION_WIDTH)} {badge}{version_note}\n"
            f"  {description}\n  {tags}"
        )

    def _render_config_line(self, source: ConfigItemSource, status: InstalledStatus | None) -> str:
        filename = source.spec.target_paths[self.target]
        name = _color(source.name, CYAN, BOLD)
        source_version = _color(f"v{source.version}", DIM)
        if status is None:
            badge = _color("not installed", DIM)
            version_note = ""
        else:
            badge = self._render_status_badge(status.status)
            installed_version = status.version or "unknown"
            local_note = _color(f"local v{installed_version}", DIM)
            version_note = f" {local_note}"
            if status.status == "update_available":
                version_note += f" {_color('→', DIM)} {_color(f'v{source.version} available', YELLOW)}"
            elif status.status == "up_to_date":
                version_note += f" {_color('✓ current', GREEN)}"
        description = self._highlight(source.description) if source.description else "Managed config file"
        target_note = _color(f"→ ./{filename}", DIM)
        return (
            f"{_pad(name, _NAME_WIDTH)} {_pad(source_version, _VERSION_WIDTH)} {badge}{version_note}\n"
            f"  {description} {target_note}"
        )

    def _grouped_skill_sections(
        self, skills: list[CanonicalSkill]
    ) -> list[tuple[str | None, list[CanonicalSkill]]]:
        by_name = {skill.name: skill for skill in skills}
        sections = group_skill_names(list(by_name), self._catalog, recommended_label=RECOMMENDED_LABEL)
        return [(header, [by_name[name] for name in names]) for header, names in sections]

    def _show_statuses(self) -> None:
        self._clear_screen()
        self._print_header()
        statuses = self._statuses()
        sources = self._canonical_index()
        config_sources = load_all_config_items(self.repo_root)
        if not statuses:
            print(_color(f"No installed skills found for target {self.target}.", YELLOW))

        status_by_name = {item.name: item for item in statuses}
        sections = group_skill_names(list(status_by_name), self._catalog, recommended_label=RECOMMENDED_LABEL)
        if statuses:
            print(_color(f"Installed skills for {self.target}:", BOLD))
        for header, names in sections:
            print()
            print(self._render_section_header(header))
            for name in names:
                item = status_by_name[name]
                source = sources.get(name)
                if source is not None:
                    print(self._render_skill_line(source, installed=item))
                else:
                    badge = self._render_status_badge(item.status)
                    version = item.version or "unknown"
                    local_version = _color(f"local v{version}", DIM)
                    print(f"{_pad(self._render_skill_name(name), _NAME_WIDTH)} {local_version} {badge}")
                if item.details:
                    print(f"  {_color(item.details, DIM)}")
                print()
        if config_sources:
            print(self._render_section_header(GUIDELINE_LABEL))
            for config_source in config_sources:
                config_state = config_status(config_source, self.project_dir, self.target)
                print(self._render_config_line(config_source, config_state))
                if config_state is not None and config_state.details:
                    print(f"  {_color(config_state.details, DIM)}")
                print()

    def _render_section_header(self, header: str) -> str:
        rule = "─" * max(46 - _visible_len(header), 4)
        return _color(f"── {header} {rule}", CYAN, BOLD)

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

    def _prompt_multi_choice(
        self,
        title: str,
        sections: list[tuple[str | None, list[str]]],
        *,
        allow_all: bool = False,
    ) -> list[int] | None:
        self._clear_screen()
        self._print_header()
        print()
        print(title)
        flat_labels: list[str] = []
        for header, labels in sections:
            if header is not None:
                print()
                print(self._render_section_header(header))
            for label in labels:
                flat_labels.append(label)
                print(f"  {_color(f'[{len(flat_labels)}]', BOLD)} {label}")
        prompt = "Enter numbers"
        if allow_all:
            prompt += ", 'a' for all"
        prompt += ", or 'q' to cancel:"
        print()
        print(prompt)
        return self._parse_multi_select(input("> "), flat_labels)

    def _install_skill(self) -> None:
        skills = self._canonical_skills()
        if not skills:
            print(_color("No canonical skills available.", YELLOW))
            return
        statuses = {item.name: item for item in self._statuses()}

        items: list[CanonicalSkill] = []
        render_sections: list[tuple[str | None, list[str]]] = []
        for header, section_skills in self._grouped_skill_sections(skills):
            labels = []
            for skill in section_skills:
                labels.append(self._render_skill_line(skill, installed=statuses.get(skill.name)))
                items.append(skill)
            render_sections.append((header, labels))

        selections = self._prompt_multi_choice(
            "Select skills to install or refresh:",
            render_sections,
            allow_all=True,
        )
        if not selections:
            print(_color("Install cancelled.", DIM))
            return

        selected = [items[index] for index in selections]
        self._clear_screen()
        self._print_header()
        print()
        print(_color("Will install/update:", BOLD))
        for skill in selected:
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

        if not self._check_skills_dir_writable():
            return

        successes: list[str] = []
        for skill in selected:
            if self._run_install(skill.name):
                successes.append(skill.name)

        if successes:
            print()
            print(_color(f"Installed/updated {len(successes)} item(s): {', '.join(successes)}", GREEN, BOLD))

    def _guideline_menu(self) -> None:
        sources = load_all_config_items(self.repo_root)
        if not sources:
            print(_color("No project guideline config items available.", YELLOW))
            return
        states = {
            source.name: config_status(source, self.project_dir, self.target) for source in sources
        }
        labels = [self._render_config_line(source, states[source.name]) for source in sources]

        selections = self._prompt_multi_choice(
            "Select guideline items to install or refresh:",
            [(GUIDELINE_LABEL, labels)],
            allow_all=True,
        )
        if not selections:
            print(_color("Install cancelled.", DIM))
            return

        selected = [sources[index] for index in selections]
        self._clear_screen()
        self._print_header()
        print()
        print(_color("Will install/update:", BOLD))
        for source in selected:
            state = states[source.name]
            filename = source.spec.target_paths[self.target]
            if state is None:
                print(f"  • {source.name} {_color(f'v{source.version}', GREEN)} {_color(f'(new → ./{filename})', DIM)}")
                continue
            local_version = state.version or "unknown"
            print(
                f"  • {source.name} {_color(f'local v{local_version}', DIM)} "
                f"{_color('→', DIM)} {_color(f'v{source.version}', GREEN)} "
                f"{self._render_status_badge(state.status)}"
            )

        successes: list[str] = []
        for source in selected:
            if self._run_config_install(source):
                successes.append(source.name)

        if successes:
            print()
            print(_color(f"Installed/updated {len(successes)} item(s): {', '.join(successes)}", GREEN, BOLD))

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
            [(None, labels)],
            allow_all=True,
        )
        if not selections:
            print(_color("Update cancelled.", DIM))
            return

        self._clear_screen()
        self._print_header()

        if not self._check_skills_dir_writable():
            return

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
            [(None, labels)],
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

    def _check_skills_dir_writable(self) -> bool:
        skills_dir = target_root(self.project_dir, self.target)
        skills_dir.mkdir(parents=True, exist_ok=True)
        if not os.access(skills_dir, os.W_OK):
            try:
                os.chmod(skills_dir, skills_dir.stat().st_mode | 0o700)
            except PermissionError:
                cmd = f"chmod -R u+w {skills_dir}"
                print(
                    _color(
                        f"Skills directory '{skills_dir}' is not writable.\n"
                        f"Suggested fix:  {cmd}",
                        RED,
                    )
                )
                return False
        return True

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

    def _run_config_install(self, source: ConfigItemSource) -> bool:
        try:
            path = install_config(
                source,
                self.project_dir,
                self.target,
                force=False,
                confirm=self._confirm_yes_no,
            )
        except ValueError as exc:
            message = str(exc)
            if "rerun install with --force" in message:
                if self._confirm_yes_no(f"{message}. Force overwrite? [y/N]: "):
                    try:
                        path = install_config(
                            source,
                            self.project_dir,
                            self.target,
                            force=True,
                            confirm=self._confirm_yes_no,
                        )
                    except (RuntimeError, ValueError) as retry_exc:
                        print(_color(str(retry_exc), RED))
                        return False
                    print(_color(f"Installed {source.name} to {path}", GREEN))
                    return True
                print(_color(f"Skipped {source.name}.", DIM))
                return False
            print(_color(message, RED))
            return False
        except RuntimeError as exc:
            print(_color(str(exc), RED))
            return False
        print(_color(f"Installed {source.name} to {path}", GREEN))
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

    def _confirm_yes_no_default_yes(self, prompt: str) -> bool:
        response = input(prompt).strip().lower()
        return response not in {"n", "no"}

    def _pause(self) -> None:
        input(_color("Press Enter to continue...", DIM))

    def _run_onboarding(self) -> None:
        """Offer the recommended baseline (security settings + install-my-skill) for the target."""
        notices: list[str] = []
        planned: list[str] = []

        security_result = None
        if self.target == "claude":
            security_result = check_security_settings(self.project_dir)
            if security_result.needs_attention:
                planned.append("Write security defaults to .claude/settings.local.json")

        baseline = next((item for item in self._statuses() if item.name == BASELINE_SKILL), None)
        baseline_action: str | None = None
        if baseline is None:
            baseline_action = "install"
            planned.append(f"Install {BASELINE_SKILL} for target {self.target}")
        elif baseline.status == "update_available":
            baseline_action = "update"
            planned.append(f"Update {BASELINE_SKILL} for target {self.target}")
        elif baseline.status in {"drift", "broken", "unmanaged"}:
            notices.append(
                _color(
                    f"[baseline] {BASELINE_SKILL} is {baseline.status}; use Install / Update skills to resolve it.",
                    YELLOW,
                )
            )

        if planned:
            print()
            print(_color("Recommended baseline for this target:", BOLD))
            for entry in planned:
                print(f"  • {entry}")
            if self._confirm_yes_no_default_yes(
                "Write recommended baseline (security settings + install-my-skill)? [Y/n]: "
            ):
                if security_result is not None and security_result.needs_attention:
                    if not security_result.exists:
                        path = init_security_settings(self.project_dir)
                        notices.append(format_created_report(path))
                    else:
                        applied = merge_security_defaults(self.project_dir)
                        if applied:
                            notices.append(format_applied_report(applied, security_result.settings_path))
                if baseline_action is not None:
                    try:
                        path = install_skill(
                            self.repo_root,
                            self.project_dir,
                            BASELINE_SKILL,
                            self.target,
                            force=False,
                            confirm=self._confirm_yes_no,
                        )
                        verb = "Installed" if baseline_action == "install" else "Updated"
                        notices.append(_color(f"[baseline] {verb} {BASELINE_SKILL} at {path}", GREEN))
                    except (ValueError, RuntimeError, FileNotFoundError) as exc:
                        notices.append(_color(f"[baseline] {exc}", YELLOW))
            else:
                notices.append(_color("[baseline] Skipped recommended baseline setup.", DIM))

        self._onboarding_notice = "\n".join(notices) if notices else None


def run_menu(repo_root: Path, project_dir: Path, *, shell_rc: Path | None = None) -> int:
    manager = InteractiveMenu(repo_root, project_dir, shell_rc=shell_rc)
    return manager.run()
