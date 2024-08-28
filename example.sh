#!/usr/bin/env bash

## Default(s)
__version__="0.0.1a";

## Stop the script execution if an error happens
#set -o errexit <-- breaks on argument case check
## Treat unset variables as an error
#set -o nounset
## When one part of a pipe fails, the whole pipe should be considered failed
#set -o pipefail

## -----------------------------------------------------------------------------

read -r -d '' HELP_MESSAGE <<- END_HELP_MESSAGE
usage: $(basename ${0}) [-h|--help] ...

...

optional arguments:
  -h, --help            Show this help message and exit.
  -v, --verbose
  -q, --quite
  --debug
  --dryrun
  --version

Program requires:
  ...

Program examples:
$ $(basename ${0}) ...

END_HELP_MESSAGE

## -----------------------------------------------------------------------------

## Argument parsing.
while :
do
    case "${1}" in
        -h | --help)
            echo "${HELP_MESSAGE}";
            exit 0;
        ;;
        -a | --abc)
            abc="$2";
            shift 2;
        ;;
        --debug)
            debug="debug";
            verbose="verbose";
            shift;
        ;;
        --dryrun)
            dryrun="dryrun";
            shift;
        ;;
        -q | --quite)
            quite="quite";
            shift;
        ;;
        -v | --verbose)
            verbose="verbose";
            shift;
        ;;
        --version)
            echo "$(basename $0) version: ${__version__}";
            exit 0;
        ;;
        --) # End of all options
            shift;
            break;
        ;;
        -*)
            echo "Unknown option: $1" >&2;
            echo "See help (-h|--help) for available options.";
            exit 1;
        ;;
        *)  # No more options
            break;
        ;;
    esac
done

function message() {
    if [ -z "${debug}" ] && [ "${1}" == "DEBUG" ]; then
        do_nothing=true
    elif [ -z "${verbose}" ] && [ "${1}" == "INFO" ]; then
        do_nothing=true
    else
        echo "$(date '+[%Y-%m-%d %H:%M:%S %Z]') ${1}: ${2}";
    fi;
}

## -----------------------------------------------------------------------------

function print_colors() {
    ## ENDC = '\033[0m'
    ## BOLD = '\033[1m'
    ## UNDERLINE = '\033[4m'
    for i in $(seq 90 96); do
        printf "\033[${i}m color test: 033[${i}m\033[0m\n";
        printf "\033[1m\033[${i}m color test: 033[1m 033[${i}m\033[0m\n";
    done;
}

function main() {

    messgae "DEBUG" "running script $0";

    message "DEBUG" "debug=${debug:-nilly}";
    message "DEBUG" "dryrun=${dryrun:-nilly}";
    message "DEBUG" "quite=${quite:-nilly}";
    message "DEBUG" "verbose=${verbose:-nilly}";

    message "DEBUG" "debug message"
    message "INFO" "INFO message"
    message "WARNING" "warning"

    print_colors;

    if [ -n "${dryrun}" ]; then
        message "WARNING" "Running in DRY-RUN mode, changes will be made!"
    fi;

    ## ${varname:-word} If varname exists and isn't null, return its value; otherwise return "word".
    ## ${varname:=word} If varname exists and isn't null, return its value; otherwise set it to word and then return its value. 
}

main;