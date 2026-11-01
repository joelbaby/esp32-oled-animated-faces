# Host setup (tested Linux path)

Use Linux Mint 22.3 x86_64 / Ubuntu 24.04 with Python 3.12.3. Other hosts need their
ESP-IDF host prerequisites and are not covered by the tested commands here.
Get the pinned source release, then work from its root:

```bash
git clone --branch v0.1.0-rc3 --depth 1 https://github.com/joelbaby/esp32-oled-animated-faces.git
cd esp32-oled-animated-faces
```

Alternatively unpack the source archive from the matching GitHub prerelease.

**Terminal — install host packages** (sudo may ask for your computer password):

```bash
sudo apt-get update
sudo apt-get install -y git wget flex bison gperf python3 python3-pip python3-venv cmake ninja-build ccache libffi-dev libssl-dev dfu-util libusb-1.0-0 build-essential
```

**Terminal — install the exact C3 SDK/toolchain in this source directory**:

```bash
bash tools/setup_idf.sh
export IDF_TOOLS_PATH="$PWD/.tools/espressif"
source .tools/esp-idf/export.sh
idf.py --version
```

Expected: ESP-IDF 6.1 at commit `9a97f6c54ec638111ce55cd36581b3c192f15207`.
The full commit, rather than the moving `release/v6.1` branch, is authoritative.
The installer downloads public SDK/submodule/tool packages. It does not touch a
connected device. A new terminal needs the `export` and `source` commands again.
Use several GB of free disk. Do not mix this pin with an existing IDF 5.x setup.

Optional host-only asset tests require a separate Python virtual environment (an
isolated set of Python packages). They are not needed to play shipped assets:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/requirements.txt
.venv/bin/python tools/test.py
```

Expected: 884 exact-frame comparisons, player checks and exact regeneration pass.
Do not install a different Pillow version for reproducibility.

## Reusing a pinned toolchain (separate cache path)

The initial validation reused C3 compilers and the IDF Python environment with a
separate **clean** SDK checkout. A later cold dependency run is recorded separately
in VALIDATION.md. To reuse your own existing pinned cache,
set these to your own clean SDK and installed tools directory:

```bash
export FACES_IDF_PATH="/path/to/clean/pinned/esp-idf"
export IDF_TOOLS_PATH="/path/to/installed/espressif-tools"
python3 "$FACES_IDF_PATH/tools/idf_tools.py" install --targets esp32c3
source "$FACES_IDF_PATH/export.sh"
```

The install command registers this SDK path with the tool cache; without it,
export.sh may try to find unrelated chip toolchains. This is an alternative to the
recommended `.tools/` install, not an extra step for beginners.
