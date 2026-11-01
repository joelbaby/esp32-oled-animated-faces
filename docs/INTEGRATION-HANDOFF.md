# Integrating source candidate 0.1.0-rc3 later

This release is a standalone dependency. It has not been applied to any concurrently
edited consumer firmware. No Wi-Fi, audio, microphone, provisioning, board pins,
button handling, OTA policy or backend changes are required to adopt the faces.

## Identity and scope

Use VERSION and SOURCE-MANIFEST.json from the exported candidate, not an older
copied asset include or an old compiled firmware binary. The generated asset hash is
`8c1c715efe1b3f975429a24de74f703d91ddd5aa8b64685bbd8750d4295f1678`.
Original Otto provenance and MIT notices remain required.

Only decorations in surprised/confused/delicious/angry/embarrassed changed: clearer detached
surprise rays, a question-mark dot, droplet, anger symbol, and blush/sweat marks. Eye animation is
identical for all 884 frames; the other 16 expressions (680 frames) are byte-identical.
Names, timing, canvas layout, decoder format and player interface are unchanged.
Payload is 183,400 bytes (+4,064 vs original; +2,867 vs rc2); offsets are 2,768 bytes (-32). Whole-firmware
size and partition fit must be measured in the receiving build.

Compared with rc2, only embarrassed changes: all 840 frames of the other 20
expressions remain identical, including the earlier four approved fixes.

## Existing custom PocketDisplay consumer

1. Finish/save the other firmware work first. Use its current authoritative patch,
   configuration and source as the integration baseline; never restore an older
   firmware snapshot merely to add this component.
2. Add this candidate as a pinned dependency. Before publication, use the reviewed
   archive checksum/manifest; after publication, pin its actual immutable commit.
   An ESP-IDF local component can contain this release's CMakeLists.txt,
   idf_component.yml, include/ and third_party/ under components/animated_faces/.
3. Where the existing face engine includes local `otto_player.h` and
   `otto_decoder.h`, use `animated_faces.h` from this component instead. The existing
   OttoPlayer/DecodeOttoFrame interfaces remain available, so keep the custom
   PocketDisplay rendering, screen controls and animation scheduling unchanged.
   Add `animated_faces` to the consuming IDF component's dependencies.
4. Check which asset include the compiler actually consumes. Do not leave an old
   board-local include silently selected by include-path order. Remove obsolete
   copies only after confirming no other consumer depends on them.
5. Capture dependency acquisition/pin and any include/CMake changes using the
   consumer repository's authoritative reconstruction mechanism. An edit in an
   ignored vendor directory alone is not a reproducible integration.
6. Run the public player/decorations tests, consumer rendering tests, full firmware
   build, size/partition checks and patch reconstruction. Compare the final diff
   against the new consumer baseline to ensure unrelated settings stayed unchanged.
7. Freeze fresh binaries/ELF/checksums for review before any hardware write.

Do not apply examples/xiaozhi/animated-faces.patch to an already customized firmware
as a shortcut: that example is for a clean pinned standard XiaoZhi checkout and
includes a separate example board. Its stock audio/network/OTA defaults are not
part of the reusable player and should not replace a custom consumer's choices.

## Already using the extracted component

Update the complete pinned component coherently, retaining notices and source
metadata, then rebuild. No new player API or canvas adaptation is required. Do not
patch compressed payload bytes by hand or replace assets inside an existing binary.

## Validation status

Host player/codec/regeneration and exhaustive decoration-preservation checks pass.
The preceding candidate passed cold builds and standard-adapter behavior tests.
Those firmware binaries contain the old decorations. This revision needs a fresh
consumer build and, separately authorized, hardware acceptance. No flash is implied
by adopting or reviewing this source package.
