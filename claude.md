# Project Files for Claude AI

Generated: /home/user/helper-scripts
Total files: 11

---

## File: README.md

**Path:** `README.md`

```md
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

### Deployment

- **deploy.sh** - Interactive deployment script to copy and customize templates

### Utilities

- **fix_nerdfonts.py** - Fix Nerd Font icon encoding issues in shell scripts

## Quick Start

### Interactive Deployment (Recommended)

Use the interactive deployment script to automatically copy and customize scripts:

```bash
./deploy.sh
```

The script will ask you for:
- Target directory
- Container name
- Docker image name
- Display name for output
- Path to Dockerfile
- Which scripts to deploy

It automatically replaces all `# CUSTOMIZE THIS` variables and makes scripts executable.

### Manual Deployment

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
```

---

## File: claude.md

**Path:** `claude.md`

```md

```

---

## File: deploy.sh

**Path:** `deploy.sh`

```sh
#!/bin/bash
# Interactive deployment script for Docker helper scripts
# Copies templates and customizes them for a new project
set -e
set -o pipefail

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly SUBTEXT='\033[38;2;186;194;222m'    # #bac2de - Subtext
readonly NC='\033[0m'                         # No Color

# Nerd Font Icons
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
readonly INFO=""
readonly ROCKET=""
readonly FOLDER=""
readonly QUESTION=""
readonly DOCKER=""
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

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

prompt() {
    local prompt_text=$1
    local default_value=$2
    local var_name=$3

    if [ -n "$default_value" ]; then
        echo -e "${BLUE}${QUESTION}  ${TEXT}${prompt_text}${NC} ${SUBTEXT}[${default_value}]${NC}"
    else
        echo -e "${BLUE}${QUESTION}  ${TEXT}${prompt_text}${NC}"
    fi

    echo -n "   > "
    read -r input

    if [ -z "$input" ] && [ -n "$default_value" ]; then
        eval "$var_name=\"$default_value\""
    else
        eval "$var_name=\"$input\""
    fi
}

prompt_yes_no() {
    local prompt_text=$1
    local default=$2

    local suffix
    if [ "$default" = "y" ]; then
        suffix="${SUBTEXT}[Y/n]${NC}"
    else
        suffix="${SUBTEXT}[y/N]${NC}"
    fi

    echo -e "${BLUE}${QUESTION}  ${TEXT}${prompt_text}${NC} ${suffix}"
    echo -n "   > "
    read -r response

    response=${response,,} # to lowercase

    if [ -z "$response" ]; then
        response=$default
    fi

    if [[ "$response" =~ ^(y|yes)$ ]]; then
        return 0
    else
        return 1
    fi
}

select_scripts() {
    local -n arr=$1

    log_header "Select scripts to deploy:"
    echo ""

    local scripts=(
        "start.sh:Start container"
        "stop.sh:Stop container"
        "status.sh:Show container status"
        "logs.sh:Check logs for errors/warnings"
        "rebuild.sh:Rebuild container image"
        "lines.sh:Count lines of code (Rust)"
        "lint.sh:Lint shell scripts"
        "fix_nerdfonts.py:Fix Nerd Font icons"
    )

    echo -e "${TEXT}Available scripts:${NC}"
    echo ""

    for i in "${!scripts[@]}"; do
        IFS=':' read -r script desc <<< "${scripts[$i]}"
        printf "${SUBTEXT}  %d)${NC} %-20s ${SUBTEXT}%s${NC}\n" $((i+1)) "$script" "$desc"
    done

    echo ""
    echo -e "${TEXT}Select scripts to deploy:${NC}"
    echo -e "${SUBTEXT}  - Enter numbers separated by spaces (e.g., 1 2 3)${NC}"
    echo -e "${SUBTEXT}  - Enter 'all' for all scripts${NC}"
    echo -e "${SUBTEXT}  - Enter 'core' for core scripts (start, stop, status, logs)${NC}"
    echo ""
    echo -n "   > "
    read -r selection

    arr=()

    if [ "$selection" = "all" ]; then
        for script_info in "${scripts[@]}"; do
            IFS=':' read -r script _ <<< "$script_info"
            arr+=("$script")
        done
    elif [ "$selection" = "core" ]; then
        arr=("start.sh" "stop.sh" "status.sh" "logs.sh")
    else
        for num in $selection; do
            if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le "${#scripts[@]}" ]; then
                IFS=':' read -r script _ <<< "${scripts[$((num-1))]}"
                arr+=("$script")
            fi
        done
    fi
}

customize_script() {
    local file=$1
    local container_name=$2
    local image_name=$3
    local display_name=$4
    local dockerfile_path=$5

    # Replace CUSTOMIZE THIS variables
    sed -i "s/readonly CONTAINER_NAME=\"your-container-name\"/readonly CONTAINER_NAME=\"${container_name}\"/" "$file"

    if grep -q "readonly IMAGE_NAME=" "$file"; then
        sed -i "s|readonly IMAGE_NAME=\"your-image-name:latest\"|readonly IMAGE_NAME=\"${image_name}\"|" "$file"
    fi

    if grep -q "readonly DISPLAY_NAME=" "$file"; then
        sed -i "s/readonly DISPLAY_NAME=\"Your Service\"/readonly DISPLAY_NAME=\"${display_name}\"/" "$file"
    fi

    if grep -q "readonly DOCKERFILE_PATH=" "$file"; then
        sed -i "s|readonly DOCKERFILE_PATH=\"./Dockerfile\"|readonly DOCKERFILE_PATH=\"${dockerfile_path}\"|" "$file"
    fi
}

main() {
    echo ""
    log_header "╔════════════════════════════════════════════════════════════╗"
    log_header "║                                                            ║"
    log_header "║         ${ROCKET}  Docker Helper Scripts Deployment             ║"
    log_header "║                                                            ║"
    log_header "╚════════════════════════════════════════════════════════════╝"
    echo ""

    # Collect configuration
    log_header "Configuration"
    echo ""

    local target_dir
    prompt "Target directory for deployment" "." target_dir

    # Expand relative paths
    if [[ "$target_dir" != /* ]]; then
        target_dir="$(pwd)/$target_dir"
    fi

    # Create directory if it doesn't exist
    if [ ! -d "$target_dir" ]; then
        if prompt_yes_no "Directory doesn't exist. Create it?" "y"; then
            mkdir -p "$target_dir"
            log_success "Directory created: $target_dir"
        else
            log_error "Deployment cancelled"
            exit 1
        fi
    fi

    echo ""

    local container_name
    prompt "Container name" "" container_name

    if [ -z "$container_name" ]; then
        log_error "Container name is required"
        exit 1
    fi

    local image_name
    prompt "Docker image name" "${container_name}:latest" image_name

    local display_name
    prompt "Display name for status output" "$container_name" display_name

    local dockerfile_path
    prompt "Path to Dockerfile" "./Dockerfile" dockerfile_path

    echo ""

    # Select scripts
    local selected_scripts
    select_scripts selected_scripts

    if [ ${#selected_scripts[@]} -eq 0 ]; then
        log_error "No scripts selected"
        exit 1
    fi

    echo ""
    log_header "Summary"
    echo ""
    echo -e "${TEXT}Target directory:${NC}  ${SAPPHIRE}${target_dir}${NC}"
    echo -e "${TEXT}Container name:${NC}    ${SAPPHIRE}${container_name}${NC}"
    echo -e "${TEXT}Image name:${NC}        ${SAPPHIRE}${image_name}${NC}"
    echo -e "${TEXT}Display name:${NC}      ${SAPPHIRE}${display_name}${NC}"
    echo -e "${TEXT}Dockerfile path:${NC}   ${SAPPHIRE}${dockerfile_path}${NC}"
    echo ""
    echo -e "${TEXT}Scripts to deploy:${NC}"
    for script in "${selected_scripts[@]}"; do
        echo -e "  ${GREEN}${CHECK}${NC}  ${script}"
    done
    echo ""

    if ! prompt_yes_no "Deploy these scripts?" "y"; then
        log_warn "Deployment cancelled"
        exit 0
    fi

    echo ""
    log_header "Deploying..."
    echo ""

    # Deploy scripts
    local deployed=0
    local failed=0

    for script in "${selected_scripts[@]}"; do
        local source_file="$SCRIPT_DIR/$script"
        local target_file="$target_dir/$script"

        if [ ! -f "$source_file" ]; then
            log_error "Source file not found: $script"
            ((failed++))
            continue
        fi

        # Check if file exists
        if [ -f "$target_file" ]; then
            if ! prompt_yes_no "  File exists: $script. Overwrite?" "n"; then
                log_warn "  Skipped: $script"
                continue
            fi
        fi

        # Copy file
        cp "$source_file" "$target_file"

        # Customize if it's a shell script
        if [[ "$script" == *.sh ]]; then
            customize_script "$target_file" "$container_name" "$image_name" "$display_name" "$dockerfile_path"
        fi

        # Make executable
        chmod +x "$target_file"

        log_success "  Deployed: $script"
        ((deployed++))
    done

    echo ""
    log_header "Deployment Complete"
    echo ""

    if [ $deployed -gt 0 ]; then
        log_success "$deployed script(s) deployed successfully"
    fi

    if [ $failed -gt 0 ]; then
        log_error "$failed script(s) failed to deploy"
    fi

    echo ""
    log_info "Scripts deployed to: ${SAPPHIRE}${target_dir}${NC}"
    echo ""

    # Show next steps
    log_header "Next Steps"
    echo ""
    echo -e "${TEXT}1. Review the deployed scripts:${NC}"
    echo -e "   ${SUBTEXT}cd ${target_dir}${NC}"
    echo ""
    echo -e "${TEXT}2. Test the scripts:${NC}"
    echo -e "   ${SUBTEXT}./status.sh${NC}"
    echo ""
    echo -e "${TEXT}3. Customize further if needed${NC}"
    echo ""

    if printf '%s\n' "${selected_scripts[@]}" | grep -q "rebuild.sh"; then
        log_warn "Remember to customize the docker run command in rebuild.sh"
        echo ""
    fi

    log_success "Deployment complete! ${ROCKET}"
    echo ""
}

# Run main
main "$@"
```

---

## File: fix_nerdfonts.py

**Path:** `fix_nerdfonts.py`

```py
#!/usr/bin/env python3
"""
Nerd Font Icon Fixer for Shell Scripts
Replaces empty icon strings with correct Nerd Font Unicode characters
"""

import sys
import re
from pathlib import Path

# Catppuccin Mocha color palette (24-bit true color)
class Colors:
    RED = '\033[38;2;243;139;168m'        # #f38ba8 - Errors
    GREEN = '\033[38;2;166;227;161m'      # #a6e3a1 - Success
    YELLOW = '\033[38;2;249;226;175m'     # #f9e2af - Warnings
    BLUE = '\033[38;2;137;180;250m'       # #89b4fa - Info
    MAUVE = '\033[38;2;203;166;247m'      # #cba6f7 - Headers
    SAPPHIRE = '\033[38;2;116;199;236m'   # #74c7ec - Success highlights
    TEXT = '\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
    SUBTEXT = '\033[38;2;186;194;222m'    # #bac2de - Subtext
    NC = '\033[0m'                         # No Color

# Nerd Font Icons
CHECK = '\uf00c'   #
CROSS = '\uf00d'   #
WARN = '\uf071'    #
INFO = '\uf05a'    #

# Nerd Font Icon mappings (Unicode codepoints)
NERD_FONTS = {
    'CHECK': '\uf00c',      #
    'CROSS': '\uf00d',      #
    'WARN': '\uf071',       #
    'INFO': '\uf05a',       #
    'SERVER': '\uf233',     # 󰒋
    'DOCKER': '\uf308',     #
    'CONTAINER': '\uf1b2',  #
    'CHART': '\uf200',      # 󰈙
    'CLOCK': '\uf64f',      # 󰥔
    'MEM': '\uf538',        # 󰍛
    'CPU': '\uf2db',        # 󰻠
    'NET': '\uf6ff',        # 󰈀
    'LOG': '\uf15c',        #
    'FILE': '\uf15b',       #
    'DATABASE': '\uf1c0',   #
    'PLAY': '\uf04b',       #
    'STOP': '\uf04d',       #
    'RESTART': '\uf01e',    #
    'STATUS': '\uf05a',     #
}

def log_success(msg: str):
    """Log success message with icon"""
    print(f"{Colors.GREEN}{CHECK}  {Colors.NC}{msg}")

def log_error(msg: str):
    """Log error message with icon"""
    print(f"{Colors.RED}{CROSS}  {Colors.NC}{msg}", file=sys.stderr)

def log_warn(msg: str):
    """Log warning message with icon"""
    print(f"{Colors.YELLOW}{WARN}  {Colors.NC}{msg}")

def log_info(msg: str):
    """Log info message with icon"""
    print(f"{Colors.BLUE}{INFO}  {Colors.NC}{msg}")

def fix_icons_in_file(filepath: Path, dry_run: bool = False) -> bool:
    """
    Fix Nerd Font icons in a shell script file

    Args:
        filepath: Path to the shell script
        dry_run: If True, only show what would be changed

    Returns:
        True if changes were made, False otherwise
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        original_content = content
        changes_made = False

        # Pattern to match: readonly ICON_NAME=""
        # We'll replace the empty string with the actual icon
        for icon_name, icon_char in NERD_FONTS.items():
            # Match patterns like: readonly CHECK=""
            pattern = rf'(readonly\s+{icon_name}=)""\s*$'
            replacement = rf'\1"{icon_char}"'

            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

            if new_content != content:
                changes_made = True
                if not dry_run:
                    log_success(f"Fixed {icon_name} in {filepath.name}")
                else:
                    log_warn(f"Would fix {icon_name} in {filepath.name}")
                content = new_content

        if changes_made and not dry_run:
            filepath.write_text(content, encoding='utf-8')
            return True

        return changes_made

    except Exception as e:
        log_error(f"Error processing {filepath}: {e}")
        return False


def write_claude_md(files: list, output_path: Path):
    """
    Write all file contents to a claude.md file

    Args:
        files: List of file paths to include
        output_path: Path to the output file
    """
    try:
        with output_path.open('w', encoding='utf-8') as out:
            out.write("# Project Files for Claude AI\n\n")
            out.write(f"Generated: {Path.cwd()}\n")
            out.write(f"Total files: {len(files)}\n\n")
            out.write("---\n\n")

            for filepath in sorted(files):
                if not filepath.exists() or not filepath.is_file():
                    continue

                try:
                    content = filepath.read_text(encoding='utf-8')
                    out.write(f"## File: {filepath.name}\n\n")
                    out.write(f"**Path:** `{filepath}`\n\n")
                    out.write("```")

                    # Add language identifier based on file extension
                    suffix = filepath.suffix.lstrip('.')
                    if suffix:
                        out.write(suffix)

                    out.write("\n")
                    out.write(content)
                    if not content.endswith('\n'):
                        out.write('\n')
                    out.write("```\n\n")
                    out.write("---\n\n")

                except Exception as e:
                    log_warn(f"Could not read {filepath}: {e}")

        log_success(f"Created {output_path}")
        return True

    except Exception as e:
        log_error(f"Error writing {output_path}: {e}")
        return False


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Fix Nerd Font icons in files and generate claude.md',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Fix all .sh files in current directory
  python3 fix_nerdfonts.py

  # Fix multiple file types
  python3 fix_nerdfonts.py sh md py

  # Fix multiple file types and create claude.md
  python3 fix_nerdfonts.py sh md py --output claude.md

  # Dry run to see what would be changed
  python3 fix_nerdfonts.py sh md --dry-run

  # Fix specific file
  python3 fix_nerdfonts.py status.sh
        '''
    )

    parser.add_argument(
        'filetypes',
        nargs='*',
        help='File types to scan (e.g., sh md py txt) or specific files. Default: sh'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )

    parser.add_argument(
        '--output',
        help='Output file to write scanned contents (e.g., claude.md)'
    )

    args = parser.parse_args()

    # Determine which files to process
    files = []

    if not args.filetypes:
        # Default: scan .sh files
        files = list(Path('.').glob('*.sh'))
    else:
        # Check if arguments are files or file types
        for arg in args.filetypes:
            arg_path = Path(arg)
            if arg_path.exists() and arg_path.is_file():
                # It's a specific file
                files.append(arg_path)
            else:
                # It's a file type - scan for files with this extension
                pattern = f'*.{arg}' if not arg.startswith('*.') else arg
                files.extend(list(Path('.').glob(pattern)))

    if not files:
        if args.filetypes:
            log_error(f"No files found matching types: {', '.join(args.filetypes)}")
        else:
            log_error("No files found!")
        return 1

    # Header
    tag = f"{Colors.MAUVE}[fix-nerdfonts]{Colors.NC}"
    if args.dry_run:
        print(f"{tag} {Colors.YELLOW}DRY RUN:{Colors.NC} Checking Nerd Font icons...")
    else:
        print(f"{tag} Fixing Nerd Font icons...")
    print()

    total_files = 0
    fixed_files = 0

    for filepath in sorted(files):
        if not filepath.exists():
            log_error(f"File not found: {filepath}")
            continue

        if not filepath.is_file():
            log_error(f"Not a file: {filepath}")
            continue

        total_files += 1
        print(f"{Colors.BLUE}Processing{Colors.NC} {filepath.name}...")

        if fix_icons_in_file(filepath, dry_run=args.dry_run):
            fixed_files += 1
        else:
            log_info(f"No changes needed for {filepath.name}")

        print()

    # Generate claude.md if requested
    if args.output:
        output_path = Path(args.output)
        print(f"{Colors.BLUE}Generating{Colors.NC} {output_path}...")
        write_claude_md(files, output_path)
        print()

    # Summary
    print(f"{Colors.GREEN}Summary:{Colors.NC}")
    print()
    print(f"{Colors.BLUE}  Total files:     {Colors.NC}{total_files}")
    print(f"{Colors.GREEN}  Files fixed:     {Colors.NC}{fixed_files}")

    if args.output:
        print(f"{Colors.SAPPHIRE}  Output file:     {Colors.NC}{args.output}")

    if args.dry_run and fixed_files > 0:
        print()
        log_info(f"Run without {Colors.BLUE}--dry-run{Colors.NC} to apply changes")

    return 0


if __name__ == '__main__':
    sys.exit(main())
```

---

## File: lines.sh

**Path:** `lines.sh`

```sh
#!/bin/bash
# Line counter script for Config Manager
# Analyzes all .rs files with detailed statistics

set -e
set -o pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly DEFAULT_LIMIT=200

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly SUBTEXT='\033[38;2;165;173;203m'    # #a5adcb - Dimmed text
readonly NC='\033[0m'                         # No Color

# Nerd Font Icons
readonly CHART="󰈙"
readonly FILE=""
readonly WARN=""
# Logging functions
log_info() {
    echo -e "${BLUE}  ${NC}$1"
}

log_warn() {
    echo -e "${YELLOW}${WARN}  ${NC}$1"
}

log_success() {
    echo -e "${SAPPHIRE}  ${NC}$1"
}

# Cleanup on exit
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo -e "\n${RED}${WARN}  ${NC}Analysis failed with exit code ${exit_code}" >&2
    fi
    cd "$SCRIPT_DIR"
}
trap cleanup EXIT

# Check required commands
check_dependencies() {
    local missing=()

    for cmd in find wc grep awk; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}${WARN}  ${NC}Missing dependencies: ${missing[*]}" >&2
        exit 1
    fi
}

# Count lines in a file, excluding comment-only lines
count_lines() {
    local file="$1"

    # Count total lines
    local total=$(wc -l < "$file")

    # Count comment-only lines (lines starting with // or ///)
    local comments=$(grep -cE '^\s*(//|///)' "$file" || true)

    # Count blank lines
    local blank=$(grep -cE '^\s*$' "$file" || true)

    # Code lines = total - comments - blank
    local code=$((total - comments - blank))

    echo "$code $comments $blank $total"
}

# Analyze files with threshold warnings
analyze_files() {
    local limit=$1
    local yellow_threshold=$((limit * 80 / 100))  # 80% of limit

    local rs_files
    rs_files=$(find "$SCRIPT_DIR" -name "*.rs" -not -path "*/target/*")

    if [ -z "$rs_files" ]; then
        log_warn "No .rs files found"
        exit 1
    fi

    local total_code=0
    local total_comments=0
    local total_blank=0
    local total_lines=0
    local file_count=0
    local max_code=0
    local max_file=""
    local min_code=999999
    local min_file=""
    local over_limit=0

    # Temporary file to store file data for sorting
    local temp_file=$(mktemp)

    # First pass: collect all file data
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            read -r code comments blank total <<< "$(count_lines "$file")"

            total_code=$((total_code + code))
            total_comments=$((total_comments + comments))
            total_blank=$((total_blank + blank))
            total_lines=$((total_lines + total))
            file_count=$((file_count + 1))

            # Track max
            if [ $code -gt $max_code ]; then
                max_code=$code
                max_file=$file
            fi

            # Track min
            if [ $code -lt $min_code ]; then
                min_code=$code
                min_file=$file
            fi

            # Count files over limit
            if [ $code -gt $limit ]; then
                over_limit=$((over_limit + 1))
            fi

            # Store: code|file for sorting
            echo "$code|$file" >> "$temp_file"
        fi
    done <<< "$rs_files"

    echo -e "${BLUE}${FILE}  File Analysis ${SUBTEXT}(limit: ${limit} lines, sorted by LOC):${NC}"
    echo ""

    # Second pass: display sorted by line count (descending)
    sort -t'|' -k1 -rn "$temp_file" | while IFS='|' read -r code file; do
        # Color code by size (green <80%, yellow 80%-100%, red >100%)
        local color icon
        if [ $code -gt $limit ]; then
            color=$RED
            icon="${WARN}"
        elif [ $code -gt $yellow_threshold ]; then
            color=$YELLOW
            icon="${WARN}"
        else
            color=$GREEN
            icon=" "
        fi

        # Display relative path for cleaner output
        local rel_file="${file#./}"
        printf "${color}${icon}  %4d lines${NC}  ${SUBTEXT}%s${NC}\n" "$code" "$rel_file"
    done

    # Cleanup temp file
    rm -f "$temp_file"

    # Calculate average
    local avg_code=0
    if [ $file_count -gt 0 ]; then
        avg_code=$((total_code / file_count))
    fi

    # Calculate percentages
    local code_pct=$(awk "BEGIN {printf \"%.1f\", ($total_code / $total_lines) * 100}")
    local comment_pct=$(awk "BEGIN {printf \"%.1f\", ($total_comments / $total_lines) * 100}")
    local blank_pct=$(awk "BEGIN {printf \"%.1f\", ($total_blank / $total_lines) * 100}")

    # Print summary
    echo ""
    echo -e "${GREEN}${CHART}  Summary:${NC}"
    echo ""
    printf "${TEXT}  Total files:     ${NC}%6d\n" "$file_count"
    printf "${TEXT}  Code lines:      ${NC}%6d ${SUBTEXT}(%s%%)${NC}\n" "$total_code" "$code_pct"
    printf "${TEXT}  Comment lines:   ${NC}%6d ${SUBTEXT}(%s%%)${NC}\n" "$total_comments" "$comment_pct"
    printf "${TEXT}  Blank lines:     ${NC}%6d ${SUBTEXT}(%s%%)${NC}\n" "$total_blank" "$blank_pct"
    printf "${YELLOW}  Total lines:     ${NC}%6d\n" "$total_lines"
    echo ""
    printf "${TEXT}  Average/file:    ${NC}%6d ${SUBTEXT}lines${NC}\n" "$avg_code"
    printf "${SAPPHIRE}  Largest file:    ${NC}%6d ${SUBTEXT}lines${NC} ${YELLOW}(%s)${NC}\n" "$max_code" "${max_file#./}"
    printf "${GREEN}  Smallest file:   ${NC}%6d ${SUBTEXT}lines${NC} ${TEXT}(%s)${NC}\n" "$min_code" "${min_file#./}"
    echo ""

    # Check if we have files over the limit
    if [ $over_limit -gt 0 ]; then
        log_warn "${over_limit} file(s) exceed ${limit} lines"
    else
        log_success "All files under ${limit} lines!"
    fi

    log_info "Comment lines include lines starting with ${TEXT}//${NC} or ${TEXT}///${NC}"
    log_info "Inline comments (code followed by //) are counted as code"
}

# Main execution
main() {
    # Parse optional line limit argument
    local limit=$DEFAULT_LIMIT
    if [ $# -gt 0 ]; then
        if [[ "$1" =~ ^[0-9]+$ ]]; then
            limit=$1
        else
            echo -e "${RED}${WARN}  ${NC}Error: Line limit must be a positive number" >&2
            echo "Usage: $0 [line_limit]" >&2
            echo "Example: $0 150" >&2
            exit 1
        fi
    fi

    echo -e "${MAUVE}[lines]${NC} ${BLUE}${CHART}${NC} Analyzing lines of code in Rust files..."
    echo ""

    check_dependencies
    analyze_files "$limit"

    echo ""
    log_success "Line count analysis complete!"
}

main "$@"
```

---

## File: lint.sh

**Path:** `lint.sh`

```sh
#!/bin/bash
# Lint shell scripts for common issues
# Basic linting without external tools

set -e
set -o pipefail

# Catppuccin Mocha color palette
readonly RED='\033[38;2;243;139;168m'
readonly GREEN='\033[38;2;166;227;161m'
readonly YELLOW='\033[38;2;249;226;175m'
readonly BLUE='\033[38;2;137;180;250m'
readonly MAUVE='\033[38;2;203;166;247m'
readonly SAPPHIRE='\033[38;2;116;199;236m'
readonly NC='\033[0m'

# Nerd Font Icons
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
log_success() {
    echo -e "${GREEN}${CHECK}  ${NC}$1"
}

log_error() {
    echo -e "${RED}${CROSS}  ${NC}$1"
}

log_warn() {
    echo -e "${YELLOW}${WARN}  ${NC}$1"
}

log_info() {
    echo -e "${BLUE}  ${NC}$1"
}

echo -e "${MAUVE}[lint]${NC} Linting shell scripts..."
echo ""

total_scripts=0
passed_scripts=0
total_issues=0

# Check each shell script
for script in *.sh; do
    [ -f "$script" ] || continue
    total_scripts=$((total_scripts + 1))

    echo -e "${BLUE}Checking ${NC}$script"
    issues=0

    # 1. Syntax check
    if ! bash -n "$script" 2>/dev/null; then
        log_error "Syntax error detected"
        issues=$((issues + 1))
    fi

    # 2. Check for set -e or set -o pipefail
    if ! grep -q "set -e" "$script" && ! grep -q "set -o errexit" "$script"; then
        log_warn "Missing 'set -e' (consider adding for safety)"
    fi

    if ! grep -q "set -o pipefail" "$script"; then
        log_warn "Missing 'set -o pipefail' (consider adding for pipe safety)"
    fi

    # 3. Check for shebang
    if ! head -n 1 "$script" | grep -q "^#!"; then
        log_error "Missing shebang line"
        issues=$((issues + 1))
    fi

    # 4. Check for unquoted variables (disabled - too many false positives)
    # This produces warnings for safe cases like echo -e "${COLOR}text${NC}"
    # Manual review is better than automated checking for this

    # 5. Check executable permission
    if [ ! -x "$script" ]; then
        log_warn "Script is not executable (chmod +x $script)"
    fi

    # 6. Check for 'local' in functions (skip - too many false positives)
    # Simple logging functions don't need local variables
    # This check is better handled by the Python linter (shellcheck_test.py)

    if [ $issues -eq 0 ]; then
        log_success "Passed basic linting"
        passed_scripts=$((passed_scripts + 1))
    else
        log_error "$issues critical issue(s) found"
        total_issues=$((total_issues + issues))
    fi

    echo ""
done

# Summary
echo -e "${GREEN}Summary:${NC}"
echo ""
printf "${BLUE}  Total scripts:     ${NC}%d\n" "$total_scripts"
printf "${GREEN}  Passed:            ${NC}%d\n" "$passed_scripts"
printf "${RED}  Critical issues:   ${NC}%d\n" "$total_issues"
echo ""

if [ $total_issues -eq 0 ]; then
    log_success "All shell scripts passed linting!"
    exit 0
else
    log_error "Some scripts have critical issues"
    exit 1
fi
```

---

## File: logs.sh

**Path:** `logs.sh`

```sh
#!/bin/bash
# Check container logs for errors and warnings
set -e
set -o pipefail

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly SUBTEXT='\033[38;2;186;194;222m'    # #bac2de - Subtext
readonly NC='\033[0m'                         # No Color

# Nerd Font Icons
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
readonly INFO=""
readonly LOG=""
readonly SEARCH=""

# CUSTOMIZE THIS
readonly CONTAINER_NAME="your-container-name"

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

# Main execution
main() {
    local lines=${1:-100}

    echo ""
    echo -e "${MAUVE}[logs]${NC} ${LOG}  Checking ${CONTAINER_NAME} logs (last ${lines} lines)..."
    echo ""

    # Check if container exists
    if ! docker ps -a --filter "name=^${CONTAINER_NAME}$" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_error "Container '${CONTAINER_NAME}' not found"
        exit 1
    fi

    # Get logs
    local logs=$(docker logs --tail "$lines" "${CONTAINER_NAME}" 2>&1)

    # Count errors and warnings
    local error_count=$(echo "$logs" | grep -c "ERROR" || true)
    local warn_count=$(echo "$logs" | grep -c "WARN" || true)

    echo -e "${MAUVE}${SEARCH}  Summary${NC}"
    echo ""
    echo -e "${SUBTEXT}  Lines checked:${NC}  ${BLUE}${lines}${NC}"
    echo -e "${SUBTEXT}  Errors found:${NC}   ${RED}${error_count}${NC}"
    echo -e "${SUBTEXT}  Warnings found:${NC} ${YELLOW}${warn_count}${NC}"
    echo ""

    # Show errors if any
    if [ "$error_count" -gt 0 ]; then
        echo -e "${RED}${CROSS}  Errors:${NC}"
        echo ""
        echo "$logs" | grep "ERROR" | while IFS= read -r line; do
            echo -e "${SUBTEXT}  ${RED}${line}${NC}"
        done
        echo ""
    fi

    # Show warnings if any
    if [ "$warn_count" -gt 0 ]; then
        echo -e "${YELLOW}${WARN}  Warnings:${NC}"
        echo ""
        echo "$logs" | grep "WARN" | while IFS= read -r line; do
            echo -e "${SUBTEXT}  ${YELLOW}${line}${NC}"
        done
        echo ""
    fi

    # Summary message
    if [ "$error_count" -eq 0 ] && [ "$warn_count" -eq 0 ]; then
        log_success "No errors or warnings found"
    elif [ "$error_count" -gt 0 ]; then
        log_error "Found ${error_count} errors and ${warn_count} warnings"
    else
        log_warn "Found ${warn_count} warnings"
    fi

    echo ""
    log_info "View full logs: ${BLUE}docker logs ${CONTAINER_NAME}${NC}"
    log_info "Follow logs: ${BLUE}docker logs -f ${CONTAINER_NAME}${NC}"
    echo ""
}

main "$@"
```

---

## File: rebuild.sh

**Path:** `rebuild.sh`

```sh
#!/bin/bash
# Rebuild Docker container (stop, rebuild image, restart)
set -e
set -o pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly NC='\033[0m'                         # No Color

# Nerd Font Icons
readonly INFO=""
readonly WARN=""
readonly CROSS=""
readonly CHECK=""
readonly DOCKER=""
readonly HAMMER=""

# CUSTOMIZE THIS
readonly CONTAINER_NAME="your-container-name"
readonly IMAGE_NAME="your-image-name:latest"
readonly DOCKERFILE_PATH="./Dockerfile"

log_info() {
    echo -e "${BLUE}${INFO}  ${NC}$1"
}

log_warn() {
    echo -e "${YELLOW}${WARN}  ${NC}$1"
}

log_error() {
    echo -e "${RED}${CROSS}  ${NC}$1" >&2
}

log_success() {
    echo -e "${SAPPHIRE}${CHECK}  ${NC}$1"
}

# Main execution
main() {
    cd "$SCRIPT_DIR"

    echo ""
    echo -e "${MAUVE}[rebuild]${NC} ${HAMMER}  Rebuilding ${CONTAINER_NAME} container..."
    echo ""

    # Check if Dockerfile exists
    if [ ! -f "$DOCKERFILE_PATH" ]; then
        log_error "Dockerfile not found at: $DOCKERFILE_PATH"
        exit 1
    fi

    # Stop container if running
    if docker ps --filter "name=^${CONTAINER_NAME}$" --filter "status=running" | grep -q "${CONTAINER_NAME}"; then
        log_info "Stopping running container..."
        docker stop "${CONTAINER_NAME}"
        sleep 1
    fi

    # Build image
    log_info "Building Docker image: ${IMAGE_NAME}..."
    docker build -t "${IMAGE_NAME}" .

    if [ $? -ne 0 ]; then
        log_error "Docker build failed"
        exit 1
    fi

    log_success "Image built successfully"

    # Remove old container if exists
    if docker ps -a --filter "name=^${CONTAINER_NAME}$" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_info "Removing old container..."
        docker rm "${CONTAINER_NAME}"
    fi

    # Start new container (customize docker run command as needed)
    log_info "Starting new container..."

    # CUSTOMIZE THIS: Add your docker run command here
    # Example:
    # docker run -d \
    #     --name "${CONTAINER_NAME}" \
    #     -p 8080:8080 \
    #     --restart unless-stopped \
    #     "${IMAGE_NAME}"

    log_warn "Docker run command not configured in rebuild.sh"
    log_info "Please customize the docker run command in this script"

    echo ""
    log_info "Image: ${BLUE}${IMAGE_NAME}${NC}"
    log_info "Next: Start container with: ${BLUE}./start.sh${NC}"
    echo ""
}

main "$@"
```

---

## File: start.sh

**Path:** `start.sh`

```sh
#!/bin/bash
# Start Docker container
set -e
set -o pipefail

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly NC='\033[0m'                         # No Color

# Nerd Font Icons
readonly INFO=""
readonly WARN=""
readonly CROSS=""
readonly CHECK=""
readonly DOCKER=""
readonly PLAY=""
# CUSTOMIZE THIS
readonly CONTAINER_NAME="your-container-name"

log_info() {
    echo -e "${BLUE}${INFO}  ${NC}$1"
}

log_warn() {
    echo -e "${YELLOW}${WARN}  ${NC}$1"
}

log_error() {
    echo -e "${RED}${CROSS}  ${NC}$1" >&2
}

log_success() {
    echo -e "${SAPPHIRE}${CHECK}  ${NC}$1"
}

# Main execution
main() {
    echo ""
    echo -e "${MAUVE}[start]${NC} ${DOCKER}  Starting ${CONTAINER_NAME} container..."
    echo ""

    # Check if container exists
    if ! docker ps -a --filter "name=^${CONTAINER_NAME}$" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_error "Container '${CONTAINER_NAME}' not found"
        exit 1
    fi

    # Check if already running
    if docker ps --filter "name=^${CONTAINER_NAME}$" --filter "status=running" | grep -q "${CONTAINER_NAME}"; then
        log_warn "Container already running"
        echo ""
        exit 0
    fi

    # Start container
    log_info "Starting container..."
    docker start "${CONTAINER_NAME}"

    # Wait for container to be healthy
    sleep 2

    # Check container status
    if docker ps --filter "name=^${CONTAINER_NAME}$" --filter "status=running" | grep -q "${CONTAINER_NAME}"; then
        echo ""
        log_success "${CONTAINER_NAME} container is running"
        echo ""
        log_info "Status: ${BLUE}./status.sh${NC}"
        log_info "Logs: ${BLUE}docker logs -f ${CONTAINER_NAME}${NC}"
        log_info "Stop: ${BLUE}./stop.sh${NC}"
    else
        echo ""
        log_error "Failed to start ${CONTAINER_NAME} container"
        log_info "Check logs with: docker logs ${CONTAINER_NAME}"
        exit 1
    fi

    echo ""
    echo -e " ${GREEN}${PLAY}${NC}  Done."
    echo ""
}

main "$@"
```

---

## File: status.sh

**Path:** `status.sh`

```sh
#!/bin/bash
# Check the current status and stats of Docker container
set -e
set -o pipefail

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly SUBTEXT='\033[38;2;186;194;222m'    # #bac2de - Subtext
readonly NC='\033[0m'                         # No Color

# Nerd Font Icons
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
readonly INFO=""
readonly SERVER=""
readonly DOCKER=""
readonly STATUS=""
readonly CLOCK=""
readonly MEM=""
readonly CPU=""
readonly NET=""
# CUSTOMIZE THIS
readonly CONTAINER_NAME="your-container-name"
readonly DISPLAY_NAME="Your Service"

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

log_stat() {
    local icon=$1
    local label=$2
    local value=$3
    local color=$4
    printf "${SUBTEXT}%-2s  %-16s${NC} ${color}%s${NC}\n" "$icon" "$label:" "$value"
}

show_container_status() {
    local container=$1
    local name=$2
    local icon=$3

    echo -e "${MAUVE}${icon}  ${name}${NC}"
    echo ""

    # Check if container exists
    if ! docker ps -a --filter "name=^${container}$" --format "{{.Names}}" | grep -q "^${container}$"; then
        log_error "Container not found: ${container}"
        echo ""
        return 1
    fi

    # Get container status
    local status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")

    # Status
    if [ "$status" = "running" ]; then
        log_stat "$STATUS" "Status" "$status" "$GREEN"
    else
        log_stat "$STATUS" "Status" "$status" "$RED"
    fi

    # Health
    if [ "$health" != "none" ]; then
        if [ "$health" = "healthy" ]; then
            log_stat "$CHECK" "Health" "$health" "$GREEN"
        elif [ "$health" = "unhealthy" ]; then
            log_stat "$CROSS" "Health" "$health" "$RED"
        else
            log_stat "$WARN" "Health" "$health" "$YELLOW"
        fi
    fi

    # Only show stats if running
    if [ "$status" = "running" ]; then
        # Uptime
        local started=$(docker inspect --format='{{.State.StartedAt}}' "$container" 2>/dev/null)
        if [ -n "$started" ]; then
            local uptime=$(docker inspect --format='{{.State.StartedAt}}' "$container" 2>/dev/null | xargs -I {} date -d {} +%s 2>/dev/null || echo "0")
            local now=$(date +%s)
            local diff=$((now - uptime))
            local days=$((diff / 86400))
            local hours=$(((diff % 86400) / 3600))
            local mins=$(((diff % 3600) / 60))

            if [ $days -gt 0 ]; then
                log_stat "$CLOCK" "Uptime" "${days}d ${hours}h ${mins}m" "$GREEN"
            elif [ $hours -gt 0 ]; then
                log_stat "$CLOCK" "Uptime" "${hours}h ${mins}m" "$GREEN"
            else
                log_stat "$CLOCK" "Uptime" "${mins}m" "$GREEN"
            fi
        fi

        # Get stats
        local stats=$(docker stats --no-stream --format "{{.MemUsage}}|{{.CPUPerc}}" "$container" 2>/dev/null)
        if [ -n "$stats" ]; then
            local mem=$(echo "$stats" | cut -d'|' -f1)
            local cpu=$(echo "$stats" | cut -d'|' -f2)

            log_stat "$MEM" "Memory" "$mem" "$YELLOW"
            log_stat "$CPU" "CPU" "$cpu" "$BLUE"
        fi

        # Ports
        local ports=$(docker port "$container" 2>/dev/null | sed 's/^/                    /' | sed 's/0.0.0.0://' || echo "none")
        if [ "$ports" != "none" ]; then
            echo -e "${SUBTEXT}${NET}  Ports:${NC}"
            echo -e "${SAPPHIRE}${ports}${NC}"
        fi
    fi

    echo ""
}

# Main execution
main() {
    echo -e "${MAUVE}[status]${NC} ${DOCKER}  Checking ${CONTAINER_NAME} container status..."
    echo ""

    # Check if container exists
    if ! docker ps -a --filter "name=^${CONTAINER_NAME}$" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_error "${CONTAINER_NAME} container not found"
        echo ""
        exit 1
    fi

    # Show container status
    show_container_status "${CONTAINER_NAME}" "${DISPLAY_NAME}" "$SERVER"

    # Show running status
    if docker ps --filter "name=^${CONTAINER_NAME}$" --filter "status=running" | grep -q "${CONTAINER_NAME}"; then
        log_success "Container is running"
    else
        log_error "Container is not running"
        echo ""
        log_info "Start container with: ${BLUE}./start.sh${NC}"
    fi

    echo ""
}

main
```

---

## File: stop.sh

**Path:** `stop.sh`

```sh
#!/bin/bash
# Stop Docker container
set -e
set -o pipefail

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly NC='\033[0m'                         # No Color

# Nerd Font Icons
readonly INFO=""
readonly WARN=""
readonly CROSS=""
readonly CHECK=""
readonly DOCKER=""
readonly STOP=""
# CUSTOMIZE THIS
readonly CONTAINER_NAME="your-container-name"

log_info() {
    echo -e "${BLUE}${INFO}  ${NC}$1"
}

log_warn() {
    echo -e "${YELLOW}${WARN}  ${NC}$1"
}

log_error() {
    echo -e "${RED}${CROSS}  ${NC}$1" >&2
}

log_success() {
    echo -e "${SAPPHIRE}${CHECK}  ${NC}$1"
}

# Main execution
main() {
    echo ""
    echo -e "${MAUVE}[stop]${NC} ${DOCKER}  Stopping ${CONTAINER_NAME} container..."
    echo ""

    # Check if containers are running
    if ! docker ps --filter "name=^${CONTAINER_NAME}$" --filter "status=running" | grep -q "${CONTAINER_NAME}"; then
        log_warn "No running ${CONTAINER_NAME} container found"
        echo ""
        exit 0
    fi

    # Stop container
    log_info "Stopping container..."
    docker stop "${CONTAINER_NAME}"

    # Verify container stopped
    sleep 1
    if docker ps --filter "name=^${CONTAINER_NAME}$" --filter "status=running" | grep -q "${CONTAINER_NAME}"; then
        log_warn "Container may still be running"
        log_info "Check with: docker ps | grep ${CONTAINER_NAME}"
    else
        echo ""
        log_success "${CONTAINER_NAME} container stopped successfully"
    fi

    echo ""
    echo -e " ${RED}${STOP}${NC}  Done."
    echo ""
}

main "$@"
```

---

