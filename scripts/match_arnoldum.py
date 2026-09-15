#!/usr/bin/env python3
"""Match the approved capture ledger against an exported Arnoldum index."""

from __future__ import annotations

import argparse
import csv
import difflib
import html
import json
import re
import unicodedata
from pathlib import Path


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-z0-9 ]", " ", value.lower())
    return " ".join(value.split())


def load_quotes(index_path: Path) -> list[dict[str, object]]:
    source = index_path.read_text(encoding="utf-8")
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        source,
    )
    if not match:
        raise SystemExit(f"Could not find __NEXT_DATA__ in {index_path}")
    payload = json.loads(html.unescape(match.group(1)))
    return payload["props"]["pageProps"]["initialQuotes"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path, help="Saved HTML from https://arnoldum.com/")
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--minimum", type=float, default=0.0)
    args = parser.parse_args()

    quotes = load_quotes(args.index)
    with args.ledger.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    print("number\tscore\tapproved quote\tmatched soundboard title\tmovie\turl")
    for row in rows:
        target = normalize(row["arnold_quote"])
        ranked: list[tuple[float, dict[str, object]]] = []
        for quote in quotes:
            title = str(quote["title"])
            score = difflib.SequenceMatcher(None, target, normalize(title)).ratio()
            ranked.append((score, quote))
        score, quote = max(ranked, key=lambda item: item[0])
        if score < args.minimum:
            continue
        movie = quote.get("movie") or {}
        print(
            f'{int(row["number"]):03d}\t{score:.3f}\t{row["arnold_quote"]}\t'
            f'{quote["title"]}\t{movie.get("title", "")}\t{quote["url"]}'
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
