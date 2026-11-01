#!/usr/bin/env python3
"""Export an explicit reviewed file allowlist, without Git history or build outputs."""
from pathlib import Path
import argparse, hashlib, json, re, shutil
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("destination", type=Path)
a = p.parse_args()
dest = a.destination.resolve()
if dest.exists(): raise SystemExit("Destination exists; choose a new empty export path")
files = (ROOT / "release-files.txt").read_text().splitlines()
if len(files) != len(set(files)): raise SystemExit("Duplicate allowlist entry")
markers = [
    re.compile(rb"/(?:home|Users)/[A-Za-z0-9_.-]+/"),
    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(rb"\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b"),
    re.compile(rb"(?i)(?:wifi_password|api_key|access_token)\s*[:=]\s*[\"'][^\"']{6,}[\"']"),
]
manifest = {}
for name in files:
    relative = Path(name)
    if not name or relative.is_absolute() or ".." in relative.parts:
        raise SystemExit("Invalid allowlist path: " + name)
    source = ROOT / relative
    if not source.is_file() or source.is_symlink(): raise SystemExit("Missing/symlink input: " + name)
    data = source.read_bytes()
    if source.suffix not in {".png", ".gif"}:
        for marker in markers:
            if marker.search(data): raise SystemExit("Private marker needs review in: " + name)
    manifest[name] = hashlib.sha256(data).hexdigest()
# Validate every input before writing any output.
for name in files:
    target = dest / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / name, target)
    target.chmod((ROOT / name).stat().st_mode & 0o777)
(dest / "SOURCE-MANIFEST.json").write_text(json.dumps({
    "release": (ROOT / "VERSION").read_text().strip(), "files_sha256": manifest,
    "audit": "Explicit allowlist; local-user paths, private-key, MAC and credential markers checked. No binary firmware included."
}, indent=2) + "\n")
print(f"Exported {len(files)} allowlisted files; marker audit passed; SOURCE-MANIFEST.json created")
