#!/usr/bin/env python3
"""
Forge Dependency Sanity Check
Ensures requirements.in and requirements.txt stay aligned.
Run during build/deploy to prevent dependency hell.
"""

import sys
from pathlib import Path


def read_requirements_file(file_path):
    """Read and parse a requirements file, ignoring comments and empty lines."""
    if not file_path.exists():
        return None, f"File {file_path.name} does not exist"

    lines = []
    try:
        with file_path.open() as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Handle line continuations and inline comments
                if " #" in line:
                    line = line.split(" #")[0].strip()
                lines.append(line)
        return lines, None
    except Exception as e:
        return None, f"Error reading {file_path.name}: {str(e)}"


def extract_package_name(requirement_line):
    """Extract the package name from a requirement line."""
    line = requirement_line.strip()

    # Skip editable installs and direct URLs for this check
    if line.startswith(("-e ", "git+", "http://", "https://")):
        return None

    # Extract package name before any version specifiers
    for specifier in ["==", ">=", "<=", "~=", ">", "<", "!="]:
        if specifier in line:
            return line.split(specifier)[0].strip().lower()

    # If no version specifier, return the whole line
    return line.lower()


def main():
    """Main sanity check function."""
    req_in = Path("requirements.in")
    req_txt = Path("requirements.txt")

    # Check if files exist
    if not req_in.exists():
        print("❌ requirements.in missing - create it with your desired dependencies")
        sys.exit(1)

    if not req_txt.exists():
        print("❌ requirements.txt missing - generate it with: pip-compile requirements.in")
        sys.exit(1)

    # Read and parse files
    in_lines, error = read_requirements_file(req_in)
    if error:
        print(f"❌ {error}")
        sys.exit(1)

    txt_lines, error = read_requirements_file(req_txt)
    if error:
        print(f"❌ {error}")
        sys.exit(1)

    # Extract package definitions (name → full line)
    in_packages = {}
    for line in in_lines:
        pkg_name = extract_package_name(line)
        if pkg_name:
            in_packages[pkg_name.lower()] = line

    txt_packages = {}
    for line in txt_lines:
        pkg_name = extract_package_name(line)
        if pkg_name:
            txt_packages[pkg_name.lower()] = line

    errors = []
    warnings = []

    # Check for missing or mismatched packages
    for pkg_name, in_line in in_packages.items():
        if pkg_name not in txt_packages:
            errors.append(f"{pkg_name} missing in requirements.txt (from: {in_line})")
        else:
            # Version mismatch detection
            if in_packages[pkg_name] != txt_packages[pkg_name]:
                errors.append(
                    f"{pkg_name} version mismatch → "
                    f"{in_packages[pkg_name]} (in) vs {txt_packages[pkg_name]} (txt)"
                )

    # Warn about extra packages in requirements.txt
    for pkg_name, txt_line in txt_packages.items():
        if pkg_name not in in_packages:
            warnings.append(f"{pkg_name} extra in requirements.txt (from: {txt_line})")

    # Report results
    if errors:
        print("\n============================")
        print("❌ CRITICAL ERRORS: Alignment issues found")
        print("============================")
        for error in errors:
            print(f"   - {error}")
        print("\n💡 Fix: Run `pip-compile requirements.in` to regenerate requirements.txt")

    if warnings:
        print("\n============================")
        print("⚠️  WARNINGS: Extra dependencies detected")
        print("============================")
        for warning in warnings:
            print(f"   - {warning}")
        print("\nℹ️  These are usually transitive dependencies, safe to ignore unless unexpected.")

    # Exit codes
    if not errors and not warnings:
        print("\n✅ Forge dependency sanity check passed - requirements are fully synchronized")
        return 0
    elif warnings and not errors:
        print("\n✅ Requirements are synchronized (warnings are acceptable)")
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
