#!/usr/bin/env bash

set -o errexit   # abort on nonzero exit status
set -o nounset   # abort on unbound variable
set -o pipefail  # don't hide errors within pipes

# Require at least one 'SOURCE|DESTINATION' pair
if [[ "$#" -eq "0" ]] || [[ "$1" = '-h' ]] || [[ "$1" = '--help' ]]; then
    echo "Use 'rclone sync' with one or more pipe separated 'SOURCE|DESTINATION' pair
Usage: $(basename $0) [--dry-run] 'SOURCE|DESTINATION' [ 'SOURCE|DESTINATION' [ ... ]]
    ";
    exit 0;
fi

DRY_RUN=false;
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true;
    shift;
fi

log() {
    printf "[$(date '+%Y-%m-%d %H:%M:%S')] INFO - $*\n";
}

# Check if rclone is installed
command -v rclone >/dev/null 2>&1 || {
    printf "ERROR - rclone is not installed. Aborting.\n";
    exit 1;
}

# Sync the SOURCE to the DESTINATION
sync() {
    # $1 should be a pipe separated 'SOURCE|DESTINATION' pair
    if [[ "${1}" != *"|"* ]]; then
        printf "ERROR - Invalid format. Expected 'SOURCE|DESTINATION', got: ${1}\n";
        exit 1;
    fi

    _source="${1%%|*}";
    _destination="${1##*|}";

    # Check if source and destination are different
    if [[ "${_source}" == "${_destination}" ]]; then
        printf "ERROR - Source and destination are the same: ${_source}\n";
        exit 1;
    fi

    if [[ "${DRY_RUN}" == "true" ]]; then
        log "Starting DRY RUN sync of '${_source}' to '${_destination}'";
        rclone sync --dry-run "${_source}" "${_destination}";
        log "Finished DRY RUN sync of '${_source}' to '${_destination}'";
    else
        log "Starting sync of '${_source}' to '${_destination}'";
        rclone sync "${_source}" "${_destination}";
        log "Finished sync of '${_source}' to '${_destination}'";
    fi
}

# Run sync for each 'SOURCE|DESTINATION' pair argument passed
for _arg in "${@}"; do
    sync "${_arg}";
done
