from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


TOOLKIT_MARKER_PREFIX = "<!-- skill-toolkit: "
TOOLKIT_MARKER_SUFFIX = " -->"
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def compute_package_sha(file_entries: list[tuple[str, str]]) -> str:
    ordered = sorted(file_entries, key=lambda item: item[0])
    payload = "".join(f"{path}:{digest}\n" for path, digest in ordered)
    return sha256_bytes(payload.encode("utf-8"))


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(value, ensure_ascii=False)


def dump_frontmatter(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, (list, dict)):
            rendered = json.dumps(value, ensure_ascii=False)
        else:
            rendered = yaml_scalar(value)
        lines.append(f"{key}: {rendered}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def make_toolkit_marker(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return f"{TOOLKIT_MARKER_PREFIX}{encoded}{TOOLKIT_MARKER_SUFFIX}\n"


def parse_toolkit_marker(content: str) -> dict[str, Any] | None:
    for line in content.splitlines():
        if line.startswith(TOOLKIT_MARKER_PREFIX) and line.endswith(TOOLKIT_MARKER_SUFFIX):
            body = line[len(TOOLKIT_MARKER_PREFIX) : -len(TOOLKIT_MARKER_SUFFIX)]
            return json.loads(body)
    return None


def has_frontmatter(content: str) -> bool:
    return FRONTMATTER_PATTERN.match(content) is not None
