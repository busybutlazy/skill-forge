from __future__ import annotations

import json
from pathlib import Path

from .models import CanonicalSkill, TargetConfig, ValidationFailure, ValidationResult
from .utils import compute_package_sha, read_text, sha256_file

OPTIONAL_ASSET_DIRS = ["examples", "references", "scripts", "assets"]
SUPPORTED_TARGETS = ("codex", "claude")
SUPPORTED_SCOPES = ("public", "maintainer")
SHARED_MANAGER_TAG = "shared"
CANONICAL_BUCKETS = {
    "regular-skills": "public",
    "manager-skills": "maintainer",
}


def canonical_root(repo_root: Path) -> Path:
    return repo_root / "canonical-skills"


def canonical_bucket_roots(repo_root: Path) -> dict[str, Path]:
    root = canonical_root(repo_root)
    return {bucket: root / bucket for bucket in CANONICAL_BUCKETS}


def iter_skill_dirs(repo_root: Path) -> list[Path]:
    skill_dirs: list[Path] = []
    for bucket_root in canonical_bucket_roots(repo_root).values():
        if not bucket_root.is_dir():
            continue
        skill_dirs.extend(sorted(path for path in bucket_root.iterdir() if path.is_dir()))
    return sorted(skill_dirs)


def _source_ref_for_skill_dir(repo_root: Path, skill_dir: Path) -> str:
    return str(skill_dir.resolve().relative_to(repo_root.resolve()))


def _scope_from_path(repo_root: Path, skill_dir: Path) -> str | None:
    try:
        relative = skill_dir.resolve().relative_to(canonical_root(repo_root).resolve())
    except ValueError:
        return None
    parts = relative.parts
    if len(parts) < 2:
        return None
    return CANONICAL_BUCKETS.get(parts[0])


def resolve_skill_dir(repo_root: Path, skill: str | Path) -> Path:
    if isinstance(skill, Path):
        return skill
    maybe_path = Path(skill)
    if maybe_path.exists():
        return maybe_path.resolve()
    matches: list[Path] = []
    for bucket_root in canonical_bucket_roots(repo_root).values():
        candidate = bucket_root / skill
        if candidate.is_dir():
            matches.append(candidate)
    if not matches:
        return canonical_root(repo_root) / skill
    if len(matches) > 1:
        raise ValueError(f"duplicate canonical skill name found in multiple buckets: {skill}")
    return matches[0]


def validate_skill_dir(skill_dir: Path, target_filter: set[str] | None = None) -> ValidationResult:
    issues: list[str] = []
    package_path = skill_dir / "package.json"
    manifest_path = skill_dir / "manifest.json"
    instruction_path = skill_dir / "instruction.md"

    package_sha = None
    package_data: dict[str, object] | None = None
    manifest_data: dict[str, object] | None = None

    if not skill_dir.is_dir():
        return ValidationResult(skill=skill_dir.name, valid=False, issues=["missing canonical skill directory"])

    if not package_path.is_file():
        issues.append("missing package.json")
    if not manifest_path.is_file():
        issues.append("missing manifest.json")
    if not instruction_path.is_file():
        issues.append("missing instruction.md")

    if not issues:
        try:
            package_data = json.loads(read_text(package_path))
        except json.JSONDecodeError as exc:
            issues.append(f"package.json is not valid JSON: {exc}")

    if not issues:
        try:
            manifest_data = json.loads(read_text(manifest_path))
        except json.JSONDecodeError as exc:
            issues.append(f"manifest.json is not valid JSON: {exc}")

    if package_data:
        if package_data.get("schema_version") != 1:
            issues.append("package.json schema_version must be 1")
        identity = package_data.get("identity")
        if not isinstance(identity, dict):
            issues.append("package.json missing identity object")
        else:
            if identity.get("name") != skill_dir.name:
                issues.append("identity.name must match directory name")
            for field in ("version", "description", "updated_at", "tags"):
                if field not in identity:
                    issues.append(f"identity missing {field}")
            tags = identity.get("tags")
            if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
                issues.append("identity.tags must be a list of strings")

        distribution = package_data.get("distribution")
        if not isinstance(distribution, dict):
            issues.append("package.json missing distribution object")
        else:
            scope = distribution.get("scope")
            if scope not in SUPPORTED_SCOPES:
                issues.append(f"distribution.scope must be one of: {', '.join(SUPPORTED_SCOPES)}")
            expected_scope = _scope_from_path(skill_dir.parents[2], skill_dir)
            if expected_scope is not None and scope != expected_scope:
                issues.append(f"distribution.scope must match canonical bucket scope: {expected_scope}")

        content = package_data.get("content")
        if not isinstance(content, dict) or content.get("instruction_file") != "instruction.md":
            issues.append("content.instruction_file must be instruction.md")

        integrity = package_data.get("integrity")
        if not isinstance(integrity, dict):
            issues.append("package.json missing integrity object")
        else:
            if integrity.get("manifest_file") != "manifest.json":
                issues.append("integrity.manifest_file must be manifest.json")
            if not isinstance(integrity.get("package_sha256"), str):
                issues.append("integrity.package_sha256 must be a string")
            else:
                package_sha = integrity["package_sha256"]

        targets = package_data.get("targets")
        if not isinstance(targets, dict):
            issues.append("package.json missing targets object")
        else:
            required_targets = target_filter or set(SUPPORTED_TARGETS)
            for target_name in required_targets:
                target_data = targets.get(target_name)
                if not isinstance(target_data, dict):
                    issues.append(f"missing target config for {target_name}")
                    continue
                frontmatter_file = target_data.get("frontmatter_file")
                install_path = target_data.get("install_path")
                if not isinstance(frontmatter_file, str):
                    issues.append(f"{target_name} frontmatter_file must be a string")
                else:
                    frontmatter_path = skill_dir / frontmatter_file
                    if not frontmatter_path.is_file():
                        issues.append(f"missing target frontmatter file for {target_name}: {frontmatter_file}")
                    else:
                        try:
                            payload = json.loads(read_text(frontmatter_path))
                        except json.JSONDecodeError as exc:
                            issues.append(f"{frontmatter_file} is not valid JSON: {exc}")
                        else:
                            if payload.get("name") != skill_dir.name:
                                issues.append(f"{frontmatter_file} name must match directory name")
                if not isinstance(install_path, str):
                    issues.append(f"{target_name} install_path must be a string")

    if manifest_data:
        manifest_files = manifest_data.get("files")
        if not isinstance(manifest_files, list):
            issues.append("manifest.json files must be a list")
        else:
            file_entries: list[tuple[str, str]] = []
            for entry in manifest_files:
                if not isinstance(entry, dict):
                    issues.append("manifest.json entries must be objects")
                    continue
                rel_path = entry.get("path")
                expected_sha = entry.get("sha256")
                if not isinstance(rel_path, str) or not isinstance(expected_sha, str):
                    issues.append("manifest.json entries require string path and sha256")
                    continue
                file_path = skill_dir / rel_path
                if not file_path.is_file():
                    issues.append(f"manifest references missing file: {rel_path}")
                    continue
                actual_sha = sha256_file(file_path)
                if actual_sha != expected_sha:
                    issues.append(f"sha256 mismatch for {rel_path}")
                file_entries.append((rel_path, actual_sha))

            if file_entries:
                computed_sha = compute_package_sha(file_entries)
                manifest_sha = manifest_data.get("package_sha256")
                if not isinstance(manifest_sha, str):
                    issues.append("manifest.json package_sha256 must be a string")
                elif manifest_sha != computed_sha:
                    issues.append("manifest.json package_sha256 does not match computed package hash")
                if package_sha and package_sha != computed_sha:
                    issues.append("package.json integrity.package_sha256 does not match computed package hash")
                package_sha = computed_sha

    return ValidationResult(skill=skill_dir.name, valid=not issues, issues=issues, package_sha256=package_sha)


def load_skill(
    repo_root: Path,
    skill: str | Path,
    target_filter: set[str] | None = None,
    *,
    allowed_scopes: set[str] | None = None,
) -> CanonicalSkill:
    skill_dir = resolve_skill_dir(repo_root, skill)
    result = validate_skill_dir(skill_dir, target_filter=target_filter)
    if not result.valid:
        raise ValidationFailure(result.issues)

    package_data = json.loads(read_text(skill_dir / "package.json"))
    identity = package_data["identity"]
    scope = package_data["distribution"]["scope"]
    if allowed_scopes is not None and scope not in allowed_scopes:
        allowed = ", ".join(sorted(allowed_scopes))
        raise ValueError(f"{identity['name']} has scope {scope}; allowed scopes: {allowed}")
    targets: dict[str, TargetConfig] = {}

    for target_name, target_data in package_data["targets"].items():
        if target_filter and target_name not in target_filter:
            continue
        frontmatter = json.loads(read_text(skill_dir / target_data["frontmatter_file"]))
        targets[target_name] = TargetConfig(
            name=target_name,
            frontmatter=frontmatter,
            install_path=target_data["install_path"],
        )

    asset_dirs = [name for name in OPTIONAL_ASSET_DIRS if (skill_dir / name).is_dir()]

    return CanonicalSkill(
        root=skill_dir,
        name=identity["name"],
        scope=scope,
        source_ref=_source_ref_for_skill_dir(repo_root, skill_dir),
        version=identity["version"],
        description=identity["description"],
        updated_at=identity["updated_at"],
        tags=list(identity["tags"]),
        instruction=read_text(skill_dir / "instruction.md"),
        package_sha256=result.package_sha256 or package_data["integrity"]["package_sha256"],
        manifest_file=package_data["integrity"]["manifest_file"],
        targets=targets,
        asset_dirs=asset_dirs,
    )


def load_all_skills(
    repo_root: Path,
    target_filter: set[str] | None = None,
    *,
    scopes: set[str] | None = None,
) -> list[CanonicalSkill]:
    skills = [load_skill(repo_root, path, target_filter=target_filter) for path in iter_skill_dirs(repo_root)]
    if scopes is None:
        return skills
    return [skill for skill in skills if skill.scope in scopes]


def load_shared_regular_skills(
    repo_root: Path,
    target_filter: set[str] | None = None,
) -> list[CanonicalSkill]:
    return [
        skill
        for skill in load_all_skills(repo_root, target_filter=target_filter, scopes={"public"})
        if SHARED_MANAGER_TAG in skill.tags
    ]


def load_manager_catalog_skills(
    repo_root: Path,
    target_filter: set[str] | None = None,
) -> list[CanonicalSkill]:
    catalog: dict[str, CanonicalSkill] = {}
    for skill in load_all_skills(repo_root, target_filter=target_filter, scopes={"maintainer"}):
        catalog[skill.name] = skill
    for skill in load_shared_regular_skills(repo_root, target_filter=target_filter):
        catalog.setdefault(skill.name, skill)
    return [catalog[name] for name in sorted(catalog)]


def load_manager_catalog_skill(
    repo_root: Path,
    skill_name: str,
    target_filter: set[str] | None = None,
) -> CanonicalSkill:
    for skill in load_manager_catalog_skills(repo_root, target_filter=target_filter):
        if skill.name == skill_name:
            return skill
    raise FileNotFoundError(f"{skill_name} is not available in the manager catalog")
