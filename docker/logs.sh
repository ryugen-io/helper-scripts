#!/bin/bash
# Check container logs for errors and warnings
set -e
set -o pipefail

# Source central theme
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$REPO_ROOT/.sys/theme/theme.sh"

# CUSTOMIZE THIS
readonly CONTAINER_NAME="your-container-name"

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
