# -*- coding: utf-8 -*-

"""URLs for log submodule."""

from django.conf.urls import url

from .views import (
    LogsMenu, LogsMostVisitedPages, LogsStatusCodes, LogsStatusCodesByDate)


def logs_urlpatterns(admin_view=lambda x: x):
    """
    Return the URL patterns for the logs views.

    Args:
        admin_view (callable): admin_view method from an AdminSite instance.

    Returns:
        list: the URL patterns for the logs views.
    """
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
            name='logs_most_visited_pages')
    ]


urlpatterns = logs_urlpatterns()
