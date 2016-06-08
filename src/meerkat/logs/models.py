# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models


# TODO: define what information retrievable from the logs are pertinent
# so we can have universal log models (nginx, apache, uwsgi, ...)
# Remember our goal is security audit, not performance audit

class RequestLog(models.Model):

    client_ip_address = models.IPAddressField()

    datetime = models.DateTimeField()
    timezone = models.CharField(max_length=10)

    url = models.URLField()
    status_code = models.SmallIntegerField()
    user_agent = models.TextField()
    referrer = models.TextField()
    upstream = models.TextField()
    host = models.TextField()
    server = models.TextField()
    verb = models.CharField(max_length=10)
    protocol = models.CharField(max_length=10)

    file_type = models.CharField(max_length=20)

    response_time = models.IntegerField()

    # proxy, https, ssl, upstreams, compression, response contents/sizes...

    # Even if we have a paid account on some geolocation service,
    # an IP address had one and only one geolocation at the time of the
    # request. Therefore, these geolocations must be stored in the DB
    # if we want to compute statistical data about it. We cannot query
    # web-services each time we want to do this (data changed over time).
    geoloc_latitude = models.CharField(max_length=255)
    geoloc_longitude = models.CharField(max_length=255)
    geoloc_hostname = models.CharField(max_length=255)
    geoloc_city = models.CharField(max_length=255)
    geoloc_region = models.CharField(max_length=255)
    geoloc_country = models.CharField(max_length=255)
    geoloc_org = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def is_access_log(self):
        return True

    def is_error_log(self):
        return False


class RequestAccessLog(RequestLog):
    bytes_sent = models.IntegerField()


class RequestErrorLog(RequestLog):
    level = models.CharField(max_length=255)
    message = models.TextField()

    pid = models.IntegerField()
    tid = models.IntegerField()
    cid = models.IntegerField()

    def is_access_log(self):
        return False

    def is_error_log(self):
        return True
