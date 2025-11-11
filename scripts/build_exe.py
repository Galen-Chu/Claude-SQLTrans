#!/usr/bin/env python3
"""Build standalone executables for SQLTrans using PyInstaller.

This script automates the build process for creating distributable executables
for Windows, macOS, and Linux.

Usage:
    python scripts/build_exe.py [--clean] [--onefile] [--debug]

Options:
    --clean     Clean build directories before building
    --onefile   Build as single executable (default: one-folder)
    --debug     Enable debug mode for PyInstaller
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Path to project root
    """
    return Path(__file__).parent.parent.resolve()


def clean_build_dirs(project_root: Path) -> None:
    """Clean build and dist directories.

    Args:
        project_root: Project root directory
    """
    print("🧹 Cleaning build directories...")

    dirs_to_clean = [
        project_root / "build",
        project_root / "dist",
    ]

    for dir_path in dirs_to_clean:
        if dir_path.exists():
            print(f"  Removing {dir_path}")
            shutil.rmtree(dir_path)

    # Remove spec file build artifacts
    for spec_file in project_root.glob("*.spec"):
        build_dir = project_root / spec_file.stem
        if build_dir.exists() and build_dir.is_dir():
            print(f"  Removing {build_dir}")
            shutil.rmtree(build_dir)

    print("✅ Clean complete")


def build_executable(
    project_root: Path,
    onefile: bool = False,
    debug: bool = False
) -> bool:
    """Build the executable using PyInstaller.

    Args:
        project_root: Project root directory
        onefile: Build as single file executable
        debug: Enable debug mode

    Returns:
        True if build succeeded, False otherwise
    """
    print("🔨 Building SQLTrans executable...")

    spec_file = project_root / "sqltrans.spec"

    if not spec_file.exists():
        print(f"❌ Error: Spec file not found at {spec_file}")
        return False

    # Build command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        str(spec_file),
    ]

    if debug:
        cmd.append("--debug=all")

    # Note: onefile/onedir is configured in the spec file
    # To switch, user needs to edit the spec file

    print(f"  Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True
        )

        print(result.stdout)

        if result.returncode == 0:
            print("✅ Build completed successfully!")

            # Show where the executable is
            dist_dir = project_root / "dist"
            if sys.platform.startswith('win'):
                exe_name = "sqltrans.exe"
            else:
                exe_name = "sqltrans"

            exe_path = dist_dir / exe_name

            if exe_path.exists():
                print(f"\n📦 Executable created at: {exe_path}")
                print(f"   Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")

            return True
        else:
            print(f"❌ Build failed with return code {result.returncode}")
            print(result.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(e.stdout)
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_executable(project_root: Path) -> bool:
    """Test the built executable.

    Args:
        project_root: Project root directory

    Returns:
        True if test succeeded, False otherwise
    """
    print("\n🧪 Testing executable...")

    dist_dir = project_root / "dist"

    if sys.platform.startswith('win'):
        exe_path = dist_dir / "sqltrans.exe"
    else:
        exe_path = dist_dir / "sqltrans"

    if not exe_path.exists():
        print(f"❌ Executable not found at {exe_path}")
        return False

    # Test --version
    try:
        result = subprocess.run(
            [str(exe_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print(f"  Version check: ✅")
            print(f"  Output: {result.stdout.strip()}")
            return True
        else:
            print(f"  Version check: ❌")
            print(f"  Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("  Version check: ❌ (timeout)")
        return False
    except Exception as e:
        print(f"  Version check: ❌ ({e})")
        return False


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description="Build SQLTrans standalone executable"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build directories before building"
    )
    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Build as single executable file (edit spec file)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable PyInstaller debug mode"
    )
    parser.add_argument(
        "--no-test",
        action="store_true",
        help="Skip testing the built executable"
    )

    args = parser.parse_args()

    project_root = get_project_root()

    print(f"📁 Project root: {project_root}")
    print(f"🖥️  Platform: {sys.platform}")
    print()

    # Clean if requested
    if args.clean:
        clean_build_dirs(project_root)
        print()

    # Build
    success = build_executable(
        project_root,
        onefile=args.onefile,
        debug=args.debug
    )

    if not success:
        return 1

    # Test
    if not args.no_test:
        test_success = test_executable(project_root)
        if not test_success:
            print("\n⚠️  Warning: Executable test failed")
            print("   The build completed but the executable may not work correctly")

    print("\n✨ Build process complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
