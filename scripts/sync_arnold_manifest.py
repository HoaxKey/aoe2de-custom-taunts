#!/usr/bin/env python3
"""Generate the primary mod manifest from the approved Arnold capture ledger."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "manifest" / "arnold_taunts_capture.csv"
MANIFEST = ROOT / "manifest" / "taunts.json"


def main() -> int:
    with LEDGER.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    errors: list[str] = []
    expected_numbers = list(range(1, 106))
    actual_numbers: list[int] = []
    taunts: list[dict[str, object]] = []
    for row_number, row in enumerate(rows, start=2):
        try:
            number = int(row["number"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"row {row_number}: number must be an integer")
            continue
        actual_numbers.append(number)
        required = ("aoe2_taunt", "arnold_quote", "movie", "mp3_filename", "wem_filename")
        missing = [name for name in required if not row.get(name, "").strip()]
        if missing:
            errors.append(f"row {row_number}: missing {', '.join(missing)}")
            continue
        if row.get("status") not in {"captured", "reviewed", "encoded", "tested_in_game"}:
            errors.append(f"row {row_number}: audio is not captured")
        expected_mp3 = f"arnold_taunt_{number:03d}.mp3"
        expected_wem = f"Play_Taunt_{number:02d}.wem"
        if row["mp3_filename"] != expected_mp3:
            errors.append(f"row {row_number}: mp3_filename must be {expected_mp3}")
        if row["wem_filename"] != expected_wem:
            errors.append(f"row {row_number}: wem_filename must be {expected_wem}")

        note_parts = [f"Arnold: “{row['arnold_quote']}” — {row['movie']}." ]
        if row.get("notes", "").strip():
            note_parts.append(row["notes"].strip())
        taunts.append(
            {
                "number": number,
                "display_name": row["aoe2_taunt"],
                "source_audio": row["mp3_filename"],
                "output_filename": row["wem_filename"],
                "notes": " ".join(note_parts),
            }
        )

    if actual_numbers != expected_numbers:
        errors.append("ledger must contain each taunt number from 1 through 105 exactly once and in order")
    if errors:
        print("ERROR: cannot generate Arnold manifest", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    payload = {
        "schema_version": 1,
        "mod": {
            "slug": "arnold-schwarzenegger-taunts",
            "title": "Arnold Schwarzenegger Taunts",
            "author": "AoE2 Arnold Taunts project",
            "version": "0.2.1",
            "description": (
                "Cosmetic, client-side Arnold Schwarzenegger replacements for AoE2DE taunts /1-/105. "
                "Every listener must install and enable the same version."
            ),
            "custom_number_start": 1,
        },
        "taunts": taunts,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"generated: {MANIFEST.relative_to(ROOT)} ({len(taunts)} taunts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
