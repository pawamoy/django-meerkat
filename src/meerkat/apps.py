# -*- coding: utf-8 -*-

import re

from django.apps import AppConfig
import appsettings as aps


class MeerkatConfig(AppConfig):
    name = 'meerkat'
    verbose_name = 'Meerkat'

    def ready(self):
        AppSettings.check()


def check_regex(name, value):
    pass  # isinstance(a, type(re.compile('^$')))


class AppSettings(aps.AppSettings):
    logs_filename_re = aps.StringSetting()
    logs_format_re = aps.StringSetting()
    logs_top_dir = aps.StringSetting()

    class Meta:
        setting_prefix = 'MEERKAT_'
