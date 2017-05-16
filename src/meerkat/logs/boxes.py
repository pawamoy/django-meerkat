# -*- coding: utf-8 -*-

"""
Django Suit Dashboard boxes.

This module defines the boxes to be used in the admin interface by
django-suit-dashboard package.
"""


import json

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.translation import ugettext as _

from suit_dashboard import Box, Widget

from ..utils.time import month_name_to_number
from .charts import (
    most_visited_pages_charts, most_visited_pages_legend_chart,
    status_codes_by_date_chart, status_codes_chart)
from .data import STATUS_CODES
from .models import RequestLog
from .stats import status_codes_by_date_stats


class BoxLogsLinks(Box):
    """The menu for log views."""

    title = _('Logs analysis')
    description = _(
        'The machine uses a program called "web server" to serve the '
        'website over the internet. This web server records every '
        'request sent by clients, with detailed information attached. '
        'These logs can be parsed to compute some statistical data.')
    template = 'meerkat/logs/links.html'


class BoxLogsStatusCodes(Box):
    """The status codes widget."""

    title = _('Status codes')

    @property
    def widgets(self):
        status_codes = status_codes_chart()
        return [
            Widget(html_id='status-codes',
                   content=json.dumps(status_codes),
                   template='meerkat/widgets/highcharts.html',
                   js_code=['tooltip.formatter']),
            Widget(html_id='status-code-description',
                   name=_('Descriptions'),
                   content=[('%s %s' % (k, v['name']), v['desc'])
                            for k, v in sorted(STATUS_CODES.items())],
                   template='meerkat/widgets/table.html',
                   classes='table-hover table-striped')
        ]


class BoxLogsStatusCodesByDate(Box):
    """The status codes by date widget."""

    title = _('Status codes by date')
    template = 'meerkat/logs/status_codes_by_date.html'

    @property
    def context(self):
        """Get the context."""
        stats = status_codes_by_date_stats()

        attacks_data = [{
            'type': 'line',
            'zIndex': 9,
            'name': _('Attacks'),
            'data': [(v[0], v[1]['attacks'])
                     for v in stats]
        }]

        codes_data = [{
            'zIndex': 4,
            'name': '2xx',
            'data': [(v[0], v[1][200]) for v in stats]
        }, {
            'zIndex': 5,
            'name': '3xx',
            'data': [(v[0], v[1][300]) for v in stats]
        }, {
            'zIndex': 6,
            'name': '4xx',
            'data': [(v[0], v[1][400]) for v in stats]
        }, {
            'zIndex': 8,
            'name': '5xx',
            'data': [(v[0], v[1][500]) for v in stats]
        }]

        return {'generic_chart': json.dumps(status_codes_by_date_chart()),
                'attacks_data': json.dumps(attacks_data),
                'codes_data': json.dumps(codes_data)}


class BoxLogsMostVisitedPagesLegend(Box):
    """The most visited pages legend."""

    widgets = [Widget(
        html_id='legend_chart',
        content=json.dumps(most_visited_pages_legend_chart()),
        template='meerkat/widgets/highcharts.html')]


class BoxLogsMostVisitedPages(Box):
    """The most visited pages legend."""

    title = _('Most visited pages')

    @property
    def widgets(self):
        """Get the items."""
        widgets = []
        for i, chart in enumerate(most_visited_pages_charts()):
            widgets.append(Widget(html_id='most_visited_chart_%d' % i,
                                  content=json.dumps(chart),
                                  template='meerkat/widgets/highcharts.html',
                                  js_code=['plotOptions.tooltip.pointFormatter']))

        return widgets
