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

## Taunt and quote list

Think one of these could be even funnier or more appropriate? Please
[submit a GitHub issue](https://github.com/HoaxKey/aoe2de-custom-taunts/issues/new)
with the taunt number, your suggested Arnold quote, the film it comes from, and
why it is a better match. Links to a clean existing soundboard clip are
especially helpful.

<!-- BEGIN GENERATED ARNOLD TAUNT TABLE -->

| Taunt | AoE2 meaning | Arnold replacement | Film |
|---:|---|---|---|
| /1 | Yes | “Affirmative.” | Terminator 2: Judgment Day |
| /2 | No | “Negative.” | Terminator 2: Judgment Day |
| /3 | Food Please | “All they want is food!” | The Running Man |
| /4 | Wood Please | “Down to the wood.” | Kindergarten Cop |
| /5 | Gold Please | “Money. That’s what I need, money.” | The Running Man |
| /6 | Stone Please | “Hand over the diamond, Garden Gal!” | Batman & Robin |
| /7 | Ahh | “You got to help me remember.” | Total Recall |
| /8 | All Hail, King of the Losers | “You’re a fucking choirboy compared to me! A choirboy!” | End of Days |
| /9 | Oooh | “You’re one ugly motherfucker.” | Predator |
| /10 | I’ll Beat You Back to Age of Empires | “You are terminated.” | Terminator 3: Rise of the Machines |
| /11 | Hahahahahah | “Ha! You didn’t know I was gonna say that, did you?” | Last Action Hero |
| /12 | Ack, He Rushed | “Men tried to kill me.” | Total Recall |
| /13 | Sure Blame it on Your ISP | “So basically, you’re lying.” | True Lies |
| /14 | Start the Game Already | “Come on, Bennett. Let’s party.” | Commando |
| /15 | Don’t Point That Thing at Me | “I’ll give you ten minutes to prove it, and then I shoot you.” | Last Action Hero |
| /16 | Enemy Sighted | “Someone’s coming.” | The Running Man |
| /17 | It is Good To be the King | “I am the hero.” | Last Action Hero |
| /18 | Monk, I Need a Monk | “You have to have faith.” | End of Days |
| /19 | Long Time, No Siege | “I’m back.” | Terminator 3: Rise of the Machines |
| /20 | My Granny Could Scrap Better Than That | “You hit like a vegetarian.” | Escape Plan |
| /21 | Nice Town, I’ll Take It | “Could I speak to the drug dealer of the house, please?” | Last Action Hero |
| /22 | Quit Touchin Me | “Don’t do that.” | Terminator 3: Rise of the Machines |
| /23 | Raiding Party | “It’s a beautiful day and we’re out killing drug dealers.” | Last Action Hero |
| /24 | Dadgum | “Jesus, Marge! What the fuck?” | End of Days |
| /25 | Ehhh Smite Me | “Do it! Come on! Kill me!” | Predator |
| /26 | The Wonder, The Wonder, The Noooooo | “This is going to be very difficult to explain.” | Terminator: Dark Fate |
| /27 | You Played 2 Hours to Die Like This | “It is in your nature to destroy yourselves.” | Terminator 2: Judgment Day |
| /28 | Yeah Well You Should See the Other Guy | “Yes, fine. No problems.” | Red Heat |
| /29 | Rogan? | “Crom laughs at your four winds.” | Conan the Barbarian |
| /30 | WOLOLO | “Come with me if you want to live.” | Terminator 2: Judgment Day |
| /31 | Attack an Enemy Now | “It’s showtime!” | The Running Man |
| /32 | Cease Creating Extra Villagers | “STOP IT!” | Kindergarten Cop |
| /33 | Create Extra Villagers | “You should clone yourself.” | The 6th Day |
| /34 | Build a Navy | “I hope Mr. Bane can swim.” | Batman & Robin |
| /35 | Stop Building a Navy | “Abort mission. We return back to base.” | The Running Man |
| /36 | Wait for my Signal to Attack | “Stay here. I’ll be back.” | Terminator 2: Judgment Day |
| /37 | Build a Wonder | “Of course, I think I’m gonna win.” | Pumping Iron |
| /38 | Give Me Your Extra Resources | “I need your help.” | Eraser |
| /39 | Ally Sound | “Trust me.” | Terminator 2: Judgment Day |
| /40 | Enemy Sound | “If it bleeds, we can kill it.” | Predator |
| /41 | Neutral Sound | “I’m not into politics. I’m into survival.” | The Running Man |
| /42 | What Age are you in | “Old. Not obsolete.” | Terminator Genisys |
| /43 | What is Your Strategy | “Now, this is the plan.” | Total Recall |
| /44 | How Many Resources do you Have | “How much is that?” | Jingle All the Way |
| /45 | Retreat Now | “Get to the chopper!” | Predator |
| /46 | Flare the Location of Your Army | “Where is this?” | Eraser |
| /47 | Attack in the Direction of the Flared Location | “Follow him.” | Commando |
| /48 | I’m Being Attacked, Please Help | “I’m counting on you, buddy.” | Total Recall |
| /49 | Build a Forward Base at the Flared Location | “Pull over here.” | True Lies |
| /50 | Build a Fortification at the Flared Location | “I want a defensive position.” | Predator |
| /51 | Keep Your Army Close to Mine and Fight With Me | “As long as I’m with you, I’m in no danger.” | Twins |
| /52 | Build a Market at the Flared Location | “We’re all businessmen.” | Jingle All the Way |
| /53 | Rebuild Your Base at the Flared Location | “I want my life back.” | The 6th Day |
| /54 | Build a Wall Between the two Flared Locations | “I can’t self-terminate. You must lower me into the steel.” | Terminator 2: Judgment Day |
| /55 | Build a Wall Around Your Town | “We make a stand now, or there will be nobody left to go to the chopper.” | Predator |
| /56 | Train Units Which Counter the Enemy’s Army | “Take two of these, and call me in the morning.” | Batman & Robin |
| /57 | Stop Training Counter Units | “Enough talk.” | Conan the Destroyer |
| /58 | Prepare to Send me all Your Resources so I can Vanquish Our Foes | “I need your clothes, your boots, and your motorcycle.” | Terminator 2: Judgment Day |
| /59 | Stop Sending me Extra Resources | “One more thing: I work alone.” | Eraser |
| /60 | Prepare to Train a Large Army, I’ll Send You as Many Resources as I can Spare | “They need a leader. They need someone with experience.” | The Running Man |
| /61 | Attack Player 1 | “I’ll be back.” | The Terminator |
| /62 | Attack Player 2 | “Consider that a divorce.” | Total Recall |
| /63 | Attack Player 3 | “Let off some steam, Bennett.” | Commando |
| /64 | Attack Player 4 | “Tonight, hell freezes over!” | Batman & Robin |
| /65 | Attack Player 5 | “You’re fired.” | True Lies |
| /66 | Attack Player 6 | “It’s not a tumor!” | Kindergarten Cop |
| /67 | Attack Player 7 | “Put that cookie down! Now!” | Jingle All the Way |
| /68 | Attack Player 8 | “Here is Subzero. Now, plain zero.” | The Running Man |
| /69 | Delete the Object on the Flared Location | “It must be destroyed.” | Terminator 2: Judgment Day |
| /70 | Delete Your Excess Villagers | “I let him go.” | Commando |
| /71 | Delete Excess Warships | “He won’t be needing it.” | Commando |
| /72 | Focus on Training Infantry Units | “See you at the party, Richter!” | Total Recall |
| /73 | Focus on Training Cavalry Units | “Stick around.” | Predator |
| /74 | Focus on Training Ranged Units | “Don’t disturb my friend. He’s dead tired.” | Commando |
| /75 | Focus on Training Warships | “To be or not to be? Not to be.” | Last Action Hero |
| /76 | Attack the Enemy With Militia | “You want to be a farmer? Here’s a couple of acres.” | Last Action Hero |
| /77 | Attack the Enemy With Archers | “You’re luggage.” | Eraser |
| /78 | Attack the Enemy With Skirmishers | “Who is your daddy, and what does he do?” | Kindergarten Cop |
| /79 | Attack the Enemy With a mix of Archers and Skirmishers | “Stop whining!” | Kindergarten Cop |
| /80 | Attack the Enemy With Scout Cavalry | “Everybody, chill!” | Batman & Robin |
| /81 | Attack the Enemy With Men-At-Arms | “Allow me to break the ice.” | Batman & Robin |
| /82 | Attack the Enemy With Eagle Scouts | “What killed the dinosaurs? The Ice Age!” | Batman & Robin |
| /83 | Attack the Enemy With Towers | “He had to split.” | The Running Man |
| /84 | Attack the Enemy With Crossbowmen | “What a hothead.” | The Running Man |
| /85 | Attack the Enemy With Cavalry Archers | “Crom!” | Conan the Barbarian |
| /86 | Attack the Enemy With Unique Units | “Get your ass to Mars.” | Total Recall |
| /87 | Attack the Enemy With Knights | “Give these people air!” | Total Recall |
| /88 | Attack the Enemy With Battle Elephants | “You think this is the real Quaid? It is!” | Total Recall |
| /89 | Attack the Enemy With Scorpions | “No problemo.” | Terminator 2: Judgment Day |
| /90 | Attack the Enemy With Monks | “I need a vacation.” | Terminator 2: Judgment Day |
| /91 | Attack the Enemy With Monks and Mangonels | “Chill out, dickwad.” | Terminator 2: Judgment Day |
| /92 | Attack the Enemy With Eagle Warriors | “Dillon! You son of a bitch!” | Predator |
| /93 | Attack the Enemy With Halberdiers and Rams | “CIA got you pushing too many pencils?” | Predator |
| /94 | Attack the Enemy With Elite Eagle Warriors | “Remember when I promised to kill you last? I lied.” | Commando |
| /95 | Attack the Enemy With Arbalests | “I eat Green Berets for breakfast.” | Commando |
| /96 | Attack the Enemy With Champions | “Knock, knock.” | Commando |
| /97 | Attack the Enemy With Galleys | “Fuck you, asshole.” | Commando |
| /98 | Attack the Enemy With Fire Galleys | “Rubber baby buggy bumpers!” | Last Action Hero |
| /99 | Attack the Enemy With Demolition Rafts | “AAAAAAARGH!” | Total Recall |
| /100 | Attack the Enemy With War Galleys | “Milk is for babies. When you grow up, you drink beer.” | Pumping Iron |
| /101 | Attack the Enemy With Fire Ships | “Money talks and bullshit walks.” | Twins |
| /102 | Attack the Enemy With Unique Warships | “Cocainum!” | Red Heat |
| /103 | Use an Onager to cut Down Trees at the Flared Location | “AAAAAAARGH!” | Predator |
| /104 | Don’t Resign | “You just gotta keep coming back stronger.” | Pumping Iron |
| /105 | You can Resign Now | “Hasta la vista, baby.” | Terminator 2: Judgment Day |

<!-- END GENERATED ARNOLD TAUNT TABLE -->

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
   `...\arnold-schwarzenegger-taunts\resources\_common\drs\sounds\Play_Taunt_01.wem`,
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
  `resources\_common\drs\sounds\Play_Taunt_01.wem` for `/1`, including the
  required leading zero for single-digit built-in taunts.
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
