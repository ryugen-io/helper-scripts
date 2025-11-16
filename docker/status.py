#!/usr/bin/env python3
"""
Check the current status and stats of Docker container
"""

import sys
import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT / '.sys' / 'theme'))

from theme import (  # noqa: E402
    Colors, Icons, log_success, log_error, log_info
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
DISPLAY_NAME = os.getenv('DISPLAY_NAME', 'Your Service')


def log_stat(icon: str, label: str, value: str, color: str):
    """Log a statistic line."""
    print(f"{Colors.SUBTEXT}{icon:2}  {label:16}{Colors.NC} "
          f"{color}{value}{Colors.NC}")


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


def get_container_info(name: str) -> dict:
    """Get container information."""
    try:
        result = subprocess.run(
            ['docker', 'inspect', name],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        return data[0] if data else {}
    except (subprocess.CalledProcessError, json.JSONDecodeError, IndexError):
        return {}


def show_container_status(name: str, display_name: str, icon: str):
    """Show detailed container status."""
    print(f"{Colors.MAUVE}{icon}  {display_name}{Colors.NC}")
    print()

    if not container_exists(name):
        log_error(f"Container not found: {name}")
        print()
        return False

    info = get_container_info(name)
    if not info:
        log_error("Failed to get container info")
        print()
        return False

    state = info.get('State', {})
    status = state.get('Status', 'unknown')
    health_info = state.get('Health', {})
    health = health_info.get('Status', 'none')

    if status == 'running':
        log_stat(Icons.STATUS, "Status:", status, Colors.GREEN)
    else:
        log_stat(Icons.STATUS, "Status:", status, Colors.RED)

    if health != 'none':
        if health == 'healthy':
            log_stat(Icons.CHECK, "Health:", health, Colors.GREEN)
        elif health == 'unhealthy':
            log_stat(Icons.CROSS, "Health:", health, Colors.RED)
        else:
            log_stat(Icons.WARN, "Health:", health, Colors.YELLOW)

    if status == 'running':
        started_str = state.get('StartedAt', '')
        if started_str:
            try:
                started = datetime.fromisoformat(
                    started_str.replace('Z', '+00:00')
                )
                now = datetime.now(started.tzinfo)
                diff = int((now - started).total_seconds())

                days = diff // 86400
                hours = (diff % 86400) // 3600
                mins = (diff % 3600) // 60

                if days > 0:
                    uptime = f"{days}d {hours}h {mins}m"
                elif hours > 0:
                    uptime = f"{hours}h {mins}m"
                else:
                    uptime = f"{mins}m"

                log_stat(Icons.CLOCK, "Uptime:", uptime, Colors.GREEN)
            except Exception:
                pass

        try:
            result = subprocess.run(
                ['docker', 'stats', '--no-stream',
                 '--format', '{{.MemUsage}}|{{.CPUPerc}}', name],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                parts = result.stdout.strip().split('|')
                if len(parts) == 2:
                    log_stat(Icons.MEM, "Memory:", parts[0], Colors.YELLOW)
                    log_stat(Icons.CPU, "CPU:", parts[1], Colors.BLUE)
        except subprocess.CalledProcessError:
            pass

        try:
            result = subprocess.run(
                ['docker', 'port', name],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                print(f"{Colors.SUBTEXT}{Icons.NET}  Ports:{Colors.NC}")
                for line in result.stdout.strip().split('\n'):
                    line = line.replace('0.0.0.0:', '')
                    print(f"{Colors.SAPPHIRE}                    {line}"
                          f"{Colors.NC}")
        except subprocess.CalledProcessError:
            pass

    print()
    return True


def main():
    """Main execution."""
    print(f"{Colors.MAUVE}[status]{Colors.NC} {Icons.DOCKER}  "
          f"Checking {CONTAINER_NAME} container status...")
    print()

    if not container_exists(CONTAINER_NAME):
        log_error(f"{CONTAINER_NAME} container not found")
        print()
        sys.exit(1)

    show_container_status(CONTAINER_NAME, DISPLAY_NAME, Icons.SERVER)

    if is_running(CONTAINER_NAME):
        log_success("Container is running")
    else:
        log_error("Container is not running")
        print()
        log_info(f"Start container with: {Colors.BLUE}./start.py{Colors.NC}")

    print()


if __name__ == '__main__':
    main()
