#include "oled_display.h"
#include "esp_lvgl_port.h"
#include <array>
#include <cassert>
#include <atomic>
#include <condition_variable>
#include <future>
#include <iostream>
#include <thread>

static uint32_t clock_ms = 0;
static uint32_t Clock() { return clock_ms; }
static void Pump(unsigned elapsed = 0) {
    lvgl_port_lock(1);
    clock_ms += elapsed;
    lv_timer_handler();
    lv_refr_now(nullptr);
    lvgl_port_unlock();
}
static lv_timer_t* Timer(OledDisplay* display) {
    for (auto* t = lv_timer_get_next(nullptr); t; t = lv_timer_get_next(t))
        if (lv_timer_get_user_data(t) == display) return t;
    return nullptr;
}
static lv_obj_t* Canvas(lv_obj_t* parent) {
    for (unsigned i = 0; i < lv_obj_get_child_count(parent); ++i) {
        auto* child = lv_obj_get_child(parent, i);
        if (lv_obj_check_type(child, &lv_canvas_class)) return child;
        if (auto* nested = Canvas(child)) return nested;
    }
    return nullptr;
}
static void FaceNow(OledDisplay* display) {
    lv_timer_ready(Timer(display));
    Pump();
}
static void Expected(const char* expression, unsigned frame) {
    std::array<uint8_t,768> pixels;
    const auto& e = otto_assets::Expressions[OttoPlayer::Find(expression)];
    unsigned id = otto_assets::FrameIds[e.first + frame % e.count];
    auto first = otto_assets::Offsets[id], end = otto_assets::Offsets[id + 1];
    assert(DecodeOttoFrame(otto_assets::Pixels + first, end - first, pixels.data(), pixels.size()));
    for (unsigned y = 0; y < 48; ++y)
        for (unsigned x = 0; x < 128; ++x)
            if (fake_port::panel[(y + 16) * 128 + x] != bool(pixels[y * 16 + x / 8] & (0x80 >> (x % 8)))) {
                std::cerr << "Mismatch: " << expression << " frame " << frame << " at " << x << "," << y << " clock " << clock_ms << "\n";
                assert(false);
            }
}
static OledDisplay* Create() {
    auto* display = new OledDisplay(nullptr, nullptr, 128, 64, false, false);
    display->SetupUI();
    display->TestSetStatus("OK");
    FaceNow(display);
    auto* canvas = Canvas(lv_screen_active());
    assert(canvas && lv_obj_get_x(canvas) == 0 && lv_obj_get_y(canvas) == 16);
    assert(lv_obj_get_width(canvas) == 128 && lv_obj_get_height(canvas) == 48);
    assert(Timer(display));
    return display;
}
static std::vector<uint8_t> Face() {
    return {fake_port::panel.begin() + 16 * 128, fake_port::panel.end()};
}
int main() {
    lv_init();
    lv_tick_set_cb(Clock);
    auto* display = Create();
    auto status = std::vector<uint8_t>(fake_port::panel.begin(), fake_port::panel.begin() + 16 * 128);
    unsigned lit = 0; for (auto bit : status) lit += bit;
    assert(lit > 5);
    unsigned frames = 0;
    for (unsigned i = 0; i < animated_faces::ExpressionCount; ++i) {
        const char* name = animated_faces::ExpressionName(i);
        assert(display->SetEmotion(name));
        FaceNow(display);
        for (unsigned frame = 0; frame < otto_assets::Expressions[i].count; ++frame) {
            if (frame) Pump(80);
            Expected(name, frame);
            assert(std::equal(status.begin(), status.end(), fake_port::panel.begin()));
            unsigned flushes = fake_port::flushes;
            FaceNow(display);
            assert(fake_port::flushes == flushes);
            ++frames;
        }
    }
    assert(frames == 884);
    assert(display->SetEmotion("smile")); FaceNow(display); Expected("happy", 0);
    assert(!display->SetEmotion("unrecognized")); FaceNow(display); Expected("neutral", 0);
    assert(display->SetEmotion("angry"));
    assert(!display->SetEmotion(nullptr)); FaceNow(display); Expected("neutral", 0);
    assert(display->SetEmotion("happy")); Pump(800); Expected("happy", 10);
    unsigned flushes = fake_port::flushes;
    assert(display->SetEmotion("happy")); FaceNow(display); Expected("happy", 10);
    assert(fake_port::flushes == flushes);

    assert(display->PreviewAnimatedExpression("angry")); FaceNow(display); Expected("angry", 0);
    Pump(800); Expected("angry", 10);
    assert(display->SetEmotion("crying")); FaceNow(display); Expected("angry", 10);
    Pump(2199); Expected("angry", 37);
    Pump(1); FaceNow(display); Expected("crying", 0);
    Pump(80); Expected("crying", 1);
    assert(display->PreviewAnimatedExpression("crying")); FaceNow(display); Expected("crying", 0);
    assert(!display->PreviewAnimatedExpression("invalid"));
    assert(!display->PreviewAnimatedExpression(nullptr));
    Pump(3000); Expected("crying", 37); // Same live label preserves its preview phase.

    assert(display->SetEmotion("happy")); FaceNow(display); Pump(800);
    auto phase = Face();
    display->SetAnimatedFacesVisible(false); assert(lv_timer_get_paused(Timer(display))); Pump(8000);
    assert(lv_obj_has_flag(Canvas(lv_screen_active()), LV_OBJ_FLAG_HIDDEN));
    display->SetAnimatedFacesVisible(true); FaceNow(display); assert(Face() == phase);
    display->SetPowerSaveMode(true); assert(lv_timer_get_paused(Timer(display))); Pump(8000);
    display->SetAnimatedFacesVisible(false);
    display->SetPowerSaveMode(false); Pump(8000);
    assert(lv_obj_has_flag(Canvas(lv_screen_active()), LV_OBJ_FLAG_HIDDEN));
    display->SetAnimatedFacesVisible(true); FaceNow(display); assert(Face() == phase);
    display->SetAnimatedFacesVisible(false);
    display->SetPowerSaveMode(true);
    display->SetAnimatedFacesVisible(true); Pump(8000);
    display->SetPowerSaveMode(false); FaceNow(display); assert(Face() == phase);
    Pump(80); assert(Face() != phase);

    assert(display->SetEmotion("sad"));
    assert(display->PreviewAnimatedExpression("angry")); FaceNow(display);
    display->SetAnimatedFacesVisible(false); Pump(4000);
    display->SetAnimatedFacesVisible(true); FaceNow(display); Expected("sad", 0);

    // Timer deletion/canvas destruction must wait for an in-flight port task.
    std::mutex gate; std::condition_variable condition;
    bool held = false, release = false;
    auto* timer = Timer(display);
    std::thread port_task([&]() {
        lvgl_port_lock(1);
        { std::lock_guard<std::mutex> guard(gate); held = true; }
        condition.notify_all();
        { std::unique_lock<std::mutex> guard(gate); condition.wait(guard, [&]() { return release; }); }
        lv_timer_ready(timer); clock_ms += 80; lv_timer_handler();
        lvgl_port_unlock();
    });
    { std::unique_lock<std::mutex> guard(gate); condition.wait(guard, [&]() { return held; }); }
    auto cleanup = std::async(std::launch::async, [display]() { delete display; });
    assert(cleanup.wait_for(std::chrono::milliseconds(20)) == std::future_status::timeout);
    { std::lock_guard<std::mutex> guard(gate); release = true; }
    condition.notify_all(); port_task.join(); cleanup.get();
    assert(fake_port::indefinite_locks == 1 && fake_port::deinits == 1);
    assert(!Timer(display));

    clock_ms = UINT32_MAX - 1000;
    display = Create();
    assert(display->SetEmotion("happy"));
    assert(display->PreviewAnimatedExpression("angry")); FaceNow(display);
    Pump(2999); Expected("angry", 37);
    Pump(1); FaceNow(display); Expected("happy", 0);
    delete display;

    lv_mem_monitor_t before{}, after{}; lv_mem_monitor(&before);
    const unsigned locks = fake_port::indefinite_locks;
    for (unsigned i = 0; i < 200; ++i) {
        display = Create();
        auto* timer_before = Timer(display);
        display->SetupUI(); // idempotent: no duplicate timer/canvas
        assert(Timer(display) == timer_before);
        display->PreviewAnimatedExpression("happy"); Pump(80);
        display->SetAnimatedFacesVisible(false); display->SetPowerSaveMode(true);
        delete display;
        assert(!Timer(display));
    }
    lv_mem_monitor(&after);
    assert(before.free_size == after.free_size);
    assert(fake_port::indefinite_locks == locks + 200);
    std::cout << "PASS: actual standard OledDisplay production source: 884 LVGL frames / 21 mappings, "
                 "fallback+alias, polarity+status, timer duplicate no-redraw, live+preview restore, "
                 "visibility/power-save combinations, clock wrap, locked teardown and 200 lifecycles\n";
}
