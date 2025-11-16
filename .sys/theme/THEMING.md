# Theming Guide

Standardized theming for all Helper Scripts with Catppuccin Mocha color palette and Nerd Font icons.

## Catppuccin Mocha Color Palette (24-bit True Color)

```bash
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
```

## Color Usage

- **RED** (`#f38ba8`) - Errors and critical messages
- **GREEN** (`#a6e3a1`) - Success and positive messages
- **YELLOW** (`#f9e2af`) - Warnings
- **BLUE** (`#89b4fa`) - Information and highlights
- **MAUVE** (`#cba6f7`) - Headers and tags
- **SAPPHIRE** (`#74c7ec`) - Success highlights
- **TEXT** (`#cdd6f4`) - Normal text
- **SUBTEXT** (`#bac2de`) - Secondary text

## Nerd Font Icons

```bash
# Nerd Font Icons
readonly CHECK=""      # \uf00c - Success
readonly CROSS=""      # \uf00d - Error
readonly WARN=""       # \uf071 - Warning
readonly INFO=""       # \uf05a - Information
readonly SERVER=""     # \uf233 - Server
readonly DOCKER=""     # \uf308 - Docker
readonly CONTAINER=""  # \uf1b2 - Container
readonly CHART="󰈙"      # \uf200 - Chart/Statistics
readonly CLOCK="󰥔"      # \uf64f - Time/Uptime
readonly MEM="󰍛"        # \uf538 - Memory
readonly CPU="󰻠"        # \uf2db - CPU
readonly NET="󰈀"        # \uf6ff - Network
readonly LOG=""        # \uf15c - Log
readonly FILE=""       # \uf15b - File
readonly DATABASE=""   # \uf1c0 - Database
readonly PLAY=""       # \uf04b - Start/Play
readonly STOP=""       # \uf04d - Stop
readonly RESTART=""    # \uf01e - Restart
readonly STATUS=""     # \uf05a - Status
readonly ROCKET=""     # \uf135 - Deployment
readonly FOLDER=""     # \uf07c - Folder
readonly QUESTION=""   # \uf128 - Question/Prompt
readonly SEARCH=""     # \uf002 - Search
readonly HAMMER=""     # \uf6e3 - Build/Rebuild
```

## Standard Log Functions

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
```

## Header/Tag Format

```bash
echo -e "${MAUVE}[script-name]${NC} ${ICON}  Description..."
```

**Examples:**
```bash
echo -e "${MAUVE}[start]${NC} ${DOCKER}  Starting container..."
echo -e "${MAUVE}[status]${NC} ${SERVER}  Checking status..."
echo -e "${MAUVE}[logs]${NC} ${LOG}  Checking logs..."
```

## Usage in Python Scripts

```python
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

def log_success(msg: str):
    print(f"{Colors.GREEN}{CHECK}  {Colors.NC}{msg}")

def log_error(msg: str):
    print(f"{Colors.RED}{CROSS}  {Colors.NC}{msg}", file=sys.stderr)

def log_warn(msg: str):
    print(f"{Colors.YELLOW}{WARN}  {Colors.NC}{msg}")

def log_info(msg: str):
    print(f"{Colors.BLUE}{INFO}  {Colors.NC}{msg}")
```

## Output Design Guidelines

**IMPORTANT: Keep output CLEAN and SIMPLE**

### What NOT to do

- **NO separator lines** like `==================== Title ====================`
- **NO Unicode Emojis** (like "", "", "") - only Nerd Font Icons!
- **NO excessive blank lines** or whitespace
- **NO verbose explanations** - keep it short and precise

### Correct Output Formatting

```bash
# Good - Clean and simple
echo -e "${GREEN}${CHECK}${NC}  No skip file - proceeding with CI/CD"
echo -e "${BLUE}${INFO}${NC}  Checking configuration..."
echo -e "${YELLOW}${WARN}${NC}  Skip file invalid - proceeding for security"

# Bad - Excessive and verbose
echo -e "${MAUVE}==================== Title ====================${NC}"
echo ""
echo -e "${BLUE}${INFO}${NC}  Detailed explanation of what we're doing..."
echo -e "${BLUE}${INFO}${NC}  More detailed information..."
echo ""
echo -e "${MAUVE}=================================================${NC}"
```

### Format Rule

All output follows the format:
```
<COLOR><ICON><NC>  <Message>
```

- One icon
- Two spaces after the icon
- Short, meaningful message
- No period at the end for single-liners
- No additional decorations

## Best Practices

1. **Consistency**: Always use the same colors for the same purposes
2. **Icons**: Choose appropriate icons for the context
3. **Error Handling**: Always send errors to stderr (`>&2`)
4. **Reset**: Always use `${NC}` at the end of colored text
5. **Headers**: Use format `[script-name]` in MAUVE for all scripts
6. **Clean Output**: No separator lines, no emojis, no verbose text

## Terminal Requirements

- Terminal with 24-bit True Color support
- Nerd Font installed (e.g. JetBrains Mono Nerd Font, Fira Code Nerd Font)

## Example Script

```bash
#!/bin/bash
set -e
set -o pipefail

# Catppuccin Mocha color palette
readonly RED='\033[38;2;243;139;168m'
readonly GREEN='\033[38;2;166;227;161m'
readonly YELLOW='\033[38;2;249;226;175m'
readonly BLUE='\033[38;2;137;180;250m'
readonly MAUVE='\033[38;2;203;166;247m'
readonly NC='\033[0m'

# Nerd Font Icons
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
readonly INFO=""
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

main() {
    echo -e "${MAUVE}[example]${NC} ${INFO}  Running example script..."
    echo ""

    log_info "Processing..."
    log_success "Operation completed successfully"
    log_warn "This is a warning"
    log_error "This is an error"

    echo ""
}

main "$@"
```

## References

- [Catppuccin Mocha Theme](https://github.com/catppuccin/catppuccin)
- [Nerd Fonts](https://www.nerdfonts.com/)
