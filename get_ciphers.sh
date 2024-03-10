#!/usr/bin/env bash

## Default(s)
__name__=$(basename $0);
__version__="0.0.5a";
default_openssl=$(which openssl);
nginx_openssl=$(echo /usr/local/openresty/openssl*/bin/openssl);
default_port="443";
default_protocols="ssl3 tls1 tls1_1 tls1_2 tls1_3";
default_delay=0.125;

## Map protocol argument names to full names
## This is used to narrow the cipher suites to a specific protocol
## TODO: Handle old bash, looking at you macOS (bash 4+ associative arrays)
declare -A protocol_full_names=(
    [ssl3]='SSLv3' 
    [tls1]='TLSv1.0' 
    [tls1_1]='TLSv1.1' 
    [tls1_2]='TLSv1.2' 
    [tls1_3]='TLSv1.3' 
    );

## -----------------------------------------------------------------------------

## Help message
read -r -d '' help_message << EOM
Usage: ${__name__} -connect <addr|host> [...]

A wrapper script to OpenSSL which attempts to enumerate available protocols and 
ciphers using the openssl s_client or similar libraries like LibreSSL.

NOTE: The cipher suites tested are based on the openssl binary used. 

The openssl in your \$PATH is used by default. Use the -openssl option to use a 
specific openssl such as the one compiled for use with NIGNX. Every cipher suite 
compiled in openssl (openssl ciphers -v 'ALL:eNULL') is tried with the protocol 
marked on the cipher suite. The -protocols option overrides the default 
set of protocols: '${default_protocols}'

List all ciphers suites compiled for your openssl:
When supported, the "-s Only supported ciphers" option is used.
  openssl ciphers -s -v 'ALL:eNULL'
  openssl ciphers -v 'ALL:eNULL'

Ciphers suite name translation:
  https://www.openssl.org/docs/manmaster/man1/openssl-ciphers.html#CIPHER-SUITE-NAMES

Required arguments:
  -connect <addr|host>
  -connect <addr|host>:<port> 
                        FQDN host or address to test. The port to use may 
                        be set as part of the host or address or passed in using
                        the -port option.

Optional arguments:
  -port <int>           The port to use (Default: ${default_port})
  -protocols 'a b ...'  Protocols to test (Default: '${default_protocols}')
  -servername <host>    SNI server name to use (-connect is used as default)
  -openssl <path>       Use a specific openssl binary (Default: ${default_openssl})
  -delay <float>        Number of seconds between tests (Default: ${default_delay})

  -h, --help            Show this help message and exit.
  -v, --verbose         Increase the amount of information
  --debug               Increase the amount of information to spam level
  --version

Program examples:
  ${__name__} -connect nateroyer.com
  ${__name__} -connect nateroyer.com -openssl /usr/bin/openssl
  ${__name__} -connect nateroyer.com -openssl ${nginx_openssl}
  ${__name__} -v -connect 10.255.0.1:8443 -servername www.example.com
  ${__name__} -v -connect 10.255.0.1 -port 8443 -protocols 'tls1_2 tls1_3'

EOM

## -----------------------------------------------------------------------------

## Argument parsing.
while :
do
    case "$1" in
        -h | --help)
              echo "${help_message}";
              echo "";
              exit 0;
        ;;
        -connect | --connect)
            connect="$2";
            shift 2;
        ;;
        -port | --port)
            port="$2";
            shift 2;
        ;;
        -protocols | --protocols | -protocol | --protocol)
            protocols="$2";
            shift 2;
        ;;
        -servername | --servername)
            servername="$2";
            shift 2;
        ;;
        -openssl | --openssl)
            my_openssl="$2";
            shift 2;
        ;;
        -delay | --delay)
            delay="$2";
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
            echo "$(which openssl) version -a";
            openssl version -a;
            echo "";
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

## Log message function
## -----------------------------------------------------------------------------
## message LEVEL MESSGAE PREFIX
function message() {
    ## message(LEVEL MESSAGE PREFIX)
    if [[ -z "${debug}" ]] && [[ "${1}" == "DEBUG" ]]; then
        do_nothing=true
    elif [[ -z "${verbose}" ]] && [[ "${1}" == "INFO" ]]; then
        do_nothing=true
    else
        #echo "$(date '+[%Y-%m-%d %H:%M:%S %Z]') ${1}: ${2}";
        echo "${3:-*} ${1}: ${2}";
    fi;
}

## General options
## -----------------------------------------------------------------------------
message "DEBUG" "debug=${debug:-nilly}";
message "DEBUG" "delay=${delay:=${default_delay}}";
message "DEBUG" "dryrun=${dryrun:-nilly}";
message "DEBUG" "quite=${quite:-nilly}";
message "DEBUG" "verbose=${verbose:-nilly}";

## Check if `connect' is set and exit if it is not
## -----------------------------------------------------------------------------
message "DEBUG" "connect=${connect:-nilly}";
if [ -z "${connect}" ]; then
    message "ERROR" "The -connect <addr|host> option is required"
    exit 1;
fi

## Check if `servername' is not set and set if it is not
## -----------------------------------------------------------------------------
message "DEBUG" "servername=${servername:-nilly}";
if [ -z "${servername}" ]; then
    servername=$(echo "${connect}" | sed -n -E 's/([^:]+)(.*)/\1/p');
    message "WARNING" "Using '${servername}' for -servername option";
    message "DEBUG" "servername=${servername:-nilly}";
fi

## Check if `port' is not set
## -----------------------------------------------------------------------------
message "DEBUG" "port=${port:-nilly}";
if [ -z "${port}" ]; then
    port=$(echo "${connect}" | sed -n -E 's/([^:]+)(.*)/\2/p');
    if [ -z "${port}" ]; then
        port="${default_port}";
        message "WARNING" "Using default port '${default_port}' ";
        connect="${connect}:${default_port}";
        message "DEBUG" "connect=${connect:-nilly} (via -connect + ':${default_port}')";
    else
        message "DEBUG" "port=${port:-nilly} (via -connect)";
    fi
else
    message "DEBUG" "port=${port:-nilly} (via -port)";
    connect="${connect}:${port}";
    message "DEBUG" "connect=${connect:-nilly} (via -connect + ':' + -port)";
fi

## Header
## -----------------------------------------------------------------------------
echo "Starting ${__name__} (${__version__}) at $(date)";
## openssl path and version information
message "DEBUG" "my_openssl=${my_openssl:=${default_openssl}}";
echo "Using openssl version: $(${my_openssl} version)";
echo "-------------------------------------------------------------------------";
if [[ -n "${debug}" ]]; then
    message "DEBUG" "${my_openssl} version -a";
    ${my_openssl} version -a;
fi;
echo "OpenSSL scan report for ${servername} (${connect})";

## Configured protocols
message "DEBUG" "protocols=${protocols:=${default_protocols}}";
echo "Checking protocol(s): ${protocols:-nilly}";

## Gather all ciphers available
## Not all libraries support the -s option
only_supported_ciphers=$(${my_openssl} ciphers -help 2>&1 | grep 'Only supported ciphers');
message "DEBUG" "only_supported_ciphers=${only_supported_ciphers:-nilly}";
if [[ -n "${only_supported_ciphers}" ]]; then
    only_supported_ciphers='-s';
fi
message "INFO" "all ciphers: ${my_openssl} ciphers ${only_supported_ciphers} -v 'ALL:eNULL' | awk -v '{print \$1}' | tr '\n' ' ';" "|    ";
all_ciphers=$(${my_openssl} ciphers ${only_supported_ciphers} -v 'ALL:eNULL' | awk '{print $1}' | tr '\n' ' ');
message "DEBUG" "all_ciphers=${all_ciphers}"
echo "Client has $(echo ${all_ciphers} | wc -w | sed 's% %%g') cipher(s) available";

## Check if the library supports the cipher suites option
## Not all libraries support the -ciphersuites option
has_ciphersuites_option=$(${my_openssl} s_client -help 2>&1 | grep "\-ciphersuites");
message "DEBUG" "has_ciphersuites_option=${has_ciphersuites_option:-nilly}";

## openssl s_client wrapper function
## -----------------------------------------------------------------------------
function s_client() {
    ## s_client $1              $2            $3               $4           $5
    ## s_client "${my_openssl}" "${protocol}" "${ciphersuite}" "${connect}" "${servername}"
    ## openssl s_client -help 2>&1 | grep cipher
    ## -ciphersuites val          Specify TLSv1.3 ciphersuites to be used
    ## -cipher val                Specify TLSv1.2 and below cipher list to be used
    ## Use TLSv3 cipher suites when available
    if [[ "${2}" == "tls1_3" && -n "${has_ciphersuites_option}" ]]; then
        echo "echo 'GET / HTTP/1.1' | ${1} s_client -${2} -ciphersuites ${3} -connect ${4} -servername ${5} 2>&1";
        echo 'GET / HTTP/1.1' | ${1} s_client -${2} -ciphersuites ${3} -connect ${4} -servername ${5} 2>&1;
    else
        echo "echo 'GET / HTTP/1.1' | ${1} s_client -${2} -cipher ${3} -connect ${4} -servername ${5} 2>&1";
        echo 'GET / HTTP/1.1' | ${1} s_client -${2} -cipher ${3} -connect ${4} -servername ${5} 2>&1;
    fi
}

function test_cipher() {
    ## Map the input to the variable names, better way?
    ## test_cipher "${connect}" "${servername}" "${protocol}" "${cipher}" result;
    connect=${1};
    servername=${2};
    protocol=${3};
    cipher=${4};
    result=${5};
    message "DEBUG" "test_cipher \"${connect}\" \"${servername}\" \"${protocol}\" \"${cipher}\"";
    ## Connect to the address with the server name using the protocol and cipher suite
    message "DEBUG" "protocol=${protocol} (-${protocol}) cipher=${cipher} connect=${connect} servername=${servername}";
    result=$(s_client "${my_openssl}" "${protocol}" "${cipher}" "${connect}" "${servername}")
    message "DEBUG" "${result:-nilly}";
    ## Check for "alert handshake failure" and move onto the next cipher suite
    ## 4569357760:error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure:ssl/record/rec_layer_s3.c:1544:SSL alert number 40
    alert_handshake_failure=$(echo "${result}" | grep "alert handshake failure");
    if [[ -n "${alert_handshake_failure}" ]]; then
        if [[ -n "${verbose}" ]]; then
            echo "|     ${cipher} Not supported (alert handshake failure)";
        fi
        result='continue';
        return
    fi
    ## Check for "no cipher match" and move onto the next cipher
    no_cipher_match=$(echo "${result}" | grep "no cipher match");
    if [[ -n "${no_cipher_match}" ]]; then
        if [[ -n "${verbose}" ]]; then
            echo "|     ${cipher} Not supported (no cipher match)";
        fi
        result='continue';
        return
    fi
    ## Check for "no peer certificate available" general error 
    no_peer_cert=$(echo "${result}" | grep "no peer certificate available");
    if [[ -n "${no_peer_cert}" ]]; then
        if [[ -n "${verbose}" ]]; then
            echo "|     ${cipher} Not supported (no peer certificate available)";
        fi
        result='continue';
        return
    fi
    ## Check for no result and move onto the next cipher
    if [[ -z "${result}" ]]; then
        echo "|     ${cipher} No result returned by openssl s_client";
        result='continue';
        return
    fi
    ## Cipher suite is supported
    message "INFO" "$(echo "${result}" | head -n 1)" "|    ";
    echo "|     ${cipher}";
    result='supported';
}

function test_ciphersuite() {
    ## Map the input to the variable names, better way?
    ## test_ciphersuite "${connect}" "${servername}" "${protocol}" "${cipher}" result;
    connect=${1};
    servername=${2};
    protocol=${3};
    ciphersuite=${4};
    result=${5};
    message "DEBUG" "test_ciphersuite: \"${connect}\" \"${servername}\" \"${protocol}\" \"${ciphersuite}\"";
    ## Connect to the address with the server name using the protocol and cipher suite
    message "DEBUG" "test_ciphersuite: protocol=${protocol} (-${protocol}) ciphersuite=${ciphersuite} connect=${connect} servername=${servername}";
    result=$(s_client "${my_openssl}" "${protocol}" "${ciphersuite}" "${connect}" "${servername}");
    message "DEBUG" "test_ciphersuite: result=${result:-nilly}";
    ## Check for "s_client: Option unknown option" and move onto the next protocol
    option_unknown=$(echo "${result}" | tr '[:upper:]' '[:lower:]' | grep "option unknown");
    if [[ -n "${option_unknown}" ]]; then
        echo "|     ${protocol} (-${protocol}) Protocol not supported by s_client (${option_unknown})";
        result='break';
        return
    fi
    ## Check for "s_client: Unknown option" and move onto the next protocol
    unknown_option=$(echo "${result}" | tr '[:upper:]' '[:lower:]' | grep "unknown option");
    if [[ -n "${unknown_option}" ]]; then
        echo "|     ${protocol} (-${protocol}) Protocol not supported by s_client (${unknown_option})";
        result='break';
        return
    fi
    ## Check for "alert protocol version" and move onto the next protocol
    ## 4369243584:error:1409442E:SSL routines:ssl3_read_bytes:tlsv1 alert protocol version:ssl/record/rec_layer_s3.c:1544:SSL alert number 70
    alert_protocol_version=$(echo "${result}" | tr '[:upper:]' '[:lower:]' | grep "alert protocol version");
    if [[ -n "${alert_protocol_version}" ]]; then
        echo "|     ${protocol} (-${protocol}) Protocol not supported by server (alert protocol version)";
        result='break';
        return
    fi
    ## Check for "alert handshake failure" and move onto the next cipher suite
    ## 4569357760:error:14094410:SSL routines:ssl3_read_bytes:sslv3 alert handshake failure:ssl/record/rec_layer_s3.c:1544:SSL alert number 40
    alert_handshake_failure=$(echo "${result}" | tr '[:upper:]' '[:lower:]' | grep "alert handshake failure");
    if [[ -n "${alert_handshake_failure}" ]]; then
        if [[ -n "${verbose}" ]]; then
            echo "|     ${ciphersuite} Not supported by server (alert handshake failure)";
        fi
        result='continue';
        return
    fi
    ## Check for "no peer certificate available" general error 
    no_peer_cert=$(echo "${result}" | tr '[:upper:]' '[:lower:]' | grep "no peer certificate available");
    if [[ -n "${no_peer_cert}" ]]; then
        if [[ -n "${verbose}" ]]; then
            echo "|     ${ciphersuite} Not supported by server (no peer certificate available)";
        fi
        result='continue';
        return
    fi
    ## Check for "no cipher match" and move onto the next cipher suite
    no_cipher_match=$(echo "${result}" | grep "no cipher match");
    if [[ -n "${no_cipher_match}" ]]; then
        if [[ -n "${verbose}" ]]; then
            echo "|     ${ciphersuite} Not supported by server (no cipher match)";
        fi
        result='continue';
        return
    fi
    ## Check for no result and move onto the next cipher suite
    if [[ -z "${result}" ]]; then
        echo "|     ${ciphersuite} No result returned by openssl s_client";
        result='continue';
        return
    fi
    ## Cipher suite is supported
    message "INFO" "$(echo "${result}" | head -n 1)" "|    ";
    echo "|     ${ciphersuite}";
    result='supported';
}

## Test
## -----------------------------------------------------------------------------
echo "|"; # leading space
for protocol in ${protocols}; do
    message "DEBUG" "protocol=${protocol}";
    message "DEBUG" "protocol_full_names[${protocol}]=${protocol_full_names[${protocol}]}";
    protocol_full_name=${protocol_full_names[${protocol}]:=Unknown};
    message "DEBUG" "protocol_full_name=${protocol_full_name}";
    echo "|   ${protocol_full_name} (${protocol})";
    ## Check for matching cipher suites for the protocol
    message "INFO" "${my_openssl} ciphers ${only_supported_ciphers} -v 'ALL:eNULL' | awk -v protocol=${protocol_full_name} '(\$2==protocol){print \$1}' | tr '\n' ' ';" "|    ";
    ciphersuites=$(${my_openssl} ciphers ${only_supported_ciphers} -v 'ALL:eNULL' | awk -v protocol=${protocol_full_name} '($2==protocol){print $1}' | tr '\n' ' ');
    message "DEBUG" "${protocol_full_name} (${protocol}) ciphersuites=${ciphersuites}"
    ## Note no support for the protocol
    if [[ -z "${ciphersuites}" ]]; then
        echo "|     ${protocol} (-${protocol}) No cipher suites, trying each cipher, takes awhile..."
        supported="";
        ## Test each cipher from all ciphers available
        for cipher in ${all_ciphers}; do
            test_cipher "${connect}" "${servername}" "${protocol}" "${cipher}" result;
            message "DEBUG" "test_cipher cipher=${cipher} result=${result}"
            if [[ "${result}" == "break" ]]; then
                message "DEBUG" "break from protocol"
                break
            elif [[ "${result}" == "continue" ]]; then
                message "DEBUG" "continue to next cipher"
                continue
            elif [[ "${result}" == "supported" ]]; then
                supported="supported";
            else
                message "DEBUG" "done with ciphers"
            fi
            message "DEBUG" "Slow your roll sleep ${delay};"
            sleep ${delay};
        done
        if [[ -z "${supported}" ]]; then
            echo "|     ${protocol} (-${protocol}) No supported cipher found"
        fi
    ## Test each cipher suite in the protocol
    else
        supported="";
        for ciphersuite in ${ciphersuites}; do
            test_ciphersuite "${connect}" "${servername}" "${protocol}" "${ciphersuite}" result;
            message "DEBUG" "test_ciphersuite ciphersuite=${ciphersuite} result=${result}"
            if [[ "${result}" == "break" ]]; then
                message "DEBUG" "break from protocol"
                break
            elif [[ "${result}" == "continue" ]]; then
                message "DEBUG" "continue to next ciphersuite"
                continue
            elif [[ "${result}" == "supported" ]]; then
                supported="supported";
            else
                message "DEBUG" "done with ciphersuites"
            fi
            message "DEBUG" "Slow your roll sleep ${delay};"
            sleep ${delay};
        done
        if [[ -z "${supported}" ]]; then
            echo "|     ${protocol} (-${protocol}) No supported cipher suite found"
        fi
    fi
    echo "|"; # trailing space after each protocol
done
echo "-------------------------------------------------------------------------";
echo ""; # trailing space