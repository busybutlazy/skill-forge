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
    scope: str
    source_ref: str
    version: str
    description: str
    updated_at: str
    tags: list[str]
    instruction: str
    package_sha256: str
    manifest_file: str
    targets: dict[str, TargetConfig]
    asset_dirs: list[str] = field(default_factory=list)

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
    managed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "target": self.target,
            "status": self.status,
            "location": str(self.location),
            "version": self.version,
            "source_package_sha256": self.source_package_sha256,
            "details": self.details,
            "managed": self.managed,
        }
