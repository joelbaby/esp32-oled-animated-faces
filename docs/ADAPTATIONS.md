# Otto OLED adaptations

Original source pin and file hashes are retained in `third_party/sources.json`.
Upstream generator and MIT notice: `third_party/otto/`.

`tools/generate_assets.py` executes all 21 unmodified original expression,
timing, morph and eye-drawing implementations offline. Each eye layer scales
uniformly by 0.34; anchors reflow to x40/88, y24. Eye aspect ratios are preserved.
For the unchanged 17 expressions, decorative outlines scale uniformly by 0.25; their anchors reflow by
0.40 horizontally and 0.15 vertically to keep hearts, tears, question marks and
sleeping marks within 128×48. This is an explicit wide-layout adaptation, not
squashing the original square and not independently imitated artwork.

Supersampled offline drawing, threshold 96, no runtime grayscale/dither. Very
small details become single pixels at this height. All 884 source frames retain
their original 80 ms duration. This source release has 691 unique rasters and a 183,400-byte payload.
The approved decoration revision below has passed host checks; a new firmware
build and physical acceptance remain pending.

Each frame independently decodes to 768 bytes. Runtime decoder validates lengths
before updating the supplied canvas; no runtime GIF/Python/rasterizer/task or
intermediate frame allocation. Player maps `smile` to `happy`, unknown labels to
neutral, pauses hidden animation phase and preserves phase for repeated cues.
Unchanged frame IDs skip decoding/redraw. Expression previews explicitly restart.

The extracted module does not include Classic RoboEyes. That renderer was removed
from the separate custom firmware before this extraction; no new firmware-removal
or audio-quality claim is made by this release.


## Approved decoration readability revision (0.1.0-rc2)

Only `surprised`, `confused`, `delicious` and `angry` decorations are revised.
The original upstream generator is byte-identical. All 884 eye-only rasters match
pre-revision frame fingerprints; all 724 full frames of the other 17 expressions
are identical to the frozen assets. Names, source-frame counts and 80 ms timing
are unchanged. These are OLED adaptation changes to Otto's original expressions,
not a claim of new original expression/artwork authorship.

- Surprise: three detached whole-pixel rays at each outer edge, away from the lids.
- Confusion: stable question hook and distinct 2×2 dot, with three blank rows between.
- Delicious: recognizable 7×8 droplet between the eyes, retaining the original
  twice-per-loop hang/fall rhythm; detached stable upper-right sparkle.
- Anger: four separate 2-pixel manga-vein corners; integer radii retain the original
  three-throbs-per-loop rhythm without fragmented subpixel strokes.

The original expression envelopes control appearance/disappearance, quantized to
whole glyphs rather than shrinking through isolated pixels. Every revised frame
clears the complete moving-eye envelope by at least two blank pixels; no clipping.
Run `python3 tools/test_decorations.py` with the pinned Pillow 10.2.0 to verify
per-frame eye fingerprints, unchanged expression rasters, clearance, connected
symbols, visibility windows and codec roundtrips. `python3 tools/test.py` verifies
the generated assets through the C++ player/decoder and exact regeneration.

Rc2 metadata (historical): 691 unique rasters, 180,533 compressed payload bytes,
2,768 offset bytes and 1,768 frame-index bytes; worst compressed frame 501 bytes.
Decoded frames remain 768 bytes. These are asset counts, not measured firmware
size. The source export and archive include this revision. Previously frozen
hardware binaries still contain the original decorations and must not be mistaken
for this revision. No firmware build or flashing accompanies this source promotion.

## Approved embarrassed readability revision (0.1.0-rc3)

Rc3 additionally revises **only `embarrassed` decorations** relative to rc2.
Previous rc2 archives and hardware binaries are retained as historical artifacts.

Three separate two-pixel diagonal blush bands now sit beneath each eye, clear of
its entire moving envelope. Their 4/5-pixel heights retain the original four-cycle,
phase-offset blush pulse. A detached 7×9 sweat-drop silhouette at the outer upper
right retains the original once-per-loop slow descent as three whole-pixel steps.
The original expression envelope controls appearance/disappearance. Row-defined
blush bands avoid cross-shaped tips and subpixel specks at this small resolution.

The original upstream generator and all 884 eye layers remain byte-identical.
All 840 full frames of the other 20 expressions match rc2, including the earlier
four approved decoration revisions. The original pre-revision fingerprints remain
in `tests/decoration-baseline.json`; `tests/decoration-rc2-baseline.json` adds the
second comparison point rather than replacing that evidence. The host decoration
check verifies both baselines, distinct blush/sweat components, two-blank-pixel
clearance from the full moving-eye envelopes, no clipping and codec roundtrips.

Current generated metadata: 691 unique rasters, 183,400 payload bytes (+2,867 vs
rc2), 2,768 offset bytes, 1,768 frame-index bytes; worst compressed frame 501 bytes.
All 884 source frames keep their names/counts and 80 ms timing; decoded frames
remain 768 bytes. These are asset figures, not measured firmware size. This approved source revision has host checks and visual previews; it has not
been rebuilt or flashed as firmware.
