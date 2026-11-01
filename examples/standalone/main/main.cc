#include "animated_faces.h"
#include "sdkconfig.h"
#include <driver/i2c_master.h>
#include <esp_lcd_panel_io.h>
#include <esp_lcd_panel_ops.h>
#include <esp_lcd_panel_vendor.h>
#include <esp_log.h>
#include <esp_timer.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <cstring>

extern "C" void app_main() {
    i2c_master_bus_config_t bus_config = {};
    bus_config.i2c_port = I2C_NUM_0;
    bus_config.sda_io_num = static_cast<gpio_num_t>(CONFIG_FACES_SDA);
    bus_config.scl_io_num = static_cast<gpio_num_t>(CONFIG_FACES_SCL);
    bus_config.clk_source = I2C_CLK_SRC_DEFAULT;
    bus_config.glitch_ignore_cnt = 7;
    bus_config.flags.enable_internal_pullup = true;
    i2c_master_bus_handle_t bus = nullptr;
    ESP_ERROR_CHECK(i2c_new_master_bus(&bus_config, &bus));
    esp_lcd_panel_io_i2c_config_t io_config = {};
    io_config.dev_addr = CONFIG_FACES_I2C_ADDRESS;
    io_config.scl_speed_hz = 400000;
    io_config.control_phase_bytes = 1;
    io_config.dc_bit_offset = 6;
    io_config.lcd_cmd_bits = 8;
    io_config.lcd_param_bits = 8;
    esp_lcd_panel_io_handle_t io = nullptr;
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_i2c(bus, &io_config, &io));
    esp_lcd_panel_ssd1306_config_t ssd_config = {};
    ssd_config.height = 64;
    esp_lcd_panel_dev_config_t panel_config = {};
    panel_config.reset_gpio_num = GPIO_NUM_NC;
    panel_config.bits_per_pixel = 1;
    panel_config.vendor_config = &ssd_config;
    esp_lcd_panel_handle_t panel = nullptr;
    ESP_ERROR_CHECK(esp_lcd_new_panel_ssd1306(io, &panel_config, &panel));
    ESP_ERROR_CHECK(esp_lcd_panel_reset(panel));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel));
    ESP_ERROR_CHECK(esp_lcd_panel_invert_color(panel, false));
    ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(panel, true));
    static uint8_t raster[animated_faces::FrameBytes];
    // This driver adapter needs a separate SSD1306 page-order screen buffer.
    // The first two pages (16 rows) stay blank; XiaoZhi supplies status there.
    static uint8_t pages[128 * 64 / 8] = {};
    animated_faces::Player player;
    unsigned expression = 0;
    uint32_t changed_at = 0;
    ESP_LOGI("faces", "21 expressions; changing every 4 seconds");
    while (true) {
        uint32_t now = static_cast<uint32_t>(esp_timer_get_time() / 1000);
        if (now - changed_at >= 4000) {
            changed_at = now;
            expression = (expression + 1) % animated_faces::ExpressionCount;
            player.Select(animated_faces::ExpressionName(expression), now, true);
            ESP_LOGI("faces", "%s", animated_faces::ExpressionName(expression));
        }
        if (player.Draw(now, raster, sizeof(raster))) {
            std::memset(pages, 0, sizeof(pages));
            for (unsigned y = 0; y < 48; ++y)
                for (unsigned x = 0; x < 128; ++x)
                    if (raster[y * 16 + x / 8] & (0x80 >> (x % 8)))
                        pages[((y + 16) / 8) * 128 + x] |= 1 << ((y + 16) % 8);
            ESP_ERROR_CHECK(esp_lcd_panel_draw_bitmap(panel, 0, 0, 128, 64, pages));
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
