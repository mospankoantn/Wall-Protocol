# Verification — 26 September 2026

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
