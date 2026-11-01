#!/usr/bin/env python3
"""Compile the exact installed standard OledDisplay source against real LVGL and host port stubs."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("checkout", type=Path, help="Pinned XiaoZhi with faces patch installed and managed components fetched")
p.add_argument("--build", type=Path, default=ROOT / "build/standard-adapter")
p.add_argument("--cmake", default="cmake")
a = p.parse_args()
checkout = a.checkout.resolve()
if subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"]).decode().strip() != "addb1ed59bd71e09a6a5e0c52ad2f1c474aa8ca1":
    raise SystemExit("Wrong XiaoZhi source commit")
version = json.loads((ROOT / "versions.json").read_text())["host_adapter_test"]
lvgl = checkout / "managed_components/lvgl__lvgl"
checksums = lvgl / "CHECKSUMS.json"
if (lvgl / ".component_hash").read_text().strip() != version["component_hash"] or hashlib.sha256(checksums.read_bytes()).hexdigest() != version["checksums_sha256"]:
    raise SystemExit("LVGL dependency differs from the pinned registry source")
for item in json.loads(checksums.read_text())["files"]:
    if hashlib.sha256((lvgl / item["path"]).read_bytes()).hexdigest() != item["hash"]:
        raise SystemExit("LVGL source checksum mismatch: " + item["path"])
records = json.loads((ROOT / "examples/xiaozhi/patch-files.json").read_text())
production = a.build.resolve() / "production"
production.mkdir(parents=True, exist_ok=True)
for name in ["main/display/oled_display.cc", "main/display/oled_display.h"]:
    source = checkout / name
    if hashlib.sha256(source.read_bytes()).hexdigest() != records[name]["after"]:
        raise SystemExit("Adapter differs from reviewed production patch: " + name)
    shutil.copyfile(source, production / source.name)
    assert source.read_bytes() == (production / source.name).read_bytes()
subprocess.run([a.cmake, "-S", str(ROOT / "tests/xiaozhi"), "-B", str(a.build.resolve()),
                "-DXIAOZHI=" + str(checkout), "-DPRODUCTION=" + str(production),
                "-DFACES=" + str(ROOT), "-DCMAKE_BUILD_TYPE=Debug"], check=True)
subprocess.run([a.cmake, "--build", str(a.build.resolve()), "-j", "4"], check=True)
subprocess.run([str(a.build.resolve() / "adapter_test")], check=True)
