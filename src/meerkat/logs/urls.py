# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url

from .views import (
    LogsMenu, LogsMostVisitedPages, LogsStatusCodes, LogsStatusCodesByDate,
    LogsView)


def logs_urlpatterns(admin_view):
    logs_view = LogsView.as_view()
    return [
        url(r'^$',
            admin_view(LogsMenu.as_view()),
            name='logs'),
        url(r'^status_codes$',
            admin_view(LogsStatusCodes.as_view()),
            name='logs_status_codes'),
        url(r'^status_codes_by_date$',
            admin_view(LogsStatusCodesByDate.as_view()),
            name='logs_status_codes_by_date'),
        url(r'^most_visited_pages$',
            admin_view(LogsMostVisitedPages.as_view()),
            name='logs_most_visited_pages'),
        url(r'^list/', include([
            url(r'^$',
                admin_view(logs_view),
                name='logs_list'),
            url(r'^(?P<year>[0-9]{4})/$',
                admin_view(logs_view),
                name='logs_list_year'),
            url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
                admin_view(logs_view),
                name='logs_list_month'),
            url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/'
                r'(?P<day>[0-9]{2})/$',
                admin_view(logs_view),
                name='logs_list_day'),
            url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/'
                r'(?P<day>[0-9]{2})/(?P<hour>[0-9]{2})/$',
                admin_view(logs_view),
                name='logs_list_hour'),
        ]))
    ]
