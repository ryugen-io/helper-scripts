#!/bin/bash
# Stop Docker container
set -e
set -o pipefail

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'      # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'    # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'   # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'     # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'    # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m' # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'     # #cdd6f4 - Normal text
readonly NC='\033[0m'                      # No Color

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
