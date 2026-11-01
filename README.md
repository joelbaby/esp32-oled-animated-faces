# ESP32 Animated Faces, Eyes & Emoji for 128×64 OLED Displays

21 animated expressions for an ESP32 robot face, adapted for a 128×64 monochrome
SSD1306 OLED. A **derivative port of [Otto Emoji GIF Component](https://github.com/txp666/otto-emoji-gif-component)
by 小鹏 (txp666)**. Otto supplies the expression designs, drawing logic, timing
and original frames. This project adds the OLED layout adaptation, offline
compression, lightweight C++ player and source integration examples.

![21 actual generated OLED expressions](docs/images/expressions.gif)

Use it for ESP32 animated faces, OLED animated eyes, an ESP32 emoji display or robot
facial expressions. Each animation occupies **128×48 pixels below a 16-pixel status
bar**. Eyes retain their proportions; decorative elements are repositioned for the
wide OLED layout. See [attribution and artwork provenance](docs/PROVENANCE.md).

## Why this exists

XiaoZhi.me can send emotion tags during a conversation. This project gives the
21 standard XiaoZhi emotion labels corresponding animated OLED expressions, so
more of the assistant's expression comes through on a small robot face.

To encourage more expressive output, add this instruction to **Role Introduction**
on your XiaoZhi configuration page, alongside your existing role instructions:

```text
## use emote tags
Remember to send system emote tags during your output so that our output is as expressive as possible. Emotions can change at the start, middle or end of a sentence.
```

The firmware reacts to the emotion tags the service sends; this prompt encourages
that behavior but does not guarantee a tag for every sentence. See the
[XiaoZhi guide](docs/XIAOZHI.md#encourage-expressive-emotion-tags) for setup details.

## Space for your status bar

The faces use **only the bottom 48 rows** of a 128×64 display. The top **16 rows
remain available for Wi-Fi, battery and status text**—the animation does not draw
over them. The XiaoZhi adapter places its canvas at `(0, 16)` and preserves the
existing status UI. The standalone demo leaves that area blank for your own UI.

![Animated face below a reserved 16-pixel status area](docs/images/status-bar-layout.gif)

*Layout illustration using the actual happy animation. The status icons/text
are illustrative, not a hardware capture or an exact XiaoZhi screenshot. Blue
and green annotations sit outside the display; the OLED content is monochrome.*

**This is a SOURCE integration requiring a firmware rebuild and flash. It is not
an animation pack that can be uploaded to arbitrary existing XiaoZhi binaries.**

Experimental source prerelease **0.1.0-rc3** includes all five approved decoration improvements, including embarrassed.
See [integration handoff](docs/INTEGRATION-HANDOFF.md) before adopting it into an existing custom firmware.

## Choose one path

- **Already using XiaoZhi, or building the complete C3 chatbot wiring below?** Follow
  [the recommended XiaoZhi source installation](docs/XIAOZHI.md). It builds a pinned,
  otherwise standard XiaoZhi checkout with a small display patch and a separately
  named example board. Existing board pinouts/audio/network code stay unchanged.
- **Want only the OLED animations, without chatbot/audio/network setup?** Follow
  [the standalone display demo](docs/STANDALONE.md). It replaces the running firmware
  with a small display-only program, so back up your current firmware first.

## What has actually been tested?

| Item | Evidence and limits |
|---|---|
| Existing derivative firmware | User observed working Otto on ESP32-C3, single core, 4 MB flash, no PSRAM; SSD1306 128×64 I²C OLED. Not an exhaustive all-expression hardware test. |
| This extracted release | Rc3 passes host frame/decoder/regeneration checks. The unchanged adapter and build path passed rendering checks and cold builds on the preceding candidate; rc3 firmware rebuild and hardware acceptance remain pending. See [validation](docs/VALIDATION.md). |
| XiaoZhi source | `78/xiaozhi-esp32` at `addb1ed59bd71e09a6a5e0c52ad2f1c474aa8ca1` (2.5.3). |
| ESP-IDF | `9a97f6c54ec638111ce55cd36581b3c192f15207` (6.1 development snapshot); exact component versions in the supplied lock. |

Other ESP32 boards, SH1106 controllers, 128×32 displays, Arduino, Windows and macOS
are **not verified by this candidate**. The C++ player is driver-independent, but
that alone does not establish hardware compatibility.

Before starting, you need Git, Python, a C++ compiler, CMake/Ninja and the pinned
ESP-IDF toolchain. The guides include host setup, exact build commands, expected
results, device actions, backup/flash/rollback and common fixes. An SDK/toolchain is
the software that compiles and writes firmware; a source build turns these files
into the program your board runs. Internet access and several GB of free disk are
needed for first-time dependencies.

## Small runtime, generated offline

- 21 expressions; 884 source frames at 80 ms/frame (12.5 frames/s), 691 unique rasters.
- 183,400 bytes compressed frame payload in flash, plus 2,768 bytes offsets,
  1,768 bytes frame IDs, expression records/names and linked code/alignment.
- A decoded frame is 768 bytes. The player writes into your existing canvas with
  no heap allocation or scratch frame. Player state is additional, ABI-dependent.
- No runtime GIF decoder, Python generator or grayscale renderer. Repeated frame
  IDs skip decoding/redraw. Neutral fallback, `smile` → `happy`, pause/resume and
  explicit preview restart are retained.
- Standalone driver additionally uses a 1,024-byte SSD1306 page-order screen buffer;
  XiaoZhi adds an LVGL canvas/palette/timer. These are adapter costs, not core claims.

These are module resource counts, **not total firmware flash/RAM usage**.

## For developers

[Public interface](docs/API.md) · [regenerate/test assets](docs/DEVELOPMENT.md) ·
[troubleshooting and rollback](docs/RECOVERY.md) · [release/publication checklist](docs/RELEASE.md)

MIT; original notices retained in [third_party](third_party/). This is a community
derivative, not an official Otto, XiaoZhi or board-vendor release. Source only;
no device backups, provisioning data or preconfigured firmware binaries are shipped.
