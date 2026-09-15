#!/usr/bin/env python3
"""Prepare manifest source audio for Wwise with ffmpeg."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "manifest" / "taunts.json"


def find_ffmpeg() -> str | None:
    override = os.environ.get("CUSTOM_TAUNTS_FFMPEG")
    return override if override else shutil.which("ffmpeg")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--source-dir", type=Path, default=ROOT / "audio" / "source")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "audio" / "preprocessed")
    parser.add_argument("--target-lufs", type=float, default=-16.0)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--check", action="store_true", help="only report dependency availability")
    args = parser.parse_args()

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print(
            "ERROR: ffmpeg was not found. Install it from https://ffmpeg.org/download.html "
            "and add it to PATH, or set CUSTOM_TAUNTS_FFMPEG to the executable path.",
            file=sys.stderr,
        )
        return 2
    if args.check:
        print(f"ffmpeg: {ffmpeg}")
        return 0

    try:
        payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read manifest: {exc}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    failed = False
    output_names: set[str] = set()
    for item in payload.get("taunts", []):
        source_name = item.get("source_audio")
        if not isinstance(source_name, str) or not source_name:
            print("ERROR: every taunt needs source_audio before preprocessing", file=sys.stderr)
            failed = True
            continue
        source = args.source_dir / source_name
        output_name = f"{Path(source_name).stem}.wav"
        if output_name.casefold() in output_names:
            print(f"ERROR: preprocessed filename collision: {output_name}", file=sys.stderr)
            failed = True
            continue
        output_names.add(output_name.casefold())
        destination = args.output_dir / output_name
        if not source.is_file():
            print(f"ERROR: missing source audio: {source}", file=sys.stderr)
            failed = True
            continue
        if destination.exists() and not args.force:
            print(f"kept existing: {destination.relative_to(ROOT)}")
            continue

        audio_filter = (
            "silenceremove=start_periods=1:start_duration=0.05:start_threshold=-50dB:"
            "stop_periods=1:stop_duration=0.35:stop_threshold=-50dB,"
            f"loudnorm=I={args.target_lufs}:TP=-1.5:LRA=11"
        )
        command = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-vn",
            "-af",
            audio_filter,
            "-ac",
            "1",
            "-ar",
            "48000",
            "-c:a",
            "pcm_s16le",
            str(destination),
        ]
        result = subprocess.run(command, check=False)
        if result.returncode:
            print(f"ERROR: ffmpeg failed for {source_name}", file=sys.stderr)
            failed = True
        else:
            print(f"prepared: {destination.relative_to(ROOT)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
