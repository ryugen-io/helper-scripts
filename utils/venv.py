#!/usr/bin/env python3
"""
Python virtual environment creator - creates and configures Python venvs
Interactive venv creation with customizable name and location
"""

import os
import sys
import subprocess
from pathlib import Path

# Add sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_ROOT / 'sys' / 'theme'))

from theme import (  # noqa: E402
    Colors, Icons, log_success, log_error, log_warn, log_info
)


def load_env_config(repo_root: Path) -> dict:
    """Load configuration from sys/env/.env.dev file"""
    env_file = repo_root / 'sys' / 'env' / '.env.dev'

    if not env_file.exists():
        raise FileNotFoundError(f"config not found: {env_file}")

    config = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip('"').strip("'")
                config[key] = value

    return config


class VenvCreator:
    def __init__(self):
        self.config = load_env_config(REPO_ROOT)

    def prompt_venv_name(self) -> str:
        """Prompt user for venv name"""
        print()
        print(f"{Colors.TEXT}Enter virtual environment name {Colors.SUBTEXT}(default: .venv){Colors.NC}")
        print(f"{Colors.SAPPHIRE}❯{Colors.NC} ", end='', flush=True)

        try:
            name = input().strip()
            return name if name else '.venv'
        except (KeyboardInterrupt, EOFError):
            print()
            log_warn("Cancelled by user")
            sys.exit(0)

    def create_venv(self, target_dir: Path, venv_name: str, interactive: bool) -> int:
        """Create virtual environment"""
        print()
        print(f"{Colors.MAUVE}[venv]{Colors.NC} {Icons.ROCKET}  python virtual environment creator")
        print()

        # Prompt for name if interactive and no name provided
        if interactive and venv_name == '.venv':
            venv_name = self.prompt_venv_name()

        venv_path = target_dir / venv_name

        # Check if venv already exists
        if venv_path.exists():
            log_error(f"Virtual environment already exists: {venv_path}")
            log_info("Remove it first or choose a different name")
            return 1

        # Display target information
        print(f"{Colors.TEXT}Target directory:      {Colors.NC}{Colors.SAPPHIRE}{target_dir.resolve()}{Colors.NC}")
        print(f"{Colors.TEXT}Virtual env name:      {Colors.NC}{Colors.SAPPHIRE}{venv_name}{Colors.NC}")
        print(f"{Colors.TEXT}Full path:             {Colors.NC}{Colors.SAPPHIRE}{venv_path.resolve()}{Colors.NC}")
        print()

        # Create venv
        log_info(f"Creating virtual environment...")
        print()

        try:
            # Run python3 -m venv
            result = subprocess.run(
                [sys.executable, '-m', 'venv', str(venv_path)],
                capture_output=True,
                text=True,
                check=True
            )

            # Success
            print()
            log_success("virtual environment created")
            print()

            # Update .env if custom venv name
            self._update_env_config(venv_name)

            # Show activation instructions
            self._show_activation_info(venv_path, venv_name)

            return 0

        except subprocess.CalledProcessError as e:
            print()
            log_error(f"Failed to create virtual environment")
            if e.stderr:
                print(f"{Colors.RED}{e.stderr.strip()}{Colors.NC}")
            return 1
        except Exception as e:
            print()
            log_error(f"Unexpected error: {e}")
            return 1

    def _update_env_config(self, venv_name: str) -> None:
        """Update .env file with new venv name if it's not the default"""
        if venv_name == '.venv':
            return

        env_file = REPO_ROOT / self.config['SYS_DIR'] / 'env' / '.env'
