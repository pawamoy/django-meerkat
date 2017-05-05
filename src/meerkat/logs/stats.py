# -*- coding: utf-8 -*-

"""
Statistics methods.

This modules stores the functions to compute statistics used by charts.
Typically, these data will be used in series for Highcharts charts.
"""

from collections import Counter
from datetime import datetime

from django.utils.timezone import make_naive

from ..utils.list import distinct
from ..utils.time import ms_since_epoch
from ..utils.url import (
    url_is_asset, url_is_common_asset, url_is_false_negative, url_is_ignored,
    url_is_old, url_is_project_url)
from .models import RequestLog


def status_codes_stats():
    """
    Get stats for status codes.

    Args:
        logs (list): logs data to use.

    Returns:
        dict: status code as key, number of apparition as value.
    """
    return dict(Counter(list(RequestLog.objects.values_list(
        'status_code', flat=True))))  # noqa


def status_codes_by_date_stats():
    """
    Get stats for status codes by date.

    Returns:
        list: status codes + date grouped by type: 2xx, 3xx, 4xx, 5xx, attacks.
    """

    def date_counter(queryset):
        return dict(Counter(map(
            lambda dt: ms_since_epoch(datetime.combine(
                make_naive(dt), datetime.min.time())),
            list(queryset.values_list('datetime', flat=True)))))

    codes = {low: date_counter(
        RequestLog.objects.filter(status_code__gte=low, status_code__lt=high))
        for low, high in ((200, 300), (300, 400), (400, 500))}
    codes[500] = date_counter(RequestLog.objects.filter(status_code__gte=500))
    codes['attacks'] = date_counter(RequestLog.objects.filter(
        status_code__in=(400, 444, 502)))

    stats = {}
    for code in (200, 300, 400, 500, 'attacks'):
        for date, count in codes[code].items():
            if stats.get(date, None) is None:
                stats[date] = {200: 0, 300: 0, 400: 0, 500: 0, 'attacks': 0}
            stats[date][code] += count

    stats = sorted([(k, v) for k, v in stats.items()], key=lambda x: x[0])
    return stats


def most_visited_pages_stats():
    """
    Get stats for most visited pages.

    Args:
        logs (list): logs data to use.

    Returns:
        dict: more_than_10 and less_than_10: list of dict (bound + url list).
    """
    stats = {'more_than_10': [], 'less_than_10': {}}
    urls = [u for u in (l['url'].lstrip('/').rstrip(' ')
                        for l in logs)
            if not url_is_ignored(u)]
    counter = Counter(urls)
    most_visited_pages = sorted(
        [(counter[u], u, url_is_project_url(u))
         for u in distinct(urls)],
        key=lambda x: x[0],
        reverse=True)

    if most_visited_pages[0][1] == '':
        most_visited_pages[0] = (
            most_visited_pages[0][0],
            '/',
            most_visited_pages[0][2])

    bounds = (10000, 1000, 100, 10)

    for i, b in enumerate(bounds):
        if i == 0:
            subset = [(c, u, v) for (c, u, v) in most_visited_pages
                      if c >= b]
        else:
            subset = [(c, u, v) for (c, u, v) in most_visited_pages
                      if b <= c < bounds[i - 1]]

        stats['more_than_10'].append({'bound': b, 'subset': subset})

    subset = [(c, u, v) for (c, u, v) in most_visited_pages if 1 <= c < 10]
    occurrences = {name: {'distinct': 0, 'total': 0} for name in (
        'project', 'old_project', 'asset', 'old_asset', 'common_asset',
        'false', 'suspicious'
    )}
    for (c, u, v) in subset:
        if v:
            if not url_is_asset(u):
                occurrences['project']['distinct'] += 1
                occurrences['project']['total'] += c
            else:
                occurrences['asset']['distinct'] += 1
                occurrences['asset']['total'] += c
        else:
            if url_is_asset(u):
                occurrences['old_asset']['distinct'] += 1
                occurrences['old_asset']['total'] += c
            elif url_is_common_asset(u):
                occurrences['common_asset']['distinct'] += 1
                occurrences['common_asset']['total'] += c
            elif url_is_old(u):
                occurrences['old_project']['distinct'] += 1
                occurrences['old_project']['total'] += c
            elif url_is_false_negative(u):
                occurrences['false']['distinct'] += 1
                occurrences['false']['total'] += c
            else:
                occurrences['suspicious']['distinct'] += 1
                occurrences['suspicious']['total'] += c

    stats['less_than_10'] = occurrences

    return stats
