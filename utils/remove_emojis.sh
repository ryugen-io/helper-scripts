#!/bin/bash
# Remove Unicode emojis (like Claude emojis) from files
# Preserves Nerd Font icons (Private Use Area)
# Removes emojis from emojidb.org/claude-emojis and similar Unicode emojis
# Useful for creating clean, emoji-free production scripts
set -e
set -o pipefail

# Source central theme
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$REPO_ROOT/.sys/theme/theme.sh"

# Script configuration


# Remove emojis from a single file
remove_emojis_from_file() {
    local file=$1
    local filename=$(basename "$file")
    local backup="${file}.emoji-backup"

    # Create backup
    cp "$file" "$backup"

    # Remove ONLY Unicode emoji characters (like Claude emojis), NOT Nerd Font icons!
    # Nerd Font icons are in Private Use Area (PUA): U+E000-U+F8FF, U+F0000-U+FFFFD
    # We MUST NOT remove these!
    #
    # This regex removes all emojis from emojidb.org/claude-emojis including:
    # - Emoji characters (🤖, 💥, 🎉, 🔥, etc.) - U+1F300-U+1FAF8
    # - Miscellaneous symbols (☁️, ⚡, ✨, etc.) - U+2600-U+27BF
    # - Dingbats (✳, ✴, ❌, etc.) - U+2700-U+27BF
    # - Mathematical/Technical (⚛, ⚙, ⏳, etc.) - U+2300-U+2BFF
    # - Regional indicators (flags) - U+1F1E6-U+1F1FF
    # - Variation selectors & joiners - U+FE00-U+FE0F, U+200D

    # Use Perl for better Unicode support
    if command -v perl &> /dev/null; then
        # Perl regex to remove ONLY Unicode emojis, NOT Nerd Font icons!
        # Nerd Fonts use Private Use Area (E000-F8FF) which we preserve
        # This covers all Claude emojis from emojidb.org/claude-emojis
        perl -i -pe '
            # Main emoji ranges (covers 99% of emojis including all Claude emojis)
            s/[\x{1F300}-\x{1FAF8}]//g;    # Emoji & Pictographs (ALL emoji blocks including extended)
            s/[\x{1F900}-\x{1F9FF}]//g;    # Supplemental Symbols and Pictographs
            s/[\x{1FA70}-\x{1FAF8}]//g;    # Extended Pictographs
            s/[\x{2600}-\x{26FF}]//g;      # Miscellaneous Symbols (☁️, ⚡, ⌚, etc.)
            s/[\x{2700}-\x{27BF}]//g;      # Dingbats (✨, ✳, ✴, ❌, etc.)
            s/[\x{2300}-\x{23FF}]//g;      # Miscellaneous Technical (⌚, ⏰, ⏳, etc.)
            s/[\x{2000}-\x{206F}]//g;      # General Punctuation (includes ZWJ)
            s/[\x{20A0}-\x{20CF}]//g;      # Currency Symbols (💵 etc.)
            s/[\x{2100}-\x{214F}]//g;      # Letterlike Symbols (ℹ, etc.)
            s/[\x{2190}-\x{21FF}]//g;      # Arrows
            s/[\x{2200}-\x{22FF}]//g;      # Mathematical Operators
            s/[\x{25A0}-\x{25FF}]//g;      # Geometric Shapes
            s/[\x{2600}-\x{27BF}]//g;      # Miscellaneous Symbols & Dingbats
            s/[\x{2900}-\x{297F}]//g;      # Supplemental Arrows-B
            s/[\x{2980}-\x{29FF}]//g;      # Miscellaneous Mathematical Symbols-B
            s/[\x{2A00}-\x{2AFF}]//g;      # Supplemental Mathematical Operators
            s/[\x{2B00}-\x{2BFF}]//g;      # Miscellaneous Symbols and Arrows (⋆, ⚛, ⚙, etc.)
            s/[\x{3000}-\x{303F}]//g;      # CJK Symbols and Punctuation
            s/[\x{1F1E6}-\x{1F1FF}]//g;    # Regional Indicators (flags)
            s/[\x{FE00}-\x{FE0F}]//g;      # Variation Selectors (emoji style)
            s/[\x{0590}-\x{05FF}]//g;      # Hebrew (includes ֎)
            s/[\x{200D}]//g;               # Zero Width Joiner (emoji combining)
            s/[\x{FE0F}]//g;               # Variation Selector-16 (emoji presentation)

            # Specific Claude emojis that might not be covered above
            s/❦//g;                        # Floral Heart
            s/⚹//g;                        # Sextile
            s/✺//g;                        # Heavy Eight Teardrop-Spoked Propeller Asterisk
            s/⛆//g;                        # Rain
            s/❋//g;                        # Heavy Eight Teardrop-Spoked Asterisk

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
