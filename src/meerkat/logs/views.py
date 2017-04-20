# -*- coding: utf-8 -*-

"""Views for logs submodule."""

from django.utils.translation import ugettext_lazy as _

from suit_dashboard.layout import Column, Grid, Row
from suit_dashboard.views import DashboardView

from .boxes import (
    BoxLogs, BoxLogsLinks, BoxLogsMostVisitedPages,
    BoxLogsMostVisitedPagesLegend, BoxLogsStatusCodes,
    BoxLogsStatusCodesByDate)


class HomeView(DashboardView):
    """Main view. Parent class and entry point for other views."""

    template_name = 'meerkat/main.html'
    crumbs = ({'name': _('Home'), 'url': 'admin:index'}, )
    grid = Grid(Row(Column(BoxLogsLinks())))


class LogsMenu(HomeView):
    """View for logs menu."""

    crumbs = ({'name': 'Logs analysis', 'url': 'admin:logs'}, )
    grid = Grid(Row(Column(BoxLogsLinks())))


class LogsStatusCodes(LogsMenu):
    """View for status codes."""

    crumbs = (
        {'name': _('Status codes'), 'url': 'admin:logs_status_codes'},
    )
    grid = Grid(Row(Column(BoxLogsLinks(), BoxLogsStatusCodes())))


class LogsStatusCodesByDate(LogsMenu):
    """View for status codes by date."""

    crumbs = ({'name': _('Status codes by date'),
               'url': 'admin:logs_status_code_by_date'},)
    grid = Grid(Row(Column(BoxLogsLinks())),
                Row(Column(BoxLogsStatusCodesByDate())))


class LogsMostVisitedPages(LogsMenu):
    """View for most visited pages."""

    crumbs = ({'name': _('Most visited pages'),
               'url': 'admin:logs_most_visited_pages'}, )
    grid = Grid(Row(Column(BoxLogsLinks(), width=5),
                    Column(BoxLogsMostVisitedPagesLegend(), width=7)),
                Row(Column(BoxLogsMostVisitedPages())))


class LogsView(LogsMenu):
    """View for logs pages."""

    crumbs = ({'name': _('Logs'), 'url': 'admin:logs'}, )

    def get(self, request, *args, **kwargs):
        """
        Allow to pass GET parameters for pagination.

        Args:
            request (request): the django request.
            *args (): request arguments.
            **kwargs (): optional year, month, day and hour, and more.

        Returns:
            the rendered django view.
        """
        self.extra_context = {
            'year': kwargs.pop('year', None),
            'month': kwargs.pop('month', None),
            'day': kwargs.pop('day', None),
            'hour': kwargs.pop('hour', None),
            'page': request.GET.get('page')
        }
        self.grid = Grid(Row(Column(BoxLogsLinks(),
                                    BoxLogs(**self.extra_context))))
        return super(LogsView, self).get(request, *args, **kwargs)
