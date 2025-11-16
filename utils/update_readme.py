#!/usr/bin/env python3
"""
Simple README Generator - Lists all project files as links
"""

import os
from pathlib import Path

def load_env_config(repo_root: Path) -> dict:
    """Load configuration from .env file."""
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

def scan_files() -> list:
    """Scan repository for all files."""
    repo_root = Path(__file__).parent.parent
    config = load_env_config(repo_root)
    files = []

    # Script directories from configuration
    script_dirs = config['SCRIPT_DIRS'].split(',')
    for directory in script_dirs:
        directory = directory.strip()
        dir_path = repo_root / directory
        if dir_path.exists():
            for file in sorted(dir_path.iterdir()):
                if file.is_file():
                    files.append(f"{directory}/{file.name}")

    # System directory (.sys)
    sys_dir = repo_root / config['SYS_DIR']
    if sys_dir.exists():
        for file in sorted(sys_dir.iterdir()):
            if file.is_file():
                files.append(f"{config['SYS_DIR']}/{file.name}")

    # GitHub skip system directory (.github/skips)
    github_skips = repo_root / config['GITHUB_DIR'] / 'skips'
    if github_skips.exists():
        for file in sorted(github_skips.iterdir()):
            if file.is_file():
                files.append(f"{config['GITHUB_DIR']}/skips/{file.name}")

    # Root level files
    for file in sorted(repo_root.iterdir()):
        if file.is_file() and file.suffix in ['.sh', '.md', '.py']:
            if file.name != 'README.md':  # Don't include the README itself
                files.append(file.name)

    return sorted(files)

def generate_readme(files: list) -> str:
    """Generate README with file links."""
    readme = "# Helper Scripts\n\n"

    for file in files:
        readme += f"- [{file}]({file})\n"

    return readme

def main():
    """Main function."""
    files = scan_files()
    readme_content = generate_readme(files)

    # Write README
    repo_root = Path(__file__).parent.parent
    readme_path = repo_root / 'README.md'

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    print(f"README.md updated with {len(files)} files")

if __name__ == '__main__':
    main()
