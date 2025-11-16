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
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
readonly INFO=""
readonly LOG=""
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
