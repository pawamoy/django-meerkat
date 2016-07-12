# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import threading
import time
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from meerkat.logs.parsers import NginXAccessLogParser
from meerkat.utils.geolocation import ip_info


# Define what information retrievable from the logs are pertinent
# so we can have universal log models (nginx, apache, uwsgi, ...).
# Remember our goal is security audit, not performance audit.


class Geolocation(models.Model):
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
        unique_together = ('latitude', 'longitude', 'hostname',
                           'city', 'region', 'country', 'org')
        verbose_name = _('Geolocation')
        verbose_name_plural = _('Geolocations')

    def __str__(self):
        return '%s,%s' % (self.latitude, self.longitude)

    @staticmethod
    def get_or_create_from_ip(ip):
        # Else check it
        data = ip_info(ip)
        loc = data['loc']
        lat, lon = loc.split(',')

        # Get or create geolocation object
        return Geolocation.objects.get_or_create(
            latitude=lat,
            longitude=lon,
            hostname=data['hostname'],
            city=data['city'],
            region=data['region'],
            country=data['country'],
            org=data['org'])


class GeolocationCheck(models.Model):
    ip_address = models.IPAddressField(
        verbose_name=_(''), unique=True)
    date = models.DateField(
        verbose_name=_(''), default=datetime.date.today)
    geolocation = models.ForeignKey(
        Geolocation, verbose_name=_(''))

    class Meta:
        verbose_name = _('Geolocation check')
        verbose_name_plural = _('Geolocation checks')


class RequestLog(models.Model):
    # General info
    client_ip_address = models.IPAddressField(
        verbose_name=_(''), blank=True)
    datetime = models.DateTimeField(
        verbose_name=_(''), blank=True)
    timezone = models.CharField(
        verbose_name=_(''), max_length=10, blank=True)
    url = models.URLField(
        verbose_name=_(''), blank=True)
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
        verbose_name=_(''), max_length=10, blank=True)
    protocol = models.CharField(
        verbose_name=_(''), max_length=10, blank=True)
    port = models.PositiveIntegerField(
        verbose_name=_(''), blank=True)
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
        verbose_name = _('Request log')
        verbose_name_plural = _('Request logs')

    def __str__(self):
        return str(self.datetime)

    def update_geolocation(self, since_days=10):
        # If ip already checked
        try:
            last_check = GeolocationCheck.objects.get(
                ip_address=self.client_ip_address)

            # If checked less than since_days ago, don't check again
            since_last = datetime.date.today() - last_check.date
            if since_last <= datetime.timedelta(days=since_days):
                return False

            # Get or create geolocation object
            geolocation, created = Geolocation.get_or_create_from_ip(
                self.client_ip_address)

            # Maybe data changed
            if created:
                last_check.geolocation = geolocation
                self.geolocation = geolocation
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

    @staticmethod
    def real_time_save_log_in_db():
        filename_re = getattr(settings, 'LOGS_FILENAME_RE', None)
        format_re = getattr(settings, 'LOGS_FORMAT_RE', None)
        top_dir = getattr(settings, 'LOGS_TOP_DIR', None)
        parser = NginXAccessLogParser(filename_re, format_re, top_dir)

        def follow(f):
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue
                yield line

        def read_continuously():
            with open('/home/pawantu/some_file.log') as f:
                for line in follow(f):
                    data = parser.parse_string(line)
                    print(data)
                    print('-------------------------------------')

        t = threading.Thread(target=read_continuously)
        t.daemon = True
        t.start()
        return t
