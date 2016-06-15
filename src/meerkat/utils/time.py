# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime, timedelta


def ms_since_epoch(dt):
    return (dt - datetime(1970, 1, 1).date()).total_seconds() * 1000


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def log_date_to_python_date(s):
    return datetime.strptime(s, '%d/%b/%Y').date()


def log_datetime_to_python_datetime(s):
    return datetime.strptime(s, '%d/%b/%Y:%H:%M:%S +%z')


def log_datetime_to_python_date(s):
    return log_datetime_to_python_datetime(s).date()
