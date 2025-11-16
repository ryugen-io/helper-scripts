#!/bin/bash
# CI Logging Helper - Clean [tag] style logging for GitHub Actions
# Usage: source this file in your workflow scripts

# Configuration
readonly LOG_DIR=".github/workflows/logs"
readonly LOG_FILE="${LOG_DIR}/$(date +%Y%m%d-%H%M%S)-workflow.log"

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

# Icons (simple, GitHub Actions compatible)
readonly CHECK="✓"
readonly CROSS="✗"
readonly WARN="⚠"
readonly INFO="ℹ"
readonly ROCKET="🚀"
readonly HAMMER="🔨"
readonly MAGIC="✨"

# Log to both stdout and file with timestamp
log_to_file() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] $1" | tee -a "${LOG_FILE}"
}

# Logging functions with [tag] style
log_success() {
    local msg="[success] ${CHECK}  $1"
    echo "${msg}"
    log_to_file "${msg}"
}

log_error() {
    local msg="[error] ${CROSS}  $1"
    echo "${msg}" >&2
    log_to_file "${msg}"
}

log_warn() {
    local msg="[warn] ${WARN}  $1"
    echo "${msg}"
    log_to_file "${msg}"
}

log_info() {
    local msg="[info] ${INFO}  $1"
    echo "${msg}"
    log_to_file "${msg}"
}

log_header() {
    local msg="[workflow] $1"
    echo ""
    echo "${msg}"
    echo ""
    log_to_file "${msg}"
}

log_step() {
    local tag="$1"
    shift
    local msg="[${tag}] $*"
    echo ""
    echo "${msg}"
    echo ""
    log_to_file "${msg}"
}

# Export functions and variables
export -f log_success log_error log_warn log_info log_header log_step log_to_file
export LOG_FILE LOG_DIR
export CHECK CROSS WARN INFO ROCKET HAMMER MAGIC
