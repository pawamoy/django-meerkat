# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
from os.path import join

from django.conf import settings
from django.utils.translation import ugettext as _

from suit_dashboard.decorators import refreshable

from meerkat.logs.data import STATUS_CODES
from meerkat.logs.parsers import NginXAccessLogParser
from meerkat.logs.stats import status_codes_stats, most_visited_pages_stats
from meerkat.utils.url import url_is_asset, url_is_old, url_is_false_negative


@refreshable
def status_codes_chart():
    parser = NginXAccessLogParser(re.compile(r'nginx-access-.*'),
                                  top_dir=join(settings.BASE_DIR, 'logs'))
    stats = status_codes_stats(parser.parse_files())
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
        # 'tooltip': {
        #     # FIXME: find a way to handle javascript code
        #     'formatter': "return this.y + '/' + this.total + ' (' + "
        #                  "Highcharts.numberFormat(this.percentage, 1) + '%)';"
        # },
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


def most_visited_pages_legend_chart():
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
                _('Valid project URL'),
                _('Valid asset URL'),
                _('Common but not valid asset URL'),
                _('Old project URL'),
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
                {'color': '#AFE4FD', 'y': 1},
                {'color': '#DBDBDB', 'y': 1},
                {'color': '#F1F2B6', 'y': 1},
                {'color': '#B6B6F2', 'y': 1},
                {'color': '#9CD8AC', 'y': 1},
                {'color': '#FFB31A', 'y': 1},
            ]
        }]
    }


def most_visited_pages_charts():
    parser = NginXAccessLogParser(re.compile(r'nginx-access-.*'),
                                  top_dir=join(settings.BASE_DIR, 'logs'))
    stats = most_visited_pages_stats(parser.parse_files())

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
                'text': _('More than %d times' % bound) if i == 0 else
                _('Between %d and %d times') % (
                    bound, stats['more_than_10'][i-1]['bound'])
            },
            'xAxis': {
                'categories': [u for (c, u, v) in subset],
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
        for index, (count, url, valid) in enumerate(subset):
            data = {
                'x': index,
                'y': count
            }
            if valid:
                if not url_is_asset(url):
                    color = '#AFE4FD'
                else:
                    color = '#DBDBDB'
            else:
                if url_is_asset(url):
                    color = '#F1F2B6'
                elif url_is_old(url):
                    color = '#B6B6F2'
                elif url_is_false_negative(url):
                    color = '#9CD8AC'
                else:
                    color = '#FFB31A'
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
    total_distinct = sum([v['distinct'] for k, v in occurrences])
    total_occurrences = sum([v['total'] for k, v in occurrences])
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
                'dis': occurrences['project']['distinct'],
                'y': occurrences['project']['total'],
                'occ': occurrences['project']['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': '#AFE4FD'
            }, {
                'name': _('Valid asset URL'),
                'dis': occurrences['asset']['distinct'],
                'y': occurrences['asset']['total'],
                'occ': occurrences['asset']['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': '#DBDBDB'
            }, {
                'name': _('Common but not valid asset URL'),
                'dis': occurrences['common_asset']['distinct'],
                'y': occurrences['common_asset']['total'],
                'occ': occurrences['common_asset']['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': '#F1F2B6'
            }, {
                'name': _('Old project URL'),
                'dis': occurrences['old']['distinct'],
                'y': occurrences['old']['total'],
                'occ': occurrences['old']['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': '#B6B6F2'
            }, {
                'name': _('False-negative project URL'),
                'dis': occurrences['false']['distinct'],
                'y': occurrences['false']['total'],
                'occ': occurrences['false']['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': '#9CD8AC'
            }, {
                'name': _('Suspicious URL (potential attack)'),
                'dis': occurrences['suspicious']['distinct'],
                'y': occurrences['suspicious']['total'],
                'occ': occurrences['suspicious']['total'],
                'total_dis': total_distinct,
                'total_occ': total_occurrences,
                'color': '#FFB31A'
            }]
        }]
    })

    return charts
