# -*- coding: utf-8 -*-

"""Geolocation utils."""

import time
from datetime import datetime, timedelta

import requests

from ..exceptions import RateExceededError


class BaseRequestRateHandler(object):
    rate = 0
    per = 0

    def __init__(self, rate=None, per=None):
        self.timedelta_type = type(timedelta())
        if rate is not None:
            self.rate = rate
        if per is not None:
            self.per = per
        if isinstance(self.per, (int, float)):
            self.per = timedelta(seconds=self.per)
        self.allowance = self.rate
        self.interval_first_hit = None

    def hit(self, number=1):
        now = datetime.now()
        if self.interval_first_hit is None:
            self.interval_first_hit = now
            self.allowance -= number
        elif now - self.interval_first_hit > self.per:
            self.interval_first_hit = now
            self.allowance = self.rate
        else:
            self.allowance -= number

    def can_hit(self, number=0):
        return self.allowance > number

    def format(self, data):
        return data

    def format_batch(self, data):
        return data

    def _get(self, ip):
        raise NotImplementedError

    def get(self, ip, wait=True):
        if self.can_hit():
            response = self._get(ip)
            self.hit()
            return self.format(response)
        elif wait:
            time.sleep(self.time_to_wait())
            return self.get(ip, wait)
        return None

    def _batch(self, ips):
        raise NotImplementedError

    def batch(self, ips, wait=True):
        if self.can_hit(len(ips)):
            response = self._batch(ips)
            self.hit(len(ips))
            return self.format_batch(response)
        elif wait:
            time.sleep(self.time_to_wait())
            return self.batch(ips, wait)
        return None

    def time_to_wait(self):
        if self.rate == 0 or self.per == timedelta(seconds=0):
            return 0
        return (self.per - (datetime.now() - self.interval_first_hit)).seconds


class IpInfoHandler(BaseRequestRateHandler):
    rate = 1000
    per = 3600 * 24

    def format(self, data):
        loc = data.get('loc', None)
        lat = lon = ''
        if loc and ',' in loc:
            lat, lon = loc.split(',')

        return dict(
            latitude=lat,
            longitude=lon,
            hostname=data.get('hostname', ''),
            city=data.get('city', ''),
            region=data.get('region', ''),
            country=data.get('country', ''),
            org=data.get('org', ''))

    def _get(self, ip):
        """
        Get information about an IP.
    
        Args:
            ip (str): an IP (xxx.xxx.xxx.xxx).
    
        Returns:
            dict: see http://ipinfo.io/developers/getting-started
        """
        # Geoloc updated up to once a week:
        # http://ipinfo.io/developers/data#geolocation-data
        retries = 10
        for retry in range(retries):
            try:
                response = requests.get('http://ipinfo.io/%s/json' % ip,
                                        verify=False, timeout=1)  # nosec
                if response.status_code == 429:
                    raise RateExceededError
                return response.json()
            except (requests.ReadTimeout, requests.ConnectTimeout):
                pass
        return {}


class IpAPIHandler(BaseRequestRateHandler):
    rate = 150
    per = 60

    def format(self, data):
        return dict(
            # reverse=data.get('reverse'),
            # asn=data.get('as'),
            # isp=data.get('isp'),
            # proxy=data.get('proxy'),
            latitude=data.get('lat'),
            longitude=data.get('lon'),
            city=data.get('city', ''),
            region=data.get('regionName', ''),
            region_code=data.get('region', ''),
            country=data.get('country', ''),
            country_code=data.get('countryCode', ''),
            org=data.get('org', ''))

    def format_batch(self, data):
        return {d['query']: self.format(d) for d in data}

    def _get(self, ip):
        retries = 10
        for retry in range(retries):
            try:
                response = requests.get(
                    'http://ip-api.com/json/%s?fields=138975' % ip,
                    verify=False, timeout=1)  # nosec
                return response.json()
            except (requests.ReadTimeout, requests.ConnectTimeout):
                pass
        return {}

    def _batch(self, ips):
        response = requests.post(
            'http://ip-api.com/batch?fields=147167',
            json=[{'query': ip} for ip in ips])
        return response.json()


ip_api_handler = IpAPIHandler()
ip_info_handler = IpInfoHandler()


def ip_geoloc(ip, hit_api=True):
    """
    Get IP geolocation.

    Args:
        ip (str): IP address to use if no data provided.
        hit_api (bool): whether to hit api if info not found.

    Returns:
        str: latitude and longitude, comma-separated.
    """
    from ..logs.models import IPInfoCheck
    try:
        obj = IPInfoCheck.objects.get(ip_address=ip).geolocation
    except IPInfoCheck.DoesNotExist:
        if hit_api:
            obj = IPInfoCheck.check_ip(ip)
        else:
            return None
    return obj.latitude, obj.longitude


def google_maps_geoloc_link(ip):
    """
    Get a link to google maps pointing on this IP's geolocation.

    Args:
        ip (str): IP address.

    Returns:
        str: a link to google maps pointing on this IP's geolocation.
    """
    lat, lon = ip_geoloc(ip)
    loc = '%s,%s' % (lat, lon)
    return 'https://www.google.com/maps/place/@%s,17z/' \
           'data=!3m1!4b1!4m5!3m4!1s0x0:0x0!8m2!3d%s!4d%s' % (loc, lat, lon)


def open_street_map_geoloc_link(ip):
    """
    Get a link to open street map pointing on this IP's geolocation.

    Args:
        ip (str): IP address.

    Returns:
        str: a link to open street map pointing on this IP's geolocation.
    """
    lat, lon = ip_geoloc(ip)
    return 'https://www.openstreetmap.org/search' \
           '?query=%s%%2C%s#map=7/%s/%s' % (lat, lon, lat, lon)
