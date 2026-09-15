#!/usr/bin/env python3
"""Download curated soundboard clips and update the capture ledger."""

from __future__ import annotations

import argparse
import csv
import os
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


ALLOWED_HOSTS = {"s3.us-east-2.amazonaws.com"}


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise SystemExit(f"Missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def download(url: str, destination: Path) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise SystemExit(f"Refusing unapproved download host: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    destination.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", dir=destination.parent
    )
    try:
        with os.fdopen(file_descriptor, "wb") as output:
            with urllib.request.urlopen(request, timeout=30) as response:
                content_type = response.headers.get_content_type()
                if not content_type.startswith("audio/") and content_type != "application/octet-stream":
                    raise SystemExit(f"Unexpected content type for {url}: {content_type}")
                output.write(response.read())
        temporary = Path(temporary_name)
        if temporary.stat().st_size < 256:
            raise SystemExit(f"Downloaded clip is unexpectedly small: {url}")
        temporary.replace(destination)
    finally:
        temporary = Path(temporary_name)
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=Path("manifest/arnold_taunts_capture.csv"))
    parser.add_argument("--sources", type=Path, default=Path("manifest/arnoldum_sources.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("audio/source"))
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    fieldnames, ledger = read_rows(args.ledger)
    _, source_rows = read_rows(args.sources)
    by_number = {int(row["number"]): row for row in ledger}
    if len(by_number) != len(ledger):
        raise SystemExit("Duplicate taunt number in capture ledger")

    completed: list[int] = []
    for source in source_rows:
        number = int(source["number"])
        row = by_number.get(number)
        if row is None:
            raise SystemExit(f"Source mapping references missing taunt /{number}")
        destination = args.output_dir / row["mp3_filename"]
        if not (args.skip_existing and destination.is_file()):
            download(source["source_url"], destination)
        row["source_url"] = source["source_url"]
        row["status"] = "captured"
        capture_notes = source.get("capture_notes", "").strip()
        if capture_notes and capture_notes not in row["notes"]:
            row["notes"] = "; ".join(filter(None, (row["notes"], capture_notes)))
        completed.append(number)
        print(f"captured /{number}: {destination}")

    with args.ledger.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(ledger)
    print(f"updated {len(completed)} rows in {args.ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
