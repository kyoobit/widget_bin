#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
from re import search, IGNORECASE
from pathlib import Path
from sys import exit
from time import time, tzname
from zoneinfo import ZoneInfo, available_timezones


__version__ = '0.0.1c'

DEFAULT_FORMAT = '%a %b %d %H:%M:%S %Y (UTC%z) %Z'
DEFAULT_FORMAT_ISO = '%Y-%m-%d %H:%M:%S (UTC%z) %Z'
DEFAULT_LOCALZONE = 'America/Denver'
PROGRAM_NAME = Path(__file__).name

class Kolor(object):

    ## https://en.wikipedia.org/wiki/ANSI_escape_code
    __color_codes = {
        'normal': 0,
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 35,
        'cyan': 36,
        'white': 37,
    }
    __style_codes = {
        'normal': 0,
        'bold': 1,
        'faint': 2,
        'italic': 3,
        'underline': 4,
        'blink': 5,
        'rapid blink': 6,
        'double underline': 21,
    }
    __background_codes = {
        'normal': 0,
        'black': 40,
        'red': 41,
        'green': 42,
        'yellow': 43,
        'blue': 44,
        'magenta': 45,
        'cyan': 46,
        'white': 47,
    }

    def __call__(self, text=None, **kwargs):
        """Return a string in a ANSI escaped color/style/background codes"""
        if text is None or kwargs.get('color') is None:
            return text

        ## Handle setting bright values
        if kwargs.get('bright', False):
            background = f"{self.__background_codes.get(str(kwargs.get('background')).lower(), 0) + 60};"
        else:
            background = f"{self.__background_codes.get(str(kwargs.get('background')).lower(), 0)};"

        ## Handle setting style values
        style = f"{self.__style_codes.get(str(kwargs.get('style')).lower(), 0)};"

        ## Handle setting color values
        if kwargs.get('bright', False):
            color = f"{self.__color_codes.get(str(kwargs.get('color')).lower(), 0) + 60}m"
        else:
            color = f"{self.__color_codes.get(str(kwargs.get('color')).lower(), 0)}m"

        return f"\033[{background}{style}{color}{text}\033[0m"


class DT(object):

    @staticmethod
    def resolve_input(dt_in:str, **kwargs) -> datetime:
        """Return a datetime object"""
        debug = kwargs.get('debug', False)

        ## Debug message
        if debug:
            print(f"DEBUG: DT.resolve_input - dt_in {type(dt_in)}: {dt_in!r}")
            print(f"DEBUG: DT.resolve_input - **kwargs {type(kwargs)}: {kwargs!r}")

        ## Current datetime WITH tzinfo set to UTC
        ## https://docs.python.org/3/library/datetime.html#datetime.datetime.now
        now = datetime.now(tz=ZoneInfo('UTC'))

        ## Debug message
        if debug:
            print(f"DEBUG: DT.resolve_input - now {type(now)}: {now!r}")

        ## Return UTC now if the dt_in is empty
        if not dt_in:
            return now

        ## Resolve Unix epoch timestamps (also matches floats)
        ## 1234567890 == Fri Feb 13 23:31:30 2009 (UTC+0000) UTC
        m = search(r'^(?P<seconds>\d+(\.\d+)?)$', dt_in)
        if m is not None:
            _EPOCH = datetime.fromtimestamp(float(dt_in), tz=ZoneInfo('UTC'))
            ## Debug message
            if debug:
                print(f"DEBUG: DT.resolve_input - _EPOCH {type(_EPOCH)}: {_EPOCH!r}")
            return _EPOCH

        ## Resolve ISO 86001 datetime format
        try:
            _ISO_86001 = dt_in
            if _ISO_86001.endswith('Z'):
                _ISO_86001 = _ISO_86001.replace('Z', '+00:00')
            elif search(r'.*[\+\-]\d\d:\d\d$', dt_in) is None:
                _ISO_86001 += '+00:00'
            _ISO_86001 = datetime.fromisoformat(_ISO_86001)
            ## Debug message
            if debug:
                print(f"DEBUG: DT.resolve_input - _ISO_86001 {type(_ISO_86001)}: {_ISO_86001!r}")
            return _ISO_86001
        except ValueError:
            pass

        ## Resolve using a provided datetime format
        if kwargs.get('fmt', False):
            _FMT = datetime.strptime(dt_in, kwargs.get('fmt'))
            ## Debug message
            if debug:
                print(f"DEBUG: DT.resolve_input - _FMT {type(_FMT)}: {_FMT!r}")
            return _FMT

        ## Simple map for month names to int values
        month_to_int = {
            'jan': 1,
            'feb': 2,
            'mar': 3,
            'apr': 4,
            'may': 5,
            'jun': 6,
            'jul': 7,
            'aug': 8,
            'sep': 9,
            'oct': 10,
            'nov': 11,
            'dec': 12,
        }

        ## Simple map for abbreviated time zone names to known zone names
        abbr_to_zone = {
            'BJT': 'Asia/Singapore', # Beijing Time, China Standard Time
            'BT':  'Europe/London',  # British Time
            'BST': 'Europe/London',  # British Summer Time
            'ET':  'US/Eastern',     # US timezone
            'EST': 'US/Eastern',     # US timezone
            'EDT': 'US/Eastern',     # US timezone
            'CT':  'US/Central',     # US timezone
            'CST': 'US/Central',     # US timezone
            'CDT': 'US/Central',     # US timezone
            'MT':  'US/Mountain',    # US timezone
            'MST': 'US/Mountain',    # US timezone
            'MDT': 'US/Mountain',    # US timezone
            'PT':  'US/Pacific',     # US timezone
            'PST': 'US/Pacific',     # US timezone
            'PDT': 'US/Pacific',     # US timezone
        }

        ## Resolve a "local" datetime format(s)
        dt = {}
        ## Date time pattern component parts
        parts = {
            'year': r'(?P<year>\d{4})',
            'month': r'(?P<month>\S+)',
            'day': r'(?P<weekday>\S+)',
            'date': r'(?P<day>\d{1,2})',
            'iso86001_date': r'(?P<year>\d{4})\-(?P<month>\d{2})\-(?P<day>\d{1,2})',
            'hour': r'(?P<hour>\d{1,2})',
            'minute': r'(?P<minute>\d{2})',
            'second': r'(:(?P<second>\d{2}))?',
            'meridiem': r'(\s*(?P<meridiem>(am|pm)))?',
            'tzinfo_required': r'(?P<tzinfo>\S+)',
            'tzinfo': r'(\s(?P<tzinfo>\S+))?',
        }
        for pattern in [
            ## YYYY-mm-dd HH:MM[:SS][ Z]
            r'{iso86001_date}.{hour}:{minute}{second}{tzinfo}'.format(**parts),
            ## Month dd HH:MM[:SS] Z YYYY
            r'{month}\s{date}\s{hour}:{minute}{second}{meridiem}\s{tzinfo_required}\s{year}'.format(**parts),
            ## Day, Month dd, YYYY HH:MM[:SS][ Z]
            r'{day},\s{month}\s{date},\s{year}\s{hour}:{minute}{second}{meridiem}{tzinfo}'.format(**parts),
            ## Day, dd Month YYYY HH:MM[:SS][ Z]
            r'{day},\s{date}\s{month}\s{year}\s{hour}:{minute}{second}{meridiem}{tzinfo}'.format(**parts),
            ## Month dd HH:MM[:SS][am|pm] YYYY[ Z]
            r'{month}\s{date}\s{hour}:{minute}{second}{meridiem}\s{year}{tzinfo}'.format(**parts),
            ## dd Month YYYY HH:MM[:SS] [Z]
            r'{date}\s{month}\s{year}\s{hour}:{minute}{second}{tzinfo}'.format(**parts),
            ## HH:MM[:SS][am|pm][ Z]
            r'{hour}:{minute}{second}{meridiem}{tzinfo}'.format(**parts),
            ## No pattern matched
            None
            ]:
            ## Raise and error as no patterns matched,
            if pattern is None:
                raise ValueError(f"No pattern matched: {dt_in!r}")
            ## Check the pattern
            m = search(pattern, dt_in)
            if m is not None:
                if debug:
                    print(f"DEBUG: DT.resolve_input - used pattern {type(pattern)}: {pattern!r}")

                dt = m.groupdict()
                if debug:
                    print(f"DEBUG: DT.resolve_input - dt {type(dt)}: {dt!r}")

                ## Drop keys with a None value
                ## A default value is used when converted later
                for key in sorted(dt.keys()):
                    if dt.get(key) is None:
                        _ = dt.pop(key)
                if debug:
                    print(f"DEBUG: DT.resolve_input - dt {type(dt)}: {dt!r}")

                ## Translate a Month name into an integer
                if dt.get('month', False) and not dt.get('month').isdigit():
                    dt.update(month = month_to_int.get(dt.get('month').lower()[:3]))
                    ## Debug message
                    if debug:
                        print(f"DEBUG: DT.resolve_input - dt {type(dt)}: {dt!r}")

                ## Translate ante/post meridian
                ## twelve hour clock to twenty four hour clock
                if dt.get('meridiem', '').lower() == 'pm' and int(dt.get('hour', 99)) < 12:
                    dt.update(hour = int(dt.get('hour')) + 12)
                    if debug:
                        print(f"DEBUG: DT.resolve_input - dt {type(dt)}: {dt!r}")

                ## UTC<+/-OFFSET> may be used in place of a timezone name
                offset_pattern = r'UTC(?P<modifier>[\+\-])(?P<hours>\d{1,2})(:)?((?P<minutes>\d{2}))?'
                offset = search(offset_pattern, str(dt.get('tzinfo')))
                if offset is not None:
                    offset = offset.groupdict()
                    ## Handle abbreviated offsets which lack minutes
                    if offset.get('minutes') is None:
                        offset.pop('minutes')
                dt.update(offset = offset)
                if debug:
                    print(f"DEBUG: DT.resolve_input - offset {type(offset)}: {offset!r}")

                ## Translate a timezone name into a ZoneInfo
                ## Default to UTC if no timezone name was matched in `abbr_to_zone' map
                tzinfo = abbr_to_zone.get(dt.get('tzinfo'), 'UTC')
                if debug:
                    print(f"DEBUG: DT.resolve_input - tzinfo {type(tzinfo)}: {tzinfo!r}")
                dt.update(tzinfo = ZoneInfo(tzinfo))

                ## No need to try additional date time patterns
                break

        ## Debug message
        if debug:
            print(f"DEBUG: DT.resolve_input - dt {type(dt)}: {dt!r}")

        ## Convert a dictionary to a datetime object
        if isinstance(dt, dict):

            ## Adjust for UTC offset, as needed
            offset = False
            offset_modifier = None
            if isinstance(dt.get('offset'), dict):
                offset = timedelta(
                    hours=int(dt.get('offset').get('hours', 0)),
                    minutes=int(dt.get('offset').get('minutes', 0)),
                    )
                if dt.get('offset').get('modifier') == '+':
                    offset_modifier = 'ahead of UTC'
                else:
                    offset_modifier = 'behind UTC'
            if debug:
                print(f"DEBUG: DT.resolve_input - offset {type(offset)}: {offset!r}")
                print(f"DEBUG: DT.resolve_input - offset_modifier {type(offset_modifier)}: {offset_modifier!r}")

            ## Create a datetime object from a dictionary object
            dt = datetime(
                year=int(dt.get('year', now.year)),
                month=int(dt.get('month', now.month)),
                day=int(dt.get('day', now.day)),
                hour=int(dt.get('hour', 0)),
                minute=int(dt.get('minute', 0)),
                second=int(dt.get('second', 0)),
                microsecond=int(dt.get('microsecond', 0)),
                tzinfo=dt.get('tzinfo', ZoneInfo('UTC')),
                )
            if debug:
                print(f"DEBUG: DT.resolve_input - dt (dict to datetime) {type(dt)}: {dt!r}")

            if offset:
                ## Subtract the offset from UTC when the modifier was positive
                if offset_modifier == 'ahead of UTC':
                    dt = dt - offset
                ## Add the offset from UTC when the modifier was negative
                elif offset_modifier == 'behind UTC':
                    dt = dt + offset
                if debug:
                    print(f"DEBUG: DT.resolve_input - dt (offset adjusted) {type(dt)}: {dt!r}")

        ## Debug message
        if debug:
            print(f"DEBUG: DT.resolve_input - dt {type(dt)}: {dt!r}")

        return dt




## -----------------------------------------------------------------------------
def main(**kwargs):
    """Pretty print some info for a datetime object"""
    debug = kwargs.get('debug', False)

    ## Debug message
    if debug:
        print(f"DEBUG: main - **kwargs {type(kwargs)}: {kwargs!r}")

    ## Use ISO 8600 format
    ## 2021-12-29 21:17:15 (UTC-0700) MST
    if kwargs.get('iso', False):
        kwargs.update(fmt = DEFAULT_FORMAT_ISO)
    ## Wed Dec 29 21:17:15 2021 (UTC-0700) MST
    else:
        kwargs.update(fmt = DEFAULT_FORMAT)
    ## Debug message
    if debug:
        print(f"DEBUG: main - kwargs.get('fmt'): {kwargs.get('fmt')!r}")

    dt = DT()

    try:
        result = dt.resolve_input(' '.join(kwargs.get('values')), debug=debug)
    except Exception as err:
        print(f"Error: {err}")
        if kwargs.get('debug', False):
            raise
        else:
            exit(1)

    ## Debug message
    if debug:
        print(f"DEBUG: main - result {type(result)}: {result!r}")

    localzone = kwargs.get('localzone', 'UTC')
    ## Debug message
    if debug:
        print(f"DEBUG: main - localzone {type(localzone)}: {localzone!r}")
        print('- - - -')

    ## Pretty print a list of timezones
    kolor = Kolor()
    print(result.astimezone(ZoneInfo(localzone)).strftime(kwargs.get('fmt')))
    print(result.astimezone(ZoneInfo('UTC')).strftime(kwargs.get('fmt')))
    print(f"Unix timestamp: {result.astimezone(ZoneInfo(localzone)).strftime('%s')}")
    print('----------------------------------------------------------------')
    for zone in [
        'UTC',
        'GMT',                 # DT     ST
        'NZ',                  #        +12:00
        'Australia/Sydney',    # +11:00 +10:00
        'Asia/Tokyo',          # ?      +09:00
        'Asia/Seoul',          # ?      +09:00
        'Asia/Shanghai',       # ?      +08:00
        'Asia/Singapore',      # ?      +08:00
        'Asia/Qatar',          # ?      +03:00
        'Europe/Moscow',       # ?      +03:00
        'Europe/Warsaw',       # +02:00 +01:00
        'Europe/Copenhagen',   # +02:00 +01:00
        'Europe/Paris',        # +02:00 +01:00
        'Europe/London',       # +01:00 +00:00
        'Atlantic/Reykjavik',  # +00:00 +00:00
        'America/Sao_Paulo',   # ?      -03:00
        'America/New_York',    # -04:00 -05:00
        'America/Chicago',     # -05:00 -06:00
        'America/Denver',      # -06:00 -07:00
        'America/Los_Angeles', # -07:00 -08:00
        'Pacific/Honolulu',    # ?      -10:00
        ]:
        zone = result.astimezone(ZoneInfo(zone))
        zone = f"{zone.strftime(kwargs.get('fmt')):<40} {zone.tzinfo}"
        ## Apply color to the `localzone'
        if zone.endswith(localzone):
            zone = kolor(zone, background='yellow', color='black', style='bold', bright=True)
        print(zone)
    print('----------------------------------------------------------------')
    print('')




## -----------------------------------------------------------------------------
if __name__ == '__main__':
    parser = ArgumentParser(prog=PROGRAM_NAME,
        description='List different time zones based on input or current datetime',
        epilog="alias datetime='python3 ${HOME}/path/to/get_datetime.py $*';",
        add_help=True,
        )
    parser.add_argument('values', metavar='<value>', nargs='*',
        help='datetime values to parse (defaults to current datetime)')
    parser.add_argument('--fmt', default=False,
        help=f"datetime format (default: {DEFAULT_FORMAT.replace('%', '%%')!r})")
    parser.add_argument('--iso', default=False, action='store_true',
        help=f"use iso format: {DEFAULT_FORMAT_ISO.replace('%', '%%')!r}")
    parser.add_argument('--list', action='store_true', dest='list_all_zones',
        help='list zones and exit')
    parser.add_argument('--localzone', '-z', metavar='<tz>', default=DEFAULT_LOCALZONE,
        help=f"local timezone name (default: {DEFAULT_LOCALZONE!r})")
    parser.add_argument('--debug', action='store_true')
    argv, remaining_argv = parser.parse_known_args()

    ## Notice message
    if remaining_argv:
        print(f"NOTICE: Ignoring argument(s): {', '.join(remaining_argv)}")

    ## Debug message
    if argv.debug:
        for key, value in vars(argv).items():
            print(f"DEBUG: __main__ - argv.{key} {type(value)}: {value!r}")

    ## Catch list option
    if argv.list_all_zones:
        for key in sorted(available_timezones()):
            print(key)
    else:
        main(**vars(argv))
