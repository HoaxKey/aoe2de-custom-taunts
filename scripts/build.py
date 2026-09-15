#!/usr/bin/env python3
"""Validate, assemble, and package the AoE2DE custom-taunts mod."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifest" / "taunts.json"
MAX_TAUNT_NUMBER = 2_147_483_647
SAFE_SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SAFE_VERSION = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._+-]*$")


class ValidationError(Exception):
    """Raised when the project cannot produce a safe package."""


@dataclass(frozen=True)
class Project:
    manifest: Path
    metadata: dict[str, Any]
    taunts: list[dict[str, Any]]


def load_project(manifest: Path, source_dir: Path) -> Project:
    errors: list[str] = []
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValidationError(f"cannot read manifest {manifest}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"manifest is not valid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValidationError("manifest root must be a JSON object")
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    metadata = payload.get("mod")
    taunts = payload.get("taunts")
    if not isinstance(metadata, dict):
        errors.append("mod must be an object")
        metadata = {}
    if not isinstance(taunts, list) or not taunts:
        errors.append("taunts must be a non-empty array")
        taunts = []

    required_meta = ("slug", "title", "author", "version", "description", "custom_number_start")
    for key in required_meta:
        if key not in metadata:
            errors.append(f"mod.{key} is required")
    slug = metadata.get("slug")
    if not isinstance(slug, str) or not SAFE_SLUG.fullmatch(slug):
        errors.append("mod.slug must contain only lowercase letters, digits, dot, underscore, or hyphen")
    for key in ("title", "author", "version", "description"):
        if not isinstance(metadata.get(key), str) or not metadata.get(key, "").strip():
            errors.append(f"mod.{key} must be a non-empty string")
        elif "\n" in metadata[key] or "\r" in metadata[key]:
            errors.append(f"mod.{key} must be a single-line string")
    version = metadata.get("version")
    if isinstance(version, str) and not SAFE_VERSION.fullmatch(version):
        errors.append("mod.version contains unsafe filename characters")
    start = metadata.get("custom_number_start")
    if isinstance(start, bool) or not isinstance(start, int) or start < 1:
        errors.append("mod.custom_number_start must be an integer of at least 1")
        start = 300

    seen_numbers: set[int] = set()
    seen_outputs: set[str] = set()
    for index, item in enumerate(taunts):
        label = f"taunts[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        number = item.get("number")
        if isinstance(number, bool) or not isinstance(number, int):
            errors.append(f"{label}.number must be an integer")
        elif number < start or number > MAX_TAUNT_NUMBER:
            errors.append(f"{label}.number must be between {start} and {MAX_TAUNT_NUMBER}")
        elif number in seen_numbers:
            errors.append(f"duplicate taunt number: {number}")
        else:
            seen_numbers.add(number)

        for key in ("display_name", "source_audio", "output_filename"):
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}.{key} must be a non-empty string")
            elif Path(value).name != value:
                errors.append(f"{label}.{key} must be a filename, not a path")

        source_name = item.get("source_audio")
        if isinstance(source_name, str) and Path(source_name).name == source_name:
            if not (source_dir / source_name).is_file():
                errors.append(f"missing source audio: audio/source/{source_name}")
        expected = f"Play_Taunt_{number}.wem" if isinstance(number, int) else None
        output = item.get("output_filename")
        if expected and output != expected:
            errors.append(f"{label}.output_filename must be exactly {expected}")
        if isinstance(output, str):
            folded = output.casefold()
            if folded in seen_outputs:
                errors.append(f"duplicate output filename: {output}")
            seen_outputs.add(folded)
        notes = item.get("notes")
        if notes is not None and not isinstance(notes, str):
            errors.append(f"{label}.notes must be a string when present")

    if errors:
        raise ValidationError("\n".join(f"- {error}" for error in errors))
    return Project(manifest=manifest, metadata=metadata, taunts=sorted(taunts, key=lambda row: row["number"]))


def validate_wem_file(path: Path) -> None:
    try:
        size = path.stat().st_size
        with path.open("rb") as handle:
            header = handle.read(12)
    except OSError as exc:
        raise ValidationError(f"cannot read WEM {path}: {exc}") from exc
    if size < 44:
        raise ValidationError(f"WEM is too small to be valid: {path} ({size} bytes)")
    if len(header) != 12 or header[:4] not in (b"RIFF", b"RIFX") or header[8:12] != b"WAVE":
        raise ValidationError(f"WEM lacks a RIFF/RIFX WAVE-family header: {path}")


def check_wems(project: Project, wem_dir: Path) -> tuple[list[tuple[dict[str, Any], Path]], list[str]]:
    found: list[tuple[dict[str, Any], Path]] = []
    missing: list[str] = []
    errors: list[str] = []
    for taunt in project.taunts:
        filename = taunt["output_filename"]
        path = wem_dir / filename
        if not path.is_file():
            missing.append(filename)
            continue
        try:
            validate_wem_file(path)
        except ValidationError as exc:
            errors.append(str(exc))
        else:
            found.append((taunt, path))
    if errors:
        raise ValidationError("\n".join(f"- {error}" for error in errors))
    return found, missing


def reference_sheet(project: Project, incomplete: bool) -> str:
    lines = [
        f"# {project.metadata['title']} — taunt reference",
        "",
        f"Version: `{project.metadata['version']}`",
        "",
        "> Client-side audio: every player who should hear these taunts must install and enable the same version.",
        "",
    ]
    if incomplete:
        lines.extend(["> **INCOMPLETE TEST BUILD:** required Wwise `.wem` files are absent. This archive is not playable.", ""])
    lines.extend(["| Command | Name | Notes |", "|---|---|---|"])
    for taunt in project.taunts:
        notes = str(taunt.get("notes", "")).replace("|", "\\|").replace("\n", " ")
        name = str(taunt["display_name"]).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `/{taunt['number']}` | {name} | {notes} |")
    lines.append("")
    return "\n".join(lines)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_deterministic_zip(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source).as_posix()
            if path.is_dir():
                info = zipfile.ZipInfo(relative + "/", date_time=(1980, 1, 1, 0, 0, 0))
                info.external_attr = (0o40755 << 16) | 0x10
                archive.writestr(info, b"")
                continue
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def build(project: Project, wem_dir: Path, build_root: Path, release_root: Path, allow_missing: bool) -> Path:
    found, missing = check_wems(project, wem_dir)
    if missing and not allow_missing:
        filenames = "\n".join(f"  - audio/wem/{name}" for name in missing)
        raise ValidationError(
            "required Wwise files are missing:\n"
            f"{filenames}\n"
            "Run the preprocessing step, convert those WAVs with Wwise for Windows, and copy the genuine "
            "outputs into audio/wem/. See docs/WWISE_CONVERSION.md."
        )

    suffix = "-INCOMPLETE" if missing else ""
    directory_name = f"{project.metadata['slug']}{suffix}"
    destination = build_root / directory_name
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    assets = ROOT / "mod-assets"
    if assets.is_dir():
        shutil.copytree(assets, destination, dirs_exist_ok=True)
    info = {
        "Author": project.metadata["author"],
        "CacheStatus": 0,
        "Description": project.metadata["description"],
        "Title": project.metadata["title"],
    }
    (destination / "info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (destination / "TAUNTS.md").write_text(reference_sheet(project, bool(missing)), encoding="utf-8")

    sound_dir = destination / "resources" / "_common" / "drs" / "sounds"
    sound_dir.mkdir(parents=True)
    for _taunt, source in found:
        shutil.copy2(source, sound_dir / source.name)

    if missing:
        notice = (
            "INCOMPLETE TEST BUILD - NOT PLAYABLE\n\n"
            "The archive layout was generated successfully, but genuine Wwise media is missing:\n"
            + "".join(f"- {name}\n" for name in missing)
            + "\nSee docs/WWISE_CONVERSION.md in the source project.\n"
        )
        (destination / "INCOMPLETE_BUILD.txt").write_text(notice, encoding="utf-8")

    checksums: list[str] = []
    for path in sorted(item for item in destination.rglob("*") if item.is_file()):
        if path.name != "CHECKSUMS.sha256":
            checksums.append(f"{sha256(path)}  {path.relative_to(destination).as_posix()}")
    (destination / "CHECKSUMS.sha256").write_text("\n".join(checksums) + "\n", encoding="utf-8")

    archive_name = f"{project.metadata['slug']}-v{project.metadata['version']}{suffix}.zip"
    archive = release_root / archive_name
    write_deterministic_zip(destination, archive)
    print(f"built directory: {destination}")
    print(f"built archive:   {archive}")
    if missing:
        print("status: INCOMPLETE test artifact; not installable until genuine WEM files are supplied")
    else:
        print(f"status: complete ({len(found)} taunts)")
    return archive


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "build"))
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--source-dir", type=Path, default=ROOT / "audio" / "source")
    parser.add_argument("--wem-dir", type=Path, default=ROOT / "audio" / "wem")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build")
    parser.add_argument("--release-dir", type=Path, default=ROOT / "releases")
    parser.add_argument("--manifest-only", action="store_true", help="skip WEM checks when validating")
    parser.add_argument(
        "--allow-missing-wem",
        action="store_true",
        help="create a conspicuously marked, non-playable archive to test the packaging pipeline",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        project = load_project(args.manifest, args.source_dir)
        if args.command == "validate":
            if args.allow_missing_wem:
                raise ValidationError("--allow-missing-wem is only valid with the build command")
            if not args.manifest_only:
                _found, missing = check_wems(project, args.wem_dir)
                if missing:
                    raise ValidationError("missing WEM files:\n" + "\n".join(f"- {name}" for name in missing))
            print(f"manifest valid: {len(project.taunts)} taunts")
            if args.manifest_only:
                print("WEM validation skipped (--manifest-only)")
            else:
                print("WEM validation passed")
            return 0
        build(project, args.wem_dir, args.build_dir, args.release_dir, args.allow_missing_wem)
        return 0
    except ValidationError as exc:
        print(f"VALIDATION FAILED:\n{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
