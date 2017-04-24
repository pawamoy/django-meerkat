# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import RequestLog, Geolocation, GeolocationCheck

admin.site.register(RequestLog)
admin.site.register(GeolocationCheck)
admin.site.register(Geolocation)
