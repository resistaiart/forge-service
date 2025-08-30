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
    
    # Check for missing packages
    for pkg_name, original_line in in_packages.items():
        if pkg_name not in txt_packages:
            errors.append(f"{pkg_name} (in {req_in.name} but missing in {req_txt.name})")
        else:
            # Version mismatch detection
            if in_packages[pkg_name] != txt_packages[pkg_name]:
                errors.append(
                    f"{pkg_name} version mismatch: "
                    f"{in_packages[pkg_name]} vs {txt_packages[pkg_name]}"
                )
    
    # Warn about extra packages in requirements.txt
    for pkg_name, original_line in txt_packages.items():
        if pkg_name not in in_packages:
            warnings.append(f"{pkg_name} (present in {req_txt.name}, not in {req_in.name})")
    
    # Report results
    if errors:
        print("❌ CRITICAL: Dependency alignment errors found:")
        for error in errors:
            print(f"   - {error}")
        print("\n💡 Run: pip-compile requirements.in to regenerate requirements.txt")
    
    if warnings:
        print("\n⚠️  WARNING: Extra packages in requirements.txt (likely transitive deps):")
        for warning in warnings:
            print(f"   - {warning}")
    
    if not errors and not warnings:
        print("✅ Forge dependency sanity check passed - requirements are synchronized")
        return 0
    elif warnings and not errors:
        print("\n✅ Requirements are synchronized (warnings are acceptable for transitive dependencies)")
        return 0
    else:
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
