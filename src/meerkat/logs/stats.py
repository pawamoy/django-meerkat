# -*- coding: utf-8 -*-


def distinct(l):
    seen = set()
    seen_add = seen.add
    return [_ for _ in l if not (_ in seen or seen_add(_))]


def status_codes_stats(NGINX_LOGS):
    stats = {k: 0 for k in distinct(
        (l['status_code'] for l in NGINX_LOGS))}
    for log_line in NGINX_LOGS:
        stats[log_line['status_code']] += 1
    return stats
