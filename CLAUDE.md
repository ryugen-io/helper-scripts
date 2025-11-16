# CLAUDE.md - AI Assistant Guide for Helper Scripts Repository

**Last Updated:** 2025-11-16
**Repository:** ryugen-io/helper-scripts
**Purpose:** Collection of standardized shell scripts for Docker container management

---

## Table of Contents

1. [Overview](#overview)
2. [Repository Structure](#repository-structure)
3. [Theming System](#theming-system)
4. [Development Scripts](#development-scripts)
5. [Docker Management Scripts](#docker-management-scripts)
6. [Utility Scripts](#utility-scripts)
7. [GitHub Actions & CI/CD](#github-actions--cicd)
8. [Skip System](#skip-system)
9. [Installation System](#installation-system)
10. [Best Practices for AI Assistants](#best-practices-for-ai-assistants)

---

## Overview

This repository provides a collection of standardized, reusable shell scripts for Docker container management and development workflows. All scripts follow consistent conventions for:

- **Error handling**: Every script uses `set -e` and `set -o pipefail`
- **Theming**: Catppuccin Mocha color scheme with Nerd Font icons
- **Logging**: Standardized logging functions (`log_success`, `log_error`, `log_warn`, `log_info`)
- **Modularity**: Scripts can be deployed individually or as a collection

### Key Features

- Interactive installation script for easy deployment
- Centralized theming system for consistent UI/UX
- Docker container management (start, stop, status, logs, rebuild)
- Development tools (linting, formatting, line counting)
- GitHub Actions integration with Claude AI
- Secure skip system for CI/CD workflows

---

## Repository Structure

```
helper-scripts/
├── .backups/ # Timestamped backups of edited files
├── .github/ # GitHub Actions and workflows
│ ├── workflows/ # Workflow definitions
│ │ ├── claude.yml # Claude AI integration (issue/PR comments)
│ │ ├── claude-code-review.yml # Automatic PR reviews
│ │ ├── check-skip.yml # Skip system validation
│ │ ├── update-readme.yml # Auto-update README
│ │ ├── scripts/ # Workflow helper scripts
│ │ └── logs/ # Workflow execution logs (persistent)
│ └── skips/ # Skip system configuration
│ ├── .skip.example # Example skip file
│ └── SKIP_SYSTEM.md # Skip system documentation
│
├── .sys/ # System/configuration files
│ ├── env/ # Environment configuration
│ │ └── .env.example # Environment template
│ └── theme/ # Centralized theming
│ ├── theme.sh # Bash theme (colors & icons)
│ ├── theme.py # Python theme (colors & icons)
│ └── THEMING.md # Theming guide
│
├── dev/ # Development tools
│ ├── check_style.sh # Style checker
│ ├── format.sh # Code formatter
│ ├── lines.sh # Line counter (Rust-focused)
│ ├── lint.sh # Shell script linter
│ ├── shellcheck.py # Python-based shellcheck wrapper
│ ├── test.py # Test runner (Python)
│ └── test.bats # BATS test suite
│
├── docker/ # Docker container management
│ ├── start.sh # Start container
│ ├── stop.sh # Stop container
│ ├── status.sh # Show container status & stats
│ ├── logs.sh # Check logs for errors/warnings
│ └── rebuild.sh # Rebuild image & recreate container
│
├── utils/ # Utility scripts
│ ├── fix_nerdfonts.py # Fix Nerd Font icon encoding
│ ├── remove_emojis.py # Remove emojis from files
│ ├── remove_emojis.sh # Shell wrapper for emoji removal
│ └── update_readme.py # Auto-generate README
│
├── install.sh # Interactive installation script
├── README.md # User-facing documentation
├── claude.md # Generated file concatenation (lowercase)
└── CLAUDE.md # This file - AI assistant guide
```

---

## Theming System

### Centralized Theme Configuration

**Location:** `.sys/theme/theme.sh` (Bash) and `.sys/theme/theme.py` (Python)

All scripts use a **Catppuccin Mocha** color palette with **Nerd Font icons** for consistent visual output.

### Color Palette

```bash
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly SUBTEXT='\033[38;2;186;194;222m'    # #bac2de - Subtext/dimmed
readonly NC='\033[0m'                         # No Color / Reset
```

### Nerd Font Icons

```bash
readonly CHECK=""     # \uf00c - Success
readonly CROSS=""     # \uf00d - Error
readonly WARN=""      # \uf071 - Warning
readonly INFO=""      # \uf05a - Information
readonly DOCKER=""    # \uf308 - Docker
readonly ROCKET=""    # \uf135 - Deployment
readonly HAMMER=""    # \uf6e3 - Build/rebuild
readonly CHART="󰈙"    # \uf200 - Chart/statistics
readonly PLAY=""      # \uf04b - Start/play
readonly CLEAN=""     # \uf0ad - Broom/clean
```

### Standard Logging Functions

```bash
log_success() {
    echo -e "${GREEN}${CHECK}  ${NC}$1"
}

log_error() {
    echo -e "${RED}${CROSS}  ${NC}$1" >&2
}

log_warn() {
    echo -e "${YELLOW}${WARN}  ${NC}$1"
}

log_info() {
    echo -e "${BLUE}${INFO}  ${NC}$1"
}

log_header() {
    echo -e "${MAUVE}$1${NC}"
}
```

### Usage in Scripts

**Bash scripts:**
```bash
#!/bin/bash
set -e
set -o pipefail

# Source central theme
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/.sys/theme/theme.sh"

echo -e "${MAUVE}[script-name]${NC} ${ICON}  Description..."
log_success "Operation completed"
```

**Python scripts:**
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add .sys/theme to path for central theming
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(REPO_ROOT / '.sys' / 'theme'))

from theme import Colors, Icons, log_success, log_error, log_warn, log_info

# Load .env configuration
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

# Initialize config
config = load_env_config(REPO_ROOT)
```

---

## Development Scripts

Location: `dev/`

### check_style.sh
Checks code style and formatting consistency.

### format.sh
Automatically formats code files.

### lines.sh
Analyzes Rust source files and counts lines of code.

**Features:**
- Excludes comments and blank lines
- Warns when files exceed threshold (default: 200 lines)
- Shows detailed statistics (total, code, comments, blank)
- Sorts files by line count

**Usage:**
```bash
./dev/lines.sh # Use default 200 line threshold
./dev/lines.sh 150 # Use custom threshold
```

### lint.sh
Lints shell scripts for common issues.

**Checks:**
- Syntax errors (`bash -n`)
- Missing shebang
- Missing `set -e` or `set -o pipefail`
- Executable permissions

### pycompile.py
Python compilation checker - validates Python syntax by compiling to bytecode.

**Features:**
- Compiles Python files using `py_compile`
- Reports compilation errors with detailed messages
- Filters out `__pycache__` and `.mypy_cache` directories
- Color-coded output with compilation status

**Usage:**
```bash
./dev/pycompile.py                    # Check current directory
./dev/pycompile.py --path script.py   # Check specific file
./dev/pycompile.py --recursive        # Check recursively
```

### pyclean.py
Python cache cleaner - removes `__pycache__` and `.mypy_cache` directories.

**Features:**
- Scans for Python cache directories recursively
- Shows size of each cache directory
- Dry run mode to preview what would be removed
- Safe removal with error handling

**Usage:**
```bash
./dev/pyclean.py                      # Clean current directory
./dev/pyclean.py --dry-run            # Preview what would be removed
./dev/pyclean.py --path /path/to/dir  # Clean specific directory
```

### shellcheck.py
Python wrapper for advanced shellcheck integration.

### test.py & test.bats
Test runners for Python and BATS test suites.

---

## Docker Management Scripts

Location: `docker/`

All Docker scripts follow a template pattern with customizable variables:
- `CONTAINER_NAME` - Docker container name
- `IMAGE_NAME` - Docker image name (used in rebuild.sh)
- `DISPLAY_NAME` - Human-readable service name (used in status.sh)
- `DOCKERFILE_PATH` - Path to Dockerfile (used in rebuild.sh)

### start.sh
Starts a Docker container.

**Features:**
- Checks if container exists
- Detects if already running
- Provides status check commands

### stop.sh
Stops a running Docker container.

**Features:**
- Verifies container is running
- Confirms successful stop
- Safe idempotent operation

### status.sh
Shows detailed container status and statistics.

**Displays:**
- Container status (running/stopped)
- Health check status
- Uptime
- Memory usage
- CPU usage
- Port mappings

### logs.sh
Checks container logs for errors and warnings.

**Features:**
- Scans last N lines (default: 100)
- Counts ERROR and WARN occurrences
- Displays matching log entries
- Color-coded output

**Usage:**
```bash
./docker/logs.sh # Check last 100 lines
./docker/logs.sh 500 # Check last 500 lines
```

### rebuild.sh
Rebuilds Docker image and recreates container.

**Process:**
1. Stops running container
2. Builds new Docker image
3. Removes old container
4. Starts new container (requires customization)

**Note:** The `docker run` command must be customized for your specific use case.

---

## Utility Scripts

Location: `utils/`

### fix_nerdfonts.py
Fixes Nerd Font icon encoding issues in shell scripts.

**Purpose:** Replaces empty icon variable definitions with correct Unicode characters.

**Example:**
```bash
# Before
readonly CHECK=""
# After
readonly CHECK=""  # \uf00c
```

### remove_emojis.py & remove_emojis.sh
Removes emoji characters from text files.

### update_readme.py
Automatically generates README.md from script headers and file listings.

---

## GitHub Actions & CI/CD

Location: `.github/workflows/`

### claude.yml - Claude AI Integration

**Triggers:**
- Issue comments containing `@claude`
- PR comments containing `@claude`
- PR reviews containing `@claude`
- Newly opened/assigned issues with `@claude`

**Permissions:**
- `contents: read` - Read repository files
- `pull-requests: read` - Read PR data
- `issues: read` - Read issue data
- `actions: read` - Read CI results
- `id-token: write` - OIDC authentication

**Features:**
- Responds to @claude mentions in issues/PRs
- Executes Claude AI tasks via `anthropics/claude-code-action@v1`
- Logs all workflow executions to `.github/workflows/logs/`
- Persists logs to repository (commits with `[skip ci]`)

**Configuration:**
- Token: `CLAUDE_CODE_OAUTH_TOKEN` (GitHub secret)
- Custom prompts via `prompt` parameter
- Additional arguments via `claude_args`

### claude-code-review.yml - Automatic PR Reviews

Automatically reviews pull requests using Claude AI.

### check-skip.yml - Skip System Validation

Validates `.skip` file for temporarily disabling Claude CI/CD.

**Outputs:**
- `should_skip` - Boolean indicating if workflows should be skipped

### update-readme.yml - Auto-Update README

Automatically updates README.md when scripts change.

### Workflow Logging

**Logger:** `.github/workflows/scripts/ci-logger.sh`

**Features:**
- Timestamped log entries
- Structured logging with tags (`[success]`, `[error]`, `[warn]`, `[info]`)
- Persistent storage in `.github/workflows/logs/`
- Automatic commit and push

**Log Format:**
```
[2025-11-16 14:30:45] [workflow] Claude Code Workflow
[2025-11-16 14:30:46] [info] Event: issue_comment
[2025-11-16 14:30:50] [success] Claude Code completed successfully
```

---

## Skip System

Location: `.github/skips/`

The **skip system** provides a secure way to temporarily disable Claude CI/CD workflows with support for **global** and **individual workflow** skipping.

### Centralized Skip Validation

All skip logic is centralized in `.github/workflows/check-skip.yml`, which is called by each workflow with its specific name. This eliminates code duplication and provides consistent behavior.

### Skip File Types

#### 1. Global Skip File: `.skip.all`

Skips **all** Claude CI/CD workflows:
- `claude.yml` - Issue/PR comments with @claude
- `claude-code-review.yml` - Automatic PR reviews
- `update-readme.yml` - README auto-updates

#### 2. Workflow-Specific Skip Files

Skip **individual** workflows:
- `.skip.claude` - Only skip @claude issue/PR comments
- `.skip.claude-review` - Only skip automatic PR reviews
- `.skip.update-readme` - Only skip README auto-updates

**Priority:** Global skip is checked first, then workflow-specific skip.

### Two Security Modes

#### 1. Default Mode (Content-based)

Each skip file has its own unique default content (no GitHub Secrets required):

| Skip File | Default Content |
|-----------|----------------|
| `.skip.all` | `SKIP_ALL` |
| `.skip.claude` | `SKIP_CLAUDE` |
| `.skip.claude-review` | `SKIP_REVIEW` |
| `.skip.update-readme` | `SKIP_README` |

**Example:**
```bash
echo -n "SKIP_ALL" > .github/skips/.skip.all
```

#### 2. Custom Mode (Hash-based)

Set workflow-specific GitHub Secrets with custom SHA256 hashes:

- `SKIP_FILE_HASH_ALL` - Custom hash for `.skip.all`
- `SKIP_FILE_HASH_CLAUDE` - Custom hash for `.skip.claude`
- `SKIP_FILE_HASH_CLAUDE_REVIEW` - Custom hash for `.skip.claude-review`
- `SKIP_FILE_HASH_UPDATE_README` - Custom hash for `.skip.update-readme`

**Generate custom hashes:**
```bash
# Manual method
echo -n "MySecretToken" > .github/skips/.skip.claude
sha256sum .github/skips/.skip.claude | awk '{print $1}'
# Add output to GitHub Secrets: SKIP_FILE_HASH_CLAUDE

# Or use the helper script (recommended)
python3 .github/skips/generate_skip_hash.py
```

### Quick Usage Examples

**Skip all workflows:**
```bash
cp .github/skips/.skip.all.example .github/skips/.skip.all
git add .github/skips/.skip.all
git commit -m "Skip all Claude workflows"
git push
```

**Skip only @claude comments:**
```bash
cp .github/skips/.skip.claude.example .github/skips/.skip.claude
git add .github/skips/.skip.claude
git commit -m "Skip only @claude comments"
git push
```

**Re-enable specific workflow:**
```bash
rm .github/skips/.skip.claude
git add .github/skips/.skip.claude
git commit -m "Re-enable @claude comments"
git push
```

### Security Features

- **Hash Validation**: Not every skip file is accepted
- **Centralized Logic**: All validation in one place (no code duplication)
- **Fallback Logic**: Invalid skip files are ignored (CI continues)
- **Audit Trail**: All skip attempts logged in workflow logs
- **Flexibility**: Supports both simple and custom modes
- **Granular Control**: Skip all workflows or individual ones

**For detailed documentation, see:** `.github/skips/SKIP_SYSTEM.md`

---

## Installation System

**Script:** `install.sh`

Interactive script for deploying helper scripts to other projects.

### Features

- **Dynamic Script Discovery**: Scans `docker/`, `dev/`, and `utils/` directories
- **Interactive Configuration**: Prompts for container name, image, paths
- **Selective Deployment**: Choose individual scripts or categories
- **Automatic Customization**: Replaces template variables
- **Comment Stripping**: Removes inline comments to reduce file size
- **Theme Integration**: Deploys `theme.sh` alongside selected scripts

### Workflow

1. **Select Target Directory**
2. **Configure Variables**:
   - Container name
   - Docker image name
   - Display name
   - Dockerfile path
3. **Select Scripts**:
   - Individual selection (e.g., `1 2 3`)
   - `all` - Deploy all scripts
   - `core` - Deploy core Docker scripts only
4. **Review Summary**
5. **Deploy**

### Template Variables (Auto-Replaced)

```bash
readonly CONTAINER_NAME="your-container-name"       User's container name
readonly IMAGE_NAME="your-image-name:latest"        User's image name
readonly DISPLAY_NAME="Your Service"                User's display name
readonly DOCKERFILE_PATH="./Dockerfile"             User's Dockerfile path
```

### Usage

```bash
./install.sh
```

---

## Best Practices for AI Assistants

### File Backup Policy

**CRITICAL: Before editing ANY file, ALWAYS create a backup first.**

- **Backup location**: `.backups/` directory in repository root
- **Naming convention**: `filename.backup-YYYYMMDD-HHMMSS`
- **Create directory if needed**: `mkdir -p .backups`

**Example:**
```bash
# Create .backups directory if it doesn't exist
mkdir -p /path/to/repo/.backups

# Create timestamped backup
cp /path/to/file /path/to/repo/.backups/file.backup-$(date +%Y%m%d-%H%M%S)

# Then make your changes
```

**This applies to:**
- Scripts (shell, Python, etc.)
- Configuration files
- Documentation
- Any file that will be modified

### When Working with Scripts

1. **Always preserve theming**:
   - Use centralized theme from `.sys/theme/theme.sh`
   - Never hardcode colors or icons
   - Use logging functions (`log_success`, `log_error`, etc.)

2. **Follow error handling conventions**:
   - Include `set -e` and `set -o pipefail` at the top
   - Use error checks for critical operations
   - Provide helpful error messages

3. **Maintain script structure**:
   ```bash
   #!/bin/bash
   # Description of what the script does
   set -e
   set -o pipefail

   # Source theme (if needed)
   SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
   source "$SCRIPT_DIR/.sys/theme/theme.sh"

   # Configuration variables
   readonly VAR_NAME="value"

   # Main function
   main() {
       # Script logic
   }

   main "$@"
   ```

4. **Use consistent formatting**:
   - Headers: `echo -e "${MAUVE}[script-name]${NC} ${ICON}  Description..."`
   - Success: `log_success "Message"`
   - Error: `log_error "Message"` (sent to stderr)
   - Warning: `log_warn "Message"`
   - Info: `log_info "Message"`

### When Creating New Scripts

1. **Add script to appropriate directory**:
   - Docker management `docker/`
   - Development tools `dev/`
   - Utilities `utils/`

2. **Include descriptive comment on line 2**:
   ```bash
   #!/bin/bash
   # Description of what this script does
   ```

3. **Make scripts executable**:
   ```bash
   chmod +x script.sh
   ```

4. **Test with linter**:
   ```bash
   ./dev/lint.sh
   ```

### When Modifying GitHub Workflows

1. **Test skip system** before disabling workflows
2. **Preserve logging** functionality in all steps
3. **Use `[skip ci]`** in commit messages to prevent recursive workflows
4. **Maintain permissions** required by Claude Code action

### When Updating Documentation

1. **Update CLAUDE.md** when:
   - Adding new scripts or directories
   - Changing conventions or patterns
   - Modifying workflows
   - Adding new features

2. **Update README.md** (or use `update_readme.py`):
   - When script descriptions change
   - When adding/removing scripts

3. **Update `.sys/THEMING.md`** when:
   - Adding new color definitions
   - Adding new icon definitions
   - Changing logging function signatures

### File Naming Conventions

- **Bash scripts**: `lowercase_with_underscores.sh` or `kebab-case.sh`
- **Python scripts**: `snake_case.py`
- **Documentation**: `UPPERCASE.md` (important docs) or `lowercase.md`
- **Configuration**: `.example` suffix for templates

### Git Practices

1. **Branch naming**: Use descriptive names
   - Features: `feature/description`
   - Fixes: `fix/description`
   - Claude branches: `claude/...` (auto-generated)

2. **Commit messages**:
   - Follow conventional commits (e.g., `fix:`, `feat:`, `docs:`, `chore:`)
   - Use `[skip ci]` when appropriate to avoid triggering workflows

3. **Workflow logs**:
   - Never manually edit files in `.github/workflows/logs/`
   - Logs are auto-generated and auto-committed

4. **CRITICAL: Commit-Pull-Push Workflow**:
   - Make changes and commit locally first
   - Pull with rebase before pushing: `git pull --rebase`
   - Push to remote: `git push`
   - **REPEAT** this cycle for every change
   - **ALWAYS** rebase before pushing (README.md and workflow logs are auto-generated)
   - Workflow: `commit → pull --rebase → push → commit → pull --rebase → push`

### Environment Variables

- **Environment config**: Store in `.sys/env/.env` (gitignored)
- **Use `.env.example`** as template for required variables
- **Never commit secrets** to the repository

### Testing Checklist

Before committing changes:

- [ ] Scripts are executable (`chmod +x`)
- [ ] All scripts pass `./dev/lint.sh`
- [ ] Nerd Font icons display correctly
- [ ] Colors use theme variables (no hardcoded ANSI codes)
- [ ] Error handling is present (`set -e`, `set -o pipefail`)
- [ ] Scripts work with both relative and absolute paths
- [ ] Documentation is updated

---

## Quick Reference

### Common Commands

```bash
# Install scripts to a project
./install.sh

# Check script quality
./dev/lint.sh

# Count lines of code
./dev/lines.sh

# Fix Nerd Font encoding
./utils/fix_nerdfonts.py

# Update README
./utils/update_readme.py

# Docker operations (after deployment)
./docker/start.sh
./docker/stop.sh
./docker/status.sh
./docker/logs.sh [lines]
./docker/rebuild.sh
```

### Important Files

- **Theme Definition**: `.sys/theme/theme.sh`
- **Theme Documentation**: `.sys/THEMING.md`
- **Skip System**: `.github/skips/SKIP_SYSTEM.md`
- **Main Workflow**: `.github/workflows/claude.yml`
- **Installation Script**: `install.sh`

### Key Patterns

**Script header:**
```bash
#!/bin/bash
# Brief description
set -e
set -o pipefail

source "$(dirname "$0")/.sys/theme/theme.sh"
```

**Tag format:**
```bash
echo -e "${MAUVE}[tag]${NC} ${ICON}  Action..."
```

**Customizable variable:**
```bash
readonly CONTAINER_NAME="your-container-name"  # Replaced by install.sh
```

---

## Version Information

- **Repository**: helper-scripts
- **Primary Language**: Bash
- **Supported Shells**: bash
- **Theme**: Catppuccin Mocha
- **Icons**: Nerd Fonts
- **CI/CD**: GitHub Actions + Claude AI
- **Container Runtime**: Docker

---

## Support & Contributing

When contributing to this repository:

1. Follow existing conventions and patterns
2. Use the centralized theming system
3. Add appropriate documentation
4. Test scripts with `./dev/lint.sh`
5. Update CLAUDE.md if adding new features/conventions

For questions about Claude AI integration:
- GitHub Action: https://github.com/anthropics/claude-code-action
- Documentation: https://docs.claude.com/en/docs/claude-code

---

**End of CLAUDE.md**
