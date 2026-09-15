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
DEFAULT_EDITS = ROOT / "manifest" / "audio_edits.json"


def find_ffmpeg() -> str | None:
    override = os.environ.get("CUSTOM_TAUNTS_FFMPEG")
    return override if override else shutil.which("ffmpeg")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--edits", type=Path, default=DEFAULT_EDITS)
    parser.add_argument("--source-dir", type=Path, default=ROOT / "audio" / "source")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "audio" / "preprocessed")
    parser.add_argument("--target-lufs", type=float, default=-16.0)
    parser.add_argument(
        "--trim-edge-silence",
        action="store_true",
        help="conservatively trim leading/trailing digital silence; disabled by default to protect quiet dialogue",
    )
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

    edit_rows: dict[str, object] = {}
    if args.edits.is_file():
        try:
            edit_payload = json.loads(args.edits.read_text(encoding="utf-8"))
            raw_edits = edit_payload.get("edits", {})
            if not isinstance(raw_edits, dict):
                raise ValueError("edits must be an object")
            edit_rows = raw_edits
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"ERROR: cannot read audio edits: {exc}", file=sys.stderr)
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

        filters: list[str] = []
        edit = edit_rows.get(str(item.get("number")))
        segments: list[list[float]] = []
        if edit is not None:
            if not isinstance(edit, dict) or not isinstance(edit.get("segments"), list):
                print(f"ERROR: invalid edit for taunt {item.get('number')}", file=sys.stderr)
                failed = True
                continue
            try:
                segments = [[float(pair[0]), float(pair[1])] for pair in edit["segments"]]
            except (TypeError, ValueError, IndexError):
                print(f"ERROR: invalid segments for taunt {item.get('number')}", file=sys.stderr)
                failed = True
                continue
            if not segments or any(start < 0 or end <= start for start, end in segments):
                print(f"ERROR: invalid segment bounds for taunt {item.get('number')}", file=sys.stderr)
                failed = True
                continue
        if args.trim_edge_silence:
            # Trim only the outside edges. This deliberately uses a very low
            # threshold and short detection window because several film clips
            # have quiet dialogue close to their boundaries.
            filters.extend(
                [
                    "silenceremove=start_periods=1:start_duration=0.01:start_threshold=-70dB",
                    "areverse",
                    "silenceremove=start_periods=1:start_duration=0.01:start_threshold=-70dB",
                    "areverse",
                ]
            )
        filters.append(f"loudnorm=I={args.target_lufs}:TP=-1.5:LRA=11")
        audio_filter = ",".join(filters)
        command = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-vn",
        ]
        if len(segments) > 1:
            trim_chains = []
            labels = []
            for segment_index, (start, end) in enumerate(segments):
                label = f"segment{segment_index}"
                labels.append(f"[{label}]")
                trim_chains.append(
                    f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[{label}]"
                )
            command.extend(
                [
                    "-filter_complex",
                    ";".join(trim_chains)
                    + ";"
                    + "".join(labels)
                    + f"concat=n={len(segments)}:v=0:a=1,{audio_filter}[out]",
                    "-map",
                    "[out]",
                ]
            )
        else:
            if segments:
                start, end = segments[0]
                audio_filter = f"atrim=start={start}:end={end},asetpts=PTS-STARTPTS,{audio_filter}"
            command.extend(["-af", audio_filter])
        command.extend([
            "-ac",
            "1",
            "-ar",
            "48000",
            "-c:a",
            "pcm_s16le",
            str(destination),
        ])
        result = subprocess.run(command, check=False)
        if result.returncode:
            print(f"ERROR: ffmpeg failed for {source_name}", file=sys.stderr)
            failed = True
        else:
            print(f"prepared: {destination.relative_to(ROOT)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
