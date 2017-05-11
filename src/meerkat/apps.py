# -*- coding: utf-8 -*-

import os
import re

from django.apps import AppConfig

import appsettings as aps


class MeerkatConfig(AppConfig):
    name = 'meerkat'
    verbose_name = 'Meerkat'

    def ready(self):
        from .models import RequestLog
        AppSettings.check()
        django_shell = os.environ.get('DJANGO_SHELL', False)
        if AppSettings.logs_start_daemon.get() and not django_shell:
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


class AppSettings(aps.AppSettings):
    logs_file_path_regex = RegexSetting()
    logs_format_regex = RegexSetting()
    logs_top_dir = aps.StringSetting(default=None)
    logs_start_daemon = aps.BoolSetting(default=False)

    class Meta:
        setting_prefix = 'MEERKAT_'
