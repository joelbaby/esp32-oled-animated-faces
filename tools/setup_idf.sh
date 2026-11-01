#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
idf="$root/.tools/esp-idf"
tools="$root/.tools/espressif"
pin=9a97f6c54ec638111ce55cd36581b3c192f15207
if [[ ! -d "$idf/.git" ]]; then
    git init "$idf"
    git -C "$idf" remote add origin https://github.com/espressif/esp-idf.git
    git -C "$idf" fetch --depth 1 origin "$pin"
    git -C "$idf" checkout --detach FETCH_HEAD
fi
[[ "$(git -C "$idf" rev-parse HEAD)" == "$pin" ]] || { echo "Wrong IDF pin; refusing to change checkout" >&2; exit 1; }
git -C "$idf" diff --quiet || { echo "Modified IDF checkout; use a clean SDK" >&2; exit 1; }
git -C "$idf" submodule update --init --recursive --depth 1
(cd "$idf"; IDF_TOOLS_PATH="$tools" ./install.sh esp32c3)
IDF_TOOLS_PATH="$tools" python3 "$idf/tools/idf_tools.py" install cmake ninja
printf 'Ready. In this shell run:\nexport IDF_TOOLS_PATH="$PWD/.tools/espressif"\nsource .tools/esp-idf/export.sh\n'
