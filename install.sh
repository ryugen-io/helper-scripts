#!/bin/bash
# Interactive installation script for helper scripts
# Copies scripts and customizes them for a new project
set -e
set -o pipefail

# Catppuccin Mocha color palette (24-bit true color)
readonly RED='\033[38;2;243;139;168m'        # #f38ba8 - Errors
readonly GREEN='\033[38;2;166;227;161m'      # #a6e3a1 - Success/Info
readonly YELLOW='\033[38;2;249;226;175m'     # #f9e2af - Warnings
readonly BLUE='\033[38;2;137;180;250m'       # #89b4fa - Info highlights
readonly MAUVE='\033[38;2;203;166;247m'      # #cba6f7 - Headers
readonly SAPPHIRE='\033[38;2;116;199;236m'   # #74c7ec - Success highlights
readonly TEXT='\033[38;2;205;214;244m'       # #cdd6f4 - Normal text
readonly SUBTEXT='\033[38;2;186;194;222m'    # #bac2de - Subtext
readonly NC='\033[0m'                         # No Color

# Nerd Font Icons
readonly CHECK=""
readonly CROSS=""
readonly WARN=""
readonly INFO=""
readonly ROCKET=""
readonly FOLDER=""
readonly QUESTION=""
readonly DOCKER=""
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load environment configuration
if [ -f "$SCRIPT_DIR/.env" ]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/.env"
fi

# Set defaults if not defined in .env
SYS_DIR="${SYS_DIR:-.sys}"
GITHUB_DIR="${GITHUB_DIR:-.github}"

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

prompt() {
    local prompt_text=$1
    local default_value=$2
    local var_name=$3

    if [ -n "$default_value" ]; then
        echo -e "${BLUE}${QUESTION}  ${TEXT}${prompt_text}${NC} ${SUBTEXT}[${default_value}]${NC}"
    else
        echo -e "${BLUE}${QUESTION}  ${TEXT}${prompt_text}${NC}"
    fi

    echo -n "   > "
    read -r input

    if [ -z "$input" ] && [ -n "$default_value" ]; then
        eval "$var_name=\"$default_value\""
    else
        eval "$var_name=\"$input\""
    fi
}

prompt_yes_no() {
    local prompt_text=$1
    local default=$2

    local suffix
    if [ "$default" = "y" ]; then
        suffix="${SUBTEXT}[Y/n]${NC}"
    else
        suffix="${SUBTEXT}[y/N]${NC}"
    fi

    echo -e "${BLUE}${QUESTION}  ${TEXT}${prompt_text}${NC} ${suffix}"
    echo -n "   > "
    read -r response

    response=${response,,} # to lowercase

    if [ -z "$response" ]; then
        response=$default
    fi

    if [[ "$response" =~ ^(y|yes)$ ]]; then
        return 0
    else
        return 1
    fi
}

get_script_description() {
    local file=$1

    # Extract description from line 2 (comment after shebang)
    # Remove leading "# " from the comment
    local desc=$(sed -n '2p' "$file" | sed 's/^#[[:space:]]*//')

    # If no description found, use generic one
    if [ -z "$desc" ]; then
        desc="Script"
    fi

    echo "$desc"
}

scan_available_scripts() {
    local -n scripts_arr=$1

    # Scan docker directory
    for script in "$SCRIPT_DIR"/docker/*.sh; do
        if [ -f "$script" ]; then
            local relative_path="docker/$(basename "$script")"
            local desc=$(get_script_description "$script")
            scripts_arr+=("${relative_path}:${desc}")
        fi
    done

    # Scan dev directory
    for script in "$SCRIPT_DIR"/dev/*.sh; do
        if [ -f "$script" ]; then
            local relative_path="dev/$(basename "$script")"
            local desc=$(get_script_description "$script")
            scripts_arr+=("${relative_path}:${desc}")
        fi
    done

    # Scan utils directory for Python scripts
    for script in "$SCRIPT_DIR"/utils/*.py; do
        if [ -f "$script" ]; then
            local relative_path="utils/$(basename "$script")"
            local desc=$(get_script_description "$script")
            scripts_arr+=("${relative_path}:${desc}")
        fi
    done
}

select_scripts() {
    local -n arr=$1

    log_header "Select scripts to install:"
    echo ""

    # Dynamically scan for available scripts
    local scripts=()
    scan_available_scripts scripts

    echo -e "${TEXT}Available scripts:${NC}"
    echo ""

    for i in "${!scripts[@]}"; do
        IFS=':' read -r script desc <<< "${scripts[$i]}"
        printf "${SUBTEXT}  %d)${NC} %-30s ${SUBTEXT}%s${NC}\n" $((i+1)) "$script" "$desc"
    done

    echo ""
    echo -e "${TEXT}Select scripts to install:${NC}"
    echo -e "${SUBTEXT}  - Enter numbers separated by spaces (e.g., 1 2 3)${NC}"
    echo -e "${SUBTEXT}  - Enter 'all' for all scripts${NC}"
    echo -e "${SUBTEXT}  - Enter 'core' for core scripts (start, stop, status, logs)${NC}"
    echo ""
    echo -n "   > "
    read -r selection

    arr=()

    if [ "$selection" = "all" ]; then
        for script_info in "${scripts[@]}"; do
            IFS=':' read -r script _ <<< "$script_info"
            arr+=("$script")
        done
    elif [ "$selection" = "core" ]; then
        # Core scripts: only docker management scripts
        for script_info in "${scripts[@]}"; do
            IFS=':' read -r script _ <<< "$script_info"
            if [[ "$script" == docker/* ]] && [[ "$script" != *rebuild.sh ]]; then
                arr+=("$script")
            fi
        done
    else
        for num in $selection; do
            if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le "${#scripts[@]}" ]; then
                IFS=':' read -r script _ <<< "${scripts[$((num-1))]}"
                arr+=("$script")
            fi
        done
    fi
}

remove_inline_comments() {
    local file=$1

    # Remove inline comments that start with "# " (excluding shebang and section headers)
    # Preserve lines that are only comments (section headers)
    # Remove inline comments like: echo "foo"  # This is a comment
    sed -i '/^#!/!s/[[:space:]]*#[[:space:]].*$//' "$file"

    # Remove empty lines that were created by comment removal (but keep intentional spacing)
    # Only remove consecutive empty lines, keeping single empty lines for readability
    sed -i '/^$/N;/^\n$/d' "$file"
}

customize_script() {
    local file=$1
    local container_name=$2
    local image_name=$3
    local display_name=$4
    local dockerfile_path=$5

    # Replace CUSTOMIZE THIS variables
    sed -i "s/readonly CONTAINER_NAME=\"your-container-name\"/readonly CONTAINER_NAME=\"${container_name}\"/" "$file"

    if grep -q "readonly IMAGE_NAME=" "$file"; then
        sed -i "s|readonly IMAGE_NAME=\"your-image-name:latest\"|readonly IMAGE_NAME=\"${image_name}\"|" "$file"
    fi

    if grep -q "readonly DISPLAY_NAME=" "$file"; then
        sed -i "s/readonly DISPLAY_NAME=\"Your Service\"/readonly DISPLAY_NAME=\"${display_name}\"/" "$file"
    fi

    if grep -q "readonly DOCKERFILE_PATH=" "$file"; then
        sed -i "s|readonly DOCKERFILE_PATH=\"./Dockerfile\"|readonly DOCKERFILE_PATH=\"${dockerfile_path}\"|" "$file"
    fi
}

main() {
    echo ""
    log_header "${ROCKET}  Helper Scripts Installation"
    echo ""

    # Collect configuration
    log_header "Configuration"
    echo ""

    local target_dir
    prompt "Target directory for installation" "." target_dir

    # Expand relative paths
    if [[ "$target_dir" != /* ]]; then
        target_dir="$(pwd)/$target_dir"
    fi

    # Create directory if it doesn't exist
    if [ ! -d "$target_dir" ]; then
        if prompt_yes_no "Directory doesn't exist. Create it?" "y"; then
            mkdir -p "$target_dir"
            log_success "Directory created: $target_dir"
        else
            log_error "Installation cancelled"
            exit 1
        fi
    fi

    echo ""

    local container_name
    prompt "Container name" "" container_name

    if [ -z "$container_name" ]; then
        log_error "Container name is required"
        exit 1
    fi

    local image_name
    prompt "Docker image name" "${container_name}:latest" image_name

    local display_name
    prompt "Display name for status output" "$container_name" display_name

    local dockerfile_path
    prompt "Path to Dockerfile" "./Dockerfile" dockerfile_path

    echo ""

    # Select scripts
    local selected_scripts
    select_scripts selected_scripts

    if [ ${#selected_scripts[@]} -eq 0 ]; then
        log_error "No scripts selected"
        exit 1
    fi

    echo ""
    log_header "Summary"
    echo ""
    echo -e "${TEXT}Target directory:${NC}  ${SAPPHIRE}${target_dir}${NC}"
    echo -e "${TEXT}Container name:${NC}    ${SAPPHIRE}${container_name}${NC}"
    echo -e "${TEXT}Image name:${NC}        ${SAPPHIRE}${image_name}${NC}"
    echo -e "${TEXT}Display name:${NC}      ${SAPPHIRE}${display_name}${NC}"
    echo -e "${TEXT}Dockerfile path:${NC}   ${SAPPHIRE}${dockerfile_path}${NC}"
    echo ""
    echo -e "${TEXT}Scripts to install:${NC}"
    for script in "${selected_scripts[@]}"; do
        echo -e "  ${GREEN}${CHECK}${NC}  ${script}"
    done
    echo ""

    if ! prompt_yes_no "Install these scripts?" "y"; then
        log_warn "Installation cancelled"
        exit 0
    fi

    echo ""
    log_header "Installing..."
    echo ""

    # Deploy theme.sh first (always needed)
    log_info "Deploying theme.sh (required for all scripts)..."
    if [ -f "$SCRIPT_DIR/$SYS_DIR/theme.sh" ]; then
        cp "$SCRIPT_DIR/$SYS_DIR/theme.sh" "$target_dir/theme.sh"
        chmod +x "$target_dir/theme.sh"
        log_success "  Deployed: theme.sh"
    else
        log_warn "  theme.sh not found in $SYS_DIR - scripts will use inline colors"
    fi
    echo ""

    # Deploy scripts
    local deployed=0
    local failed=0

    for script in "${selected_scripts[@]}"; do
        local source_file="$SCRIPT_DIR/$script"
        local script_name=$(basename "$script")
        local target_file="$target_dir/$script_name"

        if [ ! -f "$source_file" ]; then
            log_error "Source file not found: $script"
            ((failed++))
            continue
        fi

        # Check if file exists
        if [ -f "$target_file" ]; then
            if ! prompt_yes_no "  File exists: $script_name. Overwrite?" "n"; then
                log_warn "  Skipped: $script_name"
                continue
            fi
        fi

        # Copy file
        cp "$source_file" "$target_file"

        # Remove inline comments to save space
        if [[ "$script_name" == *.sh ]] || [[ "$script_name" == *.py ]]; then
            remove_inline_comments "$target_file"
        fi

        # Customize if it's a shell script
        if [[ "$script_name" == *.sh ]]; then
            customize_script "$target_file" "$container_name" "$image_name" "$display_name" "$dockerfile_path"
        fi

        # Make executable
        chmod +x "$target_file"

        log_success "  Deployed: $script_name"
        ((deployed++))
    done

    echo ""
    log_header "Installation Complete"
    echo ""

    if [ $deployed -gt 0 ]; then
        log_success "$deployed script(s) installed successfully"
    fi

    if [ $failed -gt 0 ]; then
        log_error "$failed script(s) failed to install"
    fi

    echo ""
    log_info "Scripts installed to: ${SAPPHIRE}${target_dir}${NC}"
    echo ""

    # Show next steps
    log_header "Next Steps"
    echo ""
    echo -e "${TEXT}1. Review the installed scripts:${NC}"
    echo -e "   ${SUBTEXT}cd ${target_dir}${NC}"
    echo ""
    echo -e "${TEXT}2. Test the scripts:${NC}"
    echo -e "   ${SUBTEXT}./status.sh${NC}"
    echo ""
    echo -e "${TEXT}3. Customize further if needed${NC}"
    echo ""

    if printf '%s\n' "${selected_scripts[@]}" | grep -q "docker/rebuild.sh"; then
        log_warn "Remember to customize the docker run command in rebuild.sh"
        echo ""
    fi

    log_success "Installation complete! ${ROCKET}"
    echo ""
}

# Run main
main "$@"
