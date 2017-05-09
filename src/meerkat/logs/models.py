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
import re
import sys

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from ..exceptions import RateExceededError
from ..utils.file import count_lines, follow
from ..utils.ip_info import ip_api_handler
from ..utils.thread import StoppableThread
from .parsers import get_nginx_parser

try:
    from django.core.serializers.base import ProgressBar
except ImportError:
    class ProgressBar(object):
        progress_width = 75

        def __init__(self, output, total_count):
            self.output = output
            self.total_count = total_count
            self.prev_done = 0

        def update(self, count):
            if not self.output:
                return
            perc = count * 100 // self.total_count
            done = perc * self.progress_width // 100
            if self.prev_done >= done:
                return
            self.prev_done = done
            cr = '' if self.total_count == 1 else '\r'
            self.output.write(cr + '[' + '.' * done + ' ' * (self.progress_width - done) + ']')  # noqa
            if done == self.progress_width:
                self.output.write('\n')
            self.output.flush()


# Define what information retrievable from the logs are pertinent
# so we can have universal log models (nginx, apache, uwsgi, ...).
# Remember our goal is security audit, not performance audit.


class IPInfo(models.Model):
    """A model to store IP address information."""

    # Even if we have a paid account on some ip info service,
    # an IP address had unique information at the time of the
    # request. Therefore, this information must be stored in the DB
    # if we want to compute statistical data about it. We cannot query
    # web-services each time we want to do this (data changed over time).
    latitude = models.CharField(
        verbose_name=_('Latitude'), max_length=255, blank=True)
    longitude = models.CharField(
        verbose_name=_('Longitude'), max_length=255, blank=True)
    hostname = models.CharField(
        verbose_name=_('Hostname'), max_length=255, blank=True)
    city = models.CharField(
        verbose_name=_('City'), max_length=255, blank=True)
    city_code = models.CharField(
        verbose_name=_('City code'), max_length=255, blank=True)
    region = models.CharField(
        verbose_name=_('Region'), max_length=255, blank=True)
    region_code = models.CharField(
        verbose_name=_('Region code'), max_length=255, blank=True)
    country = models.CharField(
        verbose_name=_('Country'), max_length=255, blank=True)
    country_code = models.CharField(
        verbose_name=_('Country code'), max_length=255, blank=True)
    continent = models.CharField(
        verbose_name=_('Continent'), max_length=255, blank=True)
    continent_code = models.CharField(
        verbose_name=_('Continent code'), max_length=255, blank=True)
    org = models.CharField(
        verbose_name=_('Organization'), max_length=255, blank=True)

    class Meta:
        """Meta class for Django."""

        unique_together = ('latitude', 'longitude', 'hostname',
                           'city', 'region', 'country', 'org')
        verbose_name = _('IP address information')
        verbose_name_plural = _('IP address information')

    def __str__(self):
        return '%s,%s' % (self.latitude, self.longitude)

    @staticmethod
    def get_or_create_from_ip(ip):
        """
        Get or create an entry using obtained information from an IP.

        Args:
            ip (str): IP address xxx.xxx.xxx.xxx.

        Returns:
            ip_info: an instance of IPInfo.
        """
        data = ip_api_handler.get(ip)
        if data and any(v for v in data.values()):
            return IPInfo.objects.get_or_create(**data)
        return None, False

    def ip_addresses(self):
        return list(IPInfoCheck.objects.filter(
            ip_info=self).values_list('ip_address', flat=True))


class IPInfoCheck(models.Model):
    """
    A model to keep track of the ip_info objects given IP address.

    IPInfo objects are generated from an IP address. They may already
    exist, so we don't want duplicates. This model attaches an IP to an
    ip_info object. It also adds the date of the check, because an IP will
    not always be related to the same ip_info, which changes over time.
    """

    ip_address = models.GenericIPAddressField(
        verbose_name=_('IP address'), unique=True)
    date = models.DateField(
        verbose_name=_('Date'), default=datetime.date.today)
    ip_info = models.ForeignKey(
        IPInfo, verbose_name=_('IPInfo'))

    class Meta:
        """Meta class for Django."""

        verbose_name = _('IPInfo check')
        verbose_name_plural = _('IPInfo checks')

    def __str__(self):
        return '%s %s %s' % (self.ip_address, self.date, self.ip_info)

    @staticmethod
    def check_ip(ip):
        ip_info, _ = IPInfo.get_or_create_from_ip(ip)
        if ip_info:
            IPInfoCheck.objects.create(ip_address=ip, ip_info=ip_info)
            return ip_info
        return None


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

        ip_info
    """

    VERBS = ['CONNECT', 'GET', 'HEAD', 'OPTIONS', 'POST',
             'PUT' 'TRACE', 'DELETE', 'PATCH']
    PROTOCOLS = ['HTTP/1.0', 'HTTP/1.1', 'HTTP/2.0', 'RTSP/1.0', 'SIP/2.0']

    REQUEST_REGEX = re.compile(
        r'(?P<verb>%s) (?P<url>[^\s]+?) (?P<protocol>%s)' % (
            '|'.join(VERBS), '|'.join(PROTOCOLS)))

    validate_url = URLValidator()

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
        verbose_name=_('Protocol'), max_length=30, blank=True)
    port = models.PositiveIntegerField(
        verbose_name=_('Port'), blank=True, null=True)
    file_type = models.CharField(
        verbose_name=_('File type'), max_length=30, blank=True)
    https = models.BooleanField(
        verbose_name=_('HTTPS'), default=False)
    bytes_sent = models.IntegerField(
        verbose_name=_('Bytes sent'), blank=True)
    request = models.TextField(
        verbose_name=_('Request'), blank=True)

    # Error logs
    error = models.BooleanField(
        verbose_name=_('Error'), default=False)
    level = models.CharField(
        verbose_name=_('Level'), max_length=255, blank=True)
    message = models.TextField(
        verbose_name=_('Message'), blank=True)

    # IPInfo
    ip_info = models.ForeignKey(IPInfo, verbose_name=_('IP Info'), null=True)

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

    class ParseToDBThread(StoppableThread):
        def __init__(self, parser, *args, **kwargs):
            super(RequestLog.ParseToDBThread, self).__init__(*args, **kwargs)
            self.parser = parser

        def run(self):
            file_name = self.parser.matching_files()[0]
            seek_end = True
            while True:
                for line in follow(file_name, seek_end, 1, self.stopped):
                    try:
                        data = self.parser.parse_string(line)
                    except AttributeError:
                        # TODO: log the line
                        print('Error while parsing log line: %s' % line)
                        continue
                    log_object = self.parser.data_to_log(data)
                    log_object.update_ip_info(save=True)
                    if self.stopped():
                        break
                if self.stopped():
                    break
                seek_end = False

    def __str__(self):
        return str(self.datetime)

    def update_ip_info(self, since_days=10, save=False, force=False):
        """
        Update the IP info.

        Args:
            since_days (int): if checked less than this number of days ago,
                don't check again (default to 10 days).
            save (bool): whether to save anyway or not.
            force (bool): whether to update ip_info to last checked one.

        Returns:
            bool: check was run. IPInfo might not have been updated.
        """
        # If ip already checked
        try:
            last_check = IPInfoCheck.objects.get(
                ip_address=self.client_ip_address)

            # If checked less than since_days ago, don't check again
            since_last = datetime.date.today() - last_check.date
            if since_last <= datetime.timedelta(days=since_days):
                if not self.ip_info or (
                        self.ip_info != last_check.ip_info and force):
                    self.ip_info = last_check.ip_info
                    self.save()
                    return True
                elif save:
                    self.save()
                return False

            # Get or create ip_info object
            ip_info, created = IPInfo.get_or_create_from_ip(
                self.client_ip_address)

            # Update check time
            last_check.date = datetime.date.today()
            last_check.save()

            # Maybe data changed
            if created:
                last_check.ip_info = ip_info
                self.ip_info = ip_info
                self.save()
                return True
            elif save:
                self.save()

            return False

        except IPInfoCheck.DoesNotExist:
            # Else if ip never checked, check it and set ip_info
            self.ip_info = IPInfoCheck.check_ip(self.client_ip_address)
            self.save()

            return True

    def update_request(self,
                       force_verb=False,
                       force_protocol=False,
                       force_url=False,
                       strict_url=False):
        modified = False

        try:
            data = re.match(self.REQUEST_REGEX, self.request).groupdict()
        except AttributeError:
            return

        if not self.verb or (force_verb and self.verb != data['verb']):
            self.verb = data['verb']
            modified = True

        if not self.url or (force_url and self.url != data['url']):
            if strict_url:
                try:  # FIXME: url can begin with or without /
                    self.validate_url('http://localhost%s' % data['url'])
                    self.url = data['url']
                    modified = True
                except ValidationError:
                    pass
            else:
                self.url = data['url']
                modified = True

        if not self.protocol or (force_protocol and
                                 self.protocol != data['protocol']):
            self.protocol = data['protocol']
            modified = True

        if modified:
            self.save()

    @staticmethod
    def update_requests(batch_size=512, strict_url=True, progress=True):
        not_treated = RequestLog.objects.filter(verb='', url='', protocol='')
        not_treated_count = not_treated.count()

        # perf improvement: avoid QuerySet.__getitem__ when doing qs[i]
        # FIXME: though we may need to buffer because the queryset can be huge
        not_treated = list(not_treated)

        progress_bar = ProgressBar(sys.stdout if progress else None, not_treated_count)  # noqa
        print('Updating request logs verb, url and protocol (%s)' % not_treated_count)  # noqa
        count = 0
        start = datetime.datetime.now()
        while count < not_treated_count:
            with transaction.atomic():  # is this a real improvement?
                for _ in range(batch_size):
                    not_treated[count].update_request(strict_url=strict_url)
                    count += 1
                    progress_bar.update(count)
                    if count >= not_treated_count:
                        break
            # end transaction
        end = datetime.datetime.now()
        print('Elapsed time: %s' % (end - start))

    @staticmethod
    def parse_all(buffer_size=512, progress=True):
        parser = get_nginx_parser()
        buffer = []
        start = datetime.datetime.now()
        for log_file in parser.matching_files():
            n_lines = count_lines(log_file)
            progress_bar = ProgressBar(sys.stdout if progress else None, n_lines)  # noqa
            print('Reading log file %s: %s lines' % (log_file, n_lines))
            with open(log_file) as f:
                for count, line in enumerate(f, 1):
                    try:
                        data = parser.parse_string(line)
                    except AttributeError:
                        # TODO: log the line
                        print('Error while parsing log line: %s' % line)
                        continue
                    buffer.append(RequestLog(**parser.format_data(data)))
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
    def get_ip_info():
        param = 'client_ip_address'
        unique_ips = set(RequestLog.objects.distinct(param).values_list(param, flat=True))  # noqa
        checked_ips = set(IPInfoCheck.objects.values_list('ip_address', flat=True))  # noqa
        not_checked_ips = unique_ips - checked_ips
        print('Checking IP addresses information (%s)' % len(not_checked_ips))
        check_progress_bar = ProgressBar(sys.stdout, len(not_checked_ips))
        for count, ip in enumerate(not_checked_ips, 1):
            try:
                IPInfoCheck.check_ip(ip)
            except RateExceededError:
                print(' Rate exceeded')
                break
            check_progress_bar.update(count)
        no_ip_info = RequestLog.objects.filter(ip_info=None)
        no_ip_info_ip = set(no_ip_info.distinct(param).values_list(param, flat=True))  # noqa
        checks = IPInfoCheck.objects.filter(ip_address__in=no_ip_info_ip)
        print('Updating request logs\' IP info (%s)' % no_ip_info.count())
        print('%s related checks' % checks.count())
        logs_progress_bar = ProgressBar(sys.stdout, checks.count())
        for count, check in enumerate(checks, 1):
            no_ip_info.filter(
                client_ip_address=check.ip_address
            ).update(ip_info=check.ip_info)
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
        if not hasattr(RequestLog, 'daemon'):
            parser = get_nginx_parser()
            RequestLog.daemon = RequestLog.ParseToDBThread(parser, daemon=True)
        RequestLog.daemon.start()
        return RequestLog.daemon

    @staticmethod
    def stop_daemon():
        if hasattr(RequestLog, 'daemon'):
            RequestLog.daemon.stop()
            RequestLog.daemon.join()
