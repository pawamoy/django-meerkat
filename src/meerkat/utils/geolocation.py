# -*- coding: utf-8 -*-

"""Geolocation utils."""

from ..exceptions import RateExceededError


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
        obj = IPInfoCheck.objects.get(ip_address=ip).ip_info
    except IPInfoCheck.DoesNotExist:
        if hit_api:
            try:
                obj = IPInfoCheck.check_ip(ip)
            except RateExceededError:
                return None
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
    lat_lon = ip_geoloc(ip)
    if lat_lon is not None:
        lat, lon = lat_lon
        loc = '%s,%s' % (lat, lon)
        return 'https://www.google.com/maps/place/@%s,17z/' \
               'data=!3m1!4b1!4m5!3m4!1s0x0:0x0!8m2!3d%s!4d%s' % (
                loc, lat, lon)
    return ''


def open_street_map_geoloc_link(ip):
    """
    Get a link to open street map pointing on this IP's geolocation.

    Args:
        ip (str): IP address.

    Returns:
        str: a link to open street map pointing on this IP's geolocation.
    """
    lat_lon = ip_geoloc(ip)
    if lat_lon is not None:
        lat, lon = lat_lon
        return 'https://www.openstreetmap.org/search' \
               '?query=%s%%2C%s#map=7/%s/%s' % (lat, lon, lat, lon)
    return ''
