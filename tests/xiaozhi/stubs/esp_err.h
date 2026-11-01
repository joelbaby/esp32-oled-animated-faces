#pragma once
#include <cassert>
using esp_err_t = int;
#define ESP_OK 0
#define ESP_ERR_TIMEOUT 1
#define ESP_ERROR_CHECK(result) do { assert((result) == ESP_OK); } while (0)
