# Wwise conversion handoff

The repository intentionally does **not** rename WAV files to `.wem` or claim
that `ffmpeg` can create Wwise media. The final encoding step needs
[Audiokinetic Wwise](https://www.audiokinetic.com/en/download/) (or another
encoder whose output you have personally verified in the current AoE2DE build).

## Prepare the inputs

From the repository root:

```powershell
py -3 scripts\generate_placeholders.py
py -3 scripts\preprocess_audio.py --force
```

The second command creates mono, 48 kHz, 16-bit PCM WAV files in
`audio\preprocessed`, trims leading/trailing silence, and targets -16 LUFS with
a -1.5 dB true-peak ceiling. Change `--target-lufs` if your pack needs a
different loudness, then audition the results before Wwise conversion.

## Encode genuine WEM files automatically

Install Wwise Authoring and its **Windows** platform support through the
Audiokinetic Launcher, then run from the repository root:

```powershell
py -3 scripts\convert_with_wwise.py
```

On macOS, use `python3` and the same forward-slash command used elsewhere in
this project. The helper locates the newest installed Wwise, creates the ignored
`wwise-project/CustomTaunts/CustomTaunts.wproj` scratch project if needed, uses
its Windows `Default Conversion Settings` (PCM), converts every prepared WAV,
and copies each genuine output to the manifest-assigned name under `audio/wem`.
PCM is deliberately used for these short samples: it is lossless and keeps the
placeholder pack small enough while avoiding codec-version ambiguity.

If Wwise is installed in a nonstandard location, set its path explicitly:

```powershell
$env:WWISE_CONSOLE='C:\Program Files\Audiokinetic\Wwise 2025.1.10.9233\Authoring\x64\Release\bin\WwiseConsole.exe'
py -3 scripts\convert_with_wwise.py
```

The helper stops with an error if Wwise or a prepared WAV is missing. It never
renames a WAV to `.wem` and never emits substitute media.

## Manual Authoring fallback

1. Install Wwise Authoring and its **Windows** platform support through the
   Audiokinetic Launcher. If a recent Wwise release produces silent media in
   AoE2DE, use a Wwise version/codec known to match the current game build;
   AoE2DE's audio format has changed in past updates.
2. Create a blank Wwise project and select the Windows platform.
3. Import one `audio\preprocessed\*.wav` file as an SFX object.
4. Assign a Windows Conversion Settings ShareSet. `Default Conversion Settings`
   (PCM) matches the automated path. If the game rejects it after a future
   update, follow the maintained [AoE2DE Audio Modding Guide](https://steamcommunity.com/sharedfiles/filedetails/?id=1915891079)
   for the Wwise version/codec required by that game update.
5. Convert or generate a SoundBank so Wwise writes the external media. Find the
   corresponding generated `.wem` in the project's `.cache\Windows\SFX` or
   `GeneratedSoundBanks\Windows` tree. Converting one source at a time makes the
   generated media unambiguous.
6. Audition/identify that generated file, then copy it into this repository's
   `audio\wem` directory using the exact manifest name:

   ```text
   placeholder_rally.wav   -> audio\wem\Play_Taunt_300.wem
   placeholder_ready.wav   -> audio\wem\Play_Taunt_301.wem
   placeholder_victory.wav -> audio\wem\Play_Taunt_302.wem
   ```

7. Repeat for every manifest entry, then run:

   ```powershell
   py -3 scripts\build.py validate
   py -3 scripts\build.py build
   ```

The build checks the RIFF/RIFX WAVE-family header, but Wwise codec compatibility
can only be confirmed by enabling the mod and testing each command in AoE2DE.

## Dependency detection

`scripts\check_dependencies.py` reports both `ffmpeg` and WwiseConsole.
`scripts\convert_with_wwise.py --check` checks Wwise alone. The Wwise project
and caches are intentionally generated under the ignored `wwise-project/`
directory rather than committed or packaged.
