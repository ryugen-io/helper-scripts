#!/usr/bin/env python3
"""
Python virtual environment creator - creates and configures Python venvs
Interactive venv creation with customizable name and location
"""

import os
import sys
import subprocess
from pathlib import Path

# Add .sys/theme to path for central theming
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
        print(f"{Colors.MAUVE}[venv]{Colors.NC} {Icons.ROCKET}  Python Virtual Environment Creator")
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
            log_success(f"Virtual environment created successfully")
            print()

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

    def _show_activation_info(self, venv_path: Path, venv_name: str) -> None:
        """Show activation instructions"""
        print(f"{Colors.MAUVE}Activation{Colors.NC}")
        print()

        # Detect shell and show appropriate command
        shell = Path(os.environ.get('SHELL', '/bin/bash')).name

        if shell == 'fish':
            activate_cmd = f"source {venv_name}/bin/activate.fish"
        elif shell in ['zsh', 'bash', 'sh']:
            activate_cmd = f"source {venv_name}/bin/activate"
        else:
            activate_cmd = f"source {venv_name}/bin/activate"

        print(f"{Colors.TEXT}Activate:              {Colors.NC}{Colors.SAPPHIRE}{activate_cmd}{Colors.NC}")
        print(f"{Colors.TEXT}Deactivate:            {Colors.NC}{Colors.SAPPHIRE}deactivate{Colors.NC}")
        print()

        # Additional info
        print(f"{Colors.MAUVE}Next Steps{Colors.NC}")
        print()
        print(f"{Colors.TEXT}1. Activate the venv:  {Colors.NC}{Colors.SAPPHIRE}{activate_cmd}{Colors.NC}")
        print(f"{Colors.TEXT}2. Upgrade pip:        {Colors.NC}{Colors.SAPPHIRE}pip install --upgrade pip{Colors.NC}")
        print(f"{Colors.TEXT}3. Install packages:   {Colors.NC}{Colors.SAPPHIRE}pip install <package>{Colors.NC}")
        print()


def main():
    """Main function"""
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description='Python virtual environment creator - creates and configures Python venvs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Create .venv in current directory (interactive)
  python3 venv.py

  # Create venv with specific name
  python3 venv.py --name myenv

  # Create venv in specific directory
  python3 venv.py --path /path/to/project

  # Create venv with name and path
  python3 venv.py --path /path/to/project --name myenv

  # Non-interactive mode (uses default .venv)
  python3 venv.py --no-interactive
        '''
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        default='.',
        help='Target directory for venv creation (default: current directory)'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        default='.venv',
        help='Virtual environment name (default: .venv)'
    )

    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Non-interactive mode - use defaults without prompting'
    )

    args = parser.parse_args()

    target_dir = Path(args.path)

    # Validate target directory
    if not target_dir.exists():
        log_error(f"Target directory not found: {target_dir}")
        return 1

    if not target_dir.is_dir():
        log_error(f"Target path is not a directory: {target_dir}")
        return 1

    creator = VenvCreator()
    return creator.create_venv(target_dir, args.name, not args.no_interactive)


if __name__ == '__main__':
    sys.exit(main())
