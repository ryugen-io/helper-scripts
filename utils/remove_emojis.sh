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

    # Remove all emoji and special Unicode characters
    # This regex matches:
    # - Emoji characters (U+1F300-U+1F9FF)
    # - Supplementary emoji (U+2600-U+27BF)
    # - Dingbats (U+2700-U+27BF)
    # - Miscellaneous symbols (U+2300-U+23FF, U+2B50, etc.)
    # - Variation selectors (U+FE00-U+FE0F)
    # - Zero-width joiners (U+200D)
    # - Regional indicators (U+1F1E6-U+1F1FF)

    # Use Perl for better Unicode support
    if command -v perl &> /dev/null; then
        # Perl regex to remove emojis and symbols
        perl -i -pe '
            s/[\x{1F300}-\x{1F9FF}]//g;    # Emoji & Pictographs
            s/[\x{1F600}-\x{1F64F}]//g;    # Emoticons
            s/[\x{1F680}-\x{1F6FF}]//g;    # Transport & Map
            s/[\x{2600}-\x{27BF}]//g;      # Misc symbols
            s/[\x{1F1E6}-\x{1F1FF}]//g;    # Flags
            s/[\x{2300}-\x{23FF}]//g;      # Misc Technical
            s/[\x{2B50}]//g;               # Star
            s/[\x{FE00}-\x{FE0F}]//g;      # Variation selectors
            s/[\x{200D}]//g;               # Zero-width joiner
            s/[\x{231A}-\x{231B}]//g;      # Watch
            s/[\x{23E9}-\x{23EC}]//g;      # Play buttons
            s/[\x{23F0}]//g;               # Alarm clock
            s/[\x{23F3}]//g;               # Hourglass
            s/[\x{25FD}-\x{25FE}]//g;      # Squares
            s/[\x{2614}-\x{2615}]//g;      # Umbrella, coffee
            s/[\x{2648}-\x{2653}]//g;      # Zodiac signs
            s/[\x{267F}]//g;               # Wheelchair
            s/[\x{2693}]//g;               # Anchor
            s/[\x{26A1}]//g;               # Lightning
            s/[\x{26AA}-\x{26AB}]//g;      # Circles
            s/[\x{26BD}-\x{26BE}]//g;      # Soccer, baseball
            s/[\x{26C4}-\x{26C5}]//g;      # Snowman, sun
            s/[\x{26CE}]//g;               # Ophiuchus
            s/[\x{26D4}]//g;               # No entry
            s/[\x{26EA}]//g;               # Church
            s/[\x{26F2}-\x{26F3}]//g;      # Fountain, golf
            s/[\x{26F5}]//g;               # Sailboat
            s/[\x{26FA}]//g;               # Tent
            s/[\x{26FD}]//g;               # Fuel pump
            s/[\x{2705}]//g;               # Checkmark
            s/[\x{270A}-\x{270B}]//g;      # Fists
            s/[\x{2728}]//g;               # Sparkles
            s/[\x{274C}]//g;               # Cross mark
            s/[\x{274E}]//g;               # Cross mark button
            s/[\x{2753}-\x{2755}]//g;      # Question marks
            s/[\x{2757}]//g;               # Exclamation
            s/[\x{2795}-\x{2797}]//g;      # Plus, minus
            s/[\x{27B0}]//g;               # Curly loop
            s/[\x{27BF}]//g;               # Double curly loop
            s/[\x{2B1B}-\x{2B1C}]//g;      # Squares
            s/[\x{1F004}]//g;              # Mahjong
            s/[\x{1F0CF}]//g;              # Joker
            s/[\x{1F170}-\x{1F171}]//g;    # A, B buttons
            s/[\x{1F17E}-\x{1F17F}]//g;    # O button
            s/[\x{1F18E}]//g;              # AB button
            s/[\x{1F191}-\x{1F19A}]//g;    # Squared CL, COOL, etc
            s/[\x{1F201}-\x{1F202}]//g;    # Squared Katakana
            s/[\x{1F21A}]//g;              # Squared CJK
            s/[\x{1F22F}]//g;              # Squared CJK
            s/[\x{1F232}-\x{1F23A}]//g;    # Squared CJK
            s/[\x{1F250}-\x{1F251}]//g;    # Circled CJK
            s/[\x{1F300}-\x{1F320}]//g;    # Weather, celestial
            s/[\x{1F32D}-\x{1F335}]//g;    # Food, plants
            s/[\x{1F337}-\x{1F37C}]//g;    # More food
            s/[\x{1F37E}-\x{1F393}]//g;    # Drinks, objects
            s/[\x{1F3A0}-\x{1F3CA}]//g;    # Activities
            s/[\x{1F3CF}-\x{1F3D3}]//g;    # Sports
            s/[\x{1F3E0}-\x{1F3F0}]//g;    # Buildings
            s/[\x{1F3F4}]//g;              # Flag
            s/[\x{1F3F8}-\x{1F43E}]//g;    # Animals, nature
            s/[\x{1F440}]//g;              # Eyes
            s/[\x{1F442}-\x{1F4FC}]//g;    # Body parts, objects
            s/[\x{1F4FF}-\x{1F53D}]//g;    # More objects
            s/[\x{1F54B}-\x{1F54E}]//g;    # Religious symbols
            s/[\x{1F550}-\x{1F567}]//g;    # Clocks
            s/[\x{1F57A}]//g;              # Dancing
            s/[\x{1F595}-\x{1F596}]//g;    # Hand gestures
            s/[\x{1F5A4}]//g;              # Black heart
            s/[\x{1F5FB}-\x{1F64F}]//g;    # Symbols, hands
            s/[\x{1F6A3}]//g;              # Rowboat
            s/[\x{1F6B4}-\x{1F6B6}]//g;    # Activities
            s/[\x{1F6C0}-\x{1F6C5}]//g;    # Bathroom
            s/[\x{1F6CC}]//g;              # Sleeping
            s/[\x{1F6D0}]//g;              # Place of worship
            s/[\x{1F6D1}-\x{1F6D2}]//g;    # Shopping cart
            s/[\x{1F6D5}]//g;              # Hindu temple
            s/[\x{1F6EB}-\x{1F6EC}]//g;    # Airplane
            s/[\x{1F6F4}-\x{1F6FC}]//g;    # Scooter, etc
            s/[\x{1F7E0}-\x{1F7EB}]//g;    # Geometric shapes
            s/[\x{1F90C}-\x{1F93A}]//g;    # Hands, people
            s/[\x{1F93C}-\x{1F945}]//g;    # Activities
            s/[\x{1F947}-\x{1F978}]//g;    # Awards, food
            s/[\x{1F97A}-\x{1F9CB}]//g;    # Faces, people
            s/[\x{1F9CD}-\x{1F9FF}]//g;    # More people
            s/[\x{1FA70}-\x{1FA74}]//g;    # Medical
            s/[\x{1FA78}-\x{1FA7A}]//g;    # Medical
            s/[\x{1FA80}-\x{1FA86}]//g;    # Yoyo, etc
            s/[\x{1FA90}-\x{1FAA8}]//g;    # Body parts
            s/[\x{1FAB0}-\x{1FAB6}]//g;    # Food
            s/[\x{1FAC0}-\x{1FAC2}]//g;    # People
            s/[\x{1FAD0}-\x{1FAD6}]//g;    # Food
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
