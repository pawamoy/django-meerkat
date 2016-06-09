# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from suit_dashboard.views import DashboardView
from suit_dashboard.layout import Grid, Row, Column
from meerkat.logs.boxes import BoxLogsLinks, BoxLogsStatusCodes


class HomeView(DashboardView):
    template_name = 'meerkat/main.html'
    crumbs = (
        {'url': 'admin:index', 'name': _('Home')},
    )
    grid = Grid(Row(Column(BoxLogsLinks())))


class LogsMenu(HomeView):
    crumbs = (
        {'url': 'admin:nginx', 'name': 'NginX'},
    )
    grid = Grid(Row(Column(BoxLogsLinks())))


class LogsStatusCodes(LogsMenu):
    crumbs = (
        {'url': 'admin:nginx_status_codes', 'name': _('Status codes')},
    )
    grid = Grid(Row(Column(BoxLogsLinks(), BoxLogsStatusCodes())))


# def blah():
#     return [
#         Item('traffic_chart', '', json.dumps(traffic_chart),
#              display=Item.AS_HIGHCHARTS),
#         Item(
#             'status-code-description', _('Descriptions'),
#             [
#                 ('%s %s' % (sc, STATUS_CODES[int(sc)]['name']),
#                  STATUS_CODES[int(sc)]['desc'])
#                 for sc in sorted(by_status_code.keys())
#                 ],
#             display=Item.AS_TABLE,
#             classes='table-hover'
#         )
#     ]
