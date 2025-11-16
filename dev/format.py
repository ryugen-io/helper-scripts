#!/usr/bin/env python3
"""
Shell script formatter using shfmt (like cargo fmt for Rust)
Automatically formats all shell scripts in the repository
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


def load_env_config(repo_root: Path) -> dict:
    """Load configuration from .env file"""
    config = {
        'SYS_DIR': '.sys',
        'GITHUB_DIR': '.github',
        'SCRIPT_DIRS': 'docker,dev,utils'
    }

    # Try .sys/env/.env first, fallback to .sys/env/.env.example
    sys_env_dir = repo_root / config['SYS_DIR'] / 'env'
    for env_name in ['.env', '.env.example']:
        env_file = sys_env_dir / env_name
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key] = value
            break

    return config


# shfmt configuration options
SHFMT_OPTS = ['-i', '4', '-bn', '-ci', '-sr']


def check_shfmt() -> bool:
    """Check if shfmt is installed"""
    try:
        subprocess.run(['shfmt', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_error("shfmt is not installed")
        print()
        print(f"{Colors.TEXT}Install shfmt:{Colors.NC}")
        print(f"{Colors.BLUE}  # Using Go{Colors.NC}")
        print(f"{Colors.TEXT}  go install mvdan.cc/sh/v3/cmd/shfmt@latest{Colors.NC}")
        print()
        print(f"{Colors.BLUE}  # Using Homebrew (macOS/Linux){Colors.NC}")
        print(f"{Colors.TEXT}  brew install shfmt{Colors.NC}")
        print()
        print(f"{Colors.BLUE}  # Using package manager (Debian/Ubuntu){Colors.NC}")
        print(f"{Colors.TEXT}  sudo apt install shfmt{Colors.NC}")
        print()
        print(f"{Colors.BLUE}  # Using package manager (Arch){Colors.NC}")
        print(f"{Colors.TEXT}  sudo pacman -S shfmt{Colors.NC}")
        print()
        return False


def get_shfmt_version() -> str:
    """Get shfmt version"""
    try:
        result = subprocess.run(['shfmt', '-version'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def format_file(filepath: Path, check_mode: bool = False) -> int:
    """
    Format a single shell script file
    Returns: 0=formatted, 1=unchanged, 2=failed
    """
    filename = filepath.name

    # Check if file needs formatting
    try:
        subprocess.run(
            ['shfmt'] + SHFMT_OPTS + ['-d', str(filepath)],
            capture_output=True,
            check=True
        )
        # File is already formatted
        print(f"  {Colors.TEXT}{filename}{Colors.NC} {Colors.SAPPHIRE}(no changes){Colors.NC}")
        return 1  # unchanged
    except subprocess.CalledProcessError:
        # File needs formatting
        if check_mode:
            log_warn(f"  {filename} needs formatting")
            return 0  # needs format
        else:
            # Format the file
            try:
                subprocess.run(
                    ['shfmt'] + SHFMT_OPTS + ['-w', str(filepath)],
                    check=True,
                    capture_output=True
                )
                log_success(f"  Formatted {filename}")
                return 0  # formatted
            except subprocess.CalledProcessError:
                log_error(f"  Failed to format {filename}")
                return 2  # failed


def scan_files(base_path: Path, types: List[str], recursive: bool) -> List[Path]:
    """Scan for shell script files"""
    files = []

    if base_path.is_file():
        files.append(base_path)
    elif base_path.is_dir():
        for ext in types:
            ext = ext.lstrip('*.')
            pattern = f'**/*.{ext}' if recursive else f'*.{ext}'
            files.extend(base_path.glob(pattern))

    return sorted(files)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Shell script formatter using shfmt',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Format all shell scripts in current directory
  python3 format.py

  # Check formatting without modifying files
  python3 format.py --check

  # Format files in specific directory
  python3 format.py --path /path/to/scripts

  # Format files recursively
  python3 format.py --recursive --path /path/to/project

  # Format specific file types
  python3 format.py --types sh bash
        '''
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        default='.',
        help='Path to file or directory to format (default: current directory)'
    )

    parser.add_argument(
        '-t', '--types',
        nargs='+',
        default=['sh'],
        help='File extensions to format (default: sh)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )

    parser.add_argument(
        '-c', '--check',
        action='store_true',
        help='Check mode - do not modify files, just report'
    )

    args = parser.parse_args()

    print()
    print(f"{Colors.MAUVE}[format]{Colors.NC} Shell Script Formatter (shfmt)")
    print()

    if args.check:
        log_info("Running in check mode (no files will be modified)")
        print()

    # Check if shfmt is installed
    if not check_shfmt():
        return 1

    # Show shfmt version
    version = get_shfmt_version()
    log_info(f"Using shfmt {version}")
    print()

    # Find files
    base_path = Path(args.path)

    if not base_path.exists():
        log_error(f"Path not found: {base_path}")
        return 1

    files = scan_files(base_path, args.types, args.recursive)

    if not files:
        log_error(f"No files found matching types: {', '.join(args.types)}")
        return 1

    log_info(f"Processing {len(files)} file(s)")
    print()

    # Format files
    formatted = 0
    unchanged = 0
    failed = 0

    for filepath in files:
        result = format_file(filepath, check_mode=args.check)
        if result == 0:
            formatted += 1
        elif result == 1:
            unchanged += 1
        elif result == 2:
            failed += 1

    # Print summary
    print()
    print(f"{Colors.MAUVE}Summary{Colors.NC}")
    print()

    total = formatted + unchanged + failed
    print(f"{Colors.TEXT}Total files checked:  {Colors.NC}{Colors.SAPPHIRE}{total}{Colors.NC}")

    if formatted > 0:
        action = "Need formatting" if args.check else "Formatted"
        print(f"{Colors.GREEN}{action}:         {Colors.NC}{Colors.SAPPHIRE}{formatted}{Colors.NC}")

    if unchanged > 0:
        print(f"{Colors.TEXT}Already formatted:   {Colors.NC}{Colors.SAPPHIRE}{unchanged}{Colors.NC}")

    if failed > 0:
        print(f"{Colors.RED}Failed:              {Colors.NC}{Colors.SAPPHIRE}{failed}{Colors.NC}")

    print()

    # Exit with appropriate code
    if failed > 0:
        log_error("Some files failed to format")
        return 1
    elif formatted > 0:
        if args.check:
            log_warn("Some files need formatting")
            return 1
        else:
            log_success("All files formatted successfully!")
            return 0
    else:
        log_success("All files already formatted correctly!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
