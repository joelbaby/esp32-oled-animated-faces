#pragma once
#include "esp_err.h"
using esp_lcd_panel_handle_t = void*;
inline int esp_lcd_panel_del(void*) { return 0; }
inline int esp_lcd_panel_disp_on_off(void*, bool) { return 0; }
