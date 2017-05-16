# -*- coding: utf-8 -*-

"""
Chart methods.

This module contains the methods that will build the chart dictionaries
from data.
"""

from django.utils.translation import ugettext as _

from ..utils.url import (
    ASSET, COMMON_ASSET, OLD_ASSET, OLD_PROJECT,
    PROJECT, SUSPICIOUS, FALSE_NEGATIVE)
from .data import STATUS_CODES
from .stats import most_visited_pages_stats, status_codes_stats


def status_codes_chart():
    """Chart for status codes."""
    stats = status_codes_stats()

    chart_options = {
        'chart': {
            'type': 'pie'
        },
        'title': {
            'text': ''
        },
        'subtitle': {
            'text': ''
        },
        'tooltip': {
          'formatter': "return this.y + '/' + this.total + ' (' + "
                       "Highcharts.numberFormat(this.percentage, 1) + '%)';"
        },
        'legend': {
            'enabled': True,
        },
        'plotOptions': {
            'pie': {
                'allowPointSelect': True,
                'cursor': 'pointer',
                'dataLabels': {
                    'enabled': True,
                    'format': '<b>{point.name}</b>: {point.y}/{point.total} '
                              '({point.percentage:.1f}%)'
                },
                'showInLegend': True
            }
        },
        'series': [{
            'name': _('Status Codes'),
            'colorByPoint': True,
            'data': sorted(
                [{'name': '%s %s' % (k, STATUS_CODES[int(k)]['name']), 'y': v}
                 for k, v in stats.items()],
                key=lambda x: x['y'],
                reverse=True)
        }]
    }

    return chart_options


def status_codes_by_date_chart():
    """Chart for status codes by date."""
    return {
        'chart': {
            'type': 'area',
            'zoomType': 'x'
        },
        'title': {'text': None},
        'xAxis': {'type': 'datetime'},
        'yAxis': {'title': {'text': None}},
        'legend': {'enabled': True},
        'tooltip': {'shared': True},
        'plotOptions': {
            'area': {
                'lineWidth': 1,
                'marker': {
                    'lineWidth': 1,
                }
            }
        }
    }


URL_TYPE_COLOR = {
    PROJECT: '#AFE4FD',
    ASSET: '#DBDBDB',
    COMMON_ASSET: '#F1F2B6',
    OLD_ASSET: '#808080',
    OLD_PROJECT: '#B6B6F2',
    FALSE_NEGATIVE: '#9CD8AC',
    SUSPICIOUS: '#FFB31A'
}


def most_visited_pages_legend_chart():
    """Chart for most visited pages legend."""
    return {
        'chart': {
            'type': 'bar',
            'height': 200,
        },
        'title': {
            'text': _('Legend')
        },
        'xAxis': {
            'categories': [
                _('Project URL'),
                _('Old project URL'),
                _('Asset URL'),
                _('Old asset URL'),
                _('Common asset URL'),
                _('False-negative project URL'),
                _('Suspicious URL (potential attack)')
            ],
            'title': {
                'text': None
            }
        },
        'yAxis': {
            'title': {
                'text': None,
                'align': 'high'
            },
            'labels': {
                'overflow': 'justify'
            }
        },
        'tooltip': {
            'enabled': False
        },
        'legend': {
            'enabled': False
        },
        'credits': {
            'enabled': False
        },
        'series': [{
            'name': _('Legend'),
            'data': [
                {'color': URL_TYPE_COLOR[PROJECT], 'y': 1},
                {'color': URL_TYPE_COLOR[OLD_PROJECT], 'y': 1},
                {'color': URL_TYPE_COLOR[ASSET], 'y': 1},
                {'color': URL_TYPE_COLOR[OLD_ASSET], 'y': 1},
                {'color': URL_TYPE_COLOR[COMMON_ASSET], 'y': 1},
                {'color': URL_TYPE_COLOR[FALSE_NEGATIVE], 'y': 1},
                {'color': URL_TYPE_COLOR[SUSPICIOUS], 'y': 1},
            ]
        }]
    }


def most_visited_pages_charts():
    """Chart for most visited pages."""
    stats = most_visited_pages_stats()

    charts = []

    for i, stat in enumerate(stats['more_than_10']):
        bound = stat['bound']
        subset = stat['subset']

        chart_options = {
            'chart': {
                'type': 'bar',
                'height': 15 * len(subset) + 100
            },
            'title': {
                'text': {0: _('More than %d times') % bound}.get(
                    i, _('Between %d and %d times') % (
                        bound, stats['more_than_10'][i - 1]['bound']))
            },
            'xAxis': {
                'categories': [u for (u, c, t) in subset],
                'title': {
                    'text': None
                }
            },
            'yAxis': {
                'title': {
                    'text': None
                }
            },
            'plotOptions': {
                'bar': {
                    'dataLabels': {
                        'enabled': True
                    }
                },
            },
            'tooltip': {
                'enabled': False
            },
            'legend': {
                'enabled': False
            },
            'credits': {
                'enabled': False
            },
        }

        series_data = []
        for index, (url, count, url_type) in enumerate(subset):
            data = {
                'x': index,
                'y': count
            }
            color = URL_TYPE_COLOR[url_type]
            data['color'] = color
            series_data.append(data)
        chart_options['series'] = [{
            'name': _('Requests'),
            'data': series_data
        }]

        charts.append(chart_options)

    point_formatter_code = """
        return '<br>%s: <strong>' + this.dis + '</strong>(' +
        Highcharts.numberFormat(this.dis / this.total_dis * 100, 1) + '%%)' +
        '<br>%s: <strong>' + this.occ + '</strong> (' +
        Highcharts.numberFormat(this.occ / this.total_occ * 100, 1)  + '%%)';
        """ % (_('Distinct URLs'), _('Occurrences'))

    occurrences = stats['less_than_10']
    total_distinct = sum([v['distinct'] for k, v in occurrences.items()])
    total_occurrences = sum([v['total'] for k, v in occurrences.items()])
    charts.append({
        'chart': {
            'plotBackgroundColor': None,
            'plotBorderWidth': None,
            'plotShadow': False,
            'type': 'pie'
        },
        'title': {
            'text': _('Less than 10 (type repartition)')
        },
        'plotOptions': {
            'pie': {
                'allowPointSelect': True,
                'cursor': 'pointer',
                'dataLabels': {
                    'enabled': False
                },
                'showInLegend': True,
                'tooltip': {
                    'pointFormatter': point_formatter_code
                },
            }
        },
        'series': [{
            'name': '',
            'colorByPoint': True,
            'data': [{
                'name': _('Valid project URL'),
                'dis': occurrences[PROJECT]['distinct'],
                'y': occurrences[PROJECT]['total'],
                'occ': occurrences[PROJECT]['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': URL_TYPE_COLOR[PROJECT]
            }, {
                'name': _('Old project URL'),
                'dis': occurrences[OLD_PROJECT]['distinct'],
                'y': occurrences[OLD_PROJECT]['total'],
                'occ': occurrences[OLD_PROJECT]['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': URL_TYPE_COLOR[OLD_PROJECT]
            }, {
                'name': _('Valid asset URL'),
                'dis': occurrences[ASSET]['distinct'],
                'y': occurrences[ASSET]['total'],
                'occ': occurrences[ASSET]['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': URL_TYPE_COLOR[ASSET]
            }, {
                'name': _('Old asset URL'),
                'dis': occurrences[OLD_ASSET]['distinct'],
                'y': occurrences[OLD_ASSET]['total'],
                'occ': occurrences[OLD_ASSET]['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': URL_TYPE_COLOR[OLD_ASSET]
            }, {
                'name': _('Common asset URL'),
                'dis': occurrences[COMMON_ASSET]['distinct'],
                'y': occurrences[COMMON_ASSET]['total'],
                'occ': occurrences[COMMON_ASSET]['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': URL_TYPE_COLOR[COMMON_ASSET]
            }, {
                'name': _('False-negative project URL'),
                'dis': occurrences[FALSE_NEGATIVE]['distinct'],
                'y': occurrences[FALSE_NEGATIVE]['total'],
                'occ': occurrences[FALSE_NEGATIVE]['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': URL_TYPE_COLOR[FALSE_NEGATIVE]
            }, {
                'name': _('Suspicious URL (potential attack)'),
                'dis': occurrences[SUSPICIOUS]['distinct'],
                'y': occurrences[SUSPICIOUS]['total'],
                'occ': occurrences[SUSPICIOUS]['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': URL_TYPE_COLOR[SUSPICIOUS]
            }]
        }]
    })

    return charts
