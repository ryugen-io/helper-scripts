#!/usr/bin/env python3
"""
Start Docker container
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
    config = load_env_config(REPO_ROOT)
    container_name = config['CONTAINER_NAME']

    print()
    print(f"{Colors.MAUVE}[start]{Colors.NC} {Icons.DOCKER}  "
          f"Starting {container_name} container...")
    print()

    if not container_exists(container_name):
        log_error(f"Container '{container_name}' not found")
        sys.exit(1)

    if is_running(container_name):
        log_warn("Container already running")
        print()
        sys.exit(0)

    log_info("Starting container...")
    try:
        subprocess.run(['docker', 'start', container_name], check=True)
    except subprocess.CalledProcessError:
        log_error(f"Failed to start {container_name} container")
        sys.exit(1)

    time.sleep(2)

    if is_running(container_name):
        print()
        log_success(f"{container_name} container is running")
        print()
        log_info(f"Status: {Colors.BLUE}./status.py{Colors.NC}")
        log_info(f"Logs: {Colors.BLUE}docker logs -f {container_name}"
                 f"{Colors.NC}")
        log_info(f"Stop: {Colors.BLUE}./stop.py{Colors.NC}")
    else:
        print()
        log_error(f"Failed to start {container_name} container")
        log_info(f"Check logs with: docker logs {container_name}")
        sys.exit(1)

    print()
    print(f" {Colors.GREEN}{Icons.PLAY}{Colors.NC}  Done.")
    print()


if __name__ == '__main__':
    main()
