# -*- coding: utf-8 -*-

"""
Admin sites definitions.

Currently just one DashboardSite.
"""

from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib.admin.sites import AdminSite

from suit_dashboard import get_realtime_urls

from .logs.views import (
    HomeView, LogsMenu, LogsMostVisitedPages, LogsStatusCodes,
    LogsStatusCodesByDate)


class DashboardSite(AdminSite):
    """A Django AdminSite to allow registering custom dashboard views."""

    def get_urls(self):
        """
        Get urls method.

        Returns:
            list: the list of url objects.
        """
        urls = super(DashboardSite, self).get_urls()
        custom_urls = [
            url(r'^$',
                self.admin_view(HomeView.as_view()),
                name='index'),
            url(r'^logs/', include([
                url(r'^$',
                    self.admin_view(LogsMenu.as_view()),
                    name='logs'),
                url(r'^status_codes$',
                    self.admin_view(LogsStatusCodes.as_view()),
                    name='logs_status_codes'),
                url(r'^status_codes_by_date$',
                    self.admin_view(LogsStatusCodesByDate.as_view()),
                    name='logs_status_codes_by_date'),
                url(r'^most_visited_pages$',
                    self.admin_view(LogsMostVisitedPages.as_view()),
                    name='logs_most_visited_pages'),
            ])),
        ]

        custom_urls += get_realtime_urls(self.admin_view)

        del urls[0]
        return custom_urls + urls
