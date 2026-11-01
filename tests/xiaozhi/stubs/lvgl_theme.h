#pragma once
#include "lvgl_font.h"
#include <memory>
#include <map>
#include <string>
class Theme { public: virtual ~Theme() = default; };
class LvglTheme : public Theme {
    std::shared_ptr<LvglBuiltInFont> text_, icon_, large_, emoji_;
public:
    explicit LvglTheme(const char*) {}
    void set_text_font(std::shared_ptr<LvglBuiltInFont> font) { text_ = font; }
    void set_icon_font(std::shared_ptr<LvglBuiltInFont> font) { icon_ = font; }
    void set_large_icon_font(std::shared_ptr<LvglBuiltInFont> font) { large_ = font; }
    void set_emoji_font(std::shared_ptr<LvglBuiltInFont> font) { emoji_ = font; }
    auto text_font() { return text_; }
    auto icon_font() { return icon_; }
    auto large_icon_font() { return large_; }
    auto emoji_font() { return emoji_; }
};
class LvglThemeManager {
    std::map<std::string, std::unique_ptr<Theme>> themes_;
public:
    static LvglThemeManager& GetInstance() { static LvglThemeManager manager; return manager; }
    void RegisterTheme(const char* name, Theme* theme) { themes_[name].reset(theme); }
};
