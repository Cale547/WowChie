import time
from datetime import datetime, timezone

def unix_to_human(ux_time):
    if isinstance(ux_time, float):
        ux_time = int(ux_time)
        
    if ux_time < 0:
        print("Unable to calculate dates before Unix epoch (January 1st 1970)")
        return "Unable to calculate date for " + str(ux_time)
    
    time.localtime()
    timezone_offset = 1#2 if time.daylight else 1
    time_left = ux_time + timezone_offset*3600 # unix time is one hour after glorious Sweden


    m_length = [31,28,31,30,31,30,31,31,30,31,30,31]
    year = 1970
    month = 1
    day = 1
    hour = 0
    minute = 0
    second = 0

    # 1 day is 24*3600 = 86400 seconds
    # 1 month is 86400*m_length[month] = 2678400 for a 31-day month
    # 1 year is 365*86400 = 31536000 seconds or 31536000+86400 = 31622400 seconds if year % 4 == 0
    while time_left >= 31536000:
        if year % 4 == 0:
            time_left -= 86400 # removing leap day
        time_left -= 31536000 # removing 365 days
        year += 1

    while time_left >= 2678400: # removing 31-day (and under) months
        time_left -= 86400*m_length[month-1]
        if year % 4 == 0 and month == 2:
            time_left -= 86400
        month += 1
        if month == 13:
            month = 1

    if time_left >= 2592000: # removing last 30-day month
        time_left -= 2592000
        month += 1
    elif year % 4 == 0 and time_left >= 2505600: # removing last 29-day month
        time_left -= 2505600
        month += 1
    elif year % 4 != 0 and time_left >= 2419200: # removing last 28-day month
        time_left -= 2419200
        month += 1

    while time_left >= 86400: # removing days
        time_left -= 86400
        day += 1
    while time_left >= 3600:
        time_left -= 3600
        hour += 1
    while time_left >= 60:
        time_left -= 60
        minute += 1
    while time_left >= 1:
        time_left -= 1
        second += 1
    if time_left > 0: # Should be impossible
        print("Couldn't remove all time")
        return

    timestamp1 = [f'{hour:02d}:{minute:02d}:{second:02d}', f'{year:04d}{month:02d}{day:02d}']
    timestamp2 = [f'{hour:02d}:{minute:02d}:{second:02d}', f'{day:02d}/{month:02d}/{year:04d}']
    timestampDB = [f'{hour:02d}:{minute:02d}:{second:02d}', f'{year:04d}-{month:02d}-{day:02d}']
    return timestampDB

def get_default_start_time(year: int, day: int) -> int:
    """
    Returns the official AoC start time (05:00 UTC) for a specific day.
    You can set year manually or derive it from your data getter if needed.
    """
    return int(datetime(year, 12, day, 5, 0, 0, tzinfo=timezone.utc).timestamp())