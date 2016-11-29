# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib.admin.sites import AdminSite

from suit_dashboard.urls import get_refreshable_urls

from meerkat.logs.views import (
    HomeView, LogsMenu, LogsMostVisitedPages, LogsStatusCodes,
    LogsStatusCodesByDate, LogsView)


class DashboardSite(AdminSite):
    """A Django AdminSite to allow registering custom dashboard views."""
    def get_urls(self):
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
                url(r'^list/', include([
                    url(r'^$',
                        self.admin_view(LogsView.as_view()),
                        name='logs_list'),
                    url(r'^(?P<year>[0-9]{4})/$',
                        self.admin_view(LogsView.as_view()),
                        name='logs_list_year'),
                    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
                        self.admin_view(LogsView.as_view()),
                        name='logs_list_month'),
                    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/'
                        r'(?P<day>[0-9]{2})/$',
                        self.admin_view(LogsView.as_view()),
                        name='logs_list_day'),
                    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/'
                        r'(?P<day>[0-9]{2})/(?P<hour>[0-9]{2})/$',
                        self.admin_view(LogsView.as_view()),
                        name='logs_list_hour'),
                ]))
            ])),
        ]

        custom_urls += get_refreshable_urls(self.admin_view)

        del urls[0]
        return custom_urls + urls
