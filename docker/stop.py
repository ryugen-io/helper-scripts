#!/usr/bin/env python3
"""
Stop Docker container
"""

import sys
import subprocess
import time
from pathlib import Path

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
    config = load_env_config(REPO_ROOT)
    container_name = config['CONTAINER_NAME']

    print()
    print(f"{Colors.MAUVE}[stop]{Colors.NC} {Icons.DOCKER}  "
          f"Stopping {container_name} container...")
    print()

    if not is_running(container_name):
        log_warn(f"No running {container_name} container found")
        print()
        sys.exit(0)

    log_info("Stopping container...")
    try:
        subprocess.run(['docker', 'stop', container_name], check=True)
    except subprocess.CalledProcessError:
        log_error("Failed to stop container")
        sys.exit(1)

    time.sleep(1)

    if is_running(container_name):
        log_warn("Container may still be running")
        log_info(f"Check with: docker ps | grep {container_name}")
    else:
        print()
        log_success(f"{container_name} container stopped successfully")

    print()
    print(f" {Colors.RED}{Icons.STOP}{Colors.NC}  Done.")
    print()


if __name__ == '__main__':
    main()
