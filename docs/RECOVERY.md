# Backup, installation problems and rollback

No device was flashed to prepare this candidate. The commands below are procedures
for a later intentional hardware installation, not evidence that one occurred.

## Save your current firmware privately

Activate the pinned ESP-IDF environment first; it supplies esptool 5.6. Replace
`PORT` with your actual serial device (for example `/dev/ttyACM0`). Confirm that
you have an ESP32-C3 with 4 MB flash before using the sizes below.

**Device actions:** connect a USB data cable. If connection fails, hold BOOT while
resetting/powering the C3, then release BOOT to enter the ROM download mode.

**Terminal:**

```bash
python -m esptool --port PORT flash-id
python -m esptool --chip esp32c3 --port PORT read-flash 0 0x400000 backup-before-faces.bin
sha256sum backup-before-faces.bin > backup-before-faces.bin.sha256
python -m esptool --chip esp32c3 --port PORT verify-flash 0 backup-before-faces.bin
```

Keep the 4 MB file and checksum somewhere safe and private, outside any repository
or shared release. It contains device provisioning/Wi-Fi credentials and possibly
other personal data. Never publish read-back firmware. For a different flash size,
stop and use that board's documented backup procedure instead of truncating it.

A full flash writes bootloader/partition/app/assets addresses specified by that
build. Different partition tables or metadata can invalidate/overwrite existing
stored data, even without `erase-flash`. Neither example promises to preserve
provisioning when replacing another firmware. A source-only app update is possible
only after independently verifying identical partitions, assets and compatibility;
this beginner path deliberately uses a backed-up full installation.

## Restore the previous firmware

**Device actions:** enter ROM download mode with BOOT/reset if needed.
**Terminal — with your private original backup, correct port and same device:**

```bash
sha256sum -c backup-before-faces.bin.sha256
python -m esptool --chip esp32c3 --port PORT write-flash 0 backup-before-faces.bin
python -m esptool --chip esp32c3 --port PORT verify-flash 0 backup-before-faces.bin
```

**Device actions:** reset/power-cycle. Check the original firmware starts and its
network/provisioning still works. Restoring a full backup also restores its stored
credentials; keep it private. Source rollback is an alternative: build/flash your
known-good previous source/configuration, then provision as needed.

## Common errors

| Symptom | Fix / expected result |
|---|---|
| `idf.py: command not found` | Activate the exact SDK in this terminal; see host setup. |
| Export asks for unrelated Xtensa tools | Register a reused SDK path with `idf_tools.py install --targets esp32c3`; fresh setup script already does this. |
| Component registry connection error | Check Internet/DNS/proxy access to Espressif component registry; retry the build. Do not edit managed components to bypass it. |
| Wrong pin or installer refuses changed file | Use a fresh checkout at the documented hash. Save your edits; do not reset/discard them. |
| Decoder/generation check differs | Use Python 3.12 and the pinned Pillow 10.2.0; verify upstream hashes. Do not regenerate with arbitrary versions. |
| `Permission denied` opening serial port | Check Linux dialout/serial permissions and reconnect/relogin after a group change; close other serial programs. |
| No serial connection | USB data cable, correct port, BOOT/reset ROM download mode. |
| Blank OLED / I²C timeout | Power off; verify 3.3 V/ground, SDA/SCL, 0x3c address and exact SSD1306 128×64 controller. Rebuild configured pins. |
| Only top status or old static emoji | Confirm the selected display is OledDisplay at 128×64 and the new build was installed; see source patch. |
| Large first build / missing assets | Allow all pinned component/model downloads and enough disk. Do not disable unrelated upstream assets to hide a failing build. |
| Build fits, device misbehaves | Build success does not establish hardware correctness. Restore the private backup; report exact board/controller and nonprivate errors. |

Do not erase NVS, burn eFuses or change audio/network settings as a face-animation
troubleshooting step. Preserve board-specific physical recovery behavior.
