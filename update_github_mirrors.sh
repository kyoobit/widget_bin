#!/usr/bin/env bash

# -e: exit on error
# -u: error on undefined variables
# -o pipefail: fail pipeline if any command fails
set -euo pipefail

[ -n "${GITHUB_ACCOUNT}" ] || { echo "GITHUB_ACCOUNT not set!"; exit 1; }
[ -n "${GITHUB_TOKEN}" ] || { echo "GITHUB_TOKEN not set!"; exit 1; }

log() {
    echo "[$(date --rfc-3339=seconds)] INFO - $*";
}

# Set up a mirror of the source repository
git_clone_as_mirror() {
    _repo="${1}";
    if [[ -e "${_repo}/HEAD" ]]; then
        log "Repository mirror exists: ${_repo}";
    else
        log "Repository mirror does NOT exist: ${_repo}";
        log "git clone --mirror \"git@github.com:${GITHUB_ACCOUNT}/$(basename ${_repo})\" \"${_repo}\"";
        git clone --mirror "git@github.com:${GITHUB_ACCOUNT}/$(basename ${_repo})" "${_repo}";
    fi
}

# Download objects and refs from a repository
git_fetch_all() {
    _repo="${1}";
    log "Fetch all for repository: ${_repo}";
    log "cd ${_repo} && git fetch --all";
    cd "${_repo}";
    git fetch --all;
}

log "Using github account: ${GITHUB_ACCOUNT}";

# Use the directory of this script as the base path
readonly BASE_PATH=$(dirname $0);
log "Using local path base: ${BASE_PATH}";

# gh will use GITHUB_TOKEN, no need to run login for the GITHUB_ACCOUNT
#echo "${GITHUB_TOKEN}" | gh auth login --with-token || { echo "Github login failed!"; exit 1; }

# Get a list of repo on the account using gh cli (sudo dnf install gh)
mapfile -t GITHUB_REPOSITORIES < <(gh repo list "${GITHUB_ACCOUNT}" --limit 1000 --json name --jq '.[].name' | sort)
[ ${#GITHUB_REPOSITORIES[@]} -gt 0 ] || { echo "No repositories found!"; exit 1; }
log "Found ${#GITHUB_REPOSITORIES[@]} repositories"

# Create and fetch a list of repositories
for repo in "${GITHUB_REPOSITORIES[@]}"; do
    log "Processing repository: ${repo}";
    git_clone_as_mirror "${BASE_PATH}/${repo}.git";
    git_fetch_all "${BASE_PATH}/${repo}.git";
done
