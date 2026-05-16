#!/usr/bin/env bash

# -e: exit on error
# -u: error on undefined variables
# -o pipefail: fail pipeline if any command fails
set -euo pipefail

# Defaults
# All variables must be set before use (set -u)
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
_EXIT_CLEAN=0  # Track whether we exited cleanly
ALL=""
DEBUG=""
DRYRUN=""
MORE=""
POSITIONAL_ARGS=()
VERBOSE=""

read -r -d '' HELP_MESSAGE <<- END_HELP_MESSAGE || true
usage: ${SCRIPT_NAME} [OPTIONS]

...

optional arguments:
  -h, --help             Show this help message and exit.
  -v, --verbose          Run with increase message verbosity
  --dry-run              Run without making changes
  --debug                Run with noisy message verbosity

  -A, --all              ...
  -M, --more <value>     ...

Program examples:
$ ${SCRIPT_NAME} --all
$ ${SCRIPT_NAME} --more <COWBELL>

END_HELP_MESSAGE

function _cleanup() {
    local exit_code=$?
    [[ $exit_code -ne 0 && "${_EXIT_CLEAN}" -eq 0 ]] && \
        message "ERROR" "Script exited unexpectedly with code ${exit_code}"
}

function die() {
    _EXIT_CLEAN=0  # still unclean, but message already printed
    message "ERROR" "$*"
    _EXIT_CLEAN=1  # suppress _cleanup's message
    exit 1
}

# Print messages with colored log levels
function message() {
    # Usage: message "LEVEL" "log message content"
    local _level="${1:-LOG}"
    local _message="${2:-}"
    local _color=""

    case "${_level}" in
        DEBUG   ) [[ -z "${DEBUG:-}"   ]] && return 0; _color="\033[96m" ;;  # Cyan
        INFO    ) [[ -z "${VERBOSE:-}" ]] && return 0; _color=""         ;;  # Default
        WARNING ) _color="\033[93m" ;;  # Yellow
        ERROR   ) _color="\033[91m" ;;  # Red
        *       ) _color=""         ;;  # Default
    esac

    local _timestamp
    # %F full date; like %+4Y-%m-%d
    # %T time; same as %H:%M:%S
    # %Z alphabetic time zone abbreviation (e.g., EDT)
    _timestamp="$(date '+[%F %T %Z]')"

    # Write the message to the expected file descriptor
    # fd 0 = stdin  (read from)
    # fd 1 = stdout (write to)
    # fd 2 = stderr (write to)
    local _fd=1  # stdout (default)
    [[ "${_level}" == "ERROR" || "${_level}" == "WARNING" ]] && _fd=2  # stderr

    if [[ -n "${_color}" ]]; then
        printf "%b%s %s: %s\033[0m\n" "${_color}" "${_timestamp}" "${_level}" "${_message}" >&"${_fd}"
    else
        printf "%s %s: %s\n" "${_timestamp}" "${_level}" "${_message}" >&"${_fd}"
    fi
}

# Print color text and formats
function print_colors() {
    # ENDC = '\033[0m'
    # BOLD = '\033[1m'
    # UNDERLINE = '\033[4m'
    for i in $(seq 90 96); do
        printf "%b color test: 033[${i}m\033[0m\n" "\033[${i}m"
        printf "%b color test: 033[1m 033[${i}m\033[0m\n" "\033[1m\033[${i}m"
    done
}

# Parse command-line arguments with getopt
# On macOS, use `brew install gnu-getopt` for expected outcome
function parse_args() {
    local getopt_cmd="$(which getopt)"
    local args
    args=$("${getopt_cmd}" -o hvAM: \
        --long help,verbose,dryrun,dry-run,debug,all,more: \
        -n "$0" -- "$@") || exit 1
    eval set -- "${args}"

    while true; do
        case "$1" in
            -h | --help    ) printf "%s\n\n" "${HELP_MESSAGE}"; exit 0 ;;
            -v | --verbose ) VERBOSE="enabled"; shift ;;
            --debug        ) VERBOSE="enabled"; DEBUG="enabled"; shift ;;
            --dry-run | --dryrun ) DRYRUN="enabled"; shift ;;
            -A | --all     ) ALL="enabled"; shift ;;
            -M | --more    ) MORE="$2"; shift 2 ;;
            --             ) shift; break ;;
            *              ) break ;;
        esac
    done

    # Remaining positional args after --
    POSITIONAL_ARGS=("$@")
}

function main() {
    parse_args "$@"

    message "DEBUG" "Example DEBUG message";
    message "INFO" "Example INFO message";
    message "NOISE" "Example NOISE message";
    message "WARNING" "Example WARNING message";
    message "ERROR" "Example ERROR message";

    print_colors


    message "DEBUG" "${POSITIONAL_ARGS[*]:-}"

    if [ -n "${DRYRUN}" ]; then
        message "WARNING" "DRY-RUN mode is enabled, changes will NOT be made!"
    fi;

    # Example exit on missing required argument value
    if [[ -z "${MORE}" ]]; then
        die "--more is required"
    fi

    # Example exit on unexpected positional arguments
    if [[ ${#POSITIONAL_ARGS[@]} -gt 0 ]]; then
        die "Unexpected positional argument(s): $(IFS=','; echo "${POSITIONAL_ARGS[*]}")"
    fi

    # ${varname:-word} If varname exists and isn't null, return its value; otherwise return "word".
    # ${varname:=word} If varname exists and isn't null, return its value; otherwise set it to word and then return its value. 
}

trap _cleanup EXIT
main "$@"