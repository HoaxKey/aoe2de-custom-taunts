# AoE2DE Arnold Schwarzenegger Taunts

A manifest-driven, cosmetic sound mod for **Age of Empires II: Definitive
Edition on PC**. It replaces all built-in `/1`–`/105` taunts with approved
Arnold Schwarzenegger movie quotes and noises.

> **Multiplayer limitation:** taunt audio is loaded locally. It is not sent to
> other players through chat or the game simulation. Every player who should
> hear a custom sound must install, enable, and prioritize the same mod version.
> A player without it may see the chat command but will not hear your custom
> media.

This mod changes no game data, balance, civilization, map, AI, or multiplayer
simulation files.

## Project layout

```text
audio/
  source/          editable originals (ignored by Git)
  preprocessed/    normalized WAVs for Wwise (generated, ignored)
  wem/             genuine Wwise outputs (ignored by default)
manifest/
  arnold_taunts_capture.csv  approved quote/source ledger
  audio_edits.json           explicit dialogue cut points
  taunts.json                 generated production assignments
  starter_taunts.json         preserved /300-/302 test configuration
mod-assets/        static files copied into every package
scripts/
  check_dependencies.py
  sync_arnold_manifest.py
  preprocess_audio.py
  convert_with_wwise.py
  build.py
docs/
  WWISE_CONVERSION.md
tests/
build/             assembled mod directory (generated)
releases/          ZIP packages (generated)
```

The playable package always uses the language-independent path:

```text
resources/_common/drs/sounds/Play_Taunt_<number>.wem
```

Do not place this pack under `resources/en/sound/taunt` or another language
folder. The exact capitalization of `Play_Taunt_` matters.

## Required software

- Python 3.9 or newer. The build uses only the standard library.
- `ffmpeg` on `PATH` for optional trimming, loudness normalization, and WAV
  preparation. Set `CUSTOM_TAUNTS_FFMPEG` to a full executable path instead if
  needed.
- Audiokinetic Wwise Authoring with Windows platform support for genuine `.wem`
  conversion. Wwise is not needed to validate the manifest or test ZIP layout.
- AoE2DE on PC for the final compatibility test.

## Quick start

Run these commands from the repository root. On Windows, replace `python3` with
`py -3` if needed.

```bash
python3 scripts/check_dependencies.py
python3 scripts/sync_arnold_manifest.py
python3 scripts/preprocess_audio.py --check
python3 scripts/preprocess_audio.py --force
python3 scripts/build.py validate --manifest-only
```

Next, convert the prepared WAVs with the installed Wwise command-line tool. This
creates an ignored scratch project targeting Windows and copies genuine outputs
to `audio/wem`:

```bash
python3 scripts/convert_with_wwise.py
```

If automatic discovery fails, set `WWISE_CONSOLE` to `WwiseConsole.exe` on
Windows or `WwiseConsole.sh` on macOS. The exact handoff and a manual Authoring
fallback are in [`docs/WWISE_CONVERSION.md`](docs/WWISE_CONVERSION.md). Once
genuine outputs are in `audio/wem`:

```bash
python3 scripts/build.py validate
python3 scripts/build.py build
```

The completed ZIP appears in `releases/`. It contains `info.json`, `TAUNTS.md`,
checksums, and the required `resources/_common/drs/sounds` tree at the archive
root. No source WAVs or gameplay data are packaged.

For CI or pipeline development only, this command creates a conspicuously named
and labeled non-playable archive even when WEM files are missing:

```bash
python3 scripts/build.py build --allow-missing-wem
```

It never passes as a normal release and must not be installed or published.

## Add or replace an Arnold sound

1. Update the matching row in `manifest/arnold_taunts_capture.csv` and place its
   MP3 in `audio/source/` using the row's zero-padded filename.
2. Run `python3 scripts/sync_arnold_manifest.py`. The generated
   `manifest/taunts.json` should not be edited by hand.
3. Add or adjust an entry in `manifest/audio_edits.json` when the source needs
   an explicit dialogue cut.
4. Run the preprocessor. It accepts any format your `ffmpeg` build can read and
   writes mono 48 kHz, 16-bit PCM WAV using `loudnorm` at -16 LUFS/-1.5 dBTP by
   default. Edge trimming is deliberately disabled for film dialogue because
   threshold-based trimming can remove quiet syllables; add
   `--trim-edge-silence` only for sources you have checked. Audition the result;
   automatic loudness processing is not a substitute for listening.
5. Run `python3 scripts/convert_with_wwise.py`. It converts every prepared WAV
   for Windows and assigns the exact manifest output name, such as
   `audio/wem/Play_Taunt_303.wem`.
6. Validate and build. The build rejects duplicates, numbers outside the chosen
   range, unsafe filenames, filename/number mismatches, missing source files,
   missing WEM files, undersized media, and files without a WEM-like RIFF/RIFX
   header.

Changing a number changes the command. Changing media without changing the
number replaces what that command plays. Before distributing an update, bump
`mod.version` so participants can confirm they have the same release.

## Local installation on Windows

1. In AoE2DE, open **Mods** and use **Open Directory/Open Local Folder** if it is
   available. Otherwise locate:

   ```text
   C:\Users\<Windows user>\Games\Age of Empires 2 DE\<profile id>\mods\local\
   ```

2. Create a folder named `arnold-schwarzenegger-taunts` there.
3. Extract the **contents** of the completed ZIP into that folder. The result
   must be
   `...\arnold-schwarzenegger-taunts\resources\_common\drs\sounds\Play_Taunt_1.wem`,
   not a doubled nested folder.
4. Restart the game if it was open. In **Mods > Installed Mods**, enable the mod
   and move it above any sound/taunt mod that assigns the same numbers. Some
   builds show an **Import Local Mods** button; use it if the local pack does not
   appear, then restart.

Never install by overwriting files in the Steam/Microsoft game installation.

## Enable and test

1. Confirm the mod is enabled in **Mods > Installed Mods**.
2. Under **Options > Audio**, turn up the Taunts volume. Under Online Settings,
   ensure taunts are not disabled/muted.
3. Start a lobby or match, open chat, and try representative commands such as
   `/1`, `/14`, `/45`, and `/105`.
4. Test every number after encoding and after major game updates. The build can
   validate file structure but cannot emulate the game's Wwise decoder.

## Share with multiplayer participants

Distribute the same versioned ZIP or publish the pack. Give participants the
numbered `TAUNTS.md` reference. Each listener must subscribe/install, enable,
and download the same version before launching the match. Because this is a
client-side cosmetic mod, lobby membership does not transmit the audio files.

## Publish through the AoE2DE mod system

You can publish either from the game or the official website. Sign in to the
account associated with your game, use **Mods > My Mods**, select the complete
local pack, and choose **Publish Mod** when that action is available. Add a
description, sound/cosmetic tags, a non-copyrighted thumbnail, and state the
client-side same-version requirement prominently. Alternatively, use the
[official Mods portal](https://www.ageofempires.com/mods/) to submit the
completed ZIP; its `resources` directory is already at the required archive
root. Never upload an `-INCOMPLETE.zip` artifact.

After publishing, subscribe to the published copy on a clean profile, restart
the game, and retest all numbers. The official support pages explain
[subscribing and installation](https://support.ageofempires.com/hc/en-us/articles/360050397471-Scenario-Mods-Download-and-Installation-Instructions)
and [enabling/disabling and priority](https://support.ageofempires.com/hc/en-us/articles/360047762971-How-do-I-enable-or-disable-a-mod).

## Troubleshooting

### A taunt is silent

- Verify the installed path and exact case:
  `resources\_common\drs\sounds\Play_Taunt_300.wem`.
- Run `python3 scripts/build.py validate`; a renamed WAV is not a genuine WEM.
- Confirm the file was encoded for Windows with a Wwise version/codec compatible
  with the current AoE2DE build. Re-encode and test if the game recently updated.
- Check Taunts volume, master volume, the correct output device, and `/` in the
  command. The official [Taunts & Cheats guide](https://support.ageofempires.com/hc/en-us/articles/10091280315924-Taunts-Cheats)
  confirms the leading slash, the Taunts volume control, and the global mute.

### Taunts are disabled or muted

Enable taunts in Online Settings and raise the dedicated Taunts slider under
Audio. Ask every intended listener to do the same; the sender's setting cannot
unmute another client.

### Incorrect language path

This pack is language-independent. Use `_common/drs/sounds`, not
`en/sound/taunt`, `en-US`, or a copied folder for every language. Do not install
both common and per-language variants of the same assignment.

### Conflicting number assignments or mod priority

Only one highest-priority mod can supply a given `Play_Taunt_<number>.wem`.
Search other taunt/audio mods for the same number, disable the conflict or
renumber this manifest, rebuild, and ensure all players adopt that same range.
Move this pack above conflicting sound mods in Installed Mods.

### Stale subscription or old local copy

Compare the version in installed `TAUNTS.md` with the shared release. Disable or
unsubscribe from duplicate copies, restart, resubscribe/reimport, allow the
download to finish, and restart again. Do not leave both a local and subscribed
copy enabled.

### A game update breaks the sound mod

Disable the pack to confirm the regression, check current AoE2DE patch notes and
the maintained audio-modding guide, then re-encode one short sample with a
compatible Wwise version/codec before rebuilding the whole release. Game updates
can change accepted Wwise media or reset/disable mod state; recheck enablement
and priority after updates.
