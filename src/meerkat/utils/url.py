# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.urlresolvers import Resolver404, resolve


def url_is_project_url(path, default='not_a_func'):
    try:
        u = resolve(path)
        if u and u.func != default:
            return True
    except Resolver404:
        static_url = settings.STATIC_URL
        static_url_wd = static_url.lstrip('/')
        if path.startswith(static_url):
            path = path[len(static_url):]
        elif path.startswith(static_url_wd):
            path = path[len(static_url_wd):]
        if finders.find(path):
            return True
    return False


URL_WHITE_LIST = {
    'ASSETS': {
        'PREFIXES': (
            'media/', 'static/', 'assets/', 'cache/', 'markdown/image/'
        )
    },

    'COMMON_ASSETS': {
        'CONSTANTS': (
            'favicon.ico', 'robots.txt', 'apple-touch-icon.png',
            'apple-touch-icon-precomposed.png',
            'apple-touch-icon-120x120.png',
            'apple-touch-icon-120x120-precomposed.png'
        )
    },

    'OLD': {
        'PREFIXES': (
            'admin/', 'members/', 'chart/', 'forums/', 'news/',
            'member/', 'questions/', 'matrix/', 'pprofile/', 'rosetta/'
        ),
        'CONSTANTS': (
            'visual/', 'communities/', 'welcome/', 'jsi18n/',
            'overview/', 'profile/', 'settings/', 'chart', 'login'
        )
    },

    'FALSE_NEGATIVE': {
        'PREFIXES': (
            'articles/', 'chaining/', 'login/?next='
        )
    },

    'IGNORED': {
        'PREFIXES': (
            'assets/flash/ZeroClipboard.swf',
        )
    }
}


def url_is(white_list):
    def func(url):
        prefixes = white_list.get('PREFIXES', None)
        if prefixes is not None:
            for prefix in prefixes:
                if url.startswith(prefix):
                    return True
        constants = white_list.get('CONSTANTS', None)
        if constants is not None:
            for exact_url in constants:
                if url == exact_url:
                    return True
        return False
    return func

url_is_asset = url_is(URL_WHITE_LIST['ASSETS'])
url_is_common_asset = url_is(URL_WHITE_LIST['COMMON_ASSETS'])
url_is_old = url_is(URL_WHITE_LIST['OLD'])
url_is_false_negative = url_is(URL_WHITE_LIST['FALSE_NEGATIVE'])
url_is_ignored = url_is(URL_WHITE_LIST['IGNORED'])
