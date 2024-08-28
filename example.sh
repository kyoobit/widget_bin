#!/usr/bin/env bash

## Default(s)
__version__="0.0.1a";
## Stop the script execution if an error happens
set -o errexit
## Treat unset variables as an error
set -o nounset
## When one part of a pipe fails, the whole pipe should be considered failed
set -o pipefail

## -----------------------------------------------------------------------------

## Help message
read -r -d '' help_message << EOM
usage: $(basename $0) [-h|--help] ...

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
$ $(basename $0) ...

EOM

## -----------------------------------------------------------------------------

## Argument parsing.
while :
do
    case "$1" in
        -h | --help)
              echo "${help_message}";
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

message() {
    if [ -z "${debug}" ] && [ "${1}" == "DEBUG" ]; then
        do_nothing=true
    elif [ -z "${verbose}" ] && [ "${1}" == "INFO" ]; then
        do_nothing=true
    else
        echo "$(date '+[%Y-%m-%d %H:%M:%S %Z]') ${1}: ${2}";
    fi;
}

## -----------------------------------------------------------------------------

main() {
    messgae "DEBUG" "running script $0";

    message "DEBUG" "debug=${debug:-nilly}";
    message "DEBUG" "dryrun=${dryrun:-nilly}";
    message "DEBUG" "quite=${quite:-nilly}";
    message "DEBUG" "verbose=${verbose:-nilly}";

    message "DEBUG" "debug message"
    message "INFO" "INFO message"
    message "WARNING" "warning"

## ${varname:-word} If varname exists and isn't null, return its value; otherwise return "word".
## ${varname:=word} If varname exists and isn't null, return its value; otherwise set it to word and then return its value. 

## if [ -z "${dryrun}" ]; then
##     mkdir -p ${wrk};
## fi;

}

main;
