#!/usr/bin/env python3
"""Generate three short, original synthesized WAV placeholders."""

from __future__ import annotations

import argparse
import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "audio" / "source"
RATE = 48_000

MOTIFS = {
    "placeholder_rally.wav": [(523.25, 0.16), (659.25, 0.16), (783.99, 0.24)],
    "placeholder_ready.wav": [(440.00, 0.13), (0.0, 0.06), (440.00, 0.13)],
    "placeholder_victory.wav": [(659.25, 0.14), (783.99, 0.14), (1046.50, 0.28)],
}


def synthesize(motif: list[tuple[float, float]]) -> bytes:
    samples: list[int] = []
    phase = 0.0
    for frequency, duration in motif:
        count = round(RATE * duration)
        fade = min(round(RATE * 0.012), count // 2)
        for index in range(count):
            if frequency == 0:
                value = 0.0
            else:
                envelope = 1.0
                if index < fade:
                    envelope = index / max(fade, 1)
                elif index >= count - fade:
                    envelope = (count - index - 1) / max(fade, 1)
                fundamental = math.sin(phase)
                overtone = 0.16 * math.sin(phase * 2.0)
                value = 0.28 * envelope * (fundamental + overtone)
                phase += 2.0 * math.pi * frequency / RATE
            samples.append(max(-32768, min(32767, round(value * 32767))))
    return b"".join(struct.pack("<h", sample) for sample in samples)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="overwrite existing samples")
    args = parser.parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for filename, motif in MOTIFS.items():
        destination = OUTPUT_DIR / filename
        if destination.exists() and not args.force:
            print(f"kept existing: {destination.relative_to(ROOT)}")
            continue
        with wave.open(str(destination), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes(synthesize(motif))
        print(f"generated: {destination.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
