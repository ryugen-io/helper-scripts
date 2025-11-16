#!/bin/bash
# Stop Docker container
set -e
set -o pipefail

# Source central theme
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$REPO_ROOT/.sys/theme/theme.sh"

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Set defaults first
SYS_DIR="${SYS_DIR:-.sys}"

# Load environment configuration from .sys/env/.env
if [ -f "$REPO_ROOT/$SYS_DIR/env/.env" ]; then
    # shellcheck disable=SC1090
    source "$REPO_ROOT/$SYS_DIR/env/.env"
fi

# CUSTOMIZE THIS
readonly CONTAINER_NAME="your-container-name"

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
