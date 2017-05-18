# -*- coding: utf-8 -*-

"""
Statistics methods.

This modules stores the functions to compute statistics used by charts.
Typically, these data will be used in series for Highcharts charts.
"""

from collections import Counter
from datetime import datetime

from django.utils.timezone import make_naive

from ..utils.time import ms_since_epoch
from ..utils.url import (
    ASSET, COMMON_ASSET, FALSE_NEGATIVE, IGNORED, OLD_ASSET, OLD_PROJECT,
    PROJECT, SUSPICIOUS, URL_TYPE, URL_TYPE_REVERSE, url_is_asset,
    url_is_common_asset, url_is_false_negative, url_is_ignored,
    url_is_old_project, url_is_project)
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

    counter = Counter(list(RequestLog.objects.values_list('url', flat=True)))
    most_visited_pages = counter.most_common()
    bounds = (10000, 1000, 100, 10)
    subsets = [[] for _ in bounds]

    for u, c in most_visited_pages:
        if url_is_ignored(u):
            continue
        if c >= bounds[0]:
            subsets[0].append([u, c])
        elif c < bounds[-1]:
            subsets[-1].append([u, c])
        else:
            for i, bound in enumerate(bounds[:-1]):
                if bound > c >= bounds[i+1]:
                    subsets[i+1].append([u, c])
                    break

    stats['more_than_10'] = [
        {'bound': bound, 'subset': subset}
        for bound, subset in zip(bounds[:-1], subsets[:-1])]

    for subset in subsets[:-1]:
        for uc in subset:
            if url_is_project(uc[0]):
                if url_is_asset(uc[0]):
                    uc.append(ASSET)
                else:
                    uc.append(PROJECT)
            else:
                if url_is_asset(uc[0]):
                    uc.append(OLD_ASSET)
                elif url_is_common_asset(uc[0]):
                    uc.append(COMMON_ASSET)
                elif url_is_old_project(uc[0]):
                    uc.append(OLD_PROJECT)
                elif url_is_false_negative(uc[0]):
                    uc.append(FALSE_NEGATIVE)
                else:
                    uc.append(SUSPICIOUS)

    occurrences = {name: {'distinct': 0, 'total': 0}
                   for name in set(URL_TYPE.keys()) - {IGNORED}}

    for u, c in subsets[-1]:
        if url_is_project(u):
            if url_is_asset(u):
                occurrences[ASSET]['distinct'] += 1
                occurrences[ASSET]['total'] += c
            else:
                occurrences[PROJECT]['distinct'] += 1
                occurrences[PROJECT]['total'] += c
        else:
            if url_is_asset(u):
                occurrences[OLD_ASSET]['distinct'] += 1
                occurrences[OLD_ASSET]['total'] += c
            elif url_is_common_asset(u):
                occurrences[COMMON_ASSET]['distinct'] += 1
                occurrences[COMMON_ASSET]['total'] += c
            elif url_is_old_project(u):
                occurrences[OLD_PROJECT]['distinct'] += 1
                occurrences[OLD_PROJECT]['total'] += c
            elif url_is_false_negative(u):
                occurrences[FALSE_NEGATIVE]['distinct'] += 1
                occurrences[FALSE_NEGATIVE]['total'] += c
            else:
                occurrences[SUSPICIOUS]['distinct'] += 1
                occurrences[SUSPICIOUS]['total'] += c

    stats['less_than_10'] = occurrences

    return stats
