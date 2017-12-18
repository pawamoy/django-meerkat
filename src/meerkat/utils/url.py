# -*- coding: utf-8 -*-

"""URL utils."""

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.urlresolvers import Resolver404, resolve

from ..apps import AppSettings

app_settings = AppSettings()


def url_is_project(url, default='not_a_func'):
    """
    Check if URL is part of the current project's URLs.

    Args:
        url (str): URL to check.
        default (callable): used to filter out some URLs attached to function.

    Returns:

    """
    try:
        u = resolve(url)
        if u and u.func != default:
            return True
    except Resolver404:
        static_url = settings.STATIC_URL
        static_url_wd = static_url.lstrip('/')
        if url.startswith(static_url):
            url = url[len(static_url):]
        elif url.startswith(static_url_wd):
            url = url[len(static_url_wd):]
        else:
            return False
        if finders.find(url):
            return True
    return False


def url_is(white_list):
    """
    Function generator.

    Args:
        white_list (dict): dict with PREFIXES and CONSTANTS keys (list values).

    Returns:
        func: a function to check if a URL is...
    """
    def func(url):
        prefixes = white_list.get('PREFIXES', ())
        for prefix in prefixes:
            if url.startswith(prefix):
                return True
        constants = white_list.get('CONSTANTS', ())
        for exact_url in constants:
            if url == exact_url:
                return True
        return False
    return func

ASSET = 1
PROJECT = 2
OLD_ASSET = 3
COMMON_ASSET = 4
OLD_PROJECT = 5
FALSE_NEGATIVE = 6
SUSPICIOUS = 7
IGNORED = 8

URL_TYPE = {
    ASSET: 'ASSET',
    PROJECT: 'PROJECT',
    OLD_ASSET: 'OLD_ASSET',
    COMMON_ASSET: 'COMMON_ASSET',
    OLD_PROJECT: 'OLD_PROJECT',
    FALSE_NEGATIVE: 'FALSE_NEGATIVE',
    SUSPICIOUS: 'SUSPICIOUS',
    IGNORED: 'IGNORED'
}

URL_TYPE_REVERSE = {v: k for k, v in URL_TYPE.items()}


URL_WHITELIST = app_settings.logs_url_whitelist
url_is_asset = url_is(URL_WHITELIST[URL_TYPE[ASSET]])
url_is_old_asset = url_is(URL_WHITELIST[URL_TYPE[OLD_ASSET]])
url_is_common_asset = url_is(URL_WHITELIST[URL_TYPE[COMMON_ASSET]])
url_is_old_project = url_is(URL_WHITELIST[URL_TYPE[OLD_PROJECT]])
url_is_false_negative = url_is(URL_WHITELIST[URL_TYPE[FALSE_NEGATIVE]])
url_is_ignored = url_is(URL_WHITELIST[URL_TYPE[IGNORED]])
