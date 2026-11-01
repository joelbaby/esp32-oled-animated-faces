#!/usr/bin/env python3
"""Install the faces module and exact display patch into a pinned XiaoZhi checkout."""
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess
PIN = "addb1ed59bd71e09a6a5e0c52ad2f1c474aa8ca1"
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("checkout", type=Path)
a = p.parse_args()
target = a.checkout.resolve()
def git(*args): return subprocess.check_output(["git", "-C", str(target), *args])
if git("rev-parse", "HEAD").decode().strip() != PIN:
    raise SystemExit("Wrong XiaoZhi commit; use the pinned clean checkout in docs/XIAOZHI.md")
records = json.loads((ROOT / "examples/xiaozhi/patch-files.json").read_text())
for name, record in records.items():
    file = target / name
    actual = hashlib.sha256(file.read_bytes()).hexdigest() if file.exists() else None
    if actual != record["before"]:
        raise SystemExit("Refusing to overwrite modified/existing file: " + name)
component = target / "components/animated_faces"
if component.exists(): raise SystemExit("Component already exists; use a fresh checkout")
lock = target / "dependencies.lock"
source_lock = ROOT / "examples/xiaozhi/dependencies.lock"
if lock.exists() and lock.read_bytes() != source_lock.read_bytes():
    raise SystemExit("Different dependency lock exists; use a fresh checkout")
patch = ROOT / "examples/xiaozhi/animated-faces.patch"
subprocess.run(["git", "-C", str(target), "apply", "--check", str(patch)], check=True)
component.mkdir(parents=True)
for name in ["CMakeLists.txt", "idf_component.yml", "include", "third_party"]:
    source = ROOT / name
    if source.is_dir(): shutil.copytree(source, component / name)
    else: shutil.copyfile(source, component / name)
subprocess.run(["git", "-C", str(target), "apply", str(patch)], check=True)
for name, record in records.items():
    if hashlib.sha256((target / name).read_bytes()).hexdigest() != record["after"]:
        raise SystemExit("Installed patch hash mismatch: " + name)
shutil.copyfile(source_lock, lock)
print("Installed pinned faces module/display patch. Existing board pinouts are unchanged.")
print("Build only the board matching your physical wiring; see docs/XIAOZHI.md.")
