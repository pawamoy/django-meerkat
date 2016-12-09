# -*- coding: utf-8 -*-

"""
Django Suit Dashboard boxes.

This module defines the boxes to be used in the admin interface by
django-suit-dashboard package.
"""

from __future__ import absolute_import, unicode_literals

import json

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.translation import ugettext as _

from suit_dashboard.box import Box, Item

from .charts import (
    most_visited_pages_charts, most_visited_pages_legend_chart,
    status_codes_by_date_chart, status_codes_chart)
from .data import STATUS_CODES
from .parsers import NginXAccessLogParser
from .stats import status_codes_by_date_stats


class BoxLogsLinks(Box):
    """The menu for log views."""

    def get_title(self):
        """Get the title."""
        return _('Logs analysis')

    def get_description(self):
        """Get the description."""
        return _('The machine uses a program called "web server" to serve the '
                 'website over the internet. This web server records every '
                 'request sent by clients, with detailed information attached.'
                 ' These logs can be parsed to compute some statistical data.')

    def get_template(self):
        """Get the template."""
        return 'meerkat/logs/links.html'


class BoxLogsStatusCodes(Box):
    """The status codes widget."""

    def get_title(self):
        """Get the title."""
        return _('Status codes')

    def get_items(self):
        """Get the items."""
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
    """The status codes by date widget."""

    def get_title(self):
        """Get the title."""
        return _('Status codes by date')

    def get_template(self):
        """Get the template."""
        return 'meerkat/logs/status_codes_by_date.html'

    def get_context(self):
        """Get the context."""
        filename_re = getattr(settings, 'LOGS_FILENAME_RE', None)
        format_re = getattr(settings, 'LOGS_FORMAT_RE', None)
        top_dir = getattr(settings, 'LOGS_TOP_DIR', None)
        parser = NginXAccessLogParser(filename_re, format_re, top_dir)
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
    """The most visited pages legend."""

    def get_items(self):
        """Get the items."""
        return [Item(html_id='legend_chart',
                     value=most_visited_pages_legend_chart(),
                     display=Item.AS_HIGHCHARTS)]


class BoxLogsMostVisitedPages(Box):
    """The most visited pages legend."""

    def get_title(self):
        """Get the title."""
        return _('Most visited pages')

    def get_items(self):
        """Get the items."""
        items = []
        for i, chart in enumerate(most_visited_pages_charts()):
            items.append(Item(html_id='most_visited_chart_%d' % i,
                              value=chart, display=Item.AS_HIGHCHARTS))

        return items


class BoxLogs(Box):
    """The logs views. Paging and filtering options."""

    def get_title(self):
        """Get the title."""
        return _('Logs list')

    def get_description(self):
        """Get the description."""
        return _('Logs are stored in files on the machine genida.unistra.fr. '
                 'This page allows you to consult them with pagination and '
                 'date filters.')

    def get_template(self):
        """Get the template."""
        return 'meerkat/logs/logs_list.html'

    def get_context(self):
        """Get the context."""
        filename_re = getattr(settings, 'LOGS_FILENAME_RE', None)
        format_re = getattr(settings, 'LOGS_FORMAT_RE', None)
        top_dir = getattr(settings, 'LOGS_TOP_DIR', None)
        parser = NginXAccessLogParser(filename_re, format_re, top_dir)
        all_logs = parser.parse_files()

        context = {'available_years': self.get_available_years(all_logs)}
        if hasattr(self, 'year') and self.year:
            by_year = self.logs_by_year(all_logs, self.year)
            context['available_months'] = self.get_available_months(by_year)
            if hasattr(self, 'month') and self.month:
                by_month = self.logs_by_month(by_year, self.month)
                context['available_days'] = self.get_available_days(by_month)
                if hasattr(self, 'day') and self.day:
                    by_day = self.logs_by_day(by_month, self.day)
                    context['available_hours'] = self.get_available_hours(by_day)  # NOQA
                    if hasattr(self, 'hour') and self.hour:
                        logs = self.logs_by_hour(by_day, self.hour)
                    else:
                        logs = by_day
                else:
                    logs = by_month
            else:
                logs = by_year
        else:
            logs = []
        context['total'] = len(logs)

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
        """
        Convert a month name (MMM) to its number (01-12).

        Args:
            month ():

        Returns:

        """
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

    def get_available_years(self, logs):
        """
        Get the available years from the logs.

        Args:
            logs (list): the list of logs to search in.

        Returns:
            list: available years.
        """
        return sorted(set(l['year'] for l in logs))

    def get_available_months(self, logs):
        """
        Get the available months from the logs.

        Args:
            logs (list): the list of logs to search in.

        Returns:
            list: available months.
        """
        return sorted([self.month_name_to_number(m) for m in set(
            l['month'] for l in logs)])

    def get_available_days(self, logs):
        """
        Get the available days from the logs.

        Args:
            logs (list): the list of logs to search in.

        Returns:
            list: available days.
        """
        return sorted(set(l['day'] for l in logs))

    def get_available_hours(self, logs):
        """
        Get the available hours from the logs.

        Args:
            logs (list): the list of logs to search in.

        Returns:
            list: available hours.
        """
        return sorted(set(l['hour'] for l in logs))

    def logs_by_year(self, logs, year):
        """
        Get the logs for the given year.

        Args:
            logs (list): the list of logs to filter.
            year (int): a year.

        Returns:
            list: the filtered log list.
        """
        return [l for l in logs if l['year'] == str(year)]

    def logs_by_month(self, logs, month):
        """
        Get the logs for the given month.

        Args:
            logs (list): the list of logs to filter.
            month (int): the month number.

        Returns:
            list: the filtered log list.
        """
        return [l for l in logs
                if self.month_name_to_number(l['month']) == month]

    def logs_by_day(self, logs, day):
        """
        Get the logs for the given day.

        Args:
            logs (list): the list of logs to filter.
            day (int): a day number.

        Returns:
            list: the filtered log list.
        """
        return [l for l in logs if l['day'] == str(day)]

    def logs_by_hour(self, logs, hour):
        """
        Get the logs for the given hour.

        Args:
            logs (list): the list of logs to filter.
            hour (int): an hour (format depends on the logs).

        Returns:
            list: the filtered log list.
        """
        return [l for l in logs if l['hour'] == str(hour)]