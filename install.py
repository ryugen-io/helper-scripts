#!/usr/bin/env python3
"""
Interactive installation script for helper scripts
Copies scripts and customizes them for a new project
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / 'sys' / 'theme'))

from theme import (  # noqa: E402
    Colors, Icons, log_success, log_error, log_warn, log_info, log_header
)


class Config:
    """Configuration class for environment variables."""
    def __init__(self):
        self.sys_dir = 'sys'
        self.github_dir = '.github'
        self.load_env()

    def load_env(self):
        """Load environment configuration from sys/env/.env."""
        env_path = SCRIPT_DIR / self.sys_dir / 'env' / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        setattr(self, key.lower(), value)


def prompt(prompt_text: str, default_value: str = "") -> str:
    """Prompt user for input with optional default value."""
    if default_value:
        print(f"{Colors.BLUE}{Icons.QUESTION}  {Colors.TEXT}{prompt_text}{Colors.NC} {Colors.SUBTEXT}[{default_value}]{Colors.NC}")
    else:
        print(f"{Colors.BLUE}{Icons.QUESTION}  {Colors.TEXT}{prompt_text}{Colors.NC}")

    user_input = input("   > ").strip()
    return user_input if user_input else default_value


def prompt_yes_no(prompt_text: str, default: str = "y") -> bool:
    """Prompt user for yes/no response."""
    suffix = f"{Colors.SUBTEXT}[Y/n]{Colors.NC}" if default == "y" else f"{Colors.SUBTEXT}[y/N]{Colors.NC}"
    print(f"{Colors.BLUE}{Icons.QUESTION}  {Colors.TEXT}{prompt_text}{Colors.NC} {suffix}")

    response = input("   > ").strip().lower()
    if not response:
        response = default

    return response in ('y', 'yes')


def get_script_description(file: Path) -> str:
    """Extract description from line 2 of script file."""
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                desc = lines[1].strip()
                if desc.startswith('#') or desc.startswith('"""') or desc.startswith("'''"):
                    desc = desc.lstrip('#"\'').strip()
                    if desc:
                        return desc
        return "Script"
    except Exception:
        return "Script"


def scan_available_scripts() -> List[Tuple[str, str]]:
    """Scan directories for available scripts."""
    scripts = []

    for directory in ['docker', 'dev', 'utils']:
        dir_path = SCRIPT_DIR / directory
        if dir_path.exists():
            for script in sorted(dir_path.iterdir()):
                if script.is_file() and (script.suffix in ['.sh', '.py']):
                    relative_path = f"{directory}/{script.name}"
                    desc = get_script_description(script)
                    scripts.append((relative_path, desc))

    return scripts


def select_scripts() -> List[str]:
    """Interactive script selection."""
    log_header("Select scripts to install:")
    print()

    scripts = scan_available_scripts()

    print(f"{Colors.TEXT}Available scripts:{Colors.NC}")
    print()

    for i, (script, desc) in enumerate(scripts, 1):
        print(f"{Colors.SUBTEXT}  {i:2d}){Colors.NC} {script:30s} {Colors.SUBTEXT}{desc}{Colors.NC}")

    print()
    print(f"{Colors.TEXT}Select scripts to install:{Colors.NC}")
    print(f"{Colors.SUBTEXT}  - Enter numbers separated by spaces (e.g., 1 2 3){Colors.NC}")
    print(f"{Colors.SUBTEXT}  - Enter 'all' for all scripts{Colors.NC}")
    print(f"{Colors.SUBTEXT}  - Enter 'core' for core scripts (start, stop, status, logs){Colors.NC}")
    print()

    selection = input("   > ").strip()
    selected = []

    if selection == "all":
        selected = [script for script, _ in scripts]
    elif selection == "core":
        selected = [
            script for script, _ in scripts
            if script.startswith('docker/') and 'rebuild.sh' not in script
        ]
    else:
        for num_str in selection.split():
            try:
                num = int(num_str)
                if 1 <= num <= len(scripts):
                    selected.append(scripts[num - 1][0])
            except ValueError:
                continue

    return selected


def remove_inline_comments(file_path: Path):
    """Remove inline comments from script file."""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        cleaned_lines = []
        for line in lines:
            if line.strip().startswith('#!'):
                cleaned_lines.append(line)
            else:
                line = re.sub(r'\s*#\s+.*$', '', line)
                cleaned_lines.append(line)

        while len(cleaned_lines) > 1 and cleaned_lines[-1].strip() == '' and cleaned_lines[-2].strip() == '':
            cleaned_lines.pop()

        with open(file_path, 'w') as f:
            f.writelines(cleaned_lines)
    except Exception as e:
        log_warn(f"Could not remove comments from {file_path.name}: {e}")


def customize_script(file_path: Path, container_name: str, image_name: str,
                     display_name: str, dockerfile_path: str):
    """Customize script with user-provided values."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        replacements = {
            r'readonly CONTAINER_NAME="your-container-name"':
                f'readonly CONTAINER_NAME="{container_name}"',
            r'readonly IMAGE_NAME="your-image-name:latest"':
                f'readonly IMAGE_NAME="{image_name}"',
            r'readonly DISPLAY_NAME="Your Service"':
                f'readonly DISPLAY_NAME="{display_name}"',
            r'readonly DOCKERFILE_PATH="./Dockerfile"':
                f'readonly DOCKERFILE_PATH="{dockerfile_path}"',
        }

        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content)

        with open(file_path, 'w') as f:
            f.write(content)
    except Exception as e:
        log_warn(f"Could not customize {file_path.name}: {e}")


def deploy_theme(target_dir: Path) -> bool:
    """Deploy theme.sh to target directory."""
    log_info("Deploying theme files (required for all scripts)...")

    theme_sh = SCRIPT_DIR / 'sys' / 'theme' / 'theme.sh'
    theme_py = SCRIPT_DIR / 'sys' / 'theme' / 'theme.py'

    success = True

    if theme_sh.exists():
        target_sh = target_dir / 'theme.sh'
        try:
            target_sh.write_text(theme_sh.read_text())
            target_sh.chmod(0o755)
            log_success("  Deployed: theme.sh")
        except Exception as e:
            log_warn(f"  Failed to deploy theme.sh: {e}")
            success = False
    else:
        log_warn("  theme.sh not found - Bash scripts will use inline colors")
        success = False

    if theme_py.exists():
        target_py = target_dir / 'theme.py'
        try:
            target_py.write_text(theme_py.read_text())
            target_py.chmod(0o755)
            log_success("  Deployed: theme.py")
        except Exception as e:
            log_warn(f"  Failed to deploy theme.py: {e}")
            success = False
    else:
        log_warn("  theme.py not found - Python scripts will use inline colors")

    print()
    return success


def main():
    """Main installation function."""
    print()
    log_header(f"{Colors.MAUVE}[install]{Colors.NC} {Icons.ROCKET}  Helper Scripts Installation")
    print()

    _ = Config()

    log_header("Configuration")
    print()

    target_dir_str = prompt("Target directory for installation", ".")
    target_dir = Path(target_dir_str).resolve()

    if not target_dir.exists():
        if prompt_yes_no("Directory doesn't exist. Create it?", "y"):
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                log_success(f"Directory created: {target_dir}")
            except Exception as e:
                log_error(f"Failed to create directory: {e}")
                sys.exit(1)
        else:
            log_error("Installation cancelled")
            sys.exit(1)

    print()

    container_name = prompt("Container name", "")
    if not container_name:
        log_error("Container name is required")
        sys.exit(1)

    image_name = prompt("Docker image name", f"{container_name}:latest")
    display_name = prompt("Display name for status output", container_name)
    dockerfile_path = prompt("Path to Dockerfile", "./Dockerfile")

    print()

    selected_scripts = select_scripts()
    if not selected_scripts:
        log_error("No scripts selected")
        sys.exit(1)

    print()
    log_header("Summary")
    print()
    print(f"{Colors.TEXT}Target directory:{Colors.NC}  {Colors.SAPPHIRE}{target_dir}{Colors.NC}")
    print(f"{Colors.TEXT}Container name:{Colors.NC}    {Colors.SAPPHIRE}{container_name}{Colors.NC}")
    print(f"{Colors.TEXT}Image name:{Colors.NC}        {Colors.SAPPHIRE}{image_name}{Colors.NC}")
    print(f"{Colors.TEXT}Display name:{Colors.NC}      {Colors.SAPPHIRE}{display_name}{Colors.NC}")
    print(f"{Colors.TEXT}Dockerfile path:{Colors.NC}   {Colors.SAPPHIRE}{dockerfile_path}{Colors.NC}")
    print()
    print(f"{Colors.TEXT}Scripts to install:{Colors.NC}")
    for script in selected_scripts:
        print(f"  {Colors.GREEN}{Icons.CHECK}{Colors.NC}  {script}")
    print()

    if not prompt_yes_no("Install these scripts?", "y"):
        log_warn("Installation cancelled")
        sys.exit(0)

    print()
    log_header("Installing...")
    print()

    deploy_theme(target_dir)

    deployed = 0
    failed = 0

    for script in selected_scripts:
        source_file = SCRIPT_DIR / script
        script_name = source_file.name
        target_file = target_dir / script_name

        if not source_file.exists():
            log_error(f"Source file not found: {script}")
            failed += 1
            continue

        if target_file.exists():
            if not prompt_yes_no(f"  File exists: {script_name}. Overwrite?", "n"):
                log_warn(f"  Skipped: {script_name}")
                continue

        try:
            target_file.write_text(source_file.read_text())

            if script_name.endswith('.sh'):
                remove_inline_comments(target_file)

            if script_name.endswith('.sh'):
                customize_script(
                    target_file, container_name, image_name,
                    display_name, dockerfile_path
                )

            target_file.chmod(0o755)

            log_success(f"  Deployed: {script_name}")
            deployed += 1
        except Exception as e:
            log_error(f"  Failed to deploy {script_name}: {e}")
            failed += 1

    print()
    log_header("Installation Complete")
    print()

    if deployed > 0:
        log_success(f"{deployed} script(s) installed successfully")

    if failed > 0:
        log_error(f"{failed} script(s) failed to install")

    print()
    log_info(f"Scripts installed to: {Colors.SAPPHIRE}{target_dir}{Colors.NC}")
    print()

    log_header("Next Steps")
    print()
    print(f"{Colors.TEXT}1. Review the installed scripts:{Colors.NC}")
    print(f"   {Colors.SUBTEXT}cd {target_dir}{Colors.NC}")
    print()
    print(f"{Colors.TEXT}2. Test the scripts:{Colors.NC}")
    print(f"   {Colors.SUBTEXT}./status.sh{Colors.NC}")
    print()
    print(f"{Colors.TEXT}3. Customize further if needed{Colors.NC}")
    print()

    if any('rebuild.sh' in s for s in selected_scripts):
        log_warn("Remember to customize the docker run command in rebuild.sh")
        print()

    log_success(f"Installation complete! {Icons.ROCKET}")
    print()


if __name__ == '__main__':
    main()
