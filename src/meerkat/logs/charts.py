# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json
import re
from os.path import join
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from suit_dashboard.decorators import refreshable
from meerkat.logs.data import STATUS_CODES
from meerkat.logs.stats import status_codes_stats
from meerkat.logs.parsers import NginXAccessLogParser


@refreshable
def status_codes_chart():
    parser = NginXAccessLogParser(re.compile(r'nginx-access-.*'),
                                  top_dir=join(settings.BASE_DIR, 'logs'))
    stats = status_codes_stats(parser.parse_files())
    chart_options = {
        'chart': {
            'type': 'pie'
        },
        'title': {
            'text': ''
        },
        'subtitle': {
            'text': ''
        },
        # 'tooltip': {
        #     # FIXME: find a way to handle javascript code
        #     'formatter': "return this.y + '/' + this.total + ' (' + "
        #                  "Highcharts.numberFormat(this.percentage, 1) + '%)';"
        # },
        'legend': {
            'enabled': True,
        },
        'plotOptions': {
            'pie': {
                'allowPointSelect': True,
                'cursor': 'pointer',
                'dataLabels': {
                    'enabled': True,
                    'format': '<b>{point.name}</b>: {point.y}/{point.total} '
                              '({point.percentage:.1f}%)'
                },
                'showInLegend': True
            }
        },
        'series': [{
            'name': _('Status Codes'),
            'colorByPoint': True,
            'data': sorted(
                [{'name': '%s %s' % (k, STATUS_CODES[int(k)]['name']), 'y': v}
                 for k, v in stats.items()],
                key=lambda x: x['y'],
                reverse=True)
        }]
    }

    return json.dumps(chart_options)

print('hey')
