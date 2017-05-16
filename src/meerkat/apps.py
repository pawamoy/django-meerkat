# -*- coding: utf-8 -*-

import re

from django.apps import AppConfig

import appsettings as aps


class MeerkatConfig(AppConfig):
    name = 'meerkat'
    verbose_name = 'Meerkat'

    def ready(self):
        from .models import RequestLog
        AppSettings.check()
        if AppSettings.logs_start_daemon.get():
            RequestLog.start_daemon()


class RegexSetting(aps.Setting):
    def check(self):
        value = self.get_raw()
        if value == self.default:
            return
        re_type = type(re.compile(r'^$'))
        if not isinstance(value, (re_type, str)):
            raise ValueError('%s must be a a string or a compiled regex '
                             '(use re.compile)' % self.name)

    def transform(self):
        value = self.get_raw()
        if isinstance(value, str):
            value = re.compile(value)
        return value


class URLWhitelistSetting(aps.Setting):
    def check(self):
        value = self.get_raw()
        if value == self.default:
            return
        if not (isinstance(value, dict) and
                all(isinstance(v, dict) for v in value.values())):
            raise ValueError('%s must be a dict with following items: %s ' % (
                self.full_name, self.default.keys()))
        s = {'PREFIXES', 'CONSTANTS'}
        for v in value.values():
            s_k = set(v.keys())
            if s_k - s or not s_k & s:
                raise ValueError('%s values must have %s items' % (
                        self.full_name, ', '.join(s)))

    def transform(self):
        value = self.get_raw()
        value_keys = value.keys()
        default_keys = self.default.keys()
        for key in default_keys:
            if key not in value_keys:
                value[key] = {}
        return value


class AppSettings(aps.AppSettings):
    logs_file_path_regex = RegexSetting()
    logs_format_regex = RegexSetting()
    logs_top_dir = aps.StringSetting(default=None)
    logs_start_daemon = aps.BoolSetting(default=False)
    logs_url_whitelist = URLWhitelistSetting(default={
        'ASSET': {
            'PREFIXES': (
                'media/', 'static/', 'assets/', 'cache/',
            )
        },
        'COMMON_ASSET': {
            'CONSTANTS': (
                'favicon.ico', 'robots.txt', 'apple-touch-icon.png',
                'apple-touch-icon-precomposed.png',
                'apple-touch-icon-120x120.png',
                'apple-touch-icon-120x120-precomposed.png'
            )
        },
        'OLD_ASSET': {},
        'OLD_PROJECT': {},
        'FALSE_NEGATIVE': {},
        'IGNORED': {
            'PREFIXES': (
                'assets/flash/ZeroClipboard.swf',
            )
        }
    })

    class Meta:
        setting_prefix = 'MEERKAT_'
