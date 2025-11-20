#!/usr/bin/env python3
"""
Temporary shell script linter (Python-based)
Tests shell scripts for common issues
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Add sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))

# Import central theme
from theme import Colors, Icons


def load_env_config(repo_root: Path) -> dict:
    """Load configuration from .env file"""
    config = {
        'SYS_DIR': 'sys',
        'GITHUB_DIR': '.github',
        'SCRIPT_DIRS': 'docker,dev,utils'
    }

    # Try sys/env/.env first, fallback to sys/env/.env.example
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


class ShellLinter:
    def __init__(self, script_path: Path):
        self.path = script_path
        self.content = script_path.read_text()
        self.lines = self.content.splitlines()
        self.issues = []
        self.warnings = []

    def check_syntax(self) -> bool:
        """Run bash syntax check"""
        result = subprocess.run(
            ['bash', '-n', str(self.path)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            self.issues.append(f"Syntax error: {result.stderr.strip()}")
            return False
        return True

    def check_shebang(self) -> bool:
        """Check for proper shebang"""
        if not self.lines or not self.lines[0].startswith('#!'):
            self.issues.append("Missing shebang line")
            return False
        if 'bash' not in self.lines[0]:
            self.warnings.append(f"Shebang might not be bash: {self.lines[0]}")
        return True

    def check_set_flags(self):
        """Check for set -e and set -o pipefail"""
        has_errexit = any(
            re.search(r'\bset\s+-[^ ]*e', line) or 'set -o errexit' in line
            for line in self.lines
        )
        has_pipefail = any('set -o pipefail' in line for line in self.lines)

        if not has_errexit:
            self.warnings.append("Missing 'set -e' or 'set -o errexit'")
        if not has_pipefail:
            self.warnings.append("Missing 'set -o pipefail'")

    def check_unquoted_variables(self):
        """Check for potentially unquoted variables"""
        unquoted_pattern = re.compile(r'\$[A-Za-z_][A-Za-z0-9_]*(?![}"])')

        for i, line in enumerate(self.lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue

            # Look for unquoted variables not in quotes
            if unquoted_pattern.search(line):
                # Basic check - might have false positives
                if '"' not in line and "'" not in line:
                    self.warnings.append(
                        f"Line {i}: Potentially unquoted variable: {line.strip()[:50]}"
                    )

    def check_executable(self) -> bool:
        """Check if script is executable"""
        if not self.path.stat().st_mode & 0o111:
            self.warnings.append("Script is not executable")
            return False
        return True

    def check_readonly_usage(self):
        """Check if readonly is used for constants"""
        const_pattern = re.compile(r'^readonly\s+[A-Z_][A-Z0-9_]*=')
        has_readonly = any(const_pattern.match(line.strip()) for line in self.lines)

        # Check for uppercase variables that might be constants
        uppercase_vars = re.findall(r'^([A-Z_][A-Z0-9_]*)=', '\n'.join(self.lines), re.MULTILINE)

        if uppercase_vars and not has_readonly:
            self.warnings.append("Uppercase variables found but not marked 'readonly'")

    def check_function_locals(self):
        """Check if functions use local variables"""
        in_function = False
        has_local = False
        has_variable_assignment = False
        function_lines = 0

        for line in self.lines:
            if re.match(r'^\s*(function\s+\w+|[a-z_][a-z0-9_]*\(\s*\)\s*{)', line):
                in_function = True
                has_local = False
                has_variable_assignment = False
                function_lines = 0
            elif in_function and line.strip() == '}':
                # Only warn if function assigns variables but doesn't use local
                # Skip simple one-liner functions (like logging functions)
                if has_variable_assignment and not has_local and function_lines > 2:
                    self.warnings.append("Function assigns variables without 'local'")
                in_function = False
            elif in_function:
                function_lines += 1
                if re.search(r'\blocal\b', line):
                    has_local = True
                # Check for variable assignments (but not $var or readonly)
                if re.search(r'^\s*[a-z_][a-z0-9_]*=', line) and not re.search(r'^\s*readonly\b', line):
                    has_variable_assignment = True

    def lint(self) -> Tuple[int, int]:
        """Run all checks"""
        self.check_syntax()
        self.check_shebang()
        self.check_set_flags()
        self.check_executable()
        self.check_readonly_usage()
        self.check_function_locals()
        # self.check_unquoted_variables()  # Too many false positives

        return len(self.issues), len(self.warnings)


def main():
    print(f"{Colors.MAUVE}[lint]{Colors.NC} Linting shell scripts with Python...")
    print()

    script_dir = Path.cwd()
    shell_scripts = sorted(script_dir.glob('*.sh'))

    total_issues = 0
    total_warnings = 0
    passed = 0

    for script in shell_scripts:
        print(f"{Colors.BLUE}Checking {Colors.NC}{script.name}")

        linter = ShellLinter(script)
        issues, warnings = linter.lint()

        # Print issues
        for issue in linter.issues:
            print(f"  {Colors.RED}{Icons.CROSS}  {Colors.NC}{issue}")
            total_issues += 1

        # Print warnings
        for warning in linter.warnings:
            print(f"  {Colors.YELLOW}{Icons.WARN}  {Colors.NC}{warning}")
            total_warnings += 1

        if not linter.issues and not linter.warnings:
            print(f"  {Colors.GREEN}{Icons.CHECK}  {Colors.NC}Perfect! No issues found")
            passed += 1
        elif not linter.issues:
            print(f"  {Colors.GREEN}{Icons.CHECK}  {Colors.NC}No critical issues")
            passed += 1

        print()

    # Summary
    print(f"{Colors.GREEN}Summary:{Colors.NC}")
    print()
    print(f"{Colors.BLUE}  Total scripts:     {Colors.NC}{len(shell_scripts)}")
    print(f"{Colors.GREEN}  Passed:            {Colors.NC}{passed}")
    print(f"{Colors.RED}  Critical issues:   {Colors.NC}{total_issues}")
    print(f"{Colors.YELLOW}  Warnings:          {Colors.NC}{total_warnings}")
    print()

    if total_issues == 0:
        print(f"{Colors.SAPPHIRE}  {Colors.NC}All shell scripts passed linting!")
        return 0
    else:
        print(f"{Colors.RED}  {Colors.NC}Some scripts have critical issues")
        return 1


if __name__ == '__main__':
    sys.exit(main())
