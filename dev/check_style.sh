#!/bin/bash
# Style and theming checker for helper scripts
# Validates coding guidelines and Catppuccin Mocha theming consistency
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

# Nerd Font Icons
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
readonly INFO=""
readonly CHART="󰈙"

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

# Counters for statistics
total_files=0
passed_files=0
failed_files=0
warnings=0

# Expected color palette (Catppuccin Mocha)
declare -A EXPECTED_COLORS=(
    ["RED"]="243;139;168"
    ["GREEN"]="166;227;161"
    ["YELLOW"]="249;226;175"
    ["BLUE"]="137;180;250"
    ["MAUVE"]="203;166;247"
    ["SAPPHIRE"]="116;199;236"
    ["TEXT"]="205;214;244"
)

# Required coding standards
declare -A REQUIRED_PATTERNS=(
    ["set -e"]="Error handling: set -e"
    ["set -o pipefail"]="Error handling: set -o pipefail"
    ["readonly"]="Use readonly for constants"
)

log_success() {
    echo -e "${GREEN}${CHECK}${NC}  $1"
}

log_error() {
    echo -e "${RED}${CROSS}${NC}  $1"
}

log_warn() {
    echo -e "${YELLOW}${WARN}${NC}  $1"
}

log_info() {
    echo -e "${BLUE}${INFO}${NC}  $1"
}

log_header() {
    echo -e "${MAUVE}$1${NC}"
}

# Check if file uses correct Catppuccin Mocha colors
check_colors() {
    local file=$1
    local issues=0

    # Check each expected color
    for color_name in "${!EXPECTED_COLORS[@]}"; do
        local expected_rgb="${EXPECTED_COLORS[$color_name]}"

        # Check if color is defined in file
        if grep -q "readonly ${color_name}=" "$file"; then
            # Verify it has the correct RGB values
            if ! grep -q "${expected_rgb}" "$file"; then
                log_warn "    Incorrect RGB for ${color_name} (expected: ${expected_rgb})"
                ((issues++))
                ((warnings++))
            fi
        fi
    done

    return $issues
}

# Check coding standards
check_standards() {
    local file=$1
    local issues=0

    # Check for required patterns
    if ! grep -q "set -e" "$file"; then
        log_error "    Missing: set -e"
        ((issues++))
    fi

    if ! grep -q "set -o pipefail" "$file"; then
        log_error "    Missing: set -o pipefail"
        ((issues++))
    fi

    # Check for readonly usage with color definitions
    if grep -q "RED=" "$file" && ! grep -q "readonly RED=" "$file"; then
        log_warn "    Color variables should be readonly"
        ((issues++))
        ((warnings++))
    fi

    # Check shebang
    if ! head -n1 "$file" | grep -q "^#!/bin/bash\|^#!/usr/bin/env python3"; then
        log_error "    Invalid or missing shebang"
        ((issues++))
    fi

    return $issues
}

# Check script structure
check_structure() {
    local file=$1
    local issues=0
    local filename=$(basename "$file")

    # Shell scripts should have logging functions if they use colors
    if [[ "$filename" == *.sh ]]; then
        if grep -q "readonly RED=" "$file"; then
            # Check for at least one logging function
            if ! grep -q "log_error\|log_success\|log_info\|log_warn" "$file"; then
                log_warn "    Script uses colors but has no logging functions"
                ((issues++))
                ((warnings++))
            fi
        fi

        # Check for proper comments at the top
        if ! sed -n '2p' "$file" | grep -q "^#"; then
            log_warn "    Missing description comment on line 2"
            ((warnings++))
        fi
    fi

    return $issues
}

# Check single file
check_file() {
    local file=$1
    local filename=$(basename "$file")
    local file_issues=0

    echo -e "${TEXT}Checking: ${SAPPHIRE}${filename}${NC}"

    # Run all checks
    check_colors "$file" || ((file_issues+=$?))
    check_standards "$file" || ((file_issues+=$?))
    check_structure "$file" || ((file_issues+=$?))

    if [ $file_issues -eq 0 ]; then
        log_success "  All checks passed"
        ((passed_files++))
    else
        log_error "  Found $file_issues issue(s)"
        ((failed_files++))
    fi

    echo ""
    ((total_files++))
}

# Main function
main() {
    echo ""
    log_header "${CHART}  Helper Scripts Style Checker"
    echo ""
    log_info "Validating coding guidelines and theming consistency"
    echo ""

    # Find all shell scripts from configured directories
    log_header "Checking Shell Scripts"
    echo ""

    # Check scripts in configured directories
    IFS=',' read -ra DIRS <<< "$SCRIPT_DIRS"
    for dir in "${DIRS[@]}"; do
        dir=$(echo "$dir" | xargs)  # Trim whitespace
        if [ -d "$REPO_ROOT/$dir" ]; then
            for script in "$REPO_ROOT"/"$dir"/*.sh; do
                [ -f "$script" ] && check_file "$script"
            done
        fi
    done

    # Check root scripts
    if [ -f "$REPO_ROOT/install.sh" ]; then
        check_file "$REPO_ROOT/install.sh"
    fi

    # Check Python scripts from configured directories
    log_header "Checking Python Scripts"
    echo ""

    IFS=',' read -ra DIRS <<< "$SCRIPT_DIRS"
    for dir in "${DIRS[@]}"; do
        dir=$(echo "$dir" | xargs)  # Trim whitespace
        if [ -d "$REPO_ROOT/$dir" ]; then
            for script in "$REPO_ROOT"/"$dir"/*.py; do
                [ -f "$script" ] && check_file "$script"
            done
        fi
    done

    # Print summary
    log_header "Summary"
    echo ""
    echo -e "${TEXT}Total files checked:${NC}   ${SAPPHIRE}${total_files}${NC}"
    echo -e "${GREEN}Passed:${NC}                ${SAPPHIRE}${passed_files}${NC}"

    if [ $failed_files -gt 0 ]; then
        echo -e "${RED}Failed:${NC}                ${SAPPHIRE}${failed_files}${NC}"
    fi

    if [ $warnings -gt 0 ]; then
        echo -e "${YELLOW}Warnings:${NC}              ${SAPPHIRE}${warnings}${NC}"
    fi

    echo ""

    # Exit with appropriate code
    if [ $failed_files -gt 0 ]; then
        log_error "Style check failed"
        exit 1
    else
        log_success "All checks passed!"
        exit 0
    fi
}

# Run main
main "$@"
