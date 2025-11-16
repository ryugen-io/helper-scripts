#!/bin/bash
# Catppuccin Mocha Theme - Centralized color and icon definitions
# Source this file in your scripts: source "$(dirname "$0")/theme.sh"

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'      # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'    # #a6e3a1 - Success
readonly YELLOW='\033[38;2;249;226;175m'   # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'     # #89b4fa - Info
readonly MAUVE='\033[38;2;203;166;247m'    # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m' # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'     # #cdd6f4 - Normal text
readonly SUBTEXT='\033[38;2;186;194;222m'  # #bac2de - Subtext/dimmed
readonly NC='\033[0m'                      # No Color / Reset

# Nerd Font Icons - Unicode characters for visual feedback
readonly CHECK=""    # Check mark (success)
readonly CROSS=""    # Cross mark (error)
readonly WARN=""     # Warning triangle
readonly INFO=""     # Information circle
readonly DOCKER=""   # Docker whale
readonly ROCKET=""   # Rocket (deployment)
readonly FOLDER=""   # Folder
readonly QUESTION="" # Question mark
readonly CHART="󰈙"   # Chart/graph
readonly PLAY=""     # Play button
readonly HAMMER=""   # Hammer/build
readonly CLEAN=""    # Broom/clean

# Standard logging functions for consistent output
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

log_header() {
    echo -e "${MAUVE}$1${NC}"
}

# Export all variables so they're available in subshells
export RED GREEN YELLOW BLUE MAUVE SAPPHIRE TEXT SUBTEXT NC
export CHECK CROSS WARN INFO DOCKER ROCKET FOLDER QUESTION
export CHART PLAY HAMMER CLEAN
