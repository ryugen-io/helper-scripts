#!/usr/bin/env python3
"""
Check container logs for errors and warnings
"""

import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))

from theme import (  # noqa: E402
    Colors, Icons, log_success, log_error, log_warn, log_info
)


def load_env_config(repo_root: Path) -> dict:
    """Load configuration from .env file"""
    config = {
        'SYS_DIR': 'sys',
        'GITHUB_DIR': '.github',
        'SCRIPT_DIRS': 'docker,dev,utils,rust',
        'CONTAINER_NAME': 'your-container-name',
        'IMAGE_NAME': 'your-image-name:latest',
        'DISPLAY_NAME': 'Your Service',
        'DOCKERFILE_PATH': './Dockerfile'
    }

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


def container_exists(name: str) -> bool:
    """Check if container exists."""
    try:
        result = subprocess.run(
            ['docker', 'ps', '-a', '--filter', f'name=^{name}$',
             '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            check=True
        )
        return name in result.stdout
    except subprocess.CalledProcessError:
        return False


def get_logs(name: str, lines: int) -> str:
    """Get container logs."""
    try:
        result = subprocess.run(
            ['docker', 'logs', '--tail', str(lines), name],
            capture_output=True,
            text=True,
            stderr=subprocess.STDOUT
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def main():
    """Main execution."""
    config = load_env_config(REPO_ROOT)
    container_name = config['CONTAINER_NAME']

    lines = int(sys.argv[1]) if len(sys.argv) > 1 else 100

    print()
    print(f"{Colors.MAUVE}[logs]{Colors.NC} {Icons.LOG}  "
          f"Checking {container_name} logs (last {lines} lines)...")
    print()

    if not container_exists(container_name):
        log_error(f"Container '{container_name}' not found")
        sys.exit(1)

    logs = get_logs(container_name, lines)

    error_lines = [line for line in logs.split('\n') if 'ERROR' in line]
    warn_lines = [line for line in logs.split('\n') if 'WARN' in line]

    error_count = len(error_lines)
    warn_count = len(warn_lines)

    print(f"{Colors.MAUVE}{Icons.INFO}  Summary{Colors.NC}")
    print()
    print(f"{Colors.SUBTEXT}  Lines checked:{Colors.NC}  "
          f"{Colors.BLUE}{lines}{Colors.NC}")
    print(f"{Colors.SUBTEXT}  Errors found:{Colors.NC}   "
          f"{Colors.RED}{error_count}{Colors.NC}")
    print(f"{Colors.SUBTEXT}  Warnings found:{Colors.NC} "
          f"{Colors.YELLOW}{warn_count}{Colors.NC}")
    print()

    if error_count > 0:
        print(f"{Colors.RED}{Icons.CROSS}  Errors:{Colors.NC}")
        print()
        for line in error_lines:
            print(f"{Colors.SUBTEXT}  {Colors.RED}{line}{Colors.NC}")
        print()

    if warn_count > 0:
        print(f"{Colors.YELLOW}{Icons.WARN}  Warnings:{Colors.NC}")
        print()
        for line in warn_lines:
            print(f"{Colors.SUBTEXT}  {Colors.YELLOW}{line}{Colors.NC}")
        print()

    if error_count == 0 and warn_count == 0:
        log_success("No errors or warnings found")
    elif error_count > 0:
        log_error(f"Found {error_count} errors and {warn_count} warnings")
    else:
        log_warn(f"Found {warn_count} warnings")

    print()
    log_info(f"View full logs: {Colors.BLUE}docker logs {container_name}"
             f"{Colors.NC}")
    log_info(f"Follow logs: {Colors.BLUE}docker logs -f {container_name}"
             f"{Colors.NC}")
    print()


if __name__ == '__main__':
    main()
