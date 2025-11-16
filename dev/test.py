#!/usr/bin/env python3
"""
Simple test runner for shell scripts (bats alternative)
Temporary file - not committed to repository
"""

import subprocess
import sys
from pathlib import Path

# Add .sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT / '.sys' / 'theme'))

# Import central theme
from theme import Colors, Icons


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


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def test(self, name, func):
        """Register a test"""
        self.tests.append((name, func))

    def run_command(self, cmd, check_output=None):
        """Run a command and optionally check output"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if check_output and check_output not in result.stdout:
                return False, f"Output check failed: '{check_output}' not in output"

            return result.returncode == 0, result.stderr or result.stdout
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def run_tests(self):
        """Run all registered tests"""
        print(f"{Colors.MAUVE}[test]{Colors.NC} Running shell script tests...")
        print()

        for name, test_func in self.tests:
            try:
                success, message = test_func()
                if success:
                    print(f"{Colors.GREEN}{Icons.CHECK}  {Colors.NC}{name}")
                    self.passed += 1
                else:
                    print(f"{Colors.RED}{Icons.CROSS}  {Colors.NC}{name}")
                    if message:
                        print(f"{Colors.YELLOW}     {Colors.NC}{message}")
                    self.failed += 1
            except Exception as e:
                print(f"{Colors.RED}{Icons.CROSS}  {Colors.NC}{name}")
                print(f"{Colors.YELLOW}     {Colors.NC}Exception: {e}")
                self.failed += 1

        # Summary
        print()
        print(f"{Colors.GREEN}Summary:{Colors.NC}")
        print()
        print(f"{Colors.GREEN}  Passed:  {Colors.NC}{self.passed}")
        print(f"{Colors.RED}  Failed:  {Colors.NC}{self.failed}")
        print(f"{Colors.BLUE}  Total:   {Colors.NC}{self.passed + self.failed}")
        print()

        if self.failed == 0:
            print(f"{Colors.SAPPHIRE}  {Colors.NC}All tests passed!")
            return 0
        else:
            print(f"{Colors.RED}  {Colors.NC}{self.failed} test(s) failed")
            return 1


def main():
    runner = TestRunner()

    # lines.sh tests
    runner.test("lines.sh: syntax is valid",
                lambda: runner.run_command("bash -n lines.sh"))
    runner.test("lines.sh: is executable",
                lambda: (Path("lines.sh").stat().st_mode & 0o111 != 0, ""))
    runner.test("lines.sh: runs successfully",
                lambda: runner.run_command("./lines.sh 200"))
    runner.test("lines.sh: shows summary",
                lambda: runner.run_command("./lines.sh 200 | grep -q 'Summary:'"))
    runner.test("lines.sh: accepts custom limit",
                lambda: runner.run_command("./lines.sh 100 | grep -q 'limit: 100 lines'"))

    # lint.sh tests
    runner.test("lint.sh: syntax is valid",
                lambda: runner.run_command("bash -n lint.sh"))
    runner.test("lint.sh: is executable",
                lambda: (Path("lint.sh").stat().st_mode & 0o111 != 0, ""))

    # rebuild.sh tests
    runner.test("rebuild.sh: syntax is valid",
                lambda: runner.run_command("bash -n rebuild.sh"))
    runner.test("rebuild.sh: is executable",
                lambda: (Path("rebuild.sh").stat().st_mode & 0o111 != 0, ""))
    runner.test("rebuild.sh: shows help",
                lambda: runner.run_command("./rebuild.sh --help | grep -q 'Usage:'"))

    # start.sh tests
    runner.test("start.sh: syntax is valid",
                lambda: runner.run_command("bash -n start.sh"))
    runner.test("start.sh: is executable",
                lambda: (Path("start.sh").stat().st_mode & 0o111 != 0, ""))

    # stop.sh tests
    runner.test("stop.sh: syntax is valid",
                lambda: runner.run_command("bash -n stop.sh"))
    runner.test("stop.sh: is executable",
                lambda: (Path("stop.sh").stat().st_mode & 0o111 != 0, ""))

    # General tests
    def check_shebangs():
        for script in Path.cwd().glob("*.sh"):
            with open(script) as f:
                if not f.readline().startswith("#!"):
                    return False, f"{script.name} missing shebang"
        return True, ""

    def check_set_e():
        for script in Path.cwd().glob("*.sh"):
            content = script.read_text()
            if "set -e" not in content and "set -o errexit" not in content:
                return False, f"{script.name} missing set -e"
        return True, ""

    runner.test("all scripts have proper shebangs", check_shebangs)
    runner.test("all scripts use set -e", check_set_e)

    return runner.run_tests()


if __name__ == '__main__':
    sys.exit(main())
