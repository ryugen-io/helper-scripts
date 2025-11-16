# Helper Scripts

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

### Installation

- **install.sh** - Interactive installation script for deploying scripts to projects

### Docker Container Management

- **logs.sh** - Check container logs for errors and warnings
- **rebuild.sh** - Rebuild container image and recreate container
- **start.sh** - Start a Docker container
- **status.sh** - Show detailed container status (health, uptime, CPU, memory, ports)
- **stop.sh** - Stop a Docker container

### Development Tools

- **check_style.sh** - Validate coding guidelines and theming consistency
- **lines.sh** - Count lines of code with detailed statistics
- **lint.sh** - Lint shell scripts for common issues

### Utilities

- **fix_nerdfonts.py** - Fix Nerd Font icon encoding issues in shell scripts
- **update_readme.py** - Dynamically generate README.md based on repository contents

## Customization

All scripts use:
- **Catppuccin Mocha** color palette for consistent theming
- **Nerd Font** icons (requires a Nerd Font to display correctly)
- **Set -e and -o pipefail** for proper error handling

See `THEMING.md` for detailed theming information.

## License

Free to use and modify.
