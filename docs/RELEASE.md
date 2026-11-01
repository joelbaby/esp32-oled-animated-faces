# Experimental 0.1.0-rc3 source prerelease

Repository: [joelbaby/esp32-oled-animated-faces](https://github.com/joelbaby/esp32-oled-animated-faces).
Tag: `v0.1.0-rc3`. This is an experimental source-only prerelease; no firmware binaries are distributed.

Suggested description (hardware statement scoped in README):

> 21 Otto-derived animated expressions for 128×64 monochrome OLEDs. Lightweight
> ESP32-C3 source player, SSD1306 demo and pinned XiaoZhi integration; no PSRAM.

Topics: `esp32`, `esp32-c3`, `oled`, `ssd1306`, `128x64`, `animated-eyes`,
`animated-faces`, `emoji`, `robot-face`, `animation`, `esp-idf`, `otto`, `xiaozhi`.
Search phrases in the README are natural descriptions, not measured search volume.

Release description: a small MIT derivative port of Otto's 21 expressions to a
128×48 monochrome animation area below an OLED status bar. Includes compressed
flash assets, allocation-free C++ player, reproducible offline generator, SSD1306
standalone example, pinned standard-XiaoZhi source patch, actual-assets preview
and beginner install/backup/rollback guides. Build/render verification is recorded;
new hardware acceptance remains pending. No audio-quality fix is claimed.

## Layout

```text
include/                 reusable player/decoder/compiled assets
third_party/             original source, licences and provenance
examples/standalone/     minimal IDF SSD1306 display program
examples/xiaozhi/        pinned standard source patch and dependency lock
tools/                   generation, tests, checked install/export helpers
tests/                   public-player verification
docs/                    beginner guides, provenance and validation
```

## Maintainer checklist for subsequent releases

1. Read validation/provenance and confirm remaining hardware limitations are acceptable
   for an explicitly experimental source release; run the physical test before
   claiming this extracted integration is hardware-tested.
2. Choose the final owner, repository name and visibility. Review all allowlisted
   files, MIT notices, contact-sheet labels and release description.
3. Export a fresh source directory with `tools/export_source.py`, check its manifest
   and compare it with the reviewed candidate. Do not copy the containing workspace,
   evidence/build directories or old whole-firmware release.
4. Only after authorization, initialize **fresh Git history in that export** (no
   inherited firmware history), add only the reviewed manifest, create the GitHub
   repository, commit/tag the source and push. No automation here runs these steps.
5. Set description/topics; enable a release/tag and attach the reviewed source
   archive/checksums if desired. Use an experimental label and link hardware limits.
6. Consumers should pin the resulting immutable repository commit or tag. Use the commit behind `v0.1.0-rc3` for this release;
   archive SHA256/`SOURCE-MANIFEST.json` additionally identify source contents.

Do not publish firmware read back from a device, private backups/NVS, credentials,
MAC/device IDs, private endpoints, captures, local absolute paths or configured
binaries. This source candidate contains none of those categories by design and
has an allowlist/marker audit, not a proof against every possible secret format.

This revision improves only five decorative overlays. Eyes and the other 16
expressions are unchanged. New generated assets require a consumer firmware
rebuild; previous frozen firmware binaries are not this source revision.
