#!/usr/bin/env sh

set -eu

DEFAULT_REPO_ROOT="${SKILL_FORGE_REPO_ROOT:-/opt/skill-forge}"
PROJECT_DIR="${SKILL_FORGE_PROJECT_DIR:-/workspace/project}"
SHELL_RC="/opt/skill-forge/docker/runtime-shellrc"
HOST_UID="${HOST_UID:-0}"
HOST_GID="${HOST_GID:-0}"

# Running as root: fix ownership of .claude so UID HOST_UID can write to it.
# This handles the common Docker-on-Windows case where a previous root-owned run
# left .claude/skills unwritable by the target user.
if [ "$(id -u)" = "0" ] && [ "$HOST_UID" != "0" ]; then
    CLAUDE_DIR="$PROJECT_DIR/.claude"
    mkdir -p "$CLAUDE_DIR/skills"
    chown -R "${HOST_UID}:${HOST_GID}" "$CLAUDE_DIR" 2>/dev/null || true
fi

drop() {
    if [ "$(id -u)" = "0" ] && [ "$HOST_UID" != "0" ]; then
        exec gosu "${HOST_UID}:${HOST_GID}" "$@"
    else
        exec "$@"
    fi
}

if [ "$#" -eq 0 ]; then
    drop skill-forge \
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

for arg in "$@"; do
    if [ "$arg" = "--repo-root" ]; then
        drop skill-forge "$@"
    fi
done

drop skill-forge --repo-root "$DEFAULT_REPO_ROOT" "$@"
