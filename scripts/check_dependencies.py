#!/usr/bin/env python3
"""Report availability of tools used by the custom-taunts workflow."""

from __future__ import annotations

import glob
import os
import shutil
import sys
from pathlib import Path


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


def main() -> int:
    print(f"Python:       OK ({sys.version.split()[0]})")
    ffmpeg = os.environ.get("CUSTOM_TAUNTS_FFMPEG") or shutil.which("ffmpeg")
    if ffmpeg and Path(ffmpeg).is_file():
        print(f"ffmpeg:       OK ({ffmpeg})")
    else:
        print("ffmpeg:       MISSING (optional; required for preprocessing)")
        print("               Install from https://ffmpeg.org/download.html and add it to PATH,")
        print("               or set CUSTOM_TAUNTS_FFMPEG to ffmpeg.exe.")

    wwise = find_wwise_console()
    if wwise:
        print(f"WwiseConsole: OK ({wwise})")
    else:
        print("WwiseConsole: MISSING (required for genuine .wem conversion)")
        print("               Install Wwise Authoring plus Windows platform support with")
        print("               Audiokinetic Launcher: https://www.audiokinetic.com/en/download/")
        print("               Then follow docs/WWISE_CONVERSION.md; this project does not fake WEM output.")
    return 0 if ffmpeg and wwise else 1


if __name__ == "__main__":
    raise SystemExit(main())
