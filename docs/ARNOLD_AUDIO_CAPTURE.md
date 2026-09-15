# Arnold Schwarzenegger taunt audio capture

The approved `/1`–`/105` mapping is stored in
[`manifest/arnold_taunts_capture.csv`](../manifest/arnold_taunts_capture.csv).
That CSV is the source of truth for finding, capturing, editing, and reviewing
the replacement audio.

## Status values

- `approved_needs_source`: wording and film are approved; source still required.
- `source_found`: a candidate source and timestamp have been recorded.
- `captured`: the original MP3 clip exists in `audio/source/`.
- `reviewed`: the MP3 has been auditioned and accepted.
- `encoded`: the final WEM exists in `audio/wem/`.
- `tested_in_game`: the taunt has played correctly in AoE2DE.

## Capture requirements

1. Search established Arnold/movie soundboards and ready-made clip libraries
   first. Resort to extracting audio from a film only when no suitable clean
   clip exists. Record the source location and timestamp in the CSV.
2. Capture Arnold's actual delivery, not another character repeating the line.
3. Preserve enough room tone to avoid clipped consonants, but exclude dialogue
   from other characters whenever possible.
4. Save the untouched capture using the exact `mp3_filename` in the CSV, under
   `audio/source/`.
5. Prefer a clean speech-only clip of roughly 0.5–5 seconds. Longer approved
   lines may run longer when trimming would damage the joke.
6. Do not add music, artificial reverb, memes, or normalization to the source
   MP3. The existing preprocessing stage handles trimming and loudness.
7. After capture, update the row's status and evidence fields. If an approved
   quotation proves to be a paraphrase or misattribution, replace it with the
   closest authentic Arnold line and record both the reason and original
   wording in the notes rather than silently changing it.

Soundboard availability does not establish permission to redistribute the
underlying film audio. Treat these captures as personal working material unless
the project owner separately clears the relevant rights.

## Output naming

The editable source is zero-padded for easy sorting:

```text
audio/source/arnold_taunt_001.mp3
```

The final game asset is not zero-padded and must match AoE2DE exactly:

```text
audio/wem/Play_Taunt_1.wem
```

The primary `manifest/taunts.json` is generated from this ledger by
`scripts/sync_arnold_manifest.py` and drives the `/1`–`/105` replacement build.
The original tested `/300`–`/302` starter manifest is preserved separately as
`manifest/starter_taunts.json`.
