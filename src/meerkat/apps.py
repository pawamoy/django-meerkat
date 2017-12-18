# -*- coding: utf-8 -*-

import re

from django.apps import AppConfig

import appsettings as aps
from archan import DSM as ADSM
from dependenpy import DSM as DDSM
from dependenpy.helpers import guess_depth


class MeerkatConfig(AppConfig):
    name = 'meerkat'
    verbose_name = 'Meerkat'

    def ready(self):
        from .models import RequestLog
        AppSettings.check()
        app_settings = AppSettings()
        if app_settings.logs_start_daemon:
            RequestLog.start_daemon()


class RegexSetting(aps.Setting):
    def checker(self, name, value):
        re_type = type(re.compile(r'^$'))
        if not isinstance(value, (re_type, str)):
            raise ValueError('%s must be a a string or a compiled regex '
                             '(use re.compile)' % name)

    def transform(self, value):
        if isinstance(value, str):
            value = re.compile(value)
        return value


class URLWhitelistSetting(aps.Setting):
    def checker(self, name, value):
        if not (isinstance(value, dict) and
                all(isinstance(v, dict) for v in value.values())):
            raise ValueError('%s must be a dict with following items: %s ' % (
                name, self.default.keys()))
        s = {'PREFIXES', 'CONSTANTS'}
        for v in value.values():
            s_k = set(v.keys())
            if s_k - s or not s_k & s:
                raise ValueError('%s values must have %s items' % (
                        name, ', '.join(s)))

    def transform(self, value):
        value_keys = value.keys()
        default_keys = self.default.keys()
        for key in default_keys:
            if key not in value_keys:
                value[key] = {}
        return value


class ArchanPackagesSetting(aps.Setting):
    def checker(self, name, value):
        default_keys = self.default.keys()
        if not (isinstance(value, dict) and
                all(isinstance(v, (tuple, list)) and
                    len(v) == 2 and
                    isinstance(v[0], str) and
                    isinstance(v[1], (tuple, list))
                    for v in value.values())):
            raise ValueError(
                "%s must be a dict of 2-tuples ('name', [packages]) "
                'with following keys: %s ' % (name, default_keys))
        for key in value.keys():
            if key not in default_keys:
                raise ValueError('Unknow key %s in %s' % (key, name))

    def packages_groups(self, value=None):
        if value is None:
            value = self.raw_value
        packages, groups = [], []
        for k, (n, p) in value.items():
            packages.extend(p)
            for _ in p:
                groups.append(n)
        return packages, groups

    def transform(self, value):
        packages, _ = self.packages_groups(value)
        return DDSM(*packages)

    def get_dsm(self, depth=None):
        packages, groups = self.packages_groups()
        dsm = DDSM(*packages)
        if depth is None:
            depth = guess_depth(packages)
        matrix = dsm.as_matrix(depth=depth)
        return ADSM(matrix.data, matrix.keys, groups)


class AppSettings(aps.AppSettings):
    archan_dsm = ArchanPackagesSetting(default={
        'framework': ('Django', ['django']),
        'django-apps': ('Django Apps', ['meerkat']),
        'project-apps': ('Project Apps', []),
        'project-modules': ('Project Modules', []),
        'broker': ('Broker', []),
        'data': ('Data', [])
    }, name='ARCHAN_PACKAGES')

    logs_file_path_regex = RegexSetting()
    logs_format_regex = RegexSetting()
    logs_top_dir = aps.StringSetting(default=None)
    logs_start_daemon = aps.BooleanSetting(default=False)
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
