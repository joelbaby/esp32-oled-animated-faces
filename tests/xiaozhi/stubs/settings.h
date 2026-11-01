#pragma once
class Settings {
public:
    Settings(const char*, bool) {}
    bool GetBool(const char*, bool) { return true; }
};
