from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ValidationFailure(Exception):
    def __init__(self, issues: list[str]):
        super().__init__("\n".join(issues))
        self.issues = issues


@dataclass(frozen=True)
class TargetConfig:
    name: str
    frontmatter: dict[str, Any]
    install_path: str


@dataclass(frozen=True)
class CanonicalSkill:
    root: Path
    name: str
    version: str
    description: str
    updated_at: str
    tags: list[str]
    instruction: str
    package_sha256: str
    manifest_file: str
    targets: dict[str, TargetConfig]
    asset_dirs: list[str] = field(default_factory=list)

    @property
    def source_ref(self) -> str:
        return f"canonical-skills/{self.name}"


@dataclass(frozen=True)
class ValidationResult:
    skill: str
    valid: bool
    issues: list[str]
    package_sha256: str | None = None


@dataclass(frozen=True)
class InstalledStatus:
    name: str
    target: str
    status: str
    location: Path
    version: str | None = None
    source_package_sha256: str | None = None
    details: str | None = None
