#pragma once
#include "otto_player.h"
#include "otto_decoder.h"

// Caller owns exactly 768 bytes: 128x48 row-major, MSB first, 1 = lit pixel.
// No heap, driver, task, LVGL, Arduino or runtime GIF dependency.
namespace animated_faces {
inline constexpr unsigned Width = 128, Height = 48, FrameBytes = 768;
inline constexpr unsigned FrameDurationMs = 80;
inline constexpr unsigned ExpressionCount = otto_assets::ExpressionCount;
inline const char* ExpressionName(unsigned index) {
    return index < ExpressionCount ? otto_assets::Expressions[index].name : nullptr;
}
class Player {
public:
    explicit Player(uint32_t now = 0) : timing_(now) {}
    bool Select(const char* emotion, uint32_t now, bool restart = false) {
        return timing_.Select(emotion, now, restart);
    }
    void SetVisible(bool visible, uint32_t now) { timing_.SetVisible(visible, now); }
    unsigned ExpressionId() const { return timing_.ExpressionId(); }
    unsigned FrameId(uint32_t now) const { return timing_.FrameId(now); }
    // True means changed frame written; false means unchanged or bad destination.
    // Keep destination bytes alive and unchanged between calls. Invalidate after
    // replacing/clearing a destination, even if its pointer is unchanged.
    bool Draw(uint32_t now, uint8_t* destination, size_t capacity) {
        if (!destination || capacity != FrameBytes) return false;
        const unsigned frame = timing_.FrameId(now);
        if (frame == last_frame_ && destination == last_destination_) return false;
        const auto begin = otto_assets::Offsets[frame];
        const auto end = otto_assets::Offsets[frame + 1];
        if (end <= begin || end > sizeof(otto_assets::Pixels) ||
            !DecodeOttoFrame(otto_assets::Pixels + begin, end - begin,
                             destination, capacity)) return false;
        last_frame_ = frame;
        last_destination_ = destination;
        return true;
    }
    void Invalidate() { last_frame_ = UINT32_MAX; }
private:
    OttoPlayer timing_;
    unsigned last_frame_ = UINT32_MAX;
    const uint8_t* last_destination_ = nullptr;
};
}  // namespace animated_faces
