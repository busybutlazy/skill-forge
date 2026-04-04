from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from . import __version__
from .install import install_skill, list_installed, remove_skill, sync_manager_catalog, update_skill
from .menu import run_menu
from .models import ValidationFailure
from .package_ops import refresh_skill_metadata
from .render import render_skill
from .repository import (
    SUPPORTED_SCOPES,
    SUPPORTED_TARGETS,
    iter_skill_dirs,
    load_all_skills,
    load_manager_catalog_skills,
    load_skill,
    validate_skill_dir,
)


def _repo_root_from_args(args: argparse.Namespace) -> Path:
    return Path(args.repo_root).resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill-toolkit", description="Canonical skill toolkit CLI")
    parser.add_argument("--repo-root", default=".", help="Repository root containing canonical-skills/regular-skills and canonical-skills/manager-skills")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate canonical skill packages")
    validate_parser.add_argument("skill", nargs="?", help="Skill name or canonical skill path")
    validate_parser.add_argument("--target", choices=[*SUPPORTED_TARGETS, "all"], default="all")

    render_parser = subparsers.add_parser("render", help="Render a canonical skill to a target output tree")
    render_parser.add_argument("skill", help="Skill name or canonical skill path")
    render_parser.add_argument("--target", choices=SUPPORTED_TARGETS, required=True)
    render_parser.add_argument("--output", required=True, help="Output directory root")

    install_parser = subparsers.add_parser("install", help="Install a rendered package into a project")
    install_parser.add_argument("skill", help="Skill name")
    install_parser.add_argument("--target", choices=SUPPORTED_TARGETS, required=True)
    install_parser.add_argument("--project", required=True, help="Target project root")
    install_parser.add_argument("--force", action="store_true", help="Allow overwriting drifted local changes after confirmation")

    list_parser = subparsers.add_parser("list", help="List installed packages and their status")
    list_parser.add_argument("--target", choices=SUPPORTED_TARGETS, required=True)
    list_parser.add_argument("--project", required=True, help="Target project root")
    list_parser.add_argument("--scope", choices=[*SUPPORTED_SCOPES, "all"], default="public", help="Which canonical source scope to compare against")
    list_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")

    remove_parser = subparsers.add_parser("remove", help="Remove a managed installed package")
    remove_parser.add_argument("skill", help="Skill name")
    remove_parser.add_argument("--target", choices=SUPPORTED_TARGETS, required=True)
    remove_parser.add_argument("--project", required=True, help="Target project root")

    update_parser = subparsers.add_parser("update", help="Update a managed installed package from canonical source")
    update_parser.add_argument("skill", help="Skill name")
    update_parser.add_argument("--target", choices=SUPPORTED_TARGETS, required=True)
    update_parser.add_argument("--project", required=True, help="Target project root")
    update_parser.add_argument("--force", action="store_true", help="Allow overwriting drifted local changes after confirmation")

    menu_parser = subparsers.add_parser("menu", help="Open the interactive skill manager")
    menu_parser.add_argument("--project", required=True, help="Target project root")
    menu_parser.add_argument("--shell-rc", help="Shell rc file used by expert terminal mode")

    refresh_parser = subparsers.add_parser("refresh-metadata", help="Refresh manifest and package integrity metadata for a canonical skill")
    refresh_parser.add_argument("skill", help="Skill name or canonical skill path")
    refresh_parser.add_argument("--version", help="Optionally update identity.version at the same time")
    refresh_parser.add_argument("--updated-at", help="Optionally set identity.updated_at (YYYY-MM-DD)")
    refresh_parser.add_argument("--today", action="store_true", help="Set identity.updated_at to today's date")

    sync_parser = subparsers.add_parser("sync-maintainer", help="Install or refresh maintainer-only skills into a project")
    sync_parser.add_argument("skills", nargs="*", help="Optional maintainer skill names; defaults to all maintainer-only skills")
    sync_parser.add_argument("--project", required=True, help="Target project root")
    sync_parser.add_argument("--target", choices=SUPPORTED_TARGETS, default="codex")
    sync_parser.add_argument("--force", action="store_true", help="Allow overwriting drifted maintainer installs after confirmation")

    manager_catalog_parser = subparsers.add_parser("sync-manager-catalog", help="Install or refresh manager skills plus shared regular skills into a project")
    manager_catalog_parser.add_argument("skills", nargs="*", help="Optional manager-catalog skill names; defaults to all manager and shared skills")
    manager_catalog_parser.add_argument("--project", required=True, help="Target project root")
    manager_catalog_parser.add_argument("--target", choices=[*SUPPORTED_TARGETS, "all"], default="all")
    manager_catalog_parser.add_argument("--force", action="store_true", help="Allow overwriting drifted or unmanaged local installs after confirmation")

    return parser


def run_validate(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_args(args)
    target_filter = None if args.target == "all" else {args.target}
    skill_dirs = [Path(args.skill)] if args.skill else iter_skill_dirs(repo_root)
    if not skill_dirs:
        print("No canonical skills found.", file=sys.stderr)
        return 1

    exit_code = 0
    for skill_dir in skill_dirs:
        if not skill_dir.is_absolute() and not skill_dir.exists():
            skill_dir = repo_root / "canonical-skills" / str(skill_dir)
        result = validate_skill_dir(skill_dir, target_filter=target_filter)
        if result.valid:
            print(f"VALID {result.skill} {result.package_sha256}")
        else:
            exit_code = 1
            print(f"INVALID {result.skill}")
            for issue in result.issues:
                print(f"  - {issue}")
    return exit_code


def run_render(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_args(args)
    skill = load_skill(repo_root, args.skill, target_filter={args.target})
    rendered = render_skill(skill, args.target, Path(args.output).resolve())
    print(rendered)
    return 0


def run_install(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_args(args)
    installed = install_skill(
        repo_root,
        Path(args.project).resolve(),
        args.skill,
        args.target,
        force=args.force,
        confirm=_prompt_yes_no,
    )
    print(installed)
    return 0


def run_list(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_args(args)
    source_scopes = set(SUPPORTED_SCOPES) if args.scope == "all" else {args.scope}
    statuses = list_installed(repo_root, Path(args.project).resolve(), args.target, source_scopes=source_scopes)
    if args.json:
        print(json.dumps([status.to_dict() for status in statuses], ensure_ascii=False, indent=2))
        return 0
    if not statuses:
        print("No installed packages found.")
        return 0
    for status in statuses:
        version = status.version or "-"
        digest = status.source_package_sha256 or "-"
        detail = f" {status.details}" if status.details else ""
        print(f"{status.name}\t{status.status}\t{version}\t{digest}\t{status.location}{detail}")
    return 0


def run_remove(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_args(args)
    removed = remove_skill(repo_root, Path(args.project).resolve(), args.skill, args.target)
    print(removed)
    return 0


def _prompt_yes_no(prompt: str) -> bool:
    response = input(prompt).strip().lower()
    return response in {"y", "yes"}


def run_update(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_args(args)
    updated = update_skill(
        repo_root,
        Path(args.project).resolve(),
        args.skill,
        args.target,
        force=args.force,
        confirm=_prompt_yes_no,
    )
    print(updated)
    return 0


def run_refresh_metadata(args: argparse.Namespace) -> int:
    if args.today and args.updated_at:
        raise ValueError("choose either --updated-at or --today, not both")
    repo_root = _repo_root_from_args(args)
    result = refresh_skill_metadata(
        repo_root,
        args.skill,
        version=args.version,
        updated_at=args.updated_at,
        use_today=args.today,
    )
    updated = ", ".join(result.updated_fields) if result.updated_fields else "manifest only"
    print(f"{result.skill}\t{result.package_sha256}\t{updated}")
    for rel_path in result.manifest_files:
        print(f"  - {rel_path}")
    return 0


def run_sync_maintainer(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_args(args)
    project_dir = Path(args.project).resolve()
    skills = args.skills or [skill.name for skill in load_all_skills(repo_root, target_filter={args.target}, scopes={"maintainer"})]
    if not skills:
        print("No maintainer-only skills found.")
        return 0

    for skill_name in skills:
        try:
            path = install_skill(
                repo_root,
                project_dir,
                skill_name,
                args.target,
                force=args.force,
                confirm=_prompt_yes_no,
                allowed_scopes={"maintainer"},
            )
        except ValueError as exc:
            if "is unmanaged; refusing to overwrite it" not in str(exc) or not args.force:
                raise
            if args.target == "codex":
                unmanaged_path = project_dir / ".agents" / "skills" / skill_name
            else:
                unmanaged_path = project_dir / ".claude" / "agents" / f"{skill_name}.md"
            if unmanaged_path.is_dir():
                shutil.rmtree(unmanaged_path)
            elif unmanaged_path.exists():
                unmanaged_path.unlink()
            assets_dir = unmanaged_path.with_name(f"{skill_name}.assets")
            if assets_dir.exists():
                shutil.rmtree(assets_dir)
            path = install_skill(
                repo_root,
                project_dir,
                skill_name,
                args.target,
                force=args.force,
                confirm=_prompt_yes_no,
                allowed_scopes={"maintainer"},
            )
        print(path)
    return 0


def run_sync_manager_catalog(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_args(args)
    project_dir = Path(args.project).resolve()
    targets = list(SUPPORTED_TARGETS) if args.target == "all" else [args.target]
    selected_skills = args.skills
    if not selected_skills:
        selected_skills = [skill.name for skill in load_manager_catalog_skills(repo_root)]
    if not selected_skills:
        print("No manager-catalog skills found.")
        return 0

    for target in targets:
        paths = sync_manager_catalog(
            repo_root,
            project_dir,
            target,
            skill_names=selected_skills,
            force=args.force,
            confirm=_prompt_yes_no,
        )
        for path in paths:
            print(path)
    return 0


def run_menu_command(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_args(args)
    shell_rc = Path(args.shell_rc).resolve() if args.shell_rc else None
    return run_menu(
        repo_root,
        Path(args.project).resolve(),
        shell_rc=shell_rc,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    command_handlers = {
        "validate": run_validate,
        "render": run_render,
        "install": run_install,
        "list": run_list,
        "remove": run_remove,
        "update": run_update,
        "menu": run_menu_command,
        "refresh-metadata": run_refresh_metadata,
        "sync-maintainer": run_sync_maintainer,
        "sync-manager-catalog": run_sync_manager_catalog,
    }
    try:
        return command_handlers[args.command](args)
    except (ValidationFailure, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
