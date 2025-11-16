#!/usr/bin/env python3
"""
Start Docker container
"""

import sys
import subprocess
import time
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT / '.sys' / 'theme'))

from theme import (  # noqa: E402
    Colors, Icons, log_success, log_error, log_warn, log_info
)


def load_env():
    """Load environment variables from .sys/env/.env."""
    env_file = REPO_ROOT / '.sys' / 'env' / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value)


load_env()
CONTAINER_NAME = os.getenv('CONTAINER_NAME', 'your-container-name')


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


def is_running(name: str) -> bool:
    """Check if container is running."""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', f'name=^{name}$',
             '--filter', 'status=running'],
            capture_output=True,
            text=True,
            check=True
        )
        return name in result.stdout
    except subprocess.CalledProcessError:
        return False


def main():
    """Main execution function."""
    print()
    print(f"{Colors.MAUVE}[start]{Colors.NC} {Icons.DOCKER}  "
          f"Starting {CONTAINER_NAME} container...")
    print()

    if not container_exists(CONTAINER_NAME):
        log_error(f"Container '{CONTAINER_NAME}' not found")
        sys.exit(1)

    if is_running(CONTAINER_NAME):
        log_warn("Container already running")
        print()
        sys.exit(0)

    log_info("Starting container...")
    try:
        subprocess.run(['docker', 'start', CONTAINER_NAME], check=True)
    except subprocess.CalledProcessError:
        log_error(f"Failed to start {CONTAINER_NAME} container")
        sys.exit(1)

    time.sleep(2)

    if is_running(CONTAINER_NAME):
        print()
        log_success(f"{CONTAINER_NAME} container is running")
        print()
        log_info(f"Status: {Colors.BLUE}./status.py{Colors.NC}")
        log_info(f"Logs: {Colors.BLUE}docker logs -f {CONTAINER_NAME}"
                 f"{Colors.NC}")
        log_info(f"Stop: {Colors.BLUE}./stop.py{Colors.NC}")
    else:
        print()
        log_error(f"Failed to start {CONTAINER_NAME} container")
        log_info(f"Check logs with: docker logs {CONTAINER_NAME}")
        sys.exit(1)

    print()
    print(f" {Colors.GREEN}{Icons.PLAY}{Colors.NC}  Done.")
    print()


if __name__ == '__main__':
    main()
