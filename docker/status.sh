#!/bin/bash
# Check the current status and stats of Docker container
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

# CUSTOMIZE THIS
readonly CONTAINER_NAME="your-container-name"
readonly DISPLAY_NAME="Your Service"

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
    local status=$(docker inspect --format='{{.State.Status}}' "$container" 2> /dev/null || echo "unknown")
    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2> /dev/null || echo "none")

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
        local started=$(docker inspect --format='{{.State.StartedAt}}' "$container" 2> /dev/null)
        if [ -n "$started" ]; then
            local uptime=$(docker inspect --format='{{.State.StartedAt}}' "$container" 2> /dev/null | xargs -I {} date -d {} +%s 2> /dev/null || echo "0")
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
        local stats=$(docker stats --no-stream --format "{{.MemUsage}}|{{.CPUPerc}}" "$container" 2> /dev/null)
        if [ -n "$stats" ]; then
            local mem=$(echo "$stats" | cut -d'|' -f1)
            local cpu=$(echo "$stats" | cut -d'|' -f2)

            log_stat "$MEM" "Memory" "$mem" "$YELLOW"
            log_stat "$CPU" "CPU" "$cpu" "$BLUE"
        fi

        # Ports
        local ports=$(docker port "$container" 2> /dev/null | sed 's/^/                    /' | sed 's/0.0.0.0://' || echo "none")
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
