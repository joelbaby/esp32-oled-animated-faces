# Generate and verify assets offline

From the source root on the tested host:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/requirements.txt
.venv/bin/python tools/test.py
.venv/bin/python tools/generate_assets.py
```

The generator executes the **unmodified pinned Otto generator** under
`third_party/otto/generate_emojis.py`. Its SHA256 is checked before import. Pillow
10.2.0 is pinned; Python 3.12.3 was used. Generation needs no network, credentials,
font files or source GIFs after dependencies are installed. Preview labels use
Pillow's packaged default font; those labels are not part of firmware frames.

Generated output is under ignored `build/generated/`: `otto_assets.inc`, payload,
`generation.json`, 21 PNG/GIF previews and a contact sheet. `--check` rerenders all
884 frames, checks no lit pixels exceed 128×48, verifies PackBits roundtrips and
compares the exact include against the shipped asset. It does not modify shipped
assets. The historical generator path comment inside the include is retained so
existing consumer bytes/hashes remain unchanged; the current command is above.

```bash
.venv/bin/python tools/generate_assets.py --check
```

`tools/test.py` renders independent reference rasters from the pinned original
geometry/layout, compiles `tests/player_test.cc` with the host C++ compiler and
UBSan, compares the public player output for all 884 frames, checks all mappings,
neutral/alias, repeated cues, wrap, pause/resume, preview restart, duplicate-frame
suppression, destination replacement/invalidation and malformed decoder no-write.
It then runs the exact regeneration check. Tests cross the public interface.

To intentionally update generated pixels, inspect previews and generation metadata,
review provenance/pins, copy `build/generated/otto_assets.inc` to
`include/third_party/otto/otto_assets.inc`, and rerun tests/builds. Never accept a
pixel change only because the generator ran. Do not claim hardware acceptance from
these host checks. See [adaptations](ADAPTATIONS.md) for geometry/layout details.

For a local source-only export, `python3 tools/export_source.py DEST` copies only
`release-files.txt`; it rejects missing/unexpected files and checks privacy markers.
No Git history or firmware binaries are included. Run the exporter from the final
candidate, audit the manifest and archive checksums before publication.

## Execute the standard XiaoZhi adapter on the host

After completing the pinned XiaoZhi source installation/build, return to the faces
source root (the directory containing `tools/`). With the pinned IDF environment
active so its CMake is on PATH, run:

```bash
python3 tools/test_xiaozhi_adapter.py work/xiaozhi
```

This checks the pinned XiaoZhi commit, both patched production files and every file
of the pinned LVGL registry package. It copies `oled_display.cc` and `.h`
byte-for-byte into the ignored test build directory, then compiles **that actual
adapter implementation** against real LVGL 9.5.0. The copy allows small host headers
to replace ESP-IDF port/base services without changing production source.
It does not reimplement the adapter being tested.

The harness supplies a controlled millisecond clock, host mutex/port scheduler,
fonts and base theme/settings services. It executes the real timer callbacks and
LVGL rendering: all 884 frames and 21 mappings, alias/fallback, 128×48 polarity and
unchanged status region, unchanged-frame no-redraw, repeated cues, preview expiry
and latest-live restoration, hidden preview expiry, hide/show and power-save
combinations, uint32 wrap, concurrent locked teardown and 200 create/delete cycles
without LVGL heap loss. It also checks SetupUI is idempotent. UBSan is enabled.

Expected: `PASS: actual standard OledDisplay production source...`. The test needs
no connected device. Host port/font/service substitutes mean this is software
adapter verification, not a test of ESP-IDF scheduling, SSD1306 electrical behavior,
cloud provisioning, microphone/audio or physical buttons.

Decoration-regression checks (pinned Pillow environment):

```bash
.venv/bin/python tools/test_decorations.py
```

This compares every eye frame and unchanged expression against retained pre-revision
fingerprints, then checks glyph separation, clipping and codec roundtrips.
