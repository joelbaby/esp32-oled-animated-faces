#pragma once
#include <lvgl.h>
class LvglBuiltInFont {
    const lv_font_t* font_;
public:
    explicit LvglBuiltInFont(const lv_font_t* font) : font_(font) {}
    const lv_font_t* font() const { return font_; }
};
