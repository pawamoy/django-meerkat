# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import IPInfo, IPInfoCheck, RequestLog

admin.site.register(RequestLog)
admin.site.register(IPInfoCheck)
admin.site.register(IPInfo)
