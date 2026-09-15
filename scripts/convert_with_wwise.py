#!/usr/bin/env python3
"""Convert prepared WAVs to genuine Windows WEM files with WwiseConsole."""

from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifest" / "taunts.json"
DEFAULT_PROJECT = ROOT / "wwise-project" / "CustomTaunts" / "CustomTaunts.wproj"


def first_existing(paths: list[str]) -> str | None:
    for candidate in paths:
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def find_wwise_console() -> str | None:
    override = os.environ.get("WWISE_CONSOLE")
    on_path = shutil.which("WwiseConsole") or shutil.which("WwiseConsole.exe")
    common_macos = sorted(
        glob.glob("/Applications/Audiokinetic/Wwise_*/Wwise.app/Contents/Tools/WwiseConsole.sh"),
        reverse=True,
    )
    common_windows = sorted(
        glob.glob(r"C:\Program Files\Audiokinetic\Wwise *\Authoring\x64\Release\bin\WwiseConsole.exe"),
        reverse=True,
    )
    return first_existing([override or "", on_path or "", *common_macos, *common_windows])


def embedded_wwise_path(path: Path) -> str:
    """Return a path readable from a WSOURCES file, including Wwise-on-macOS Wine."""
    resolved = str(path.resolve())
    if sys.platform == "darwin":
        return "Z:" + resolved.replace("/", "\\")
    return resolved


def run(command: list[str]) -> None:
    print("running:", " ".join(f'"{part}"' if " " in part else part for part in command))
    result = subprocess.run(command, check=False)
    if result.returncode:
        raise RuntimeError(f"WwiseConsole exited with status {result.returncode}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--input-dir", type=Path, default=ROOT / "audio" / "preprocessed")
    parser.add_argument("--wem-dir", type=Path, default=ROOT / "audio" / "wem")
    parser.add_argument("--project", type=Path, default=DEFAULT_PROJECT)
    parser.add_argument("--conversion", default="Default Conversion Settings")
    parser.add_argument("--check", action="store_true", help="only report WwiseConsole availability")
    args = parser.parse_args()

    console = find_wwise_console()
    if not console:
        print("ERROR: WwiseConsole was not found.", file=sys.stderr)
        print(
            "Install Wwise Authoring plus Windows platform support with Audiokinetic Launcher, "
            "or set WWISE_CONSOLE to WwiseConsole.exe/WwiseConsole.sh.",
            file=sys.stderr,
        )
        print("See docs/WWISE_CONVERSION.md. No substitute or renamed WAV was created.", file=sys.stderr)
        return 2
    if args.check:
        print(f"WwiseConsole: {console}")
        return 0

    try:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read manifest: {exc}", file=sys.stderr)
        return 2

    mappings: list[tuple[Path, str]] = []
    seen_input_names: set[str] = set()
    seen_output_names: set[str] = set()
    for index, taunt in enumerate(payload.get("taunts", [])):
        try:
            source_name = taunt["source_audio"]
            output_name = taunt["output_filename"]
            number = taunt["number"]
        except (KeyError, TypeError):
            print(
                f"ERROR: taunts[{index}] is missing number, source_audio, or output_filename",
                file=sys.stderr,
            )
            return 2
        if isinstance(number, bool) or not isinstance(number, int) or number < 1:
            print(f"ERROR: taunts[{index}].number must be an integer of at least 1", file=sys.stderr)
            return 2
        if not isinstance(source_name, str) or Path(source_name).name != source_name:
            print(f"ERROR: taunts[{index}].source_audio must be a filename", file=sys.stderr)
            return 2
        expected_output = f"Play_Taunt_{number}.wem"
        if not isinstance(output_name, str) or Path(output_name).name != output_name:
            print(f"ERROR: taunts[{index}].output_filename must be a filename", file=sys.stderr)
            return 2
        if output_name != expected_output:
            print(
                f"ERROR: taunts[{index}].output_filename must be exactly {expected_output}",
                file=sys.stderr,
            )
            return 2
        if output_name.casefold() in seen_output_names:
            print(f"ERROR: duplicate output filename: {output_name}", file=sys.stderr)
            return 2
        seen_output_names.add(output_name.casefold())
        prepared = args.input_dir / f"{Path(source_name).stem}.wav"
        if prepared.name.casefold() in seen_input_names:
            print(f"ERROR: prepared filename collision: {prepared.name}", file=sys.stderr)
            return 2
        seen_input_names.add(prepared.name.casefold())
        if not prepared.is_file():
            print(f"ERROR: missing prepared WAV: {prepared}", file=sys.stderr)
            print("Run scripts/preprocess_audio.py first.", file=sys.stderr)
            return 2
        mappings.append((prepared, output_name))
    if not mappings:
        print("ERROR: manifest contains no taunts", file=sys.stderr)
        return 2

    project = args.project.resolve()
    if project.parent.name != project.stem:
        print(
            "ERROR: Wwise requires the project folder and .wproj stem to match "
            f"(expected .../{project.stem}/{project.stem}.wproj).",
            file=sys.stderr,
        )
        return 2

    try:
        if not project.is_file():
            project.parent.mkdir(parents=True, exist_ok=True)
            run([console, "create-new-project", str(project), "--platform", "Windows"])

        wsources = project.with_suffix(".wsources")
        root = ET.Element(
            "ExternalSourcesList",
            {"SchemaVersion": "1", "Root": embedded_wwise_path(args.input_dir)},
        )
        for prepared, _output_name in mappings:
            ET.SubElement(root, "Source", {"Path": prepared.name, "Conversion": args.conversion})
        ET.indent(root, space="  ")
        ET.ElementTree(root).write(wsources, encoding="utf-8", xml_declaration=True)

        converted = project.parent / "Converted"
        converted.mkdir(parents=True, exist_ok=True)
        run(
            [
                console,
                "convert-external-source",
                str(project),
                "--platform",
                "Windows",
                "--source-file",
                str(wsources),
                "--output",
                "Windows",
                str(converted),
            ]
        )

        args.wem_dir.mkdir(parents=True, exist_ok=True)
        for prepared, output_name in mappings:
            generated = converted / f"{prepared.stem}.wem"
            if not generated.is_file():
                raise RuntimeError(f"Wwise reported success but did not create {generated}")
            destination = args.wem_dir / output_name
            shutil.copy2(generated, destination)
            print(f"created: {destination.relative_to(ROOT)}")
    except (OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print("No fake WEM fallback was used. See docs/WWISE_CONVERSION.md.", file=sys.stderr)
        return 1

    print(f"converted {len(mappings)} taunts with Wwise for Windows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
