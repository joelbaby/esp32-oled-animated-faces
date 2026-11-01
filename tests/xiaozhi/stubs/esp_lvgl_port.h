#pragma once
#include <lvgl.h>
#include <cstdint>
#include <cassert>
#include <atomic>
#include <mutex>
#include <vector>
struct lvgl_port_cfg_t { int task_priority = 0, task_stack = 0, task_affinity = 0; };
#define ESP_LVGL_PORT_INIT_CONFIG() lvgl_port_cfg_t{}
struct lvgl_port_display_cfg_t {
    void* io_handle; void* panel_handle; void* control_handle;
    uint32_t buffer_size; bool double_buffer; uint32_t trans_size;
    uint32_t hres, vres; bool monochrome;
    struct { bool swap_xy, mirror_x, mirror_y; } rotation;
    struct { unsigned buff_dma, buff_spiram, sw_rotate, full_refresh, direct_mode; } flags;
};
namespace fake_port {
inline std::recursive_mutex mutex;
inline thread_local unsigned depth = 0;
inline lv_display_t* display = nullptr;
inline std::vector<uint16_t> buffer;
inline std::vector<uint8_t> panel;
inline unsigned flushes = 0, indefinite_locks = 0, deinits = 0;
inline void Flush(lv_display_t* disp, const lv_area_t* area, uint8_t* pixels) {
    ++flushes;
    auto* color = reinterpret_cast<lv_color16_t*>(pixels);
    for (int y = area->y1; y <= area->y2; ++y)
        for (int x = area->x1; x <= area->x2; ++x)
            panel[y * 128 + x] = color[(y-area->y1)*(area->x2-area->x1+1)+x-area->x1].blue > 16 ? 0 : 1;
    lv_display_flush_ready(disp);
}
}
inline void lvgl_port_init(const lvgl_port_cfg_t*) {}
inline bool lvgl_port_lock(uint32_t timeout) {
    fake_port::mutex.lock(); ++fake_port::depth;
    if (!timeout) ++fake_port::indefinite_locks;
    return true;
}
inline void lvgl_port_unlock() { assert(fake_port::depth); --fake_port::depth; fake_port::mutex.unlock(); }
inline lv_display_t* lvgl_port_add_disp(const lvgl_port_display_cfg_t* cfg) {
    fake_port::display = lv_display_create(cfg->hres, cfg->vres);
    fake_port::buffer.assign(cfg->hres * cfg->vres, 0);
    fake_port::panel.assign(cfg->hres * cfg->vres, 0);
    lv_display_set_color_format(fake_port::display, LV_COLOR_FORMAT_RGB565);
    lv_display_set_buffers(fake_port::display, fake_port::buffer.data(), nullptr,
        fake_port::buffer.size() * 2, LV_DISPLAY_RENDER_MODE_FULL);
    lv_display_set_flush_cb(fake_port::display, fake_port::Flush);
    return fake_port::display;
}
inline void lvgl_port_deinit() {
    assert(fake_port::depth == 0); // Must unlock before stopping the port task.
    lv_display_delete(fake_port::display); fake_port::display = nullptr; ++fake_port::deinits;
}
