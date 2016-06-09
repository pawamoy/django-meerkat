# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from suit_dashboard.box import Box, Item
from meerkat.logs.charts import status_codes_chart


class BoxLogsLinks(Box):
    def get_title(self):
        return _('Logs analysis')

    def get_description(self):
        return _('The machine uses a program called "web server" to serve the '
                 'website over the internet. This web server records every '
                 'request sent by clients, with detailed information attached.'
                 ' These logs can be parsed to compute some statistical data.')

    def get_template(self):
        return 'meerkat/logs/links.html'


class BoxLogsStatusCodes(Box):
    def get_title(self):
        return _('Status codes')

    def get_context(self):
        value = status_codes_chart
        return [
            Item(value=value,
                 display=Item.AS_REFRESHABLE_HIGHCHARTS)
        ]
