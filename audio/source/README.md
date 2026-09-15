# Source audio

Put editable WAV, MP3, FLAC, M4A, or other `ffmpeg`-readable source files here.
Filenames must match `source_audio` in `manifest/taunts.json`.

This directory is ignored by Git by default because audio can be large or may
have licensing restrictions. Add only audio that you have the right to share;
use `git add -f audio/source/<file>` when committing is deliberate.

Run `python3 scripts/generate_placeholders.py` to recreate the three original,
copyright-free synthesized sample WAV files referenced by the starter manifest.
