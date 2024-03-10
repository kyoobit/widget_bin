# Widget Bin

A collection of widget scripts, normally a single file to provide a tool for a simple purpose.

--------------------------------------------------------------------------------




# `get_ciphers.sh`

A wrapper script to OpenSSL which attempts to enumerate available protocols and 
ciphers using the `openssl s_client` or similar libraries like LibreSSL. This is handy for systems where `nmap` cannot be installed. The `-openssl` option allows for a specific library binary path to be specified. The `--help` option has more information.

```
get_ciphers.sh -connect nateroyer.com
get_ciphers.sh -connect nateroyer.com -openssl /usr/bin/openssl
get_ciphers.sh -v -connect 10.255.0.1:8443 -servername www.example.com
get_ciphers.sh -v -connect 10.255.0.1 -port 8443 -protocols 'tls1_2 tls1_3'
```

Example output:

```
% bash get_ciphers.sh -connect nateroyer.com
* WARNING: Using 'nateroyer.com' for -servername option
* WARNING: Using default port '443' 
Starting get_ciphers.sh (0.0.5a) at Sun Mar 10 08:06:20 MDT 2024
Using openssl version: OpenSSL 3.2.1 30 Jan 2024 (Library: OpenSSL 3.2.1 30 Jan 2024)
-------------------------------------------------------------------------
OpenSSL scan report for nateroyer.com (nateroyer.com:443)
Checking protocol(s): ssl3 tls1 tls1_1 tls1_2 tls1_3
Client has 68 cipher(s) available
|
|   SSLv3 (ssl3)
|     ssl3 (-ssl3) Protocol not supported by s_client (s_client: unknown option: -ssl3)
|     ssl3 (-ssl3) No supported cipher suite found
|
|   TLSv1.0 (tls1)
|     tls1 (-tls1) No cipher suites, trying each cipher, takes awhile...
|     tls1 (-tls1) No supported cipher found
|
|   TLSv1.1 (tls1_1)
|     tls1_1 (-tls1_1) No cipher suites, trying each cipher, takes awhile...
|     tls1_1 (-tls1_1) No supported cipher found
|
|   TLSv1.2 (tls1_2)
|     ECDHE-RSA-AES256-GCM-SHA384
|     ECDHE-RSA-CHACHA20-POLY1305
|     ECDHE-RSA-AES128-GCM-SHA256
|     ECDHE-RSA-AES256-SHA384
|     ECDHE-RSA-AES128-SHA256
|     AES256-GCM-SHA384
|     AES128-GCM-SHA256
|     AES256-SHA256
|     AES128-SHA256
|
|   TLSv1.3 (tls1_3)
|     TLS_AES_256_GCM_SHA384
|     TLS_CHACHA20_POLY1305_SHA256
|     TLS_AES_128_GCM_SHA256
|
-------------------------------------------------------------------------
```




# `get_datetime.py`

List different time zones based on input or current datetime. This makes use of the [zoneinfo](https://docs.python.org/3/library/zoneinfo.html) added in Python 3.9. See `-h/--help` for available options.

* [get_datetime.py](https://github.com/kyoobit/widgets_bin/blob/main/get_datetime.py)

Example usage:

```
get_datetime.py
get_datetime.py 1234567890.1234
get_datetime.py 2009-02-14T00:31:30+0100
```

Example output:

```
Fri Feb 13 16:31:30 2009 (UTC-0700) MST
Fri Feb 13 23:31:30 2009 (UTC+0000) UTC
Unix timestamp: 1234567890
----------------------------------------------------------------
Fri Feb 13 23:31:30 2009 (UTC+0000) UTC  UTC
Fri Feb 13 23:31:30 2009 (UTC+0000) GMT  GMT
Sat Feb 14 12:31:30 2009 (UTC+1300) NZDT NZ
Sat Feb 14 10:31:30 2009 (UTC+1100) AEDT Australia/Sydney
Sat Feb 14 08:31:30 2009 (UTC+0900) JST  Asia/Tokyo
Sat Feb 14 08:31:30 2009 (UTC+0900) KST  Asia/Seoul
Sat Feb 14 07:31:30 2009 (UTC+0800) CST  Asia/Shanghai
Sat Feb 14 07:31:30 2009 (UTC+0800) +08  Asia/Singapore
Sat Feb 14 02:31:30 2009 (UTC+0300) +03  Asia/Qatar
Sat Feb 14 02:31:30 2009 (UTC+0300) MSK  Europe/Moscow
Sat Feb 14 00:31:30 2009 (UTC+0100) CET  Europe/Warsaw
Sat Feb 14 00:31:30 2009 (UTC+0100) CET  Europe/Copenhagen
Sat Feb 14 00:31:30 2009 (UTC+0100) CET  Europe/Paris
Fri Feb 13 23:31:30 2009 (UTC+0000) GMT  Europe/London
Fri Feb 13 23:31:30 2009 (UTC+0000) GMT  Atlantic/Reykjavik
Fri Feb 13 21:31:30 2009 (UTC-0200) -02  America/Sao_Paulo
Fri Feb 13 18:31:30 2009 (UTC-0500) EST  America/New_York
Fri Feb 13 17:31:30 2009 (UTC-0600) CST  America/Chicago
Fri Feb 13 16:31:30 2009 (UTC-0700) MST  America/Denver
Fri Feb 13 15:31:30 2009 (UTC-0800) PST  America/Los_Angeles
Fri Feb 13 13:31:30 2009 (UTC-1000) HST  Pacific/Honolulu
----------------------------------------------------------------
```

Example Python test usage:

```
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip pytest
python -m pytest -v get_datetime_test.py
```




# `get_ipaddress.py`

A wrapper script to the Python `ipaddress` module which provides information about IP addresses. Supplement information may be read from Maxmind GeoLite2 databases for additional information about IP addresses.

Example usage:

```
get_ipaddress.py 140.82.112.3 2a09:bac3:6596:1ceb::/64
get_ipaddress.py 140.82.112.3/25 2a09:bac3:6596:1ceb::2f8:1e
get_ipaddress.py 140.82.113.123 --in 140.82.112.0/23
```

Example output:

```
% python3 get_ipaddress.py 140.82.112.3 2a09:bac3:6596:1ceb::2f8:1e --geoinfo
address: 140.82.112.3
----------------------------------------------------------------
version           : 4
compressed        : 140.82.112.3
exploded          : 140.82.112.3
packed            : b'\x8cRp\x03'
reverse_pointer   : 3.112.82.140.in-addr.arpa
asn               : 36459
asn_network       : GITHUB
asn_organization  : 140.82.112.0/20
continent         : NA, North America
country           : US, United States
subdivisions      : None, None

address: 2a09:bac3:6596:1ceb::2f8:1e
----------------------------------------------------------------
version           : 6
compressed        : 2a09:bac3:6596:1ceb::2f8:1e
exploded          : 2a09:bac3:6596:1ceb:0000:0000:02f8:001e
packed            : b'*\t\xba\xc3e\x96\x1c\xeb\x00\x00\x00\x00\x02\xf8\x00\x1e'
reverse_pointer   : e.1.0.0.8.f.2.0.0.0.0.0.0.0.0.0.b.e.c.1.6.9.5.6.3.c.a.b.9.0.a.2.ip6.arpa
asn               : 13335
asn_network       : CLOUDFLARENET
asn_organization  : 2a09:bac3::/32
city              : Salinas
continent         : NA, North America
country           : US, United States
subdivisions      : CA, California
```




# `get_maxmind_database.sh`

Download one or more Maxmind GeoLite2 database editions using an API key. 
Optionally unpack the mmdb from the archive and remove the archive.

See Also:

* https://www.maxmind.com/en/geoip-databases
* https://dev.maxmind.com/geoip/geolite2-free-geolocation-data

* [get_maxmind_database.sh](https://github.com/kyoobit/widgets_bin/blob/main/get_maxmind_database.sh)

Example usage:

```
get_maxmind_database.sh --key <KEY> --database GeoLite2-ASN
get_maxmind_database.sh -u -e GeoLite2-ASN,GeoLite2-City -k <KEY>
```




# `raspberrypi_blinker.py`

A fun script that toggles GPIO pin power states on a Raspberry Pi which blinks dozens of LEDs wired to the system. That is it, just blinking LEDs for the fun of computing. The frequency of LED power state changes will increase and decrease with a configurable peak time option. A quiet period to turn on/off the LED blinking is also an option since some LEDs can be quite bright.



