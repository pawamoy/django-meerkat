# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import re
from os.path import join

from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.translation import ugettext as _

from meerkat.logs.parsers import NginXAccessLogParser
from suit_dashboard.box import Box, Item

from meerkat.logs.charts import (
    most_visited_pages_charts, most_visited_pages_legend_chart,
    status_codes_chart, status_codes_by_date_chart)
from meerkat.logs.data import STATUS_CODES
from meerkat.logs.stats import status_codes_by_date_stats


class BoxLogsLinks(Box):
    def get_title(self):
        return _('Logs analysis')

    def get_description(self):
        return _('The machine uses a program called "web server" to serve the '
                 'website over the internet. This web server records every '
                 'request sent by clients, with detailed information attached.'
                 ' These logs can be parsed to compute some statistical data.')

    def get_template(self):
        return 'meerkat/logs/links.html'


class BoxLogsStatusCodes(Box):
    def get_title(self):
        return _('Status codes')

    def get_items(self):
        return [
            Item(value=status_codes_chart(),
                 display=Item.AS_HIGHCHARTS),
            Item('status-code-description', _('Descriptions'),
                 [('%s %s' % (k, v['name']), v['desc'])
                  for k, v in sorted(STATUS_CODES.items())],
                 display=Item.AS_TABLE,
                 classes='table-hover table-striped')
        ]


class BoxLogsStatusCodesByDate(Box):
    def get_title(self):
        return _('Status codes by date')

    def get_template(self):
        return 'meerkat/logs/status_codes_by_date.html'

    def get_context(self):
        parser = NginXAccessLogParser(re.compile(r'nginx-access-.*'),
                                      top_dir=join(settings.BASE_DIR, 'logs'))
        stats = status_codes_by_date_stats(parser.parse_files())

        unique_ip_data = [{
            'type': 'column',
            'zIndex': 7,
            'name': _('Unique IPs'),
            'data': [(v['date'], v['unique_ip'])
                     for v in stats]
        }]

        attacks_data = [{
            'type': 'line',
            'zIndex': 9,
            'name': _('Attacks'),
            'data': [(v['date'], v['attacks'])
                     for v in stats]
        }]

        codes_data = [{
            'zIndex': 4,
            'name': '2xx',
            'data': [(v['date'], v['2xx']) for v in stats]
        }, {
            'zIndex': 5,
            'name': '3xx',
            'data': [(v['date'], v['3xx']) for v in stats]
        }, {
            'zIndex': 6,
            'name': '4xx',
            'data': [(v['date'], v['4xx']) for v in stats]
        }, {
            'zIndex': 8,
            'name': '5xx',
            'data': [(v['date'], v['5xx']) for v in stats]
        }]

        return {'generic_chart': json.dumps(status_codes_by_date_chart()),
                'unique_ip_data': json.dumps(unique_ip_data),
                'attacks_data': json.dumps(attacks_data),
                'codes_data': json.dumps(codes_data)}


class BoxLogsMostVisitedPagesLegend(Box):
    def get_items(self):
        return [Item(html_id='legend_chart',
                     value=most_visited_pages_legend_chart(),
                     display=Item.AS_HIGHCHARTS)]


class BoxLogsMostVisitedPages(Box):
    def get_title(self):
        return _('Most visited pages')

    def get_items(self):
        items = []
        for i, chart in enumerate(most_visited_pages_charts()):
            items.append(Item(html_id='most_visited_chart_%d' % i,
                              value=chart, display=Item.AS_HIGHCHARTS))

        return items


class BoxLogs(Box):
    def get_title(self):
        return _('Logs list')

    def get_description(self):
        return _('Logs are stored in files on the machine genida.unistra.fr. '
                 'This page allows you to consult them with pagination and '
                 'date filters.')

    def get_template(self):
        return 'meerkat/logs/logs_list.html'

    def get_context(self):
        filename_re = getattr(settings, 'LOGS_FILENAME_RE', None)
        format_re = getattr(settings, 'LOGS_FORMAT_RE', None)
        top_dir = getattr(settings, 'LOGS_TOP_DIR', None)
        parser = NginXAccessLogParser(filename_re, format_re, top_dir)
        all_logs = parser.parse_files()

        context = {'available_years': self.get_logs_years(all_logs)}
        if hasattr(self, 'year') and self.year:
            self.set_logs_by_year(all_logs, self.year)
            context['available_months'] = self.get_logs_year_months()
            if hasattr(self, 'month') and self.month:
                self.set_logs_by_month(self.month)
                context['available_days'] = self.get_logs_month_days()
                if hasattr(self, 'day') and self.day:
                    self.set_logs_by_day(self.day)
                    context['available_hours'] = self.get_logs_day_hours()
                    if hasattr(self, 'hour') and self.hour:
                        self.set_logs_by_hour(self.hour)
                        logs = self.by_hour
                        context['total'] = len(self.by_hour)
                    else:
                        logs = self.by_day
                        context['total'] = len(self.by_day)
                else:
                    logs = self.by_month
                    context['total'] = len(self.by_month)
            else:
                logs = self.by_year
                context['total'] = len(self.by_year)
        else:
            logs = []
            context['total'] = 0

        results_per_page = 25
        paginator = Paginator(logs, results_per_page)
        page = self.page if hasattr(self, 'page') else None
        try:
            context['logs'] = paginator.page(page)
        except PageNotAnInteger:
            context['logs'] = paginator.page(1)
        except EmptyPage:
            context['logs'] = paginator.page(paginator.num_pages)

        return context

    def month_name_to_number(self, month):
        return {
            'Jan': '01',
            'Feb': '02',
            'Mar': '03',
            'Apr': '04',
            'May': '05',
            'Jun': '06',
            'Jul': '07',
            'Aug': '08',
            'Sep': '09',
            'Oct': '10',
            'Nov': '11',
            'Dec': '12',
        }.get(month)

    def get_logs_years(self, logs):
        return sorted(set(l['year'] for l in logs))

    def get_logs_year_months(self):
        return sorted([self.month_name_to_number(m) for m in set(
            l['month'] for l in self.by_year)])

    def get_logs_month_days(self):
        return sorted(set(l['day'] for l in self.by_month))

    def get_logs_day_hours(self):
        return sorted(set(l['hour'] for l in self.by_day))

    def set_logs_by_year(self, logs, year):
        self.by_year = [l for l in logs if l['year'] == str(year)]

    def set_logs_by_month(self, month):
        self.by_month = [l for l in self.by_year
                         if self.month_name_to_number(l['month']) == month]

    def set_logs_by_day(self, day):
        self.by_day = [l for l in self.by_month if l['day'] == str(day)]

    def set_logs_by_hour(self, hour):
        self.by_hour = [l for l in self.by_day if l['hour'] == str(hour)]