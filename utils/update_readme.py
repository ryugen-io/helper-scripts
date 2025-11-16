#!/usr/bin/env python3
"""
Dynamic README Generator
Scans the repository and generates a clean README with current script listings
"""

import os
from pathlib import Path
from typing import Dict, List

# Catppuccin Mocha color palette
class Colors:
    RED = '\033[38;2;243;139;168m'        # #f38ba8 - Errors
    GREEN = '\033[38;2;166;227;161m'      # #a6e3a1 - Success
    BLUE = '\033[38;2;137;180;250m'       # #89b4fa - Info
    MAUVE = '\033[38;2;203;166;247m'      # #cba6f7 - Headers
    NC = '\033[0m'                         # No Color

# Nerd Font Icons
CHECK = '\uf00c'   #
INFO = '\uf05a'    #

# Script descriptions
DESCRIPTIONS = {
    'docker/start.sh': 'Start a Docker container',
    'docker/stop.sh': 'Stop a Docker container',
    'docker/status.sh': 'Show detailed container status (health, uptime, CPU, memory, ports)',
    'docker/logs.sh': 'Check container logs for errors and warnings',
    'docker/rebuild.sh': 'Rebuild container image and recreate container',
    'dev/lines.sh': 'Count lines of code with detailed statistics',
    'dev/lint.sh': 'Lint shell scripts for common issues',
    'utils/fix_nerdfonts.py': 'Fix Nerd Font icon encoding issues in shell scripts',
    'utils/update_readme.py': 'Dynamically generate README.md based on repository contents',
    'install.sh': 'Interactive installation script for deploying scripts to projects',
}

# Category titles
CATEGORIES = {
    'docker': 'Docker Container Management',
    'dev': 'Development Tools',
    'utils': 'Utilities',
    'root': 'Installation',
}

def scan_scripts() -> Dict[str, List[str]]:
    """Scan repository for scripts and organize by category."""
    repo_root = Path(__file__).parent.parent
    scripts_by_category = {
        'docker': [],
        'dev': [],
        'utils': [],
        'root': [],
    }

    # Scan each category directory
    for category in ['docker', 'dev', 'utils']:
        category_path = repo_root / category
        if category_path.exists():
            for file in sorted(category_path.iterdir()):
                if file.is_file() and (file.suffix in ['.sh', '.py']):
                    scripts_by_category[category].append(f"{category}/{file.name}")

    # Check for root level scripts
    for file in sorted(repo_root.iterdir()):
        if file.is_file() and file.name == 'install.sh':
            scripts_by_category['root'].append(file.name)

    return scripts_by_category

def generate_readme(scripts_by_category: Dict[str, List[str]]) -> str:
    """Generate README content."""
    readme = """# Helper Scripts

Collection of helper scripts for Docker container management, development, and utilities.

## Features

- Catppuccin Mocha color scheme
- Nerd Font icons
- Consistent error handling
- Modular and reusable
- Clean, minimal design

## Quick Start

Use the installation script to deploy scripts to your project:

```bash
./install.sh
```

The script will:
- Ask for your project directory
- Let you select which scripts to install
- Automatically customize variables (container name, image name, etc.)
- Make scripts executable

## Scripts

"""

    # Add scripts by category
    for category_key in ['root', 'docker', 'dev', 'utils']:
        scripts = scripts_by_category.get(category_key, [])
        if not scripts:
            continue

        category_title = CATEGORIES.get(category_key, category_key.title())
        readme += f"### {category_title}\n\n"

        for script in scripts:
            description = DESCRIPTIONS.get(script, 'Script')
            script_name = os.path.basename(script)
            readme += f"- **{script_name}** - {description}\n"

        readme += "\n"

    # Add footer
    readme += """## Customization

All scripts use:
- **Catppuccin Mocha** color palette for consistent theming
- **Nerd Font** icons (requires a Nerd Font to display correctly)
- **Set -e and -o pipefail** for proper error handling

See `THEMING.md` for detailed theming information.

## License

Free to use and modify.
"""

    return readme

def main():
    """Main function."""
    print(f"{Colors.BLUE}{INFO}{Colors.NC}  Scanning repository for scripts...")

    scripts_by_category = scan_scripts()

    total_scripts = sum(len(scripts) for scripts in scripts_by_category.values())
    print(f"{Colors.GREEN}{CHECK}{Colors.NC}  Found {total_scripts} scripts")

    print(f"{Colors.BLUE}{INFO}{Colors.NC}  Generating README.md...")

    readme_content = generate_readme(scripts_by_category)

    # Write README
    repo_root = Path(__file__).parent.parent
    readme_path = repo_root / 'README.md'

    with open(readme_path, 'w') as f:
        f.write(readme_content)

    print(f"{Colors.GREEN}{CHECK}{Colors.NC}  README.md updated successfully")

if __name__ == '__main__':
    main()
