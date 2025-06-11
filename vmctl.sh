#!/usr/bin/env bash

set -o errexit   # abort on nonzero exit status
set -o nounset   # abort on unbound variable
set -o pipefail  # don't hide errors within pipes

log() {
    printf "[$(date '+%Y-%m-%d %H:%M:%S')] INFO - ${*}\n";
}

check_hadoop() {
    vm_name="${1}";
    log "Checking hadoop services on ${vm_name}...";
    printf -- "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
    # ...not implemented yet
}

check_kubernetes() {
    vm_name="${1}";
    log "Checking kubernetes services on ${vm_name}...";
    printf -- "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
    # ...not implemented yet
}

destroy() {
    vm_name="${1}";
    log "Destroy ${vm_name}...";
    printf -- "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
    virsh destroy "${vm_name}";
}

poweroff() {
    vm_name="${1}";
    log "Shutdown ${vm_name}...";
    printf -- "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
    # Send an ACPI shutdown signal (/sys/firmware/acpi)
    virsh shutdown "${vm_name}";
}

reboot() {
    vm_name="${1}";
    log "Rebooting ${vm_name}...";
    printf -- "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
    ssh -q "${vm_name}" 'sudo systemctl reboot';
}

shutdown() {
    vm_name="${1}";
    log "Shutdown ${vm_name}...";
    printf -- "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
    ssh -q "${vm_name}" 'sudo systemctl poweroff';
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
    printf -- "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
    ssh -q "${vm_name}" 'apt list --upgradable 2>/dev/null';
    printf -- "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - \n"
    ssh -q "${vm_name}" 'sudo apt-get upgrade --yes';
}

help() {
    _action="${1}";

    # When _action is defined, ass-u-me the _action is unknown
    if [[ -n "${_action}" ]]; then
        printf "ERROR - Unknown action: ${_action}\n\n";
    fi

    printf "A simple script to perform common actions on one or more VMs.

USAGE:
  $(basename $0) 'ACTION' 'VM_NAME' ['VM_NAME' [...]]

ACTIONS:

  OS ACTIONS
  update            issue 'apt-get update' and 'apt-get upgrade'
  reboot            issue 'systemctl reboot'
  shutdown          issue 'systemctl poweroff'

  VIRT ACTIONS
  start             issue 'virsh start'
  poweroff          issue 'virsh shutdown' (ACPI shutdown signal)
  destroy           issue 'virsh destroy' (forced poweroff)

  HEALTH ACTIONS
  check_hadoop      Check the general health of Hadoop services
  check_kubernetes  Check the general health of Kubernetes services

~/.profile
  ## WIDGETS!
  ## git clone https://github.com/kyoobit/widget_bin.git
  ## For silly VMs control
  alias vmctl='\$HOME/widget_bin/vmctl.sh \$*';

";

    # When _action is defined, ass-u-me an error
    if [[ -n "${_action}" ]]; then
        exit 1;
    else
        exit 0;
    fi
}

# Require at least two arguments: "ACTION" "VM_NAME" or call the "help" function
if [[ "${#}" -lt "2" ]] || [[ "${1}" = '-h' ]] || [[ "${1}" = '--help' ]]; then
    help "";
fi

# Check if virsh is installed
command -v virsh >/dev/null 2>&1 || {
    printf "ERROR - virsh is not installed. Aborting.\n";
    exit 1;
}

action="${1}";

# Shift the action out of the arguments to pass to the function
shift 1;

# Check if the "action" function is defined, else call the "help" function
if declare -f "${action}" > /dev/null 2>&1; then
    for _arg in "${@}"; do
        "$action" "${_arg}"
    done
else
    help "${action}";
fi
