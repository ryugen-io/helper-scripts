#!/bin/bash
# Shell script formatter using shfmt (like cargo fmt for Rust)
# Automatically formats all shell scripts in the repository
set -e
set -o pipefail

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly NC='\033[0m'                         # No Color

# Nerd Font Icons - Unicode characters for visual feedback
readonly CHECK=""     # Success icon
readonly CROSS=""     # Error icon
readonly WARN=""      # Warning icon
readonly INFO=""      # Info icon
readonly MAGIC="✨"    # Sparkles for formatting

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Set defaults first
SYS_DIR="${SYS_DIR:-.sys}"
SCRIPT_DIRS="${SCRIPT_DIRS:-docker,dev,utils}"

# Load environment configuration from .sys/env/.env
if [ -f "$REPO_ROOT/$SYS_DIR/env/.env" ]; then
    # shellcheck disable=SC1090
    source "$REPO_ROOT/$SYS_DIR/env/.env"
fi

# shfmt configuration options
# -i 4: Use 4 spaces for indentation
# -bn: Binary operators at beginning of line
# -ci: Indent switch cases
# -sr: Add space after redirect operators
readonly SHFMT_OPTS="-i 4 -bn -ci -sr"

# Logging functions for consistent output formatting
log_success() {
    # Display success message in green with check icon
    echo -e "${GREEN}${CHECK}${NC}  $1"
}

log_error() {
    # Display error message in red with cross icon (stderr)
    echo -e "${RED}${CROSS}${NC}  $1" >&2
}

log_warn() {
    # Display warning message in yellow with warning icon
    echo -e "${YELLOW}${WARN}${NC}  $1"
}

log_info() {
    # Display informational message in blue with info icon
    echo -e "${BLUE}${INFO}${NC}  $1"
}

log_header() {
    # Display header in mauve color
    echo -e "${MAUVE}$1${NC}"
}

# Check if shfmt is installed on the system
check_shfmt() {
    if ! command -v shfmt &> /dev/null; then
        # shfmt not found - provide installation instructions
        log_error "shfmt is not installed"
        echo ""
        echo -e "${TEXT}Install shfmt:${NC}"
        echo -e "${BLUE}  # Using Go${NC}"
        echo -e "${TEXT}  go install mvdan.cc/sh/v3/cmd/shfmt@latest${NC}"
        echo ""
        echo -e "${BLUE}  # Using Homebrew (macOS/Linux)${NC}"
        echo -e "${TEXT}  brew install shfmt${NC}"
        echo ""
        echo -e "${BLUE}  # Using package manager (Debian/Ubuntu)${NC}"
        echo -e "${TEXT}  sudo apt install shfmt${NC}"
        echo ""
        echo -e "${BLUE}  # Using package manager (Arch)${NC}"
        echo -e "${TEXT}  sudo pacman -S shfmt${NC}"
        echo ""
        return 1
    fi
    return 0
}

# Format a single shell script file
# Returns: 0=formatted, 1=unchanged, 2=failed
format_file() {
    local file=$1
    local filename=$(basename "$file")

    # Check if file has already been formatted correctly
    # Run shfmt in check mode (-d flag) to see if changes are needed
    if shfmt $SHFMT_OPTS -d "$file" &> /dev/null; then
        # File is already formatted correctly - no changes needed
        echo -e "${TEXT}  ${filename}${NC} ${SAPPHIRE}(no changes)${NC}"
        return 1  # unchanged
    else
        # Format the file in-place using -w flag (write)
        if shfmt $SHFMT_OPTS -w "$file"; then
            log_success "  Formatted ${filename}"
            return 0  # formatted
        else
            # Formatting failed - syntax error or other issue
            log_error "  Failed to format ${filename}"
            return 2  # failed
        fi
    fi
}

# Main function - orchestrates the formatting process
main() {
    local check_mode=0
    local formatted=0
    local unchanged=0
    local failed=0

    echo ""
    log_header "${MAGIC}  Shell Script Formatter (shfmt)"
    echo ""

    # Parse command line arguments
    # -c or --check: Check mode (don't modify files, just report)
    if [[ "$1" == "-c" ]] || [[ "$1" == "--check" ]]; then
        check_mode=1
        log_info "Running in check mode (no files will be modified)"
        echo ""
    fi

    # Verify shfmt is installed before proceeding
    if ! check_shfmt; then
        exit 1
    fi

    # Display shfmt version for debugging
    local shfmt_version=$(shfmt -version)
    log_info "Using shfmt ${shfmt_version}"
    echo ""

    log_header "Formatting Shell Scripts"
    echo ""

    # Format script directories from configuration
    IFS=',' read -ra DIRS <<< "$SCRIPT_DIRS"
    for dir in "${DIRS[@]}"; do
        dir=$(echo "$dir" | xargs)  # Trim whitespace
        if [ -d "$REPO_ROOT/$dir" ]; then
            echo -e "${MAUVE}$(echo ${dir^}) Scripts:${NC}"  # Capitalize first letter
            for script in "$REPO_ROOT"/"$dir"/*.sh; do
                # Check if file exists (glob might not match anything)
                if [ -f "$script" ]; then
                    format_file "$script"
                    result=$?
                    # Evaluate return code: 0=formatted, 1=unchanged, 2=failed
                    case $result in
                        0) ((formatted++)) ;;
                        1) ((unchanged++)) ;;
                        2) ((failed++)) ;;
                    esac
                fi
            done
            echo ""
        fi
    done

    # Format root level scripts (like install.sh)
    echo -e "${MAUVE}Root Scripts:${NC}"
    for script in "$REPO_ROOT"/*.sh; do
        if [ -f "$script" ]; then
            format_file "$script"
            result=$?
            case $result in
                0) ((formatted++)) ;;
                1) ((unchanged++)) ;;
                2) ((failed++)) ;;
            esac
        fi
    done
    echo ""

    # Print summary statistics
    log_header "Summary"
    echo ""

    local total=$((formatted + unchanged + failed))
    echo -e "${TEXT}Total files checked:${NC}  ${SAPPHIRE}${total}${NC}"

    if [ $formatted -gt 0 ]; then
        echo -e "${GREEN}Formatted:${NC}           ${SAPPHIRE}${formatted}${NC}"
    fi

    if [ $unchanged -gt 0 ]; then
        echo -e "${TEXT}Already formatted:${NC}   ${SAPPHIRE}${unchanged}${NC}"
    fi

    if [ $failed -gt 0 ]; then
        echo -e "${RED}Failed:${NC}              ${SAPPHIRE}${failed}${NC}"
    fi

    echo ""

    # Exit with appropriate status code
    if [ $failed -gt 0 ]; then
        log_error "Some files failed to format"
        exit 1
    elif [ $formatted -gt 0 ]; then
        log_success "All files formatted successfully! ${MAGIC}"
        exit 0
    else
        log_success "All files already formatted correctly! ${MAGIC}"
        exit 0
    fi
}

# Run main function with all command line arguments
main "$@"
