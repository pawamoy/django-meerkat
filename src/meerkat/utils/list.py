# -*- coding: utf-8 -*-

"""List utils."""


def distinct(l):
    """
    Return a list where the duplicates have been removed.

    Args:
        l (list): the list to filter.

    Returns:
        list: the same list without duplicates.
    """
    seen = set()
    seen_add = seen.add
    return (_ for _ in l if not (_ in seen or seen_add(_)))
