"""
Forge sanity check — ensures requirements.in and requirements.txt stay aligned.
Run at build/deploy.
"""

import sys
from pathlib import Path

req_in = Path("requirements.in")
req_txt = Path("requirements.txt")

if not req_in.exists() or not req_txt.exists():
    print("⚠️ requirements.in or requirements.txt missing")
    sys.exit(1)

# Read both files
with req_in.open() as f:
    in_lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
with req_txt.open() as f:
    txt_lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

# Check each package in .in exists in .txt
errors = []
for line in in_lines:
    pkg = line.split("==")[0].lower()
    if not any(l.lower().startswith(pkg + "==") for l in txt_lines):
        errors.append(pkg)

if errors:
    print("❌ Mismatch detected between requirements.in and requirements.txt:")
    for e in errors:
        print(f"   - {e} is in requirements.in but not pinned in requirements.txt")
    sys.exit(1)

print("✅ Forge dependency sanity check passed")
