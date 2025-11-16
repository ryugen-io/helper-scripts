#!/bin/bash
# Start Docker container
set -e
set -o pipefail

# Source central theme
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$REPO_ROOT/.sys/theme/theme.sh"

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load environment configuration from .sys/env/.env
if [ -f "$REPO_ROOT/.sys/env/.env" ]; then
    # shellcheck disable=SC1090
    source "$REPO_ROOT/.sys/env/.env"
fi

# Set defaults if not defined by .env
SYS_DIR="${SYS_DIR:-.sys}"

# CUSTOMIZE THIS - Set your container name here
readonly CONTAINER_NAME="your-container-name"

# Main execution function
main() {
    echo ""
    echo -e "${MAUVE}[start]${NC} ${DOCKER}  Starting ${CONTAINER_NAME} container..."
    echo ""

    # Verify container exists in Docker (check all containers including stopped)
    # Using exact name match with ^$ anchors to avoid partial matches
    if ! docker ps -a --filter "name=^${CONTAINER_NAME}$" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        log_error "Container '${CONTAINER_NAME}' not found"
        exit 1
    fi

    # Check if container is already running to avoid unnecessary operations
    # Filter for both name and running status simultaneously
    if docker ps --filter "name=^${CONTAINER_NAME}$" --filter "status=running" | grep -q "${CONTAINER_NAME}"; then
        log_warn "Container already running"
        echo ""
        exit 0
    fi

    # Start the container using docker start command
    log_info "Starting container..."
    docker start "${CONTAINER_NAME}"

    # Brief pause to allow container to initialize
    # Gives the container time to start up before status check
    sleep 2

    # Verify container started successfully
    # Double-check the container is now in running state
    if docker ps --filter "name=^${CONTAINER_NAME}$" --filter "status=running" | grep -q "${CONTAINER_NAME}"; then
        echo ""
        log_success "${CONTAINER_NAME} container is running"
        echo ""
        # Show helpful next steps for the user
        log_info "Status: ${BLUE}./status.sh${NC}"
        log_info "Logs: ${BLUE}docker logs -f ${CONTAINER_NAME}${NC}"
        log_info "Stop: ${BLUE}./stop.sh${NC}"
    else
        # Container failed to start - provide troubleshooting info
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
