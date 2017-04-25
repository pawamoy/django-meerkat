# -*- coding: utf-8 -*-

"""Geolocation utils."""

import requests

from ..exceptions import RateExceededError


def ip_info(ip):
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
                                    verify=False, timeout=1)
            if response.status_code == 429:
                raise RateExceededError
            return response.json()
        except (requests.ReadTimeout, requests.ConnectTimeout):
            pass


# FIXME: maybe not hit ipinfo but db instead
def ip_geoloc(ip, data=None):
    """
    Get IP geolocation.

    Args:
        ip (str): IP address to use if no data provided.
        data (dict): optional already obtained data.

    Returns:
        str: latitude and longitude, comma-separated.
    """
    if data is None:
        data = ip_info(ip)
    return data['loc']


def google_maps_geoloc_link(ip):
    """
    Get a link to google maps pointing on this IP's geolocation.

    Args:
        ip (str): IP address.

    Returns:
        str: a link to google maps pointing on this IP's geolocation.
    """
    loc = ip_geoloc(ip)
    lat, lon = loc.split(',')
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
    loc = ip_geoloc(ip)
    lat, lon = loc.split(',')
    return 'https://www.openstreetmap.org/search' \
           '?query=%s%%2C%s#map=7/%s/%s' % (lat, lon, lat, lon)
