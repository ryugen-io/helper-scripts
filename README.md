# Docker Helper Scripts Templates

Collection of standardized shell scripts for Docker container management.

## Features

- Catppuccin Mocha color scheme
- Nerd Font icons
- Consistent error handling with `set -e` and `set -o pipefail`
- Modular and reusable

## Scripts

### Container Management

- **start.sh** - Start a Docker container
- **stop.sh** - Stop a Docker container
- **status.sh** - Show detailed container status (health, uptime, CPU, memory, ports)
- **logs.sh** - Check container logs for errors and warnings
- **rebuild.sh** - Rebuild container image and recreate container

### Development Tools

- **lines.sh** - Count lines of code in Rust files with detailed statistics
- **lint.sh** - Lint shell scripts for common issues

### Utilities

- **fix_nerdfonts.py** - Fix Nerd Font icon encoding issues in shell scripts

## Usage

1. Copy the template scripts to your project directory
2. Customize the following variables in each script:
   - `CONTAINER_NAME` - Your container name
   - `IMAGE_NAME` - Your Docker image name (rebuild.sh)
   - `DISPLAY_NAME` - Display name for status output (status.sh)
   - `DOCKERFILE_PATH` - Path to Dockerfile (rebuild.sh)
3. Make scripts executable: `chmod +x *.sh`
4. Run the scripts: `./start.sh`, `./status.sh`, etc.

## Customization

### rebuild.sh

Add your `docker run` command in the rebuild.sh script:

```bash
docker run -d \
    --name "${CONTAINER_NAME}" \
    -p 8080:8080 \
    --restart unless-stopped \
    "${IMAGE_NAME}"
```

### logs.sh

By default, checks last 100 lines. Pass a number to check more:

```bash
./logs.sh 500  # Check last 500 lines
```

### lines.sh

By default, uses 200 line limit. Pass a number to change:

```bash
./lines.sh 150  # Set warning threshold to 150 lines
```

## Color Scheme

Uses Catppuccin Mocha palette:
- Red: Errors
- Yellow: Warnings
- Blue: Info
- Green: Success
- Mauve: Headers
- Sapphire: Highlights

## Icons

Requires a Nerd Font to display icons correctly. Icons used:
- ✓ Check
- ✗ Cross
- ⚠ Warning
- ℹ Info
-  Docker
-  Server
-  Clock
-  Memory
-  CPU
-  Network

## License

Free to use and modify.
