# -*- coding: utf-8 -*-

import json

import requests


def ip_info(ip):
    # Geoloc updated up to once a week:
    # http://ipinfo.io/data#geolocation-data
    response = requests.get('http://ipinfo.io/%s' % ip)
    return json.loads(response.content)


def ip_geoloc(ip, data=None):
    if data is None:
        data = ip_info(ip)
    return data['loc']


def google_maps_geoloc_link(ip):
    loc = ip_geoloc(ip)
    lat, lon = loc.split(',')
    return 'https://www.google.com/maps/place/@%s,17z/' \
           'data=!3m1!4b1!4m5!3m4!1s0x0:0x0!8m2!3d%s!4d%s' % (loc, lat, lon)


def open_street_map_geoloc_link(ip):
    loc = ip_geoloc(ip)
    lat, lon = loc.split(',')
    return 'https://www.openstreetmap.org/search' \
           '?query=%s%%2C%s#map=7/%s/%s' % (lat, lon, lat, lon)
