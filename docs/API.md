# C++ player interface

Include `animated_faces.h`, compile as C++17 or later. This header-only module
uses only C/C++ standard headers and immutable compiled assets. It needs no
ESP-IDF, LVGL or Arduino at runtime. The IDF CMake wrapper exposes `include/`;
consumers may instead add it to their compiler's include path.

```cpp
#include "animated_faces.h"
uint8_t canvas[animated_faces::FrameBytes]; // 768 bytes, supplied by caller
animated_faces::Player player(0);
player.Select("happy", now_ms);
if (player.Draw(now_ms, canvas, sizeof(canvas))) {
    // Submit this changed canvas to your display adapter.
}
player.SetVisible(false, now_ms); // pause phase while hidden
player.SetVisible(true, later_ms); // resume phase
player.Select("surprised", later_ms, true); // restart for a preview
```

Use a monotonic unsigned 32-bit millisecond clock; wrap is handled by unsigned
elapsed arithmetic. `now_ms` and `later_ms` above are your clock values. Calls are
not internally synchronized; use the display lock or a single owning task.

Output is 128×48, row-major, 16 bytes per row, MSB-first; a set bit means illuminated
pixel. Capacity must equal 768. Keep the destination bytes alive and unchanged
between calls. `Draw` returns true after writing a changed frame, false for an
unchanged ID or invalid destination; invalid decode is not expected for compiled,
verified assets. A different destination pointer forces a decode. Call
`Invalidate()` after clearing/reusing a destination at the same address.

`Select` uses the 21 names returned by `ExpressionName(index)`;
`ExpressionName` returns null outside the valid range. `smile` aliases `happy`;
unknown/null uses neutral. Repeating a selection preserves phase unless
`restart=true`. `ExpressionId()`/`FrameId(now)` expose selected indexes for adapters
and tests; never assume an ID equals its expression's frame number.

The lower-level existing `OttoPlayer` and `DecodeOttoFrame` headers are retained
for minimal migration of existing consumers. The decoder validates the complete
compressed input before writing, with exact capacity required. Input and output
must not overlap. Public data/metadata live in `otto_assets`; keep them read-only.

The core stores no frame buffer and allocates no heap. Flash metadata/payload
counts are in README; player-state size varies by target ABI. An LVGL I1 canvas
needs 8 palette bytes before the 768 pixel bytes. SSD1306 hardware uses page order,
so the raw standalone adapter explicitly converts to a separate screen buffer.
