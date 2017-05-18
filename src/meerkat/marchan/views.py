# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

from suit_dashboard import Grid, Row, Column

from ..views import HomeView
from .boxes import BoxArchan


class ArchanView(HomeView):
    crumbs = ({'name': 'Archan', 'url': 'admin:dashboard:archan'}, )
    grid = Grid(Row(Column(BoxArchan())))
