# Standalone OLED demo

Use this path to show the 21 expressions without XiaoZhi, Wi-Fi or audio.
Requires ESP32-C3, 4 MB flash and SSD1306 128×64 I²C OLED. New extraction build
verified on the host; hardware flashing/acceptance of this example is pending.

**Device actions:** power off before wiring. Connect OLED ground to board ground,
OLED 3.3 V power as specified by your module, SDA GPIO20 and SCL GPIO10 for this
example wiring. Use address 0x3c. Do not use these GPIOs blindly on another board.
The top 16 pixels remain blank in this demo; there is no chatbot status UI.

1. Complete [host setup](HOST-SETUP.md); keep that terminal open in the source root.
2. **Terminal — build:**

   ```bash
   idf.py -C examples/standalone -DIDF_TARGET=esp32c3 build
   ```

   Expected: `Project build complete`, `animated_faces_demo.bin`, within its app
   partition. No device is needed for the build. Shipped compressed assets are
   compiled directly; generation is optional.
3. Before any write, follow [backup and rollback](RECOVERY.md). This display-only
   program replaces your chatbot and uses a different partition layout; do not
   apply it as an app-only update to an arbitrary existing XiaoZhi installation.
4. **Terminal — only when you have chosen to install on matching hardware:**

   ```bash
   idf.py -C examples/standalone -p PORT flash monitor
   ```

   Replace `PORT` with your actual serial port, for example `/dev/ttyACM0`; it is
   a placeholder, not a command to paste unchanged. This writes the demo's
   bootloader/partition table/app. It changes the firmware layout and can make
   existing provisioning unusable. Keep the private full-flash backup.
5. **Device actions:** allow reset. Two white eyes appear on a black background,
   cycling expressions every four seconds. The monitor prints their names. Exit
   the monitor with Ctrl+]. Verify all 21, reset/reboot and restore your backup
   when finished. No hardware pass is claimed until you perform these checks.

## Different wiring (separate adaptation)

Run `idf.py -C examples/standalone menuconfig`, open **Animated faces display
wiring**, set SDA/SCL/address to your physical board, save and rebuild. This
changes only the demo, not the reusable player. Controller/size support must still
match SSD1306 128×64; this is not verified support for arbitrary wiring/hardware.
