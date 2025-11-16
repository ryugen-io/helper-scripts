#!/usr/bin/env python3
"""
Stop Docker container
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
    """Main execution."""
    print()
    print(f"{Colors.MAUVE}[stop]{Colors.NC} {Icons.DOCKER}  "
          f"Stopping {CONTAINER_NAME} container...")
    print()

    if not is_running(CONTAINER_NAME):
        log_warn(f"No running {CONTAINER_NAME} container found")
        print()
        sys.exit(0)

    log_info("Stopping container...")
    try:
        subprocess.run(['docker', 'stop', CONTAINER_NAME], check=True)
    except subprocess.CalledProcessError:
        log_error("Failed to stop container")
        sys.exit(1)

    time.sleep(1)

    if is_running(CONTAINER_NAME):
        log_warn("Container may still be running")
        log_info(f"Check with: docker ps | grep {CONTAINER_NAME}")
    else:
        print()
        log_success(f"{CONTAINER_NAME} container stopped successfully")

    print()
    print(f" {Colors.RED}{Icons.STOP}{Colors.NC}  Done.")
    print()


if __name__ == '__main__':
    main()
