#!/bin/bash
# Remove ALL emojis and Unicode symbols from files in directory
# Useful for creating clean, emoji-free production scripts
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

# Nerd Font Icons - NO EMOJIS in this script!
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
readonly INFO=""
readonly CLEAN=""  # Broom icon (Nerd Font, not emoji)

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Logging functions
log_success() {
    echo -e "${GREEN}${CHECK}${NC}  $1"
}

log_error() {
    echo -e "${RED}${CROSS}${NC}  $1" >&2
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

# Remove emojis from a single file
remove_emojis_from_file() {
    local file=$1
    local filename=$(basename "$file")
    local backup="${file}.emoji-backup"

    # Create backup
    cp "$file" "$backup"

    # Remove ONLY emoji characters, NOT Nerd Font icons!
    # Nerd Font icons are in Private Use Area (PUA): U+E000-U+F8FF, U+F0000-U+FFFFD
    # We MUST NOT remove these!
    #
    # This regex matches ONLY:
    # - Emoji characters (U+1F300-U+1F9FF) - Color emojis
    # - Miscellaneous symbols (U+2600-U+27BF) - Sun, umbrella, etc.
    # - Dingbats (U+2700-U+27BF) - Scissors, airplane, etc.
    # - Regional indicators (U+1F1E6-U+1F1FF) - Flag emojis
    # - Variation selectors (U+FE00-U+FE0F) - Emoji style selectors
    # - Zero-width joiners (U+200D) - Emoji combining

    # Use Perl for better Unicode support
    if command -v perl &> /dev/null; then
        # Perl regex to remove ONLY emojis, NOT Nerd Font icons!
        # Nerd Fonts use Private Use Area (E000-F8FF) which we preserve
        perl -i -pe '
            # Main emoji ranges - ONLY these!
            s/[\x{1F300}-\x{1F9FF}]//g;    # Emoji & Pictographs (ALL emoji blocks)
            s/[\x{2600}-\x{26FF}]//g;      # Miscellaneous Symbols (sun, stars, etc.)
            s/[\x{2700}-\x{27BF}]//g;      # Dingbats (scissors, checkmarks, etc.)
            s/[\x{1F1E6}-\x{1F1FF}]//g;    # Regional Indicators (flags)
            s/[\x{FE00}-\x{FE0F}]//g;      # Variation Selectors (emoji style)
            s/[\x{200D}]//g;               # Zero Width Joiner (emoji combining)
            s/[\x{2B50}]//g;               # Star emoji
            s/[\x{231A}-\x{231B}]//g;      # Watch, hourglass
            s/[\x{2328}]//g;               # Keyboard
            s/[\x{23CF}]//g;               # Eject button
            s/[\x{23E9}-\x{23F3}]//g;      # Media control symbols
            s/[\x{23F8}-\x{23FA}]//g;      # More media controls
            s/[\x{24C2}]//g;               # Circled M
            s/[\x{25AA}-\x{25AB}]//g;      # Black squares
            s/[\x{25B6}]//g;               # Play button
            s/[\x{25C0}]//g;               # Reverse button
            s/[\x{25FB}-\x{25FE}]//g;      # White/black squares
            s/[\x{2934}-\x{2935}]//g;      # Arrows
            s/[\x{2B05}-\x{2B07}]//g;      # Arrow emojis
            s/[\x{2B1B}-\x{2B1C}]//g;      # Black/white large squares
            s/[\x{3030}]//g;               # Wavy dash
            s/[\x{303D}]//g;               # Part alternation mark
            s/[\x{3297}]//g;               # Circled ideograph congratulation
            s/[\x{3299}]//g;               # Circled ideograph secret

            # DO NOT TOUCH: E000-F8FF (Private Use Area - Nerd Fonts!)
            # DO NOT TOUCH: F0000-FFFFD (Supplementary Private Use Area)
        ' "$file"
    else
        # Fallback to sed with basic Unicode support
        # This won't catch all emojis but will remove common ones
        log_warn "Perl not found, using sed (less comprehensive)"
        # Remove common emoji ranges using sed
        LC_ALL=C sed -i '
            s/[\xF0\x9F][\x80-\xBF][\x80-\xBF][\x80-\xBF]//g
        ' "$file"
    fi

    # Check if file was modified
    if diff -q "$file" "$backup" > /dev/null 2>&1; then
        # No changes - remove backup
        rm "$backup"
        echo -e "${TEXT}  ${filename}${NC} ${SAPPHIRE}(no emojis found)${NC}"
        return 1  # unchanged
    else
        log_success "  Cleaned ${filename}"
        log_info "    Backup: ${backup}"
        return 0  # cleaned
    fi
}

# Main function
main() {
    local target_dir="${1:-.}"
    local cleaned=0
    local unchanged=0
    local failed=0

    echo ""
    log_header "${CLEAN}  Emoji & Symbol Remover"
    echo ""

    # Verify target directory exists
    if [ ! -d "$target_dir" ]; then
        log_error "Directory not found: $target_dir"
        exit 1
    fi

    log_info "Scanning directory: ${SAPPHIRE}${target_dir}${NC}"
    echo ""

    # Process shell scripts
    log_header "Shell Scripts (.sh)"
    echo ""
    for file in "$target_dir"/*.sh "$target_dir"/**/*.sh; do
        # Check if file exists (glob expansion might fail)
        [ -f "$file" ] || continue

        remove_emojis_from_file "$file"
        local result=$?
        case $result in
            0) ((cleaned++)) ;;
            1) ((unchanged++)) ;;
            *) ((failed++)) ;;
        esac
    done

    # Process Python scripts
    if compgen -G "$target_dir/*.py" > /dev/null 2>&1 || compgen -G "$target_dir/**/*.py" > /dev/null 2>&1; then
        echo ""
        log_header "Python Scripts (.py)"
        echo ""
        for file in "$target_dir"/*.py "$target_dir"/**/*.py; do
            [ -f "$file" ] || continue

            remove_emojis_from_file "$file"
            local result=$?
            case $result in
                0) ((cleaned++)) ;;
                1) ((unchanged++)) ;;
                *) ((failed++)) ;;
            esac
        done
    fi

    # Print summary
    echo ""
    log_header "Summary"
    echo ""

    local total=$((cleaned + unchanged + failed))
    echo -e "${TEXT}Total files processed:${NC}  ${SAPPHIRE}${total}${NC}"

    if [ $cleaned -gt 0 ]; then
        echo -e "${GREEN}Cleaned:${NC}               ${SAPPHIRE}${cleaned}${NC}"
    fi

    if [ $unchanged -gt 0 ]; then
        echo -e "${TEXT}No emojis found:${NC}       ${SAPPHIRE}${unchanged}${NC}"
    fi

    if [ $failed -gt 0 ]; then
        echo -e "${RED}Failed:${NC}                ${SAPPHIRE}${failed}${NC}"
    fi

    echo ""

    if [ $cleaned -gt 0 ]; then
        log_info "Backups created with .emoji-backup extension"
        log_warn "Review changes before deleting backups!"
    fi

    echo ""

    # Exit with appropriate code
    if [ $failed -gt 0 ]; then
        log_error "Some files failed to process"
        exit 1
    elif [ $cleaned -gt 0 ]; then
        log_success "Emoji removal complete!"
        exit 0
    else
        log_success "No emojis found in any files!"
        exit 0
    fi
}

# Run main with all arguments
main "$@"
