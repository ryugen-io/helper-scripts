#!/usr/bin/env python3
"""
Style and theming checker for helper scripts
Validates coding guidelines and Catppuccin Mocha theming consistency
"""

import sys
from pathlib import Path
from typing import List

# Add .sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT / '.sys' / 'theme'))

from theme import (  # noqa: E402
    Colors, Icons, log_success, log_error, log_warn, log_info
)


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


EXPECTED_COLORS = {
    'RED': '243;139;168',
    'GREEN': '166;227;161',
    'YELLOW': '249;226;175',
    'BLUE': '137;180;250',
    'MAUVE': '203;166;247',
    'SAPPHIRE': '116;199;236',
    'TEXT': '205;214;244',
}


class StyleChecker:
    def __init__(self):
        self.total_files = 0
        self.passed_files = 0
        self.failed_files = 0
        self.warnings = 0
        self.ignored_files = self._load_ignore_list()
        self.config = load_env_config(REPO_ROOT)

    def _load_ignore_list(self) -> set:
        """Not used - files self-declare ignore status"""
        return set()

    def should_ignore(self, filepath: Path) -> bool:
        """Check if file contains STYLECHECK_IGNORE marker"""
        try:
            content = filepath.read_text(encoding='utf-8')
            # Check first 10 lines for the marker
            for line in content.split('\n')[:10]:
                if 'STYLECHECK_IGNORE' in line:
                    return True
        except Exception:
            pass
        return False

    def check_colors(self, filepath: Path) -> int:
        """Check if file uses correct Catppuccin Mocha colors"""
        issues = 0
        content = filepath.read_text(encoding='utf-8')

        for color_name, expected_rgb in EXPECTED_COLORS.items():
            # Check if color is defined
            if f'readonly {color_name}=' in content or f'{color_name}=' in content:
                # Verify correct RGB values
                if expected_rgb not in content:
                    log_warn(f"    Incorrect RGB for {color_name} (expected: {expected_rgb})")
                    issues += 1
                    self.warnings += 1

        return issues

    def check_standards(self, filepath: Path) -> int:
        """Check coding standards"""
        issues = 0
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')

        # Check shebang
        if lines and not (lines[0].startswith('#!/bin/bash') or lines[0].startswith('#!/usr/bin/env python3')):
            log_error("    Invalid or missing shebang")
            issues += 1

        if filepath.suffix == '.sh':
            # Check for set -e
            if 'set -e' not in content:
                log_error("    Missing: set -e")
                issues += 1

            # Check for set -o pipefail
            if 'set -o pipefail' not in content:
                log_error("    Missing: set -o pipefail")
                issues += 1

            # Check for readonly usage with colors
            if 'RED=' in content and 'readonly RED=' not in content:
                log_warn("    Color variables should be readonly")
                issues += 1
                self.warnings += 1

        return issues

    def check_structure(self, filepath: Path) -> int:
        """Check script structure"""
        issues = 0
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')

        if filepath.suffix == '.sh':
            # Check for logging functions if colors are used
            if 'readonly RED=' in content:
                if not any(fn in content for fn in ['log_error', 'log_success', 'log_info', 'log_warn']):
                    log_warn("    Script uses colors but has no logging functions")
                    issues += 1
                    self.warnings += 1

            # Check for .env integration
            sys_dir = self.config.get('SYS_DIR', '.sys')
            env_path = f'{sys_dir}/env/.env'
            if env_path not in content and f'source "$REPO_ROOT/{env_path}"' not in content:
                log_warn(f"    Missing .env integration ({env_path})")
                self.warnings += 1

            # Check for description comment on line 2
            if len(lines) > 1 and not lines[1].startswith('#'):
                log_warn("    Missing description comment on line 2")
                self.warnings += 1

        if filepath.suffix == '.py':
            # Check for .env integration in Python scripts
            if 'load_env' not in content:
                log_warn("    Missing .env integration (load_env function)")
                self.warnings += 1

        return issues

    def check_file(self, filepath: Path) -> bool:
        """Check a single file"""
        # Skip ignored files
        if self.should_ignore(filepath):
            print(f"{Colors.SUBTEXT}Skipping: {Colors.YELLOW}{filepath.name}{Colors.NC} {Colors.SUBTEXT}(STYLECHECK_IGNORE){Colors.NC}")
            return True  # Count as passed

        file_issues = 0

        print(f"{Colors.TEXT}Checking: {Colors.SAPPHIRE}{filepath.name}{Colors.NC}")

        # Run all checks
        file_issues += self.check_colors(filepath)
        file_issues += self.check_standards(filepath)
        file_issues += self.check_structure(filepath)

        if file_issues == 0:
            log_success("  All checks passed")
            self.passed_files += 1
            return True
        else:
            log_error(f"  Found {file_issues} issue(s)")
            self.failed_files += 1
            return False

    def scan_files(self, base_path: Path, types: List[str], recursive: bool) -> List[Path]:
        """Scan for files to check"""
        files = []

        if base_path.is_file():
            files.append(base_path)
        elif base_path.is_dir():
            for ext in types:
                ext = ext.lstrip('*.')
                pattern = f'**/*.{ext}' if recursive else f'*.{ext}'
                files.extend(base_path.glob(pattern))

        return sorted(files)

    def run(self, base_path: Path, types: List[str], recursive: bool) -> int:
        """Run style checker"""
        print()
        print(f"{Colors.MAUVE}[style]{Colors.NC} {Icons.CHART}  Helper Scripts Style Checker")
        print()
        log_info("Validating coding guidelines and theming consistency")
        print()

        files = self.scan_files(base_path, types, recursive)

        if not files:
            log_error(f"No files found matching types: {', '.join(types)}")
            return 1

        log_info(f"Checking {len(files)} file(s)")
        print()

        for filepath in files:
            self.check_file(filepath)
            self.total_files += 1
            print()

        # Print summary
        print(f"{Colors.MAUVE}Summary{Colors.NC}")
        print()
        print(f"{Colors.TEXT}Total files checked:   {Colors.NC}{Colors.SAPPHIRE}{self.total_files}{Colors.NC}")
        print(f"{Colors.GREEN}Passed:                {Colors.NC}{Colors.SAPPHIRE}{self.passed_files}{Colors.NC}")

        if self.failed_files > 0:
            print(f"{Colors.RED}Failed:                {Colors.NC}{Colors.SAPPHIRE}{self.failed_files}{Colors.NC}")

        if self.warnings > 0:
            print(f"{Colors.YELLOW}Warnings:              {Colors.NC}{Colors.SAPPHIRE}{self.warnings}{Colors.NC}")

        print()

        if self.failed_files > 0:
            log_error("Style check failed")
            return 1
        else:
            log_success("All checks passed!")
            return 0


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Style and theming checker for helper scripts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Check all shell scripts in current directory
  python3 check_style.py

  # Check specific file types
  python3 check_style.py --types sh py

  # Check files in specific directory
  python3 check_style.py --path /path/to/scripts

  # Check files recursively
  python3 check_style.py --recursive --path /path/to/project
        '''
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        default='.',
        help='Path to file or directory to check (default: current directory)'
    )

    parser.add_argument(
        '-t', '--types',
        nargs='+',
        default=['sh', 'py'],
        help='File extensions to check (default: sh py)'
    )

    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Search recursively in subdirectories'
    )

    args = parser.parse_args()

    base_path = Path(args.path)

    if not base_path.exists():
        log_error(f"Path not found: {base_path}")
        return 1

    checker = StyleChecker()
    return checker.run(base_path, args.types, args.recursive)


if __name__ == '__main__':
    sys.exit(main())
