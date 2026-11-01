#!/usr/bin/env python3
"""Render every original frame, then verify the public C++ player/decoder against it."""
from pathlib import Path
import importlib.util, os, subprocess, tempfile, sys
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("faces_generator", ROOT / "tools/generate_assets.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
with tempfile.TemporaryDirectory(prefix="faces-test-") as temporary:
    work = Path(temporary)
    reference = work / "reference.bin"
    frames = 0
    with reference.open("wb") as output:
        for name, (_, count) in gen.original.EXPRESSIONS.items():
            for index in range(count):
                image, guard = gen.render(name, index)
                output.write(gen.pack(image))
                frames += 1
    assert frames == 884
    binary = work / "player_test"
    subprocess.run([os.environ.get("CXX", "c++"), "-std=c++17", "-O1", "-g",
                    "-Wall", "-Wextra", "-Werror", "-fsanitize=undefined",
                    "-fno-sanitize-recover=all", "-I", str(ROOT / "include"),
                    str(ROOT / "tests/player_test.cc"), "-o", str(binary)], check=True)
    subprocess.run([str(binary), str(reference)], check=True)
subprocess.run([sys.executable, str(ROOT / "tools/generate_assets.py"), "--check"], check=True)
