# -*- coding: utf-8 -*-

"""
Admin sites definitions.

Currently just one DashboardSite.
"""

from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib.admin.sites import AdminSite

from suit_dashboard import get_realtime_urls

from .views import HomeView
from .logs.urls import logs_urlpatterns


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
            url(r'^logs/', include(logs_urlpatterns(self.admin_view))),
        ]

        custom_urls += get_realtime_urls(self.admin_view)

        del urls[0]
        return custom_urls + urls
