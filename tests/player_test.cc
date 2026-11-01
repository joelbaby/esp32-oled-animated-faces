#include "animated_faces.h"
#include <array>
#include <cassert>
#include <fstream>
#include <iostream>
#include <vector>

int main(int argc, char** argv) {
    assert(argc == 2);
    std::ifstream reference(argv[1], std::ios::binary);
    assert(reference);
    animated_faces::Player player;
    std::array<uint8_t, 770> guarded;
    std::array<uint8_t, 768> expected;
    unsigned frames = 0;
    uint32_t now = 0;
    for (unsigned expression = 0; expression < animated_faces::ExpressionCount; ++expression) {
        player.Select(animated_faces::ExpressionName(expression), now, true);
        assert(player.ExpressionId() == expression);
        const unsigned count = otto_assets::Expressions[expression].count;
        for (unsigned frame = 0; frame < count; ++frame) {
            reference.read(reinterpret_cast<char*>(expected.data()), expected.size());
            assert(reference.gcount() == expected.size());
            guarded.front() = 0x65; guarded.back() = 0x76;
            player.Draw(now, guarded.data() + 1, expected.size());
            assert(!std::memcmp(guarded.data() + 1, expected.data(), expected.size()));
            assert(guarded.front() == 0x65 && guarded.back() == 0x76);
            assert(!player.Draw(now, guarded.data() + 1, expected.size()));
            now += 80;
            ++frames;
        }
    }
    assert(frames == 884);
    assert(animated_faces::ExpressionName(21) == nullptr);
    assert(OttoPlayer::Find(nullptr) == 0 && OttoPlayer::Find("unknown") == 0);
    assert(OttoPlayer::Find("smile") == OttoPlayer::Find("happy"));
    player.Select("happy", now, true);
    now += 800;
    auto phase = player.FrameId(now);
    assert(!player.Select("happy", now));
    assert(player.FrameId(now) == phase);
    player.SetVisible(false, now);
    now += 8000;
    assert(player.FrameId(now) == phase);
    player.SetVisible(true, now);
    assert(player.FrameId(now) == phase);
    player.Select("angry", now, true);
    assert(player.FrameId(now) == otto_assets::FrameIds[otto_assets::Expressions[OttoPlayer::Find("angry")].first]);
    OttoPlayer wrap(UINT32_MAX - 39);
    assert(wrap.FrameNumber(40) == 1);
    // A new destination gets the current frame even when its ID is unchanged.
    std::array<uint8_t,768> other{};
    assert(player.Draw(now, other.data(), other.size()));
    assert(!player.Draw(now, other.data(), other.size()));
    other.fill(0); player.Invalidate(); assert(player.Draw(now, other.data(), other.size()));
    assert(!player.Draw(now, nullptr, 768));
    assert(!player.Draw(now, other.data(), 767));
    // Truncated literals/runs, overrun, underfill: reject before any output write.
    const std::vector<std::vector<uint8_t>> bad = {{0},{0x80},{0x81,42},{1,42},{0,42}};
    for (const auto& source : bad) {
        std::array<uint8_t,3> output = {17,18,19};
        auto before = output;
        assert(!DecodeOttoFrame(source.data(), source.size(), output.data(), output.size()));
        assert(output == before);
    }
    std::cout << "PASS: 884 frames equal independent original-generator rasters; 21 mappings; "
              << "fallback, alias, timing, wrap, pause/resume, preview restart, duplicate skip, "
              << "destination invalidation and malformed decoder atomicity\n";
    std::cout << "Player state bytes (host ABI): " << sizeof(player) << "; frame bytes: 768\n";
}
