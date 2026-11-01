# Local software validation

## Current source revision: 0.1.0-rc3

User-approved decoration-only changes affect surprised, confused, delicious, angry and embarrassed.
All 884 eye-layer frames and all 680 full frames of the other 16 expressions remain
identical. Two-pixel clearance, zero clipping, codec roundtrips, C++ player checks
and exact regeneration pass. Current assets: 691 unique rasters, 183,400 payload
bytes and 2,768 offset bytes. Runtime/player/adapter code is unchanged.
Rc3 also verifies all 840 non-embarrassed frames against rc2; the four earlier
approved changes remain exact. All 44 embarrassed masks pass clearance checks.

The cold firmware builds and adapter tests described below were performed on the
previous source candidate. They establish the unchanged build/runtime path, but
are not firmware-build or hardware evidence for these revised assets. Rebuild and
verify the receiving firmware after integration. Frozen old binaries are not rc3.
The disposable validation/toolchain directories were subsequently deleted; logs,
provenance, original binaries and matching debug ELF were preserved.

## Previous candidate validation evidence

Prepared 2026-11-02 (Australia/Perth). The standalone build, standard XiaoZhi
build, actual standard display-adapter behavior, player and asset regeneration
checks pass. The final dependency installation started with empty SDK, tool,
Python-package and component caches. No device flash, serial session, commit,
push, remote creation or publication occurred.

## Cold dependency setup and written commands

Tested host: Linux Mint 22.3 x86_64 (Ubuntu 24.04 base), Python 3.12.3. **Installed
OS packages and libraries were reused; this was not a fresh OS or apt test.**
No previous SDK, compiler/tool binaries, virtual environment, downloaded component
source, wheel/download cache or configured vendor tree was copied into this run.

A fresh source directory initially contained only the release's allowlisted files.
The following cache variables pointed to initially empty directories inside it:

| Variable | Task-local value relative to that source root |
|---|---|
| `IDF_TOOLS_PATH` | `.tools/espressif` (set by setup and activation) |
| `XDG_CACHE_HOME` | `.cache` |
| `PIP_CACHE_DIR` | `.cache/pip` |
| `IDF_COMPONENT_CACHE_PATH` | `.cache/idf-components` |

`PIP_CONFIG_FILE=/dev/null` and `GIT_CONFIG_GLOBAL=/dev/null` excluded personal pip
and Git configuration. Component-manager configuration used the new tools root,
which had no pre-existing profile. HOME was not changed. Both CMake configurations
explicitly recorded `CCACHE_ENABLE=False`, and all 891 standalone / 1,912 XiaoZhi
compile commands were checked for absence of a ccache launcher. Compile metadata
references only the new SDK/tools, with no original vendor or older toolchain
paths. The SDK and XiaoZhi Git repositories have no object alternates.

Executed the same setup and build commands documented in the beginner guides:

1. `bash tools/setup_idf.sh`: fresh public fetch of the exact SDK commit and
   recursive submodules, new C3 compiler/debug tools, CMake/Ninja and IDF Python
   environment. SDK worktree stayed clean. Tool versions are in `versions.json`.
2. `export IDF_TOOLS_PATH="$PWD/.tools/espressif"` and
   `source .tools/esp-idf/export.sh`; `idf.py --version` confirmed the pinned SDK.
3. `idf.py -C examples/standalone -DIDF_TARGET=esp32c3 build`: passed from no
   sdkconfig/build directory. App **364,608 bytes**, fits its 1,048,576-byte partition.
4. Exact documented `mkdir`, `git init`, `remote add`, public `fetch --depth 1`,
   detached pinned XiaoZhi checkout and `python3 tools/apply_xiaozhi.py work/xiaozhi`.
5. From that checkout,
   `python3 scripts/build.py oled-faces-c3 --name oled-faces-c3-4mb --language en-US --wake-word hiesp`:
   passed. All 62 registry/SDK dependencies were obtained with the initially empty
   component cache; no managed-component source was copied from another build.
   The shipped dependency lock remained byte-identical. App **2,180,208 bytes**,
   fits its 3,080,192-byte partition. SDK/component sources have no custom patches.
6. `python3 -m venv .venv`, `.venv/bin/python -m pip install -r tools/requirements.txt`
   and `.venv/bin/python tools/test.py`: freshly downloaded Pillow 10.2.0 and all
   player/regeneration checks passed.
7. `python3 tools/test_xiaozhi_adapter.py work/xiaozhi`: passed against the freshly
   downloaded, checksum-verified LVGL package and actual patched production files.

The run downloaded its dependencies from public origins. Within-run reuse between
these two build paths is normal: the second build uses the SDK just installed by
step 1, not an earlier workspace cache. To fit available disk, only newly downloaded
tool archives were removed **after successful extraction**; archive names/hashes
were retained in local evidence. Earlier caches, evidence and user files were kept.
SDK Python packages were resolved through the pinned SDK's official requirements
and constraints; the constraints hash, full installed package versions, submodule
pins, cache provenance and network/build logs are retained in local audit evidence.
The OS package installation command remains a prerequisite, not a fresh-OS claim.

## Actual standard XiaoZhi adapter behavior

The public test runner verifies the pinned XiaoZhi commit, exact patched source
hashes and every file checksum in the pinned LVGL 9.5.0 registry package. It
compiles byte-identical copies of production `oled_display.cc` and `.h` against
**real LVGL**, executing the actual adapter methods and timer callbacks. Host
headers substitute only the ESP-IDF port/mutex interface, font/theme/settings and
base-display services; this does not test the actual IDF scheduler or hardware.
It is not a copied reimplementation of the adapter logic.

Passed under UBSan:

- All 884 rendered frames, all 21 emotion mappings, `smile` alias and null/unknown
  neutral fallback; exact 128×48 raster polarity below y=16 and unchanged status pixels.
- Timer-driven updates, unchanged-ID no-redraw and repeated-cue phase preservation.
- Three-second preview expiry, latest live label restoration, explicit preview
  restart, rejected invalid previews and preview expiry while hidden. Restoring the
  same live expression preserves its current phase, as normal selection does.
- Hide/show, paused timer state and power-save combinations; uint32 clock wrap.
- Teardown waits for an in-flight simulated port task, deletes its timer/canvas
  while locked and releases the lock before port deinitialization.
- Idempotent SetupUI and 200 repeated create/delete cycles without LVGL heap loss.

See [reproducible host-adapter test instructions](DEVELOPMENT.md). These tests do
not establish SSD1306 electrical behavior, real ESP-IDF scheduling, cloud
provisioning, microphone/audio or physical-button operation.

## Player, generation and existing custom consumer

The public player checks independently render the pinned original geometry/layout
and compare every decoded frame. All 884 frames, 21 mappings, fallback/alias,
phase-preserving repeat cues, clock wrap, pause/resume, preview restart,
duplicate-frame suppression, destination replacement/invalidation and malformed
decoder no-partial-write checks pass under UBSan.

Exact generation reproduces the shipped include byte-for-byte: 884 source frames,
699 unique rasters, 179,336 compressed payload bytes, 80 ms duration and zero clipped
frames. README previews come from those actual assets, not a hardware demonstration.

Separately, the existing custom firmware was reconstructed from a saved authoritative
pre-extraction patch and consumed the module by changing only its face-engine
include and CMake dependency. Its original player/decoder/assets remain byte-identical.
Custom full build passed (**2,190,928-byte app**). Actual custom-adapter LVGL checks
passed all frames, polarity/status, duplicate no-refresh, pause/resume and 200
lifecycles. Original firmware source was not changed by this extraction; concurrent
unrelated edits were preserved. Pins, recovery, provisioning, audio/cloud source and
inactive backend remain outside the module. Total firmware sizes above are not
module resource counts; bit-identical whole-firmware builds are not claimed.

## Export audit and remaining physical acceptance

`release-files.txt` is the explicit source allowlist; `SOURCE-MANIFEST.json` records
exported file hashes. No Git history, read-back firmware, NVS, private backup,
configured binary, capture/log, credential, device identifier or local user path
is included. Path/key/MAC/credential marker and image-metadata checks passed;
this is not a proof against every possible secret format. MIT and procedural
artwork provenance are documented in [PROVENANCE.md](PROVENANCE.md); no specific
checked code/artwork redistribution blocker was found.

**Physical acceptance remains pending.** Verify all expressions, status/previews,
text toggle, sleep/wake, BOOT recovery, cloud provisioning/conversation and
microphone/speaker on the actual new integration before claiming a hardware pass.
No other board/controller/host/Arduino support or audio-gap fix is implied.
