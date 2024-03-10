#!/usr/bin/env python3

import ipaddress
import logging

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from sys import exc_info

## python -m pip install --upgrade pip geoip2
try:
    import geoip2.database
    import geoip2.errors
except:
    pass


__version__ = '0.0.2a'

PROGRAM_NAME = Path(__file__).name


## -----------------------------------------------------------------------------
def echo(item, attr, **kwargs):
    """Print the attribute value for a provided item

    item <obj>: object to attempt value attribute access
    attr <str>: attribute key name

    **kwargs
      offset <int>: Right justify value used in the print statement
        Default: 18
    """
    offset = kwargs.get('offset', 18)
    value = False
    if isinstance(item, dict) and item.get(attr, False):
        value = item.get(attr)
    elif hasattr(item, attr):
        value = getattr(item, attr, False)
    if value:
        print(f"{attr:<{offset}}: {value}")


## -----------------------------------------------------------------------------
def get_geoinfo(address, **kwargs):
    """"""
    logging.debug(f"get_geoinfo - address: {address}")
    logging.debug(f"get_geoinfo - **kwargs: {kwargs}")
    geoinfo = {}

    ## Query ASN data for the addres 
    try:
        geolite2_asn = geoip2.database.Reader(kwargs.get('geolite2_asn'))
        result = geolite2_asn.asn(str(address))
        geoinfo.update(asn = result.autonomous_system_number)
        geoinfo.update(asn_network = result.autonomous_system_organization)
        geoinfo.update(asn_organization = str(result.network))  # IPv4Network
    except geoip2.errors.AddressNotFoundError:
        logging.debug(f"get_geoinfo - {address} asn query {err}")
    except Exception as err:
        logging.error(f"get_geoinfo - {address} asn query {err}")

    ## Query address data
    try:
        geolite2_city = geoip2.database.Reader(kwargs.get('geolite2_city'))
        result = geolite2_city.city(str(address))
        geoinfo.update(city = result.city.names.get('en'))
        geoinfo.update(continent = "{}, {}".format(
            result.continent.code,
            result.continent.names.get('en'),
            ))
        geoinfo.update(country = "{}, {}".format(
            result.country.iso_code,
            result.country.names.get('en'),
            ))
        #geoinfo.update(location = result.location)
        #geoinfo.update(postal = result.postal.code)
        geoinfo.update(subdivisions = "{}, {}".format(
            result.subdivisions.most_specific.iso_code,
            result.subdivisions.most_specific.name,
            ))
    except geoip2.errors.AddressNotFoundError:
        logging.debug(f"get_geoinfo - {address} city query {err}")
    except Exception as err:
        logging.error(f"get_geoinfo - {address} city query {err}")

    return geoinfo


## -----------------------------------------------------------------------------
def main(*args, **kwargs):
    """Print information about IP addresses to stdout

    **kwargs:
      addresses <list>: A list of IP address strings
      offset <int>: Used to offset key: value text formatting
      verbose <bool>: Include additional information on each address
    """
    logging.debug(f"main - *args: {args}")
    logging.debug(f"main - **kwargs: {kwargs}")

    addresses = kwargs.get('addresses')
    if addresses is None:
        raise ValueError("`addresses' should not be None-Type")

    ip_network = kwargs.get('ip_network', False)
    if ip_network:
        ip_network = ipaddress.ip_network(ip_network, strict=False)
    logging.debug(f"main - ip_network {type(ip_network)}: {ip_network!r}")

    offset = int(kwargs.get('offset', 18))
    kwargs.update(offset = offset) # pass through, as needed

    for address in addresses:
        logging.debug(f"main - address {type(address)}: {address!r}")
        print(f"address: {address}")
        print("----------------------------------------------------------------")
        try:
            if address.find('/') != -1:
                logging.debug("main - ass-u-me ipaddress.ip_network")
                address = ipaddress.ip_network(address, strict=False)
            else:
                logging.debug("main - ass-u-me ipaddress.ip_address")
                address = ipaddress.ip_address(address)
        except Exception as err:
            logging.error(f"ERROR: `{address}' {err}")
            print("")
            continue
        logging.debug(f"main - address {type(address)}: {address!r}")

        echo(address, 'version', **kwargs)
        echo(address, 'compressed', **kwargs)
        echo(address, 'exploded', **kwargs)
        echo(address, 'packed', **kwargs)
        echo(address, 'broadcast_address', **kwargs)
        echo(address, 'hostmask', **kwargs)
        echo(address, 'reverse_pointer', **kwargs)
        echo(address, 'netmask', **kwargs)
        echo(address, 'network_address', **kwargs)
        echo(address, 'num_addresses', **kwargs)
        if hasattr(address, 'hosts'):
            ## This is slow for large networks
            if kwargs.get('verbose', False) or address.num_addresses <= 1024:
                hosts = list(address.hosts())
                print(f"{'hosts':<{offset}}: {hosts[0]} - {hosts[-1]}")
            else:
                print(f"{'hosts':<{offset}}: <first - last> (-v)")
        echo(address, 'prefixlen', **kwargs)
        echo(address, 'is_link_local', **kwargs)
        echo(address, 'is_loopback', **kwargs)
        echo(address, 'is_multicast', **kwargs)
        echo(address, 'is_private', **kwargs)
        echo(address, 'is_reserved', **kwargs)
        echo(address, 'is_site_local', **kwargs)
        echo(address, 'is_unspecified', **kwargs)
        echo(address, 'with_prefixlen', **kwargs)
        echo(address, 'with_netmask', **kwargs)
        echo(address, 'with_hostmask', **kwargs)
        echo(address, 'ipv4_mapped', **kwargs)
        echo(address, 'sixtofour', **kwargs)
        echo(address, 'teredo', **kwargs)

        if ip_network:
            print("")
            print(f"{str(address)} in network {ip_network}: {(address in ip_network)}")

        # Additional module options not handled currently
        """
        overlaps(other)
        print(f"{'overlaps':<{offset}}: {ip_network.overlaps(address)}")
        address_exclude(network)
        subnets(prefixlen_diff=1, new_prefix=None)
        print(f"{'subnet_of':<{offset}}: {ip_network.subnet_of(address)}")
        supernet(prefixlen_diff=1, new_prefix=None)
        print(f"{'supernet_of':<{offset}}: {ip_network.supernet_of(address)}")
        subnet_of(other)
        supernet_of(other)
        compare_networks(other)
        """

        # Print additional GEO information
        if kwargs.get('geoinfo', False):
            geoinfo = get_geoinfo(address, **kwargs)
            echo(geoinfo, 'asn', **kwargs)
            echo(geoinfo, 'asn_network', **kwargs)
            echo(geoinfo, 'asn_organization', **kwargs)
            echo(geoinfo, 'city', **kwargs)
            echo(geoinfo, 'continent', **kwargs)
            echo(geoinfo, 'country', **kwargs)
            echo(geoinfo, 'subdivisions', **kwargs)

        #print("--------------------------------")
        print("")


## -----------------------------------------------------------------------------
if __name__ == '__main__':
    parser = ArgumentParser(
        prog=PROGRAM_NAME,
        description=f"""
A wrapper script to the Python ipaddress module which provides information about 
IP addresses. Supplement information may be read from Maxmind GeoLite2 databases 
for additional information about IP addresses.

See Also:
  https://docs.python.org/3/library/ipaddress.html

Example Usage:
$ {PROGRAM_NAME} 140.82.112.3 2a09:bac3:6596:1ceb::/64
$ {PROGRAM_NAME} 140.82.112.3/25 2a09:bac3:6596:1ceb::2f8:1e
$ {PROGRAM_NAME} 140.82.113.123 --in 140.82.112.0/23
        """,
        formatter_class=RawDescriptionHelpFormatter,
        )
    parser.add_argument('addresses', metavar='<address>', nargs='+',
        help='IP network address(es)')
    parser.add_argument('--debug', action='store_true',
        help='run with noisy debug message output')
    parser.add_argument('--version', '-V', action='version',
        version=f"version {__version__}")
    parser.add_argument('--verbose', '-v', action='count', default=False,
        help='run with verbose message output')
    parser.add_argument('--in', metavar='<network>', dest='ip_network', default=False,
        help='check if an address is in a network')
    parser.add_argument('--geoinfo', '-g', action='store_true',
        help='lookup info for the address in GeoLite2 databases (Default: False)')
    parser.add_argument('--geolite2-asn', default='./GeoLite2-ASN.mmdb', metavar='<path>',
        help='path to a GeoLite2-ASN database (Defaut: ./GeoLite2-ASN.mmdb)')
    parser.add_argument('--geolite2-city', default='./GeoLite2-City.mmdb', metavar='<path>',
        help='path to a GeoLite2-ASN database (Defaut: ./GeoLite2-City.mmdb)')
    parser.set_defaults(func=main)
    argv, remaining_argv = parser.parse_known_args()

    # Setup logging
    logger = logging.getLogger()
    console_handler = logging.StreamHandler()
    log_level = logging.WARNING
    if argv.debug:
        log_level = logging.DEBUG
    elif argv.verbose:
        log_level = logging.INFO
    logger.setLevel(log_level)
    console_handler.setLevel(log_level)
    formatter = logging.Formatter("%(message)s".format(name = PROGRAM_NAME))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Pass parsed arguments to main
    try:
        argv.func(cli=True, remaining_argv=remaining_argv, **vars(argv))
    # Throw up on exceptions
    except Exception as err:
        logging.error("{exe_info}; {err}".format(exe_info = exc_info()[0], err = err))
        if argv.debug:
            raise
