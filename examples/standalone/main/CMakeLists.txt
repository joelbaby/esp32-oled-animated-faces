idf_component_register(SRCS "main.cc" INCLUDE_DIRS "."
    REQUIRES esp_lcd esp_driver_i2c esp_timer)
# The source checkout directory can have any name.
target_include_directories(${COMPONENT_LIB} PRIVATE "${CMAKE_CURRENT_LIST_DIR}/../../../include")
