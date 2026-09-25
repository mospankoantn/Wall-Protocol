# Art and audio provenance

**Wall Protocol / Eclipse Wire, 26 September 2026.**

- Studio logo: user-supplied `Eclipse_Wire_logo.png`, preserved without artistic changes; imported as `spr_studio`.
- Environment, sprite atlas and ground: generated with the built-in OpenAI image generation tool. Final sources are stored locally in `art/menu_keyart.png`, `art/defense_atlas.png`, `art/forest_ground.png`.
- Windows icon: the shield/crystal emblem from that atlas, stored in `art/game_icon.png` and `options/windows/icons/icon.ico` (16–256 px).
- Sprite extraction: individual measured rectangles imported into native GameMaker sprites, retaining alpha. `tools/import_atlas.py` records the rectangles. Enemy walk cycles use two supplied poses. All PNG layers and sequences are included.
- UI plates, editor handles, road and particles: code-native shapes.
- Audio: original deterministic procedural synthesis produced for this project, 44.1 kHz mono WAV sources in `sounds/`. Nine short effects and one 32-second ambient loop. No downloaded music or sample pack was used. Synthesis is recorded in `tools/build_resources.py`.
- Fonts: bitmap atlases rendered from installed Arial and Georgia, with Latin and Ukrainian glyph ranges. The project contains compiled font bitmaps rather than copies of Windows TTF files.
- Coding and production assistance: OpenAI tools. Creative direction and studio attribution: Oleh / Eclipse Wire.
- Development-only JSON5 parser: `json5` 0.15.0, Apache-2.0; its license is preserved in `tools/vendor/json5-0.15.0.dist-info/licenses/LICENSE`. It is not part of the playable Windows package.

These generated images should be described as AI-assisted assets in the portfolio; the logo is owner-supplied. No third-party artists are credited as having painted them.

## Final generation prompts

The built-in image tool was used; no API key or fallback CLI was used. An unsuccessful atlas-edit variation was discarded and is not used by the project.

### Menu key art

Use case: stylized-concept. Asset type: finished widescreen main-menu illustration for the dark fantasy tower defense PC game Wall Protocol. Create a cinematic painterly environment at dusk: a colossal weathered medieval stone defense wall and luminous cyan rune crystal guarding the last passage, dark conifer forest, ruined battlements, cold teal mist and restrained amber braziers, distant undead silhouettes. Sophisticated atmospheric hand-painted indie strategy game art, restrained details, readable shapes. Composition 1536x1024 landscape: important wall/crystal artwork in right two thirds, left third very dark uncluttered negative space for menu text which will be rendered separately. No text, no letters, no title, no logos, no watermark, no interface, no border. Palette charcoal blue, desaturated teal, old gold; dramatic premium key art.

### Defense atlas

Use case: stylized-concept. Asset type: ONE production game sprite atlas, 1536x1024 pixels, EXACT grid of 6 columns x 4 rows of 256x256 cells. Transparent background. Every object centered in its cell with generous transparent margin, no cell borders or labels. Dark fantasy tower-defense, matching polished hand-painted miniature game art, three-quarter top-down view, muted stone blue-gray with small vivid magic accents, clear silhouettes readable at 64px. Layout row 1: (1) golden wooden ballista archer tower, (2) violet rune obelisk tower, (3) cyan frost crystal tower, (4) luminous teal crystal core on stone plinth, (5) violet necromancer portal arch, (6) circular empty stone tower build foundation. Row 2: (1) undead skeleton soldier with tiny axe, (2) large armored undead brute, (3) slim hooded spectral runner cyan eyes, (4) large bone-armored skeleton boss, (5) dark conifer tree, (6) mossy jagged boulders. Row 3: same skeleton soldier, brute, runner, boss in alternate walking poses, then (5) lit amber stone brazier, (6) ruined gray crenellated wall segment. Row 4: (1) symmetrical heraldic shield featuring a crenellated wall and luminous cyan crystal, suitable for game icon, (2) arrow projectile, (3) violet magic orb, (4) cyan ice shard, (5) small golden aether crystal resource, (6) small grave marker. No text, no watermark, no grid lines, consistent scale and perspective, each object fully isolated within exact cell. Actual transparent pixels surrounding objects.

### Forest ground

Use case: stylized-concept. Asset type: a single seamless tileable ground texture for a top-down dark fantasy tower defense game. Square 1024x1024. Pure overhead orthographic surface, dark desaturated blue-green forest earth, patches of fine short moss and soft dirt, very subtle sparse tiny pebbles, muted hand-painted strategy game texture. Low contrast, almost uniform lighting, small scale fine detail. No trees, no bushes, no large rocks, no paths, no roads, no shadows of objects, no horizon, no buildings, no game pieces, no text, no checkerboard, no border. It must be usable as quiet ground beneath an editable stone path and tower sprites, rich tactile quality while remaining visually subdued. Seamless edges.
