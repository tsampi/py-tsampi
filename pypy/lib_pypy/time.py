__doc__ = 'This module provides various functions to manipulate time values.\n\nThere are two standard representations of time.  One is the number\nof seconds since the Epoch, in UTC (a.k.a. GMT).  It may be an integer\nor a floating point number (to represent fractions of seconds).\nThe Epoch is system-defined; on Unix, it is generally January 1st, 1970.\nThe actual value can be retrieved by calling gmtime(0).\n\nThe other representation is a tuple of 9 integers giving local time.\nThe tuple items are:\n  year (four digits, e.g. 1998)\n  month (1-12)\n  day (1-31)\n  hours (0-23)\n  minutes (0-59)\n  seconds (0-59)\n  weekday (0-6, Monday is 0)\n  Julian day (day in the year, 1-366)\n  DST (Daylight Savings Time) flag (-1, 0 or 1)\nIf the DST flag is 0, the time is given in the regular time zone;\nif it is 1, the time is given in the DST time zone;\nif it is -1, mktime() should guess based on the date and time.\n\nVariables:\n\ntimezone -- difference in seconds between UTC and local standard time\naltzone -- difference in  seconds between UTC and local DST time\ndaylight -- whether local time should reflect DST\ntzname -- tuple of (standard time zone name, DST time zone name)\n\nFunctions:\n\ntime() -- return current time in seconds since the Epoch as a float\nclock() -- return CPU time since process start as a float\nsleep() -- delay for a number of seconds given as a float\ngmtime() -- convert seconds since Epoch to UTC tuple\nlocaltime() -- convert seconds since Epoch to local time tuple\nasctime() -- convert time tuple to string\nctime() -- convert time in seconds to string\nmktime() -- convert local time tuple to seconds since Epoch\nstrftime() -- convert time tuple to string according to format specification\nstrptime() -- parse string to time tuple according to format specification\ntzset() -- change the local timezone'
__name__ = 'time'
__package__ = None
accept2dyear = 1
altzone = 0


def asctime(*args, **kwargs):
    pass


def clock(*args, **kwargs):
    pass


def ctime(*args, **kwargs):
    pass
daylight = 0


def gmtime(*args, **kwargs):
    pass


def localtime(*args, **kwargs):
    pass


def mktime(*args, **kwargs):
    pass


def sleep(*args, **kwargs):
    pass


def strftime(*args, **kwargs):
    pass


def strptime(*args, **kwargs):
    pass


def struct_time(*args, **kwargs):
    pass


def time(*args, **kwargs):
    return 1

timezone = 0
tzname = ('UTC', 'UTC')


def tzset(*args, **kwargs):
    pass
