# Provenance, artwork and modifications

This is a derivative monochrome OLED port of **Otto Emoji GIF Component by 小鹏
(txp666)**, not newly created expression artwork. Original expression designs,
animation drawing/timing/morph logic and frame content come from Otto.

- [Pinned source tree](https://github.com/txp666/otto-emoji-gif-component/tree/4a666924e8e4e2bb55fb9d3167211bb936224abf)
- [Pinned generator](https://github.com/txp666/otto-emoji-gif-component/blob/4a666924e8e4e2bb55fb9d3167211bb936224abf/tools/generate_emojis.py)
- [Pinned README, generation and licensing statements](https://github.com/txp666/otto-emoji-gif-component/blob/4a666924e8e4e2bb55fb9d3167211bb936224abf/README.md)
- [Pinned MIT notice](https://github.com/txp666/otto-emoji-gif-component/blob/4a666924e8e4e2bb55fb9d3167211bb936224abf/LICENSE)

Original files, notices and source hashes are retained under `third_party/otto/`
and `third_party/sources.json`. Independently fetched pinned generator and licence
matched the recorded hashes:

| File | SHA256 |
|---|---|
| tools/generate_emojis.py | `40dd14781fda254184b7f7d139b2abc803bf9efb09f7555ee0f6b174a0ddad58` |
| LICENSE | `bd806361232a065ead834a53a04b34ba51eacb257ccdb21a6506f0e8738930d8` |
| README.md | `731a025d93b84aa91f0afd155ab74845aa990f982936521baf4a24bbadae8283` |

## Artwork redistribution evidence

The pinned README says all 21 expressions come from its Python generator, without
hand-drawn source assets, and declares MIT. Inspection of that exact generator
found procedural geometric drawing with Python standard library and Pillow
Image/ImageDraw/ImageChops; no external raster, GIF, font or downloaded asset is
loaded into expression frames. This release regenerates those frames from the
original code; it does **not** redistribute unidentified third-party GIF inputs.
The contact sheet/GIF previews are derived from these same generated rasters.
This evidence supports distributing this procedural derivative under the retained
MIT terms; it is more specific than assuming any repository licence clears every
possible asset. It is not an independent guarantee of ultimate ownership.

## This project's modifications

- Offline OLED adaptation: uniformly scaled eyes (0.34), anchors reflowed to x40/88,
  y24; most decorations locally scale 0.25 with anchors reflowed to the 128×48 area.
  Five expressions use the documented pixel-grid readability adaptations in ADAPTATIONS.md.
- Thresholded 1-bit rasters, deduplication and independent byte-PackBits compression.
- Lightweight validated decoder, timer/mapping player and caller-owned canvas interface.
- Standalone IDF SSD1306 page adapter and separate XiaoZhi source/display integration.
- Reproducible tooling, tests, generated previews and beginner documentation.

These modifications are MIT, retaining original copyright **2025 小鹏** and the
MIT notice. The top-level notice adds 2026 project contributors for modifications;
no expression/artwork authorship is claimed by that added line.

The XiaoZhi example patch and board adaptation derive from
[78/xiaozhi-esp32](https://github.com/78/xiaozhi-esp32/tree/addb1ed59bd71e09a6a5e0c52ad2f1c474aa8ca1).
Its exact MIT notice is retained in `third_party/xiaozhi/LICENSE`. ESP-IDF and
managed components are downloaded build dependencies, not bundled runtime source
in this source export; their own licences/notices continue to apply to downstream
firmware distribution. This candidate ships no firmware binaries or speech models.

No specific code/artwork redistribution blocker was found in this checked chain.
Before publishing binaries or changing assets/dependencies, review their additional
notices separately; a source release does not relicense downloaded dependencies.
