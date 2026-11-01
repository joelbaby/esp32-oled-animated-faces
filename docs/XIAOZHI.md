# XiaoZhi source integration — recommended C3 example

This guide builds [standard XiaoZhi](https://github.com/78/xiaozhi-esp32) 2.5.3 at
`addb1ed59bd71e09a6a5e0c52ad2f1c474aa8ca1` with the OLED faces patch. You do not
need the separate custom firmware repository. **It is source integration: rebuild
and flash firmware. It cannot upload expressions to an existing arbitrary binary.**

The recommended example is **only** ESP32-C3 / 4 MB / no PSRAM with this wiring:

| Connection | GPIO |
|---|---:|
| SSD1306 SDA / SCL (128×64, address 0x3c) | 20 / 10 |
| Shared I²S BCLK / WS | 2 / 1 |
| MAX98357 amplifier DIN | 3 |
| INMP441 microphone SD | 8 |
| BOOT/action | 9 |

The existing custom firmware with this wiring has user-observed working Otto.
This new, otherwise standard integration is **build/render verified only**; its
cloud/audio/button operation requires a separately authorized physical test.
Pins are not universal. Power off before wiring and follow each device's power
requirements. Use 3.3 V-compatible signals and common ground.

## 1. Prepare the host

Complete [host setup](HOST-SETUP.md). Keep the activated ESP-IDF terminal open in
the faces source root. The example uses upstream NoAudioCodecDuplex at a shared
24 kHz clock; no custom mic filters, queue sizes or Wi-Fi buffer tuning are added.

## 2. Get the exact clean XiaoZhi source and install

**Terminal — from the faces source root:**

```bash
mkdir -p work/xiaozhi
git -C work/xiaozhi init
git -C work/xiaozhi remote add origin https://github.com/78/xiaozhi-esp32.git
git -C work/xiaozhi fetch --depth 1 origin addb1ed59bd71e09a6a5e0c52ad2f1c474aa8ca1
git -C work/xiaozhi checkout --detach FETCH_HEAD
python3 tools/apply_xiaozhi.py work/xiaozhi
```

Expected: `Installed pinned faces module/display patch`. The installer checks the
commit and exact before hashes of files it touches, refuses existing installations
or conflicting edits, copies the reusable module to `components/animated_faces`,
and installs the version-pinned dependency lock. Start from a fresh directory if
you need to repeat this installation; do not reset an existing modified checkout.

## 3. Build the selected example

**Terminal — from the faces source root:**

```bash
cd work/xiaozhi
python3 scripts/build.py oled-faces-c3 --name oled-faces-c3-4mb --language en-US --wake-word hiesp
```

The canonical upstream build command selects the unique **oled-faces-c3** board,
its 4 MB partition layout, English and the built-in Hi ESP wake word. Internet
access is needed to obtain/verify components and models. No flash occurs here.
Expected: a successful build and `build/xiaozhi.bin` plus `build/merged-binary.bin`.
Check the printed board/target matches `oled-faces-c3-4mb` / `esp32c3` before writing.
A build is not proof that hardware/cloud/audio works. See [validation](VALIDATION.md).

## 4. Back up, then choose to install

**Device actions:** connect the matching board with a USB data cable. Do not
substitute this new board identity for another board's firmware.
Follow [backup/restore](RECOVERY.md) before any write. **Terminal — still in
`work/xiaozhi`, only after backup and when intentionally installing:**

```bash
idf.py -p PORT flash monitor
```

Replace `PORT` with your actual serial port. Full `flash` writes the selected
bootloader, partition table, application and generated assets/initial metadata.
A partition-layout change or initial OTA metadata can make old provisioning
unusable; some stored data can be overwritten. This is not presented as a
provisioning-preserving app-only update. Do not run `erase-flash`.

**Device actions:** reset if needed, follow standard XiaoZhi Wi-Fi setup and cloud
activation, then test BOOT/action, microphone, speaker and conversation. Standard
upstream provisioning and OTA policy remain in this example. Future stock OTA
updates may replace this source modification; rebuild/reapply when upgrading.
No personal activation code, endpoint or Wi-Fi credential belongs in a public log.
Exit serial monitor with Ctrl+].

## 5. Verify the faces

Look for the normal status bar in rows 0–15 and animated eyes in rows 16–63.
Cloud emotion labels select the matching Otto expression; `smile` aliases `happy`,
unknown or missing labels use `neutral`. Repeating the same cue does not restart
its animation. The 80 ms LVGL timer runs on the existing display task, not the
audio task. Duplicate frame IDs skip decode and invalidate.

This patch overlays the lower subtitle/emotion content with a full-width face.
The top status/notification UI and low-battery popup remain. Application code can
call `SetAnimatedFacesVisible(false)` on OledDisplay to restore normal lower text,
and `true` to resume faces. Hiding or power-save pauses the animation phase.

The C3 example adds one MCP tool, `self.display.preview_expression`, with a string
`expression`. Ask the assistant to invoke it with `happy` (or another name below),
or invoke it through your XiaoZhi tool client. It previews for three seconds then
restores the most recent live cloud emotion. If a cloud service does not expose
that tool, test through application code calling `PreviewAnimatedExpression()`;
tool invocation itself is part of pending physical/cloud acceptance.

Supported names: `neutral`, `happy`, `laughing`, `funny`, `sad`, `angry`, `crying`,
`loving`, `embarrassed`, `surprised`, `shocked`, `thinking`, `winking`, `cool`,
`relaxed`, `delicious`, `kissy`, `confident`, `sleepy`, `silly`, `confused`.

Check all expressions, status visibility, preview restoration, text/face toggle,
sleep/wake, normal conversation, provisioning and BOOT recovery before accepting
a physical installation. The standalone demo cycles all expressions automatically.
Audio gaps/stalls from the separate firmware are not solved by this module.

## Existing upstream board (separate adaptation)

Use a **new clean checkout** and the same installer, then keep your existing board
and variant in upstream `scripts/build.py`; do not choose the C3 example above.
The display patch activates faces only in OledDisplay's 128×64 layout and keeps
existing board pins, audio and network code. It does not convert TFT/128×32/SH1106
boards into supported hardware. Other variants are not built/verified here.
The supplied dependency lock targets C3; other targets need their own resolved
and reviewed lock. The preview API is available, but the example-only MCP tool
must be added by that board's maintainer if wanted.

## Uninstall

Use a fresh source checkout of your previous pinned firmware and rebuild it, or
restore the private full-flash backup as described in [recovery](RECOVERY.md).
Do not remove files from your only working source checkout to roll back.
