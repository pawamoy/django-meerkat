# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib.admin.sites import AdminSite

from suit_dashboard.urls import get_refreshable_urls

from meerkat.logs.views import HomeView, LogsMenu, LogsStatusCodes


class DashboardSite(AdminSite):
    """A Django AdminSite to allow registering custom dashboard views."""
    def get_urls(self):
        urls = super(DashboardSite, self).get_urls()
        custom_urls = [
            url(r'^$',
                self.admin_view(HomeView.as_view()),
                name='index'),
            url(r'^nginx/', include([
                url(r'^$',
                    self.admin_view(LogsMenu.as_view()),
                    name='nginx'),
                url(r'^status_codes$',
                    self.admin_view(LogsStatusCodes.as_view()),
                    name='nginx_status_codes'),
            ])),
        ]

        custom_urls += get_refreshable_urls(self.admin_view)

        del urls[0]
        return custom_urls + urls
