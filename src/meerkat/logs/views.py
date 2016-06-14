# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from suit_dashboard.layout import Column, Grid, Row
from suit_dashboard.views import DashboardView

from meerkat.logs.boxes import (
    BoxLogsLinks, BoxLogsStatusCodes, BoxLogsMostVisitedPages,
    BoxLogsMostVisitedPagesLegend)


class HomeView(DashboardView):
    template_name = 'meerkat/main.html'
    crumbs = (
        {'url': 'admin:index', 'name': _('Home')},
    )
    grid = Grid(Row(Column(BoxLogsLinks())))


class LogsMenu(HomeView):
    crumbs = (
        {'url': 'admin:logs', 'name': 'Logs analysis'},
    )
    grid = Grid(Row(Column(BoxLogsLinks())))


class LogsStatusCodes(LogsMenu):
    crumbs = (
        {'url': 'admin:logs_status_codes', 'name': _('Status codes')},
    )
    grid = Grid(Row(Column(BoxLogsLinks(), BoxLogsStatusCodes())))


class LogsMostVisitedPages(LogsMenu):
    crumbs = (
        {'url': 'admin:logs_most_visited_pages',
         'name': _('Most visited pages')},
    )
    grid = Grid(Row(Column(BoxLogsLinks(), width=5),
                    Column(BoxLogsMostVisitedPagesLegend(), width=7)),
                Row(Column(BoxLogsMostVisitedPages(lazy=True))))
