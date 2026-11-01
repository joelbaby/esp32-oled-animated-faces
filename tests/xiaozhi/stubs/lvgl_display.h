#pragma once
#include "lvgl_theme.h"
#include "esp_log.h"
#include <string>
class Display {
protected:
    int width_ = 0, height_ = 0;
    bool setup_ui_called_ = false;
    Theme* current_theme_ = nullptr;
    friend class DisplayLockGuard;
    virtual bool Lock(int = 0) = 0;
    virtual void Unlock() = 0;
public:
    virtual ~Display() = default;
    virtual void SetupUI() { setup_ui_called_ = true; }
    virtual void SetChatMessage(const char*, const char*) {}
    virtual void RemoveChatMessage(const char*, const char*) {}
    virtual bool SetEmotion(const char*) { return false; }
    virtual void SetTheme(Theme*) {}
    virtual bool IsMonochrome() const { return false; }
};
class DisplayLockGuard {
    Display* display_;
    bool locked_;
public:
    explicit DisplayLockGuard(Display* display) : display_(display), locked_(display->Lock(30000)) {}
    ~DisplayLockGuard() { if (locked_) display_->Unlock(); }
    explicit operator bool() const { return locked_; }
};
class LvglDisplay : public Display {
protected:
    lv_display_t* display_ = nullptr;
    lv_obj_t *network_label_ = nullptr, *status_label_ = nullptr, *notification_label_ = nullptr;
    lv_obj_t *mute_label_ = nullptr, *battery_label_ = nullptr;
    lv_obj_t *low_battery_popup_ = nullptr, *low_battery_label_ = nullptr;
public:
    virtual void SetPowerSaveMode(bool) {}
    lv_display_t* TestDisplay() { return display_; }
    void TestSetStatus(const char* text) { lv_label_set_text(status_label_, text); }
};
