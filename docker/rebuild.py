#!/usr/bin/env python3
"""
Rebuild Docker container (stop, rebuild image, restart)
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
    config = load_env_config(REPO_ROOT)
    container_name = config['CONTAINER_NAME']
    image_name = config['IMAGE_NAME']
    dockerfile_path = config['DOCKERFILE_PATH']

    print()
    print(f"{Colors.MAUVE}[rebuild]{Colors.NC} {Icons.HAMMER}  "
          f"Rebuilding {container_name} container...")
    print()

    dockerfile = Path(dockerfile_path)
    if not dockerfile.exists():
        log_error(f"Dockerfile not found at: {dockerfile_path}")
        sys.exit(1)

    if is_running(container_name):
        log_info("Stopping running container...")
        try:
            subprocess.run(['docker', 'stop', container_name], check=True)
            time.sleep(1)
        except subprocess.CalledProcessError:
            log_error("Failed to stop container")
            sys.exit(1)

    log_info(f"Building Docker image: {image_name}...")
    try:
        subprocess.run(
            ['docker', 'build', '-t', image_name, '.'],
            cwd=SCRIPT_DIR,
            check=True
        )
    except subprocess.CalledProcessError:
        log_error("Docker build failed")
        sys.exit(1)

    log_success("Image built successfully")

    if container_exists(container_name):
        log_info("Removing old container...")
        try:
            subprocess.run(['docker', 'rm', container_name], check=True)
        except subprocess.CalledProcessError:
            log_error("Failed to remove old container")
            sys.exit(1)

    log_info("Starting new container...")

    log_warn("Docker run command not configured in rebuild.py")
    log_info("Please customize the docker run command in this script")

    print()
    log_info(f"Image: {Colors.BLUE}{image_name}{Colors.NC}")
    log_info(f"Next: Start container with: {Colors.BLUE}./start.py"
             f"{Colors.NC}")
    print()


if __name__ == '__main__':
    main()
