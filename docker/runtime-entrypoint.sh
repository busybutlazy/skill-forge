#!/usr/bin/env sh

set -eu

DEFAULT_REPO_ROOT="${SKILL_TOOLKIT_REPO_ROOT:-/opt/skill-toolkit}"
PROJECT_DIR="${SKILL_TOOLKIT_PROJECT_DIR:-/workspace/project}"
SHELL_RC="/opt/skill-toolkit/docker/runtime-shellrc"

run_cli() {
    for arg in "$@"; do
        if [ "$arg" = "--repo-root" ]; then
            exec skill-toolkit "$@"
        fi
    done

    exec skill-toolkit --repo-root "$DEFAULT_REPO_ROOT" "$@"
}

if [ "$#" -eq 0 ]; then
    exec skill-toolkit \
        --repo-root "$DEFAULT_REPO_ROOT" \
        menu \
        --project "$PROJECT_DIR" \
        --shell-rc "$SHELL_RC"
fi

if [ "$1" = "bash" ] || [ "$1" = "shell" ]; then
    shift || true
    exec bash --noprofile --rcfile "$SHELL_RC" "$@"
fi

if [ "$1" = "skill-toolkit" ]; then
    shift
fi

run_cli "$@"
