# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from suit_dashboard.box import Box, Item
from meerkat.logs.charts import status_codes_chart
from meerkat.logs.data import STATUS_CODES


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

    def get_items(self):
        return [
            Item(value=status_codes_chart(),
                 display=Item.AS_HIGHCHARTS),
            Item('status-code-description', _('Descriptions'),
                 [('%s %s' % (k, v['name']), v['desc'])
                  for k, v in sorted(STATUS_CODES.items())],
                 display=Item.AS_TABLE,
                 classes='table-hover table-striped')
        ]
