import datetime
import zoneinfo

import pytest

from get_datetime import DT

def test_resolve_input_no_input():
    with pytest.raises(TypeError):
        dt = DT()
        dt.resolve_input()

def test_resolve_input_empty_input():
    dt = DT()
    result = dt.resolve_input('')
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_unix_epoch_timestamp():
    dt = DT()
    result = dt.resolve_input('1234567890') ## Fri Feb 13 23:31:30 2009 (UTC+0000) UTC
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 30
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_unix_epoch_timestamp_as_decimal():
    dt = DT()
    result = dt.resolve_input('1234567890.8765') ## Fri Feb 13 23:31:30 2009 (UTC+0000) UTC
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 30
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_ISO_86001_format():
    dt = DT()
    result = dt.resolve_input('2009-02-13T23:31:30')
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 30
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_ISO_86001_format_Z():
    dt = DT()
    result = dt.resolve_input('2009-02-13T23:31:30Z')
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 30
    #assert result.tzinfo == timezone.utc
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_ISO_86001_format_w_offset():
    dt = DT()
    result = dt.resolve_input('2009-02-13T23:31:30-06:00')
    print(f"result {type(result)}: {result!r}")
    print(f"dt {type(dt)}: {dt!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 30
    assert result.tzinfo == datetime.timezone(datetime.timedelta(days=-1, seconds=64800))
    assert str(result.tzinfo) == 'UTC-06:00'

def test_resolve_input_ISO_86001_format_w_zone():
    dt = DT()
    result = dt.resolve_input('2009-02-13T23:31:30 MT')
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 30
    assert result.tzinfo == zoneinfo.ZoneInfo(key='US/Mountain')
    assert str(result.tzinfo) == 'US/Mountain'

def test_resolve_input_Month_dd_HH_MM_SS_Z_YYYY():
    dt = DT()
    result = dt.resolve_input('February 13 23:31:30 UTC 2009') ## Month dd HH:MM:SS Z YYYY
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 30
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_Month_dd_HH_MM_Z_YYYY():
    dt = DT()
    result = dt.resolve_input('February 13 23:31 UTC 2009') ## Month dd HH:MM Z YYYY
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 0
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_Month_dd_HH_MM_MDT_YYYY():
    dt = DT()
    result = dt.resolve_input('February 13 23:31 MDT 2009') ## Month dd HH:MM Z YYYY
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 0
    assert str(result.tzinfo) == 'US/Mountain'

def test_resolve_input_DayC_Month_ddC_YYYY_HH_MM_SS_format():
    dt = DT()
    result = dt.resolve_input('Friday, February 13, 2009 23:31:30') ## Day, Month dd, YYYY HH:MM:SS
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 30
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_DayC_Month_ddC_YYYY_HH_MM_format():
    dt = DT()
    result = dt.resolve_input('Fri, Feb 13, 2009 23:31') ## Day, Month dd, YYYY HH:MM
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 0
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_DayC_dd_Month_YYYY_HH_MM_SS_format():
    dt = DT()
    result = dt.resolve_input('Friday, 13 February 2009 23:31:30') ## Day, dd Month YYYY HH:MM:SS
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 30
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_DayC_dd_Month_YYYY_HH_MM_format():
    dt = DT()
    result = dt.resolve_input('Fri, 13 February 2009 23:31') ## Day, dd Month YYYY HH:MM
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 0
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_DayC_dd_Month_YYYY_HH_MM_Z_format():
    dt = DT()
    result = dt.resolve_input('Fri, 13 February 2009 23:31 PST') ## Day, dd Month YYYY HH:MM
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 0
    assert str(result.tzinfo) == 'US/Pacific'

def test_resolve_input_Month_dd_HH_MM_SS_YYYY_format():
    dt = DT()
    result = dt.resolve_input('February 13 23:31:30 2009') ## Month dd HH:MM:SS YYYY
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 30
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_Month_dd_HH_MM_YYYY_format():
    dt = DT()
    result = dt.resolve_input('February 13 23:31 2009') ## Month dd HH:MM YYYY
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 0
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_Month_dd_HH_MM_YYYY_Z_format():
    dt = DT()
    result = dt.resolve_input('February 13 23:31 2009 ET', debug=True) ## Month dd HH:MM YYYY
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2009
    assert result.month == 2
    assert result.day == 13
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 0
    assert str(result.tzinfo) == 'US/Eastern'

def test_resolve_input_dd_Month_YYYY_HH_MM_SS_Z0_format():
    dt = DT()
    result = dt.resolve_input('21 July 2023 19:32:01 UTC+12', debug=True) ## dd Month YYYY HH:MM[:SS] [Z]
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2023
    assert result.month == 7
    assert result.day == 21
    assert result.hour == 7
    assert result.minute == 32
    assert result.second == 1
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_dd_Month_YYYY_HH_MM_SS_Z1_format():
    dt = DT()
    result = dt.resolve_input('21 July 2023 19:32 UTC+1200', debug=True) ## dd Month YYYY HH:MM[:SS] [Z]
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2023
    assert result.month == 7
    assert result.day == 21
    assert result.hour == 7
    assert result.minute == 32
    assert result.second == 0
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_dd_Month_YYYY_HH_MM_SS_Z2_format():
    dt = DT()
    result = dt.resolve_input('21 July 2023 19:32 UTC+12:30', debug=True) ## dd Month YYYY HH:MM[:SS] [Z]
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == 2023
    assert result.month == 7
    assert result.day == 21
    assert result.hour == 7
    assert result.minute == 2
    assert result.second == 0
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_HH_MM_SS_format():
    now = datetime.datetime.utcnow()
    dt = DT()
    result = dt.resolve_input('23:31:30') ## HH:MM:SS
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == now.year
    assert result.month == now.month
    assert result.day == now.day
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 30
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_HH_MM_format():
    now = datetime.datetime.utcnow()
    dt = DT()
    result = dt.resolve_input('23:31') ## HH:MM
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == now.year
    assert result.month == now.month
    assert result.day == now.day
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 0
    assert str(result.tzinfo) == 'UTC'

def test_resolve_input_HH_MM_Z_format():
    now = datetime.datetime.utcnow()
    dt = DT()
    result = dt.resolve_input('23:31 MT')
    print(f"result {type(result)}: {result!r}")
    assert isinstance(result, datetime.datetime) is True
    assert result.year == now.year
    assert result.month == now.month
    assert result.day == now.day
    assert result.hour == 23
    assert result.minute == 31
    assert result.second == 0
    assert str(result.tzinfo) == 'US/Mountain'

def test_resolve_input_no_pattern_matched():
    dt = DT()
    with pytest.raises(ValueError):
        result = dt.resolve_input('this is not a known datetime')

@pytest.mark.xfail()
def test_resolve_input_zoneinfo_NotFoundError():
    dt = DT()
    result = dt.resolve_input('')
    print(f"result {type(result)}: {result!r}")
    pass
    # from re import search, IGNORECASE
    ## Month dd HH:MM[:SS] Z YYYY
    r'{month}\s{date}\s{hour}:{minute}{second}{meridiem}{tzinfo}\s{year}'.format(**parts),
    # search(pattern, 'Apr 1 2:34 GMT 2022', IGNORECASE).groupdict()
    # search(pattern, 'April 01 02:34 GMT 2022', IGNORECASE).groupdict()
    # search(pattern, 'May 1 2:34:56 GMT 2022', IGNORECASE).groupdict()
    # search(pattern, 'June 01 02:34:56 GMT 2022', IGNORECASE).groupdict()
    # search(pattern, 'May 1 2:34:56pm GMT 2022', IGNORECASE).groupdict()
    # search(pattern, 'June 01 02:34:56AM GMT 2022', IGNORECASE).groupdict()
    ## Day, Month dd, YYYY HH:MM[:SS][ Z]
    r'{day},\s{month}\s{date}\s{year}\s{hour}:{minute}{second}{meridiem}{tzinfo}'.format(**parts),
    # search(pattern, 'Fri, April 1 2022 2:34', IGNORECASE).groupdict()
    # search(pattern, 'Friday, May 01 2022 2:34', IGNORECASE).groupdict()
    # search(pattern, 'Sat, Jun 1 2022 2:34:56pm', IGNORECASE).groupdict()
    # search(pattern, 'Saturday, July 01 2022 2:34:56AM', IGNORECASE).groupdict()
    # search(pattern, 'Sun, Aug 1 2022 2:34:56 GMT', IGNORECASE).groupdict()
    # search(pattern, 'Sunday, September 01 2022 2:34:56AM GMT', IGNORECASE).groupdict()
    ## Day, dd Month YYYY HH:MM[:SS][ Z]
    r'{day},\s{date}\s{month}\s{year}\s{hour}:{minute}{second}{meridiem}{tzinfo}'.format(**parts),
    # search(pattern, 'Fri, 1 Apr 2022 2:34', IGNORECASE).groupdict()
    # search(pattern, 'Friday, 1 April 2022 2:34', IGNORECASE).groupdict()
    # search(pattern, 'Sat, 01 Apr 2022 2:34:56pm', IGNORECASE).groupdict()
    # search(pattern, 'Saturday, 01 April 2022 2:34:56AM', IGNORECASE).groupdict()
    # search(pattern, 'Sun, 01 Apr 2022 2:34:56 GMT', IGNORECASE).groupdict()
    # search(pattern, 'Sunday, 01 April 2022 2:34:56AM GMT', IGNORECASE).groupdict()
    ## Month dd HH:MM[:SS][am|pm] YYYY[ Z]
    r'{month}\s{date}\s{hour}:{minute}{second}{meridiem}\s{year}{tzinfo}'.format(**parts),
    # search(pattern, 'Apr  1  2:34 2022', IGNORECASE).groupdict()
    # search(pattern, 'April  1  2:34pm 2022', IGNORECASE).groupdict()
    # search(pattern, 'May 01 12:34 2022', IGNORECASE).groupdict()
    # search(pattern, 'June 12 02:34pm 2022', IGNORECASE).groupdict()
    # search(pattern, 'Jul 01 12:34:56 2022', IGNORECASE).groupdict()
    # search(pattern, 'August 12 02:34:56 PM 2022', IGNORECASE).groupdict()
    # search(pattern, 'Sep 01 12:34:56 2022 GMT', IGNORECASE).groupdict()
    # search(pattern, 'October 12 02:34:56 AM 2022 GMT', IGNORECASE).groupdict()
    ## dd Month YYYY HH:MM[:SS] [Z]
    r'{date}\s{month}\s{year}\s{hour}:{minute}{second}{tzinfo}'.format(**parts),
    ## HH:MM[:SS][am|pm][ Z]
    r'{hour}:{minute}{second}{meridiem}{tzinfo}'.format(**parts),
    # search(pattern, '2:34', IGNORECASE).groupdict()
    # search(pattern, '2:34pm', IGNORECASE).groupdict()
    # search(pattern, '12:34', IGNORECASE).groupdict()
    # search(pattern, '12:34 am', IGNORECASE).groupdict()
    # search(pattern, '02:34:56', IGNORECASE).groupdict()
    # search(pattern, '12:34:56 PM', IGNORECASE).groupdict()
    # search(pattern, '12:34:56 GMT', IGNORECASE).groupdict()
    # search(pattern, '12:34:56 AM GMT', IGNORECASE).groupdict()
