#!/usr/bin/env bash

set -o errexit   # abort on nonzero exit status
set -o nounset   # abort on unbound variable
set -o pipefail  # don't hide errors within pipes

log() {
    printf "[$(date '+%Y-%m-%d %H:%M:%S')] INFO - ${*}\n";
}

check_gluster() {
    vm_name="${1}";
    log "Checking glusterfs services on ${vm_name}...";
    result=$(ssh -q "${name}" 'cat /mnt/data/is_working' | grep 'is working');
    if [[ -z "${result}" ]]; then
        log "Restarting glusterfs services on ${vm_name}...";
        ssh -q "${vm_name}" 'sudo systemctl restart glusterd';
        sleep 10;
        ssh -q "${vm_name}" 'sudo mount -a';
        result=$(ssh -q "${name}" 'cat /mnt/data/is_working' | grep 'is working');
    fi
    log "${result}";
}

check_hadoop() {
    vm_name="${1}";
    log "Checking hadoop services on ${vm_name}...";
    # ...not implemented yet
}

check_kubernetes() {
    vm_name="${1}";
    log "Checking kubernetes services on ${vm_name}...";
    # ...not implemented yet
}

reboot() {
    vm_name="${1}";
    log "Rebooting ${vm_name}...";
    ssh -q "${vm_name}" 'sudo systemctl reboot';
}

shutdown() {
    vm_name="${1}";
    log "Shutdown ${vm_name}...";
    # Send an ACPI shutdown signal (/sys/firmware/acpi)
    virsh shutdown "${name}";
}

start() {
    vm_name="${1}";
    log "Starting ${vm_name}...";
    virsh start "${vm_name}";
}

update() {
    vm_name="${1}";
    log "Updating ${vm_name}...";
    ssh -q "${vm_name}" 'sudo apt-get update';
    ssh -q "${vm_name}" 'sudo apt-get list --upgradable';
    ssh -q "${vm_name}" 'sudo apt-get upgrade --yes';
}

# Check if virsh is installed
command -v virsh >/dev/null 2>&1 || {
    printf "ERROR - virsh is not installed. Aborting.\n";
    exit 1;
}

# Require at least one "ACTION" verb and one "VM_NAME"
if [[ "${#}" -lt "2" ]] || [[ "${1}" = '-h' ]] || [[ "${1}" = '--help' ]]; then
    printf "A simple script to perform some actions on one or more VMs.
Usage:
  $(basename $0) 'start|update|reboot|shutdown' 'VM_NAME' ['VM_NAME' [...]]
  $(basename $0) 'check_(gluster|hadoop|kubernetes|...)' 'VM_NAME' ['VM_NAME' [...]]
       \n";
    exit 0;
fi

case ${1} in 
    start)
        shift 1;
        for _arg in "${@}"; do
            start "${_arg}";
        done
    ;;
    update)
        shift 1;
        for _arg in "${@}"; do
            update "${_arg}";
        done
    ;;
    reboot)
        shift 1;
        for _arg in "${@}"; do
            reboot "${_arg}";
        done
    ;;
    shutdown)
        shift 1;
        for _arg in "${@}"; do
            shutdown "${_arg}";
        done
    ;;
    check_gluster)
        shift 1;
        for _arg in "${@}"; do
            check_gluster "${_arg}";
        done
    ;;
    check_hadoop)
        shift 1;
        for _arg in "${@}"; do
            check_hadoop "${_arg}";
        done
    ;;
    check_kubernetes)
        shift 1;
        for _arg in "${@}"; do
            check_kubernetes "${_arg}";
        done
    ;;
    *)
        printf "Unknown action: ${1}\n" >&2;
        printf "Should be one of: 'start|update|reboot|shutdown'\n";
        exit 1;
    ;;
esac
