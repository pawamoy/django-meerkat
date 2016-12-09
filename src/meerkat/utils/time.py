# -*- coding: utf-8 -*-

"""Time utils."""


from __future__ import unicode_literals

from datetime import datetime, timedelta


def ms_since_epoch(dt):
    """
    Get the milliseconds since epoch until specific a date and time.

    Args:
        dt (datetime): date and time limit.

    Returns:
        int: number of milliseconds.
    """
    return (dt - datetime(1970, 1, 1).date()).total_seconds() * 1000


def daterange(start_date, end_date):
    """
    Yield one date per day from starting date to ending date.

    Args:
        start_date (date): starting date.
        end_date (date): ending date.

    Yields:
        date: a date for each day within the range.
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def log_date_to_python_date(s):
    """
    Convert a log date (string) to a Python date object.

    Args:
        s (str): string representing the date ('%d/%b/%Y').

    Returns:
        date: Python date object.
    """
    return datetime.strptime(s, '%d/%b/%Y').date()


def log_datetime_to_python_datetime(s):
    """
    Convert a log datetime (string) to a Python datetime object.

    Args:
        s (str): string representing the datetime ('%d/%b/%Y:%H:%M:%S +%z').

    Returns:
        datetime: Python datetime object.
    """
    return datetime.strptime(s, '%d/%b/%Y:%H:%M:%S +%z')


def log_datetime_to_python_date(s):
    """
    Convert a log datetime (string) to a Python date object.

    Args:
        s (str): string representing the datetime ('%d/%b/%Y:%H:%M:%S +%z').

    Returns:
        date: Python date object.
    """
    return log_datetime_to_python_datetime(s).date()
