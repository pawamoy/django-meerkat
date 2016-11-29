# -*- coding: utf-8 -*-


def distinct(l):
    seen = set()
    seen_add = seen.add
    return [_ for _ in l if not (_ in seen or seen_add(_))]
