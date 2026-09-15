# Wwise output

Run `python3 scripts/convert_with_wwise.py` to create genuine Windows Wwise
Encoded Media here, named exactly as declared in the manifest, for example
`Play_Taunt_300.wem`. You can also place verified WEM files here manually.

This directory is ignored by Git by default. The build validates that every
required file exists and has a RIFF/RIFX WAVE-family header. That structural
check catches missing or obviously renamed files, but only an in-game test can
prove codec compatibility with the current AoE2DE build.

See `docs/WWISE_CONVERSION.md` for the conversion handoff.
