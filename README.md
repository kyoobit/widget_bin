# Widget Bin

A collection of widget scripts, normally a single file to provide a tool for a simple purpose.

--------------------------------------------------------------------------------




# `get_address`

...




# `get_datetime`

...




# `get_maxmind_database`

Download one or more Maxmind GeoLite2 database editions using an API key. 
Optionally unpack the mmdb from the archive and remove the archive.

See Also:

* https://www.maxmind.com/en/geoip-databases
* https://dev.maxmind.com/geoip/geolite2-free-geolocation-data

* [get_maxmind_database.sh](https://github.com/kyoobit/widgets_bin/blob/main/get_maxmind_database.sh)

Example usage:

    get_maxmind_database.sh --key <KEY> --database GeoLite2-ASN
    get_maxmind_database.sh -u -e GeoLite2-ASN,GeoLite2-City -k <KEY>
