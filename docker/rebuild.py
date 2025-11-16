#!/usr/bin/env python3
"""
Rebuild Docker container (stop, rebuild image, restart)
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
IMAGE_NAME = os.getenv('IMAGE_NAME', 'your-image-name:latest')
DOCKERFILE_PATH = os.getenv('DOCKERFILE_PATH', './Dockerfile')


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


def main():
    """Main execution."""
    print()
    print(f"{Colors.MAUVE}[rebuild]{Colors.NC} {Icons.HAMMER}  "
          f"Rebuilding {CONTAINER_NAME} container...")
    print()

    dockerfile = Path(DOCKERFILE_PATH)
    if not dockerfile.exists():
        log_error(f"Dockerfile not found at: {DOCKERFILE_PATH}")
        sys.exit(1)

    if is_running(CONTAINER_NAME):
        log_info("Stopping running container...")
        try:
            subprocess.run(['docker', 'stop', CONTAINER_NAME], check=True)
            time.sleep(1)
        except subprocess.CalledProcessError:
            log_error("Failed to stop container")
            sys.exit(1)

    log_info(f"Building Docker image: {IMAGE_NAME}...")
    try:
        subprocess.run(
            ['docker', 'build', '-t', IMAGE_NAME, '.'],
            cwd=SCRIPT_DIR,
            check=True
        )
    except subprocess.CalledProcessError:
        log_error("Docker build failed")
        sys.exit(1)

    log_success("Image built successfully")

    if container_exists(CONTAINER_NAME):
        log_info("Removing old container...")
        try:
            subprocess.run(['docker', 'rm', CONTAINER_NAME], check=True)
        except subprocess.CalledProcessError:
            log_error("Failed to remove old container")
            sys.exit(1)

    log_info("Starting new container...")

    log_warn("Docker run command not configured in rebuild.py")
    log_info("Please customize the docker run command in this script")

    print()
    log_info(f"Image: {Colors.BLUE}{IMAGE_NAME}{Colors.NC}")
    log_info(f"Next: Start container with: {Colors.BLUE}./start.py"
             f"{Colors.NC}")
    print()


if __name__ == '__main__':
    main()
