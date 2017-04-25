# -*- coding: utf-8 -*-

"""
Logs models.

These models are used to store the logs into the database. Using a database
allows to query the logs more efficiently without having to read the log
files every time.

Of course, these tables have to be updated in the background and in real-time,
which is the difficulty here. Work is in progress.
"""

import datetime
import sys
import time

from django.core.serializers.base import ProgressBar
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dateutil import parser as dateutil_parser

from ..apps import AppSettings
from ..exceptions import RateExceededError
from ..utils.file import follow
from ..utils.geolocation import ip_info
from ..utils.threading import StoppableThread
from ..utils.time import month_name_to_number
from .parsers import NginXAccessLogParser


# Define what information retrievable from the logs are pertinent
# so we can have universal log models (nginx, apache, uwsgi, ...).
# Remember our goal is security audit, not performance audit.


class Geolocation(models.Model):
    """A model to store a geolocation."""

    # Even if we have a paid account on some geolocation service,
    # an IP address had one and only one geolocation at the time of the
    # request. Therefore, these geolocations must be stored in the DB
    # if we want to compute statistical data about it. We cannot query
    # web-services each time we want to do this (data changed over time).
    latitude = models.CharField(
        verbose_name=_('Latitude'), max_length=255)
    longitude = models.CharField(
        verbose_name=_('Longitude'), max_length=255)
    hostname = models.CharField(
        verbose_name=_('Hostname'), max_length=255)
    city = models.CharField(
        verbose_name=_('City'), max_length=255)
    city_code = models.CharField(
        verbose_name=_('City code'), max_length=255, blank=True)
    region = models.CharField(
        verbose_name=_('Region'), max_length=255)
    region_code = models.CharField(
        verbose_name=_('Region code'), max_length=255, blank=True)
    country = models.CharField(
        verbose_name=_('Country'), max_length=255)
    country_code = models.CharField(
        verbose_name=_('Country code'), max_length=255, blank=True)
    continent = models.CharField(
        verbose_name=_('Continent'), max_length=255, blank=True)
    continent_code = models.CharField(
        verbose_name=_('Continent code'), max_length=255, blank=True)
    org = models.CharField(
        verbose_name=_('Organization'), max_length=255)

    class Meta:
        """Meta class for Django."""

        unique_together = ('latitude', 'longitude', 'hostname',
                           'city', 'region', 'country', 'org')
        verbose_name = _('Geolocation')
        verbose_name_plural = _('Geolocations')

    def __str__(self):
        return '%s,%s' % (self.latitude, self.longitude)

    @staticmethod
    def get_or_create_from_ip(ip):
        """
        Get or create an entry using obtained information from an IP.

        Args:
            ip (str): IP address xxx.xxx.xxx.xxx.

        Returns:
            geolocation: an instance of Geolocation.
        """
        data = ip_info(ip)
        loc = data.get('loc', None)
        lat = lon = ''
        if loc:
            lat, lon = loc.split(',')

        return Geolocation.objects.get_or_create(
            latitude=lat,
            longitude=lon,
            hostname=data.get('hostname', ''),
            city=data.get('city', ''),
            region=data.get('region', ''),
            country=data.get('country', ''),
            org=data.get('org', ''))

    def ip_addresses(self):
        return list(GeolocationCheck.objects.filter(
            geolocation=self).values_list('ip_address', flat=True))


class GeolocationCheck(models.Model):
    """
    A model to keep track of the geolocation objects given IP address.

    Geolocation objects are generated from an IP address. They may already
    exist, so we don't want duplicates. This model attaches an IP to a
    geolocation object. It also adds the date of the check, because an IP will
    not always be related to the same geolocation, which changes over time.
    """

    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP address'), unique=True)
    date = models.DateField(
        verbose_name=_('Date'), default=datetime.date.today)
    geolocation = models.ForeignKey(
        Geolocation, verbose_name=_('Geolocation'))

    class Meta:
        """Meta class for Django."""

        verbose_name = _('Geolocation check')
        verbose_name_plural = _('Geolocation checks')

    @staticmethod
    def check_ip(ip):
        geolocation, created = Geolocation.get_or_create_from_ip(ip)
        GeolocationCheck.objects.create(
            ip_address=ip,
            geolocation=geolocation)
        return geolocation


class RequestLog(models.Model):
    """
    A model to store the request logs.

    Work in progress.

    Attributes:
        client_ip_address
        datetime
        timezone
        url
        status_code
        user_agent
        referrer
        upstream
        host
        server
        verb
        protocol
        port
        file_type
        https
        bytes_sent

        error
        level
        message

        geolocation
    """

    # General info
    client_ip_address = models.GenericIPAddressField(
        verbose_name=_('Client IP address'), blank=True, null=True)
    datetime = models.DateTimeField(
        verbose_name=_('Datetime'), blank=True)
    timezone = models.CharField(
        verbose_name=_('Timezone'), max_length=10, blank=True)
    url = models.URLField(
        max_length=2047, verbose_name=_('URL'), blank=True)
    status_code = models.SmallIntegerField(
        verbose_name=_('Status code'), blank=True)
    user_agent = models.TextField(
        verbose_name=_('User agent'), blank=True)
    referrer = models.TextField(
        verbose_name=_('Referrer'), blank=True)
    upstream = models.TextField(
        verbose_name=_('Upstream'), blank=True)
    host = models.TextField(
        verbose_name=_('Host'), blank=True)
    server = models.TextField(
        verbose_name=_('Server'), blank=True)
    verb = models.CharField(
        verbose_name=_('Verb'), max_length=30, blank=True)
    protocol = models.CharField(
        verbose_name=_('Protocol'), max_length=10, blank=True)
    port = models.PositiveIntegerField(
        verbose_name=_('Port'), blank=True, null=True)
    file_type = models.CharField(
        verbose_name=_('File type'), max_length=20, blank=True)
    https = models.BooleanField(
        verbose_name=_('HTTPS'), default=False)
    bytes_sent = models.IntegerField(
        verbose_name=_('Bytes sent'), blank=True)

    # Error logs
    error = models.BooleanField(
        verbose_name=_('Error'), default=False)
    level = models.CharField(
        verbose_name=_('Level'), max_length=255, blank=True)
    message = models.TextField(
        verbose_name=_('Message'), blank=True)

    # Geolocation
    geolocation = models.ForeignKey(
        Geolocation,
        verbose_name=_('IP geolocation'), null=True)

    # Not really useful for now
    # request = models.TextField()
    # response_time = models.TimeField()
    # response_header = models.TextField()
    # response_body = models.TextField()
    #
    # proxy_host = models.CharField(max_length=255)
    # proxy_port = models.PositiveIntegerField()
    # proxy_protocol_address = models.CharField(max_length=255)
    # proxy_protocol_port = models.PositiveIntegerField()
    #
    # ssl_cipher = models.CharField(max_length=255)
    # ssl_client_cert = models.CharField(max_length=255)
    # ssl_client_fingerprint = models.CharField(max_length=255)
    # ssl_client_i_dn = models.CharField(max_length=255)
    # ssl_client_raw_cert = models.CharField(max_length=255)
    # ssl_client_s_dn = models.CharField(max_length=255)
    # ssl_client_serial = models.CharField(max_length=255)
    # ssl_client_verify = models.CharField(max_length=255)
    # ssl_protocol = models.CharField(max_length=255)
    # ssl_server_name = models.CharField(max_length=255)
    # ssl_session_id = models.CharField(max_length=255)
    # ssl_session_reused = models.CharField(max_length=255)
    #
    # tcp_info_rtt = models.CharField(max_length=255)
    # tcp_info_rtt_var = models.CharField(max_length=255)
    # tcp_info_snd_cwnd = models.CharField(max_length=255)
    # tcp_info_rcv_space = models.CharField(max_length=255)
    #
    # upstream_address = models.CharField(max_length=255)
    # upstream_cache_status = models.CharField(max_length=255)
    # upstream_connect_time = models.CharField(max_length=255)
    # upstream_cookie = models.CharField(max_length=255)
    # upstream_header_time = models.CharField(max_length=255)
    # upstream_http = models.CharField(max_length=255)
    # upstream_response_length = models.CharField(max_length=255)
    # upstream_response_time = models.CharField(max_length=255)
    # upstream_status = models.CharField(max_length=255)

    class Meta:
        """Meta class for Django."""

        verbose_name = _('Request log')
        verbose_name_plural = _('Request logs')

    def __str__(self):
        return str(self.datetime)

    def update_geolocation(self, since_days=10, save=False, force=False):
        """
        Update the geolocation.

        Args:
            since_days (int): if checked less than this number of days ago,
                don't check again (default to 10 days).
            save (bool): whether to save anyway or not.
            force (bool): whether to update geolocation to last checked one.

        Returns:
            bool: check was run. Geolocation might not have been updated.
        """
        # If ip already checked
        try:
            last_check = GeolocationCheck.objects.get(
                ip_address=self.client_ip_address)

            # If checked less than since_days ago, don't check again
            since_last = datetime.date.today() - last_check.date
            if since_last <= datetime.timedelta(days=since_days):
                if not self.geolocation or (
                        self.geolocation != last_check.geolocation and force):
                    self.geolocation = last_check.geolocation
                    self.save()
                    return True
                elif save:
                    self.save()
                return False

            # Get or create geolocation object
            geolocation, created = Geolocation.get_or_create_from_ip(
                self.client_ip_address)

            # Update check time
            last_check.date = datetime.date.today()
            last_check.save()

            # Maybe data changed
            if created:
                last_check.geolocation = geolocation
                self.geolocation = geolocation
                self.save()
                return True
            elif save:
                self.save()

            return False

        except GeolocationCheck.DoesNotExist:
            # Else if ip never checked, check it and set geolocation
            self.geolocation = GeolocationCheck.check_ip(self.client_ip_address)
            self.save()

            return True

    @staticmethod
    def data_to_log(data):
        log_datetime = '%s%s%sT%s%s%s%s' % (
            data.pop('year'),
            month_name_to_number(data.pop('month')),
            data.pop('day'),
            data.pop('hour'),
            data.pop('minute'),
            data.pop('second'),
            data.get('timezone'))
        data['datetime'] = dateutil_parser.parse(log_datetime)
        data['client_ip_address'] = data.pop('ip_address')
        data = {k: v for k, v in data.items() if v is not None}
        return RequestLog(**data)

    @staticmethod
    def parse_all(buffer_size=512):
        parser = NginXAccessLogParser(
            file_path_regex=AppSettings.get_logs_file_path_regex(),
            log_format_regex=AppSettings.get_logs_format_regex(),
            top_dir=AppSettings.get_logs_top_dir())

        buffer = []
        start = datetime.datetime.now()
        for log_file in parser.matching_files():
            n_lines = count_lines(log_file)
            progress_bar = ProgressBar(sys.stdout, n_lines)
            print('Reading log file %s: %s lines' % (log_file, n_lines))
            with open(log_file) as f:
                for count, line in enumerate(f, 1):
                    try:
                        data = parser.parse_string(line)
                    except AttributeError:
                        # TODO: log the line
                        print('Error while parsing log line: %s' % line)
                        continue
                    buffer.append(RequestLog.data_to_log(data))
                    if len(buffer) >= buffer_size:
                        RequestLog.objects.bulk_create(buffer)
                        buffer.clear()
                    progress_bar.update(count)
                if len(buffer) > 0:
                    RequestLog.objects.bulk_create(buffer)
                    buffer.clear()
        end = datetime.datetime.now()
        print('Elapsed time: %s' % (end - start))

    @staticmethod
    def geolocalize():
        param = 'client_ip_address'
        unique_ips = set(RequestLog.objects.distinct(param).values_list(param, flat=True))
        checked_ips = set(GeolocationCheck.objects.values_list('ip_address', flat=True))
        not_checked_ips = unique_ips - checked_ips
        print('Checking IPs geolocations (%s)' % len(not_checked_ips))
        # check_progress_bar = ProgressBar(sys.stdout, len(not_checked_ips))
        for count, ip in enumerate(not_checked_ips, 1):
            print('Checking IP %s' % ip)
            try:
                GeolocationCheck.check_ip(ip)
            except RateExceededError:
                break
            # check_progress_bar.update(count)
        checks = GeolocationCheck.objects.all()
        print('Updating request logs geolocations (%s)' % checks.count())
        logs_progress_bar = ProgressBar(sys.stdout, checks.count())
        for count, check in enumerate(checks, 1):
            RequestLog.objects.filter(
                geolocation=None, client_ip_address=check.ip_address
            ).update(geolocation=check.geolocation)
            logs_progress_bar.update(count)

    @staticmethod
    def start_daemon():
        """
        Start a thread to continuously read log files and append lines in DB.

        Work in progress. Currently the thread doesn't append anything,
        it only print the information parsed from each line read.

        Returns:
            thread: the started thread.
        """
        parser = NginXAccessLogParser(
            file_path_regex=AppSettings.get_logs_file_path_regex(),
            log_format_regex=AppSettings.get_logs_format_regex(),
            top_dir=AppSettings.get_logs_top_dir())

        class ParseLogToDBThread(StoppableThread):
            def run(self):
                file_name = parser.matching_files()[0]
                seek_end = True
                while True:
                    for line in follow(file_name, seek_end):
                        try:
                            data = parser.parse_string(line)
                        except AttributeError:
                            # TODO: log the line
                            print('Error while parsing log line: %s' % line)
                            continue
                        log_object = RequestLog.data_to_log(data)
                        log_object.update_geolocation(save=True)
                        if self.stopped():
                            break
                    if self.stopped():
                        break
                    seek_end = False

        RequestLog.daemon = ParseLogToDBThread(daemon=True)
        RequestLog.daemon.start()
        return RequestLog.daemon

    @staticmethod
    def stop_daemon():
        if hasattr(RequestLog, 'daemon'):
            RequestLog.daemon.stop()


def count_lines(file_name):
    i = -1
    with open(file_name) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
