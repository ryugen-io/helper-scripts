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
readonly INFO=""
readonly WARN=""
readonly CROSS=""
readonly CHECK=""
readonly DOCKER=""
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
