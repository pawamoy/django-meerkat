# -*- coding: utf-8 -*-

import json

from django.utils.translation import ugettext as _

from archan.checkers import (
    CodeClean, CompleteMediation, EconomyOfMechanism, LayeredArchitecture,
    LeastCommonMechanism, LeastPrivileges, OpenDesign,
    SeparationOfPrivileges, Checker)
from suit_dashboard import Box, Widget

from ..apps import AppSettings


app_settings = AppSettings()


class BoxArchan(Box):
    title = 'Design Structure Matrix'
    description = _(
        'This matrix represents the dependencies between the '
        'different parts of the GenIDA application. Values in '
        'cells are the number of dependencies from the module '
        'on the Y axis to the module on the X axis.')

    @property
    def widgets(self):
        def second_largest(numbers):
            count = 0
            m1 = m2 = float('-inf')
            for x in numbers:
                count += 1
                if x > m2:
                    if x >= m1:
                        m1, m2 = x, m1
                    else:
                        m2 = x
            return m2 if count >= 2 else None

        dsm = AppSettings.archan_dsm.get_dsm()

        heatmap_data = []
        for i in range(dsm.size):
            for j in range(dsm.size):
                v = dsm.dependency_matrix[i][j]
                if v > 0:
                    heatmap_data.append([i, j, v])

        chart_height = 18 * dsm.size + 200
        legend_height = chart_height - 0
        heatmap_chart_options = {
            'chart': {
                'type': 'heatmap',
                'height': chart_height,
                'inverted': True
            },
            'plotOptions': {
                'series': {
                    'turboThreshold': 0
                }
            },
            'title': {
                'text': _('Dependencies')
            },
            'xAxis': {
                'categories': dsm.entities
            },
            'yAxis': {
                'categories': dsm.entities,
                'title': None
            },
            'colorAxis': {
                'min': 0,
                'max': second_largest(j for i in dsm.dependency_matrix for j in i),
                'maxColor': '#FF900F'
            },
            'legend': {
                'align': 'right',
                'layout': 'vertical',
                'margin': 0,
                'verticalAlign': 'top',
                'y': 25,
                'symbolHeight': legend_height,
                'reversed': True
            },
            'tooltip': {
                'formatter': """
                    return '<b>' + this.series.xAxis.categories[
                        this.point.x] + '</b> imports <br><b>' +
                    this.point.value + '</b> items from <br><b>' +
                    this.series.yAxis.categories[this.point.y] + '</b>';"""
            },
            'series': [{
                'name': _('Dependencies'),
                'data': heatmap_data,
                'dataLabels': {
                    'enabled': True,
                }
            }]
        }

        checkers = [
            CompleteMediation(),
            EconomyOfMechanism(),
            SeparationOfPrivileges(),
            LeastPrivileges(),
            LeastCommonMechanism(),
            LayeredArchitecture(),
            OpenDesign(ok=False, ignore=True),
            CodeClean(ignore=True)
        ]
        results = [checker.run(dsm) for checker in checkers]

        return [
            Widget(
                html_id='heatmap_chart',
                content=json.dumps(heatmap_chart_options),
                template='meerkat/widgets/highcharts.html',
                js_code=['tooltip.formatter']),
            Widget(
                html_id='evaluation',
                name=_('Evaluation'),
                content={
                    'head': (
                        _('Criterion'), _('Result'), _('Description'), _('Message'), _('Hint')),
                    'body': [{
                        'cells': (
                            result.checker.name, {
                                Checker.PASSED: _('Passed'),
                                Checker.FAILED: _('Failed'),
                                Checker.NOT_IMPLEMENTED: _('Not implemented'),
                                Checker.IGNORED: _('Ignored')
                            }.get(result.code),
                            result.checker.description,
                            result.messages,
                            result.checker.hint),
                        'classes': {
                            Checker.PASSED: 'success',
                            Checker.FAILED: 'error',
                            Checker.NOT_IMPLEMENTED: 'default',
                            Checker.IGNORED: 'warning'
                        }.get(result.code)
                    } for result in results]
                },
                template='meerkat/archan/evaluation.html',
                classes='table-hover')
        ]


class BoxArchanLinks(Box):
    title = _('Architecture analysis')
    description = _('Analysis of the architecture strengths or weaknesses based on some criteria.')
    template = 'meerkat/archan/links.html'
