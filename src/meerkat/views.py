# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

from suit_dashboard import DashboardView, Grid, Row, Column


class HomeView(DashboardView):
    """Main view. Parent class and entry point for other views."""

    template_name = 'meerkat/main.html'
    crumbs = ({'name': _('Home'), 'url': 'admin:index'}, )
    # TODO: find a way to add menu boxes for each meerkat plugin
    grid = Grid(Row(Column()))
