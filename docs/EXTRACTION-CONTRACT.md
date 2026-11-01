# Extraction contract

Keep the existing Otto assets, decoder and animation timing byte-for-byte.
Expose a small header-only C++17 player writing into a caller-owned 768-byte
128×48 MSB-first raster. No runtime allocation, GIF, LVGL or device dependency.
Keep the display drivers and XiaoZhi adapter in examples. Unknown labels map to
neutral; smile maps to happy; repeat cues preserve phase; visibility pauses phase;
preview restarts explicitly; repeated frame IDs skip decode/redraw.

Deliver pinned ESP-IDF standalone and otherwise standard XiaoZhi source builds,
actual-asset preview, reproducible generation, documented rollback and allowlisted
source export. No audio/network tuning, private data, flash, commits or publishing.
Verify custom consumption in an isolated reconstruction without changing the dirty
original firmware tree or authoritative patch.
