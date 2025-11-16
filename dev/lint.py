#!/usr/bin/env python3
"""
Shell script linter - checks for common issues
Basic linting without external tools
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# Add .sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT / '.sys' / 'theme'))

# Import central theme
from theme import Colors, Icons, log_success, log_error, log_warn, log_info


def check_syntax(filepath: Path) -> bool:
    """Check shell script syntax"""
    try:
        subprocess.run(['bash', '-n', str(filepath)], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def check_shebang(filepath: Path) -> bool:
    """Check for shebang line"""
    try:
        first_line = filepath.read_text(encoding='utf-8').split('\n')[0]
        return first_line.startswith('#!')
    except Exception:
        return False


def check_set_e(filepath: Path) -> bool:
    """Check for set -e or set -o errexit"""
    try:
        content = filepath.read_text(encoding='utf-8')
        return 'set -e' in content or 'set -o errexit' in content
    except Exception:
        return False


def check_pipefail(filepath: Path) -> bool:
    """Check for set -o pipefail"""
    try:
        content = filepath.read_text(encoding='utf-8')
        return 'set -o pipefail' in content
    except Exception:
        return False


def lint_file(filepath: Path) -> Tuple[bool, int]:
    """
    Lint a single shell script
    Returns: (passed, critical_issues)
    """
    issues = 0

    print(f"{Colors.BLUE}Checking {Colors.NC}{filepath}")

    # 1. Syntax check
    if not check_syntax(filepath):
        log_error("  Syntax error detected")
        issues += 1

    # 2. Check for set -e
    if not check_set_e(filepath):
        log_warn("  Missing 'set -e' (consider adding for safety)")

    # 3. Check for set -o pipefail
    if not check_pipefail(filepath):
        log_warn("  Missing 'set -o pipefail' (consider adding for pipe safety)")

    # 4. Check for shebang
    if not check_shebang(filepath):
        log_error("  Missing shebang line")
        issues += 1

    # 5. Check executable permission
    if not filepath.stat().st_mode & 0o111:
        log_warn(f"  Script is not executable (chmod +x {filepath.name})")

    if issues == 0:
        log_success("  Passed basic linting")
        return True, 0
    else:
        log_error(f"  {issues} critical issue(s) found")
        return False, issues


def scan_files(base_path: Path, recursive: bool) -> List[Path]:
    """Scan for shell script files"""
    files = []

    if base_path.is_file():
        if base_path.suffix == '.sh':
            files.append(base_path)
    elif base_path.is_dir():
        pattern = '**/*.sh' if recursive else '*.sh'
        files.extend(base_path.glob(pattern))

    return sorted(files)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Shell script linter - checks for common issues',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Lint all shell scripts in current directory
  python3 lint.py

  # Lint shell scripts in specific directory
  python3 lint.py --path /path/to/scripts

  # Lint shell scripts recursively
  python3 lint.py --recursive --path /path/to/project

  # Lint a specific file
  python3 lint.py --path script.sh
        '''
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        default='.',
        help='Path to file or directory to lint (default: current directory)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )

    args = parser.parse_args()

    print()
    print(f"{Colors.MAUVE}[lint]{Colors.NC} Linting shell scripts...")
    print()

    base_path = Path(args.path)

    if not base_path.exists():
        log_error(f"Path not found: {base_path}")
        return 1

    # Scan files
    files = scan_files(base_path, args.recursive)

    if not files:
        log_error("No shell scripts found")
        return 1

    # Lint files
    total_scripts = 0
    passed_scripts = 0
    total_issues = 0

    for filepath in files:
        passed, issues = lint_file(filepath)
        total_scripts += 1
        if passed:
            passed_scripts += 1
        total_issues += issues
        print()

    # Summary
    print(f"{Colors.GREEN}Summary:{Colors.NC}")
    print()
    print(f"{Colors.BLUE}  Total scripts:     {Colors.NC}{total_scripts}")
    print(f"{Colors.GREEN}  Passed:            {Colors.NC}{passed_scripts}")
    print(f"{Colors.RED}  Critical issues:   {Colors.NC}{total_issues}")
    print()

    if total_issues == 0:
        log_success("All shell scripts passed linting!")
        return 0
    else:
        log_error("Some scripts have critical issues")
        return 1


if __name__ == '__main__':
    sys.exit(main())
