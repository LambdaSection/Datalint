"""Verify all dependencies are installed before going offline."""
import sys
import os

required_packages = [
    'pandas',
    'numpy',
    'click',
    'yaml',  # pyyaml
]

optional_packages = [
    'pytest',
    'jinja2',
    'openpyxl',
    'scipy',
]

print("=" * 60)
print("DataLint Installation Verification")
print("=" * 60)

print("\n1. Checking required packages...")
print("-" * 60)
missing_required = []
for pkg in required_packages:
    try:
        __import__(pkg)
        print(f"✅ {pkg}")
    except ImportError:
        print(f"❌ {pkg} - MISSING!")
        missing_required.append(pkg)

print("\n2. Checking optional packages...")
print("-" * 60)
missing_optional = []
for pkg in optional_packages:
    try:
        __import__(pkg)
        print(f"✅ {pkg}")
    except ImportError:
        print(f"⚠️  {pkg} - not installed (optional)")
        missing_optional.append(pkg)

print("\n3. Checking project structure...")
print("-" * 60)
project_files = [
    'datalint/engine/base.py',
    'datalint/engine/validators.py',
    'setup.py',
    'CODING.md'
]
missing_files = []
for file in project_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - MISSING!")
        missing_files.append(file)

print("\n4. Testing project imports...")
print("-" * 60)
try:
    from datalint.engine.base import BaseValidator, ValidationResult, ValidationRunner
    print("✅ datalint.engine.base imports OK")
except ImportError as e:
    print(f"❌ Cannot import datalint.engine.base: {e}")

try:
    from datalint.engine.validators import check_missing_values
    print("✅ datalint.engine.validators imports OK")
except ImportError as e:
    print(f"⚠️  datalint.engine.validators: {e} (may be expected if not implemented)")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if missing_required:
    print(f"\n❌ ERROR: Missing required packages: {', '.join(missing_required)}")
    print(f"\nInstall with:")
    print(f"  pip install {' '.join(missing_required)}")
    sys.exit(1)

if missing_files:
    print(f"\n⚠️  WARNING: Missing project files: {', '.join(missing_files)}")
    print("Make sure you're running this from the project root directory")

if missing_optional:
    print(f"\nℹ️  INFO: Optional packages not installed: {', '.join(missing_optional)}")
    print("These are recommended but not required:")

print("\n✅ All required packages installed!")
print("✅ Ready for offline development!")
print("\nNext steps:")
print("  1. Read CODING.md for implementation guide")
print("  2. Start implementing validators, CLI, etc.")
print("  3. Run tests: pytest tests/")

