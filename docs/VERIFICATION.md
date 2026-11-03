# Verification

## Version 1.4 — static checks and a balance simulation only

Story mode, four generated maps and the slot system were written without GameMaker. What *was* done:

- `python tools/check_gml.py` — 84 GML files, 131 project functions, 8 macros: **OK**.
- `python tools/validate_project.py` — **3005 checks passed** (114 resources, 33 objects, 6 rooms).
- `tools/story_maps.py --report`: every generated map passes its geometry checks (pads clear of the road and of each other, route inside the field, portal/core separated). Previews are in `docs/maps/`.
- `tools/story_maps.py --write` and `tools/build_story_art.py` were re-run; outputs are deterministic.
- `tools/balance_sim.py`: Python port of the battle rules with a scripted player. HP margin: survival x2.8; chapters x3.4, x3.0, x2.8, x2.5, x2.3. **This is an estimate** — a human player will do better or worse.
- 30 new runtime assertions were added to `obj_test` (rules and wave lists, chapter maps, story progress, save format 2/3, slot write / backup recovery / damage / delete, a story battle on a generated map across save, new game and load, story victory unlocking the next chapter). **They have never been run.**

**Not done:** compiling, Project Health, Run, `tools/test.ps1`, any play-through of the five chapters, a check that cutscene and slot text fit their panels in English and Ukrainian, the new main-menu layout, weather performance. The story text has not been proof-read by a native speaker. Checklist: `Що треба зробити.md`.

## Version 1.3 — static checks and numeric audio analysis only

The 1.3 changes (graphics, animation, audio, UI; see `CHANGELOG.md`) were written without GameMaker. What *was* done:

- `python tools/check_gml.py` — 81 GML files, 72 project functions, 6 macros: **OK**.
- `python tools/validate_project.py` — **2826 checks passed** (JSON5 metadata, resource links, sprites, fonts, audio format — music must be stereo, effects mono — and `duration` in each sound `.yy` matching its WAV).
- Every GML built-in function new in 1.3 was listed and checked by hand for existence; argument counts of the riskiest ones (`draw_roundrect_color`, `draw_sprite_pos`, `draw_rectangle_color`, `matrix_build`, `draw_sprite_tiled_ext`, `array_delete`, `audio_sound_pitch`) were verified against the manual.
- `tools/build_fx_art.py` and `tools/build_audio.py` were re-run: the `.yyp`, all WAVs, PNGs and `.yy` files are byte-identical (deterministic, idempotent).
- Sprites were inspected visually on contact sheets; the fog texture was verified to tile seamlessly.
- Audio: peak/RMS and loop-seam discontinuity measured (`build_audio.py --report`): `snd_ambience` seam 0.054 vs. max normal step 0.115; `snd_battle` 0.029 vs. 0.044.

**Not done:** compiling, Project Health, Run, `tools/test.ps1`, **and listening** to any sound or music. Numeric analysis cannot tell whether the audio sounds good, is balanced against the effects, or loops without a perceptible gap. Whether GameMaker accepts the stereo uncompressed music import as configured (`channelFormat: 1`, `compression: 0`) is an assumption from the file format. Treat 1.3 as unverified; the checklist is in `Що треба зробити.md`.

## Version 1.2 — static checks only

The 1.2 changes (see `CHANGELOG.md`) were written without access to GameMaker. What *was* done:

- `python tools/check_gml.py` — brackets, strings, project function calls and argument counts, `_local` variables, resource and palette names across all 80 GML files: **OK**. The checker itself was validated against deliberately corrupted copies of the project.
- `python tools/validate_project.py` — JSON5 metadata, resource links, room order, sprites, fonts (including Ukrainian glyph coverage), audio, icon, UTF-8/LF: **2594 checks passed**. No `.yy`/`.yyp` file was modified.
- Hand review of every changed GML line against the original; the save format change is additive (optional `mode`, optional `best_*`) so 1.1 saves and the existing round-trip test remain valid by construction.

**Not done:** compiling, Project Health, Run, `tools/test.ps1`. Until those pass, treat 1.2 as unverified. The checklist is in `Що треба зробити.md`.

# Verification — 26 September 2026 (version 1.1)

GameMaker IDE metadata version: 2026.0.0.16. Windows VM compiler/runner: 2026.0.0.23.

## Passed

- Native compiler loaded and linked the complete project, compiled GML and produced a Windows ZIP.
- JSON5 parser: all 85 project resources checked; 33 objects, 6 rooms. Room instance order, property overrides, parent references, complete sprite layers/sequences, fonts, audio formats, icon and UTF-8/LF verified.
- 64 runtime integration assertions passed. They cover economy, upgrades, refunds, occupied pads, save validation, exact active-battle round trips (including an in-flight projectile and slow status), bad save version/data, changed maps, corrupted primary/backup recovery, frozen pause state, language/options persistence, room navigation, fallback and reset.
- The manual test room opens paused with three tower types, four enemy types and its own authored route. Tests cover all spawn controls, clearing, aether, healing, invulnerability on/off, final wave selection, victory/defeat, reset/retry, button recovery, forced periodic autosave and unchanged expedition save/backup after returning to the main game. English and Ukrainian runtime screenshots inspected.
- Eight waves won at 1x and 2x using the starting 280 aether and normal earned income. Both runs ended with 20 core HP and 121 kills. The scripted player builds a mix of three tower types between waves.
- Actual core-breach path separately produced defeat.
- Runtime screenshots inspected for the studio splash, language choice, both-language menu, Ukrainian guide, options, pause, battle and results. Atlas extraction and paragraph breaks were corrected after visual inspection.
- ZIP integrity and byte-for-byte contents checked. It contains the EXE, data.win, options.ini, PLAY.md and ART.md.
- The executable's PE icon resources were extracted and compared with the custom icon: **all 7 resolutions embedded; 256px pixel comparison error 0**. The option uses `${options_dir}`, avoiding GameMaker's default icon directory.

Machine-readable reports: `build/metadata-check.json`, `build/verification/runtime-results.json`, `build/verification/package-check.json`, `build/verification/icon-check.json`. Screenshots: `build/verification/` and selected copies in `docs/screenshots/`.

## Not claimed

- Project Health and Run initiated through the IDE UI. Native capture failed with `SetIsBorderRequired`, then desktop control was stopped with Escape. Official compiler/runner verification succeeded independently.
- Human playtesting, subjective audio approval, another physical PC, and other operating systems.
- Automated gameplay proves functionality and a viable strategy; it does not prove final difficulty or entertainment value.

## Repeat

`python tools/validate_project.py`

`./tools/build.ps1`

`./tools/test.ps1`

`python tools/inspect_exe_icon.py`

`python tools/verify_package.py`

The runtime test only uses `wp_test_*` files. The normal player's settings and save are untouched.
