from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .install import install_skill, list_installed, remove_skill
from .render import render_skill
from .repository import SUPPORTED_TARGETS, iter_skill_dirs, load_skill, validate_skill_dir


def _repo_root_from_args(args: argparse.Namespace) -> Path:
    return Path(args.repo_root).resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill-toolkit", description="Canonical skill toolkit CLI")
    parser.add_argument("--repo-root", default=".", help="Repository root containing canonical-skills/")
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

    list_parser = subparsers.add_parser("list", help="List installed packages and their status")
    list_parser.add_argument("--target", choices=SUPPORTED_TARGETS, required=True)
    list_parser.add_argument("--project", required=True, help="Target project root")

    remove_parser = subparsers.add_parser("remove", help="Remove a managed installed package")
    remove_parser.add_argument("skill", help="Skill name")
    remove_parser.add_argument("--target", choices=SUPPORTED_TARGETS, required=True)
    remove_parser.add_argument("--project", required=True, help="Target project root")

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
    installed = install_skill(repo_root, Path(args.project).resolve(), args.skill, args.target)
    print(installed)
    return 0


def run_list(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_args(args)
    statuses = list_installed(repo_root, Path(args.project).resolve(), args.target)
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


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    command_handlers = {
        "validate": run_validate,
        "render": run_render,
        "install": run_install,
        "list": run_list,
        "remove": run_remove,
    }
    return command_handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
