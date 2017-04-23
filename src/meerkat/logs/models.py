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
import os
import threading
import time

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from dateutil import parser as dateutil_parser

from ..utils.geolocation import ip_info
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
        verbose_name=_(''), max_length=255)
    longitude = models.CharField(
        verbose_name=_(''), max_length=255)
    hostname = models.CharField(
        verbose_name=_(''), max_length=255)
    city = models.CharField(
        verbose_name=_(''), max_length=255)
    city_code = models.CharField(
        verbose_name=_(''), max_length=255, blank=True)
    region = models.CharField(
        verbose_name=_(''), max_length=255)
    region_code = models.CharField(
        verbose_name=_(''), max_length=255, blank=True)
    country = models.CharField(
        verbose_name=_(''), max_length=255)
    country_code = models.CharField(
        verbose_name=_(''), max_length=255, blank=True)
    continent = models.CharField(
        verbose_name=_(''), max_length=255, blank=True)
    continent_code = models.CharField(
        verbose_name=_(''), max_length=255, blank=True)
    org = models.CharField(
        verbose_name=_(''), max_length=255)

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
        loc = data['loc']
        lat, lon = loc.split(',')

        return Geolocation.objects.get_or_create(
            latitude=lat,
            longitude=lon,
            hostname=data.get('hostname', ''),
            city=data.get('city', ''),
            region=data.get('region', ''),
            country=data.get('country', ''),
            org=data.get('org', ''))


class GeolocationCheck(models.Model):
    """
    A model to keep track of the geolocation objects given IP address.

    Geolocation objects are generated from an IP address. They may already
    exist, so we don't want duplicates. This model attaches an IP to a
    geolocation object. It also adds the date of the check, because an IP will
    not always be related to the same geolocation, which changes over time.
    """

    ip_address = models.GenericIPAddressField(
        verbose_name=_(''), unique=True)
    date = models.DateField(
        verbose_name=_(''), default=datetime.date.today)
    geolocation = models.ForeignKey(
        Geolocation, verbose_name=_(''))

    class Meta:
        """Meta class for Django."""

        verbose_name = _('Geolocation check')
        verbose_name_plural = _('Geolocation checks')


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
        verbose_name=_(''), blank=True, null=True)
    datetime = models.DateTimeField(
        verbose_name=_(''), blank=True)
    timezone = models.CharField(
        verbose_name=_(''), max_length=10, blank=True)
    url = models.URLField(
        max_length=2047, verbose_name=_(''), blank=True, null=True)
    status_code = models.SmallIntegerField(
        verbose_name=_(''), blank=True)
    user_agent = models.TextField(
        verbose_name=_(''), blank=True)
    referrer = models.TextField(
        verbose_name=_(''), blank=True)
    upstream = models.TextField(
        verbose_name=_(''), blank=True)
    host = models.TextField(
        verbose_name=_(''), blank=True)
    server = models.TextField(
        verbose_name=_(''), blank=True)
    verb = models.CharField(
        verbose_name=_(''), max_length=30, blank=True, null=True)
    protocol = models.CharField(
        verbose_name=_(''), max_length=10, blank=True, null=True)
    port = models.PositiveIntegerField(
        verbose_name=_(''), blank=True, null=True)
    file_type = models.CharField(
        verbose_name=_(''), max_length=20, blank=True)
    https = models.BooleanField(
        verbose_name=_(''), default=False)
    bytes_sent = models.IntegerField(
        verbose_name=_(''), blank=True)

    # Error logs
    error = models.BooleanField(
        verbose_name=_(''), default=False)
    level = models.CharField(
        verbose_name=_(''), max_length=255, blank=True)
    message = models.TextField(
        verbose_name=_(''), blank=True)

    # Geolocation
    geolocation = models.ForeignKey(
        Geolocation,
        verbose_name=_(''), null=True)

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

    def update_geolocation(self, since_days=10, save=False):
        """
        Update the geolocation.

        Args:
            since_days (int): if checked less than this number of days ago,
                don't check again (default to 10 days).
            save (bool): whether to save anyway or not.

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
                if save:
                    self.save()
                return False

            # Get or create geolocation object
            geolocation, created = Geolocation.get_or_create_from_ip(
                self.client_ip_address)

            # Maybe data changed
            if created:
                last_check.geolocation = geolocation
                self.geolocation = geolocation
                self.save()
            elif save:
                self.save()

            # Update check time
            last_check.date = datetime.date.today()
            last_check.save()

            return True

        except GeolocationCheck.DoesNotExist:
            # Else if ip never checked, check it
            # Get or create geolocation object
            geolocation, created = Geolocation.get_or_create_from_ip(
                self.client_ip_address)

            # Create LastChecked object
            GeolocationCheck.objects.create(
                ip_address=self.client_ip_address,
                geolocation=geolocation)

            # Set geolocation
            self.geolocation = geolocation
            self.save()

            return True

    # TODO: write an init function (read past logs and insert all in db)

    @staticmethod
    def start_daemon():
        """
        Start a thread to continuously read log files and append lines in DB.

        Work in progress. Currently the thread doesn't append anything,
        it only print the information parsed from each line read.

        Returns:
            thread: the started thread.
        """
        filename_re = getattr(settings, 'LOGS_FILENAME_RE', None)
        format_re = getattr(settings, 'LOGS_FORMAT_RE', None)
        top_dir = getattr(settings, 'LOGS_TOP_DIR', None)
        parser = NginXAccessLogParser(filename_re, format_re, top_dir)

        # TODO: use a buffer to reduce number of commits in db (do bulk):
        # while read line
        #   append line to list
        #   if list's length > buffer
        #       create objects and insert in db
        #       empty list
        # if list's length > 0:
        #   create objects and insert in db

        def follow(file_name, seek_end):
            with open(file_name) as f:
                if seek_end:
                    f.seek(0, 2)
                while True:
                    line = f.readline()
                    if not line:
                        try:
                            if f.tell() > os.path.getsize(file_name):
                                f.close()
                                break
                        except FileNotFoundError:
                            pass
                        time.sleep(1)
                        continue
                    yield line

        def read_continuously():
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
                    log_object = RequestLog(**data)
                    log_object.update_geolocation(save=True)
                seek_end = False  # rotation occurred, do not seek end anymore

        RequestLog.daemon = threading.Thread(target=read_continuously)
        RequestLog.daemon.daemon = True
        RequestLog.daemon.start()
        return RequestLog.daemon

    # FIXME: see https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread-in-python#325528
    @staticmethod
    def stop_daemon():
        if hasattr(RequestLog, 'daemon'):
            RequestLog.daemon.join(timeout=1)
