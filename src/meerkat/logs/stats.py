# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from collections import Counter

from meerkat.utils.list import distinct
from meerkat.utils.time import log_date_to_python_date, ms_since_epoch
from meerkat.utils.url import (
    url_is_asset, url_is_common_asset, url_is_false_negative, url_is_ignored,
    url_is_old, url_is_project_url)


def status_codes_stats(logs):
    stats = {k: 0 for k in distinct(
        (l['status_code'] for l in logs))}
    for log_line in logs:
        stats[log_line['status_code']] += 1
    return stats


def status_codes_by_date_stats(logs):
    stats = {}
    for req in logs:
        date = '%s/%s/%s' % (req['day'], req['month'], req['year'])
        if stats.get(date, None) is None:
            stats[date] = {'date': date, 'requests': []}
        stats[date]['requests'].append(req)

    for k, v in stats.items():
        v['unique_ip'] = len(distinct(r['ip_address'] for r in v['requests']))
        v['2xx'] = 0
        v['3xx'] = 0
        v['4xx'] = 0
        v['5xx'] = 0
        v['attacks'] = 0

        v['date'] = ms_since_epoch(log_date_to_python_date(v['date']))

        for r in v['requests']:
            if r['status_code'].startswith('2'):
                v['2xx'] += 1
            elif r['status_code'].startswith('3'):
                v['3xx'] += 1
            elif r['status_code'].startswith('4'):
                v['4xx'] += 1
            elif r['status_code'].startswith('5'):
                v['5xx'] += 1

            if r['status_code'] in ('400', '444', '502'):
                v['attacks'] += 1

        v['requests'] = len(v['requests'])

    stats = sorted(
        [v for k, v in stats.items()],
        key=lambda x: x['date'])

    return stats


def most_visited_pages_stats(logs):
    stats = {'more_than_10': [], 'less_than_10': None}
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
