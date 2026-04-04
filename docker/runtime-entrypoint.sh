#!/usr/bin/env sh

set -eu

DEFAULT_REPO_ROOT="${SKILL_FORGE_REPO_ROOT:-/opt/skill-forge}"
PROJECT_DIR="${SKILL_FORGE_PROJECT_DIR:-/workspace/project}"
SHELL_RC="/opt/skill-forge/docker/runtime-shellrc"

run_cli() {
    for arg in "$@"; do
        if [ "$arg" = "--repo-root" ]; then
            exec skill-forge "$@"
        fi
    done

    exec skill-forge --repo-root "$DEFAULT_REPO_ROOT" "$@"
}

if [ "$#" -eq 0 ]; then
    exec skill-forge \
        --repo-root "$DEFAULT_REPO_ROOT" \
        menu \
        --project "$PROJECT_DIR" \
        --shell-rc "$SHELL_RC"
fi

if [ "$1" = "bash" ] || [ "$1" = "shell" ]; then
    shift || true
    exec bash --noprofile --rcfile "$SHELL_RC" "$@"
fi

if [ "$1" = "skill-forge" ]; then
    shift
fi

run_cli "$@"
