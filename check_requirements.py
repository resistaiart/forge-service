#!/usr/bin/env python3
"""
Forge Dependency Sanity Check
Ensures requirements.in and requirements.txt stay aligned and pinned.
Run during build/deploy to prevent dependency drift.
"""

import sys
from pathlib import Path

def read_requirements_file(file_path: Path):
    """Read and parse a requirements file, ignoring comments and empty lines."""
    if not file_path.exists():
        return None, f"File {file_path.name} does not exist"

    lines = []
    try:
        with file_path.open() as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if " #" in line:
                    line = line.split(" #")[0].strip()
                lines.append(line)
        return lines, None
    except Exception as e:
        return None, f"Error reading {file_path.name}: {str(e)}"

def extract_package_name(requirement_line: str):
    """Extract the package name from a requirement line."""
    line = requirement_line.strip()
    if line.startswith(("-e ", "git+", "http://", "https://")):
        return None
    for specifier in ["==", ">=", "<=", "~=", ">", "<", "!="]:
        if specifier in line:
            return line.split(specifier)[0].strip().lower()
    return line.lower()

def check_for_unpinned(requirements):
    """Warn if any requirements are not pinned with ==."""
    return [req for req in requirements if "==" not in req and not req.startswith(("-e", "git+"))]

def main():
    req_in = Path("requirements.in")
    req_txt = Path("requirements.txt")

    if not req_in.exists():
        print("❌ requirements.in missing - create it with your desired dependencies")
        sys.exit(1)
    if not req_txt.exists():
        print("❌ requirements.txt missing - generate it with: pip-compile requirements.in")
        sys.exit(1)

    in_lines, err = read_requirements_file(req_in)
    if err:
        print(f"❌ {err}")
        sys.exit(1)

    txt_lines, err = read_requirements_file(req_txt)
    if err:
        print(f"❌ {err}")
        sys.exit(1)

    in_packages = {extract_package_name(line): line for line in in_lines if extract_package_name(line)}
    txt_packag_
