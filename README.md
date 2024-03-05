# Widget Bin

A collection of widget scripts, normally a single file to provide a tool for a simple purpose.

--------------------------------------------------------------------------------




# `get_address`

...




# `get_datetime`

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

# `get_maxmind_database`

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



