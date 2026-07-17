from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from .utils import sha256_bytes


@dataclass(frozen=True)
class BundleArtifactSpec:
    artifact_id: str
    source_path: PurePosixPath
    target_paths: dict[str, PurePosixPath]
    comment_prefix: str
    executable: bool = False


@dataclass(frozen=True)
class BundleArtifactSource:
    spec: BundleArtifactSpec
    content: bytes

    @property
    def sha256(self) -> str:
        return sha256_bytes(_canonical_content(self.content))


@dataclass(frozen=True)
class ManagedBundleSource:
    name: str
    root: Path
    version: str
    description: str
    updated_at: str
    artifacts: tuple[BundleArtifactSource, ...]


@dataclass(frozen=True)
class BundleArtifactStatus:
    artifact_id: str
    status: str
    location: Path
    version: str | None = None
    recorded_sha256: str | None = None
    details: str | None = None
    managed: bool = False


@dataclass(frozen=True)
class ManagedBundleStatus:
    name: str
    target: str
    status: str
    version: str
    artifacts: tuple[BundleArtifactStatus, ...]


@dataclass(frozen=True)
class _OriginalFile:
    path: Path
    content: bytes | None
    mode: int | None


def load_managed_bundle(repo_root: Path, name: str) -> ManagedBundleSource | None:
    root = repo_root / "canonical-configs" / name
    config_path = root / "config.json"
    if not config_path.is_file():
        return None

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"invalid managed bundle config for {name}: {exc}") from exc
    if not isinstance(config, dict) or config.get("schema_version") != 1:
        raise ValueError(f"invalid managed bundle config for {name}: schema_version must be 1")
    if config.get("name") != name:
        raise ValueError(f"invalid managed bundle config for {name}: name must match its directory")

    version = config.get("version")
    raw_artifacts = config.get("artifacts")
    if not isinstance(version, str) or not version or any(character.isspace() for character in version):
        raise ValueError(f"invalid managed bundle config for {name}: version is required")
    if not isinstance(raw_artifacts, list) or not raw_artifacts:
        raise ValueError(f"invalid managed bundle config for {name}: artifacts must be a non-empty list")

    seen_ids: set[str] = set()
    seen_targets: set[tuple[str, PurePosixPath]] = set()
    artifacts: list[BundleArtifactSource] = []
    for raw_artifact in raw_artifacts:
        spec = _parse_artifact_spec(name, raw_artifact)
        if spec.artifact_id in seen_ids:
            raise ValueError(f"invalid managed bundle config for {name}: duplicate artifact id {spec.artifact_id}")
        seen_ids.add(spec.artifact_id)
        for target, target_path in spec.target_paths.items():
            target_key = (target, target_path)
            if target_key in seen_targets:
                raise ValueError(
                    f"invalid managed bundle config for {name}: duplicate target path {target_path} for {target}"
                )
            seen_targets.add(target_key)
        source_path = root.joinpath(*spec.source_path.parts)
        if source_path.is_symlink() or not source_path.is_file():
            raise ValueError(f"managed bundle {name} is missing artifact source: {spec.source_path}")
        artifacts.append(BundleArtifactSource(spec=spec, content=source_path.read_bytes()))

    return ManagedBundleSource(
        name=name,
        root=root,
        version=version,
        description=str(config.get("description", "")),
        updated_at=str(config.get("updated_at", "")),
        artifacts=tuple(artifacts),
    )


def managed_bundle_status(
    source: ManagedBundleSource,
    project_dir: Path,
    target: str,
) -> ManagedBundleStatus:
    artifact_statuses = tuple(
        _artifact_status(source, artifact, project_dir, target) for artifact in source.artifacts
    )
    states = {artifact.status for artifact in artifact_statuses}
    installed_count = sum(artifact.status != "not_installed" for artifact in artifact_statuses)

    if installed_count == 0:
        status = "not_installed"
    elif "unmanaged" in states:
        status = "unmanaged"
    elif "drift" in states:
        status = "drift"
    elif "broken" in states or "not_installed" in states:
        status = "broken"
    elif "update_available" in states:
        status = "update_available"
    else:
        status = "up_to_date"
    return ManagedBundleStatus(
        name=source.name,
        target=target,
        status=status,
        version=source.version,
        artifacts=artifact_statuses,
    )


def install_managed_bundle(
    source: ManagedBundleSource,
    project_dir: Path,
    target: str,
    *,
    force: bool = False,
    confirm: Callable[[str], bool] | None = None,
    post_install: Callable[[], None] | None = None,
) -> tuple[Path, ...]:
    status = managed_bundle_status(source, project_dir, target)
    unmanaged = [artifact for artifact in status.artifacts if artifact.status == "unmanaged"]
    if unmanaged:
        names = ", ".join(artifact.artifact_id for artifact in unmanaged)
        raise ValueError(f"bundle {source.name} has unmanaged artifact(s): {names}; refusing to overwrite")
    drifted = [artifact for artifact in status.artifacts if artifact.status == "drift"]
    if drifted:
        if not force:
            raise ValueError(
                f"bundle {source.name} has drifted artifact(s); rerun install with --force to overwrite local changes"
            )
        if confirm is None:
            raise ValueError(f"bundle {source.name} has drifted artifact(s) and requires confirmation")
        names = ", ".join(artifact.artifact_id for artifact in drifted)
        if not confirm(
            f"Bundle {source.name} artifact(s) {names} have drifted. "
            "Install will overwrite local changes. Continue? [y/N]: "
        ):
            raise RuntimeError("Update aborted by user.")

    planned: list[tuple[Path, bytes, int]] = []
    originals: list[_OriginalFile] = []
    for artifact in source.artifacts:
        path = bundle_artifact_path(artifact, project_dir, target)
        mode = 0o755 if artifact.spec.executable else 0o644
        planned.append((path, render_bundle_artifact(source, artifact), mode))
        originals.append(_capture_original(path))

    written: list[Path] = []
    try:
        for path, content, mode in planned:
            _atomic_write(path, content, mode)
            written.append(path)
        if post_install is not None:
            post_install()
    except Exception as exc:
        rollback_errors = _restore_originals(originals)
        if rollback_errors:
            details = "; ".join(rollback_errors)
            raise RuntimeError(f"bundle install failed: {exc}; rollback also failed: {details}") from exc
        raise
    return tuple(written)


def bundle_artifact_path(
    artifact: BundleArtifactSource,
    project_dir: Path,
    target: str,
) -> Path:
    try:
        relative = artifact.spec.target_paths[target]
    except KeyError:
        raise ValueError(f"artifact {artifact.spec.artifact_id} does not support target {target}") from None
    return project_dir.joinpath(*relative.parts)


def render_bundle_artifact(
    source: ManagedBundleSource,
    artifact: BundleArtifactSource,
) -> bytes:
    body = _canonical_content(artifact.content)
    marker = (
        f"{artifact.spec.comment_prefix} skill-forge:{source.name}/{artifact.spec.artifact_id} "
        f"version={source.version} sha256={artifact.sha256}\n"
    ).encode("utf-8")
    return body + marker


def _parse_artifact_spec(name: str, raw: object) -> BundleArtifactSpec:
    if not isinstance(raw, dict):
        raise ValueError(f"invalid managed bundle config for {name}: artifact must be an object")
    artifact_id = raw.get("id")
    source = raw.get("source")
    targets = raw.get("targets")
    comment_prefix = raw.get("comment_prefix")
    if not isinstance(artifact_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", artifact_id):
        raise ValueError(f"invalid managed bundle config for {name}: invalid artifact id")
    if not isinstance(source, str):
        raise ValueError(f"invalid managed bundle config for {name}: artifact source is required")
    source_path = _safe_relative_path(source, f"artifact {artifact_id} source")
    if not isinstance(targets, dict) or not targets:
        raise ValueError(f"invalid managed bundle config for {name}: artifact {artifact_id} needs targets")
    target_paths: dict[str, PurePosixPath] = {}
    for target, path in targets.items():
        if not isinstance(target, str) or not isinstance(path, str):
            raise ValueError(f"invalid managed bundle config for {name}: invalid target for {artifact_id}")
        target_paths[target] = _safe_relative_path(path, f"artifact {artifact_id} target")
    if comment_prefix not in {"#", "//"}:
        raise ValueError(f"invalid managed bundle config for {name}: unsupported comment_prefix")
    executable = raw.get("executable", False)
    if not isinstance(executable, bool):
        raise ValueError(f"invalid managed bundle config for {name}: executable must be boolean")
    return BundleArtifactSpec(
        artifact_id=artifact_id,
        source_path=source_path,
        target_paths=target_paths,
        comment_prefix=comment_prefix,
        executable=executable,
    )


def _safe_relative_path(value: str, label: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"invalid {label}: path must stay within its root")
    return path


def _artifact_status(
    source: ManagedBundleSource,
    artifact: BundleArtifactSource,
    project_dir: Path,
    target: str,
) -> BundleArtifactStatus:
    path = bundle_artifact_path(artifact, project_dir, target)
    if not path.exists():
        return BundleArtifactStatus(artifact.spec.artifact_id, "not_installed", path)
    if path.is_symlink() or not path.is_file():
        return BundleArtifactStatus(
            artifact.spec.artifact_id,
            "unmanaged",
            path,
            details="target exists but is not a regular file",
        )

    content = path.read_bytes()
    marker_re = _artifact_marker_re(source, artifact)
    match = marker_re.search(content)
    if match is None:
        return BundleArtifactStatus(
            artifact.spec.artifact_id,
            "unmanaged",
            path,
            details="missing skill-forge bundle marker",
        )

    version = match.group("version").decode("utf-8")
    recorded_sha = match.group("sha").decode("ascii")
    body = _canonical_content(content[: match.start()] + content[match.end() :])
    actual_sha = sha256_bytes(body)
    if actual_sha != recorded_sha:
        return BundleArtifactStatus(
            artifact.spec.artifact_id,
            "drift",
            path,
            version,
            recorded_sha,
            "installed content differs from the recorded hash",
            True,
        )
    if version != source.version:
        return BundleArtifactStatus(
            artifact.spec.artifact_id,
            "update_available",
            path,
            version,
            recorded_sha,
            managed=True,
        )
    if recorded_sha != artifact.sha256:
        return BundleArtifactStatus(
            artifact.spec.artifact_id,
            "drift",
            path,
            version,
            recorded_sha,
            "canonical artifact changed without a version bump",
            True,
        )
    if artifact.spec.executable and not path.stat().st_mode & 0o111:
        return BundleArtifactStatus(
            artifact.spec.artifact_id,
            "broken",
            path,
            version,
            recorded_sha,
            "managed executable artifact is missing its executable mode",
            True,
        )
    return BundleArtifactStatus(
        artifact.spec.artifact_id,
        "up_to_date",
        path,
        version,
        recorded_sha,
        managed=True,
    )


def _artifact_marker_re(
    source: ManagedBundleSource,
    artifact: BundleArtifactSource,
) -> re.Pattern[bytes]:
    prefix = re.escape(artifact.spec.comment_prefix.encode("utf-8"))
    identity = re.escape(f"skill-forge:{source.name}/{artifact.spec.artifact_id}".encode("utf-8"))
    return re.compile(
        rb"^" + prefix + rb" " + identity + rb" version=(?P<version>\S+) sha256=(?P<sha>[0-9a-f]{64})\n?",
        re.MULTILINE,
    )


def _canonical_content(content: bytes) -> bytes:
    return content.rstrip(b"\n") + b"\n"


def _capture_original(path: Path) -> _OriginalFile:
    if not path.exists():
        return _OriginalFile(path, None, None)
    if not path.is_file():
        return _OriginalFile(path, None, None)
    stat = path.stat()
    return _OriginalFile(path, path.read_bytes(), stat.st_mode & 0o777)


def _atomic_write(path: Path, content: bytes, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        temp_path.chmod(mode)
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _restore_originals(originals: list[_OriginalFile]) -> list[str]:
    errors: list[str] = []
    for original in reversed(originals):
        try:
            if original.content is None:
                if original.path.is_file():
                    original.path.unlink()
            else:
                _atomic_write(original.path, original.content, original.mode or 0o644)
        except OSError as exc:
            errors.append(f"{original.path}: {exc}")
    return errors
