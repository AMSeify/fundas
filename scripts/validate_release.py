#!/usr/bin/env python3
"""
Pre-publish validation script.
Run this before creating a release to ensure everything is ready.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report status."""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ {description} - FAILED")
        if result.stderr:
            print(result.stderr)
        if result.stdout:
            print(result.stdout)
        return False


def main():
    """Run all pre-publish checks."""
    print("\n" + "="*60)
    print("🚀 FUNDAS PRE-PUBLISH VALIDATION")
    print("="*60)

    checks = []

    # 1. Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Run this from the project root.")
        sys.exit(1)

    # 2. Run tests
    checks.append(
        run_command(
            "pytest tests/ --cov=fundas --cov-report=term-missing",
            "Running test suite",
        )
    )

    # 3. Check code formatting
    checks.append(
        run_command(
            "black --check fundas/ tests/",
            "Checking code formatting with black",
        )
    )

    # 4. Run linter
    checks.append(
        run_command(
            "flake8 fundas/ tests/ --max-line-length=88 "
            "--extend-ignore=E203 --count",
            "Linting with flake8",
        )
    )

    # 5. Build package
    checks.append(run_command("python -m build", "Building distribution packages"))

    # 6. Check distribution
    if Path("dist").exists():
        checks.append(
            run_command("twine check dist/*", "Validating distribution packages")
        )

    # Summary
    print("\n" + "="*60)
    print("📊 VALIDATION SUMMARY")
    print("="*60)

    passed = sum(checks)
    total = len(checks)

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n✅ All checks passed! Ready to publish.")
        print("\nNext steps:")
        print("1. Update version in fundas/__init__.py")
        print("2. Commit: git commit -am 'Bump version to X.Y.Z'")
        print("3. Tag: git tag vX.Y.Z")
        print("4. Push: git push origin main --tags")
        print("5. Create release on GitHub")

        # Clean up build artifacts
        print("\n🧹 Cleaning up build artifacts...")
        subprocess.run("rm -rf dist/ build/ *.egg-info", shell=True)
        print("✅ Cleanup complete")

        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues before publishing.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
