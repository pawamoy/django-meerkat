# -*- coding: utf-8 -*-

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from .models import IPInfo, IPInfoCheck, RequestLog
from ..utils.ip_info import google_maps_geoloc_link


class RequestLogAdmin(admin.ModelAdmin):
    list_display = (
        'datetime', 'timezone', 'client_ip_address', 'ip_info_link',
        'request', 'verb', 'url', 'protocol', 'suspicious',
        'status_code', 'bytes_sent', 'file_type', 'port', 'https',
        'user_agent', 'referrer', 'upstream', 'host', 'server',
        'error', 'level', 'message',
    )

    list_filter = (
        'status_code', 'verb', 'protocol', 'file_type', 'https', 'error',
        'level', 'suspicious')

    def ip_info_link(self, obj):
        instance = obj.ip_info
        if instance is None:
            return ''
        info = (instance._meta.app_label, instance._meta.model_name)
        admin_url = reverse('admin:%s_%s_change' % info,
                            args=(instance.pk,))
        return format_html('<a href="{}">{}</a>', admin_url, instance)
    ip_info_link.short_description = 'IP information'


class IPInfoCheckAdmin(admin.ModelAdmin):
    list_display = ('date', 'ip_address', 'ip_info')


class IPInfoAdmin(admin.ModelAdmin):
    list_display = (
        'org', 'asn', 'isp', 'proxy', 'hostname', 'see_on_map', 'continent',
        'continent_code', 'country', 'country_code', 'region', 'region_code',
        'city', 'city_code', 'latitude', 'longitude'
    )

    fieldsets = (
        (None, {
            'fields': ('org', 'asn', 'isp', 'proxy', 'hostname')
        }),
        (_('Geolocation'), {
            'fields': (
                'continent', 'continent_code', 'country', 'country_code',
                'region', 'region_code', 'city', 'city_code',
                'latitude', 'longitude', 'see_on_map'),
        }),
    )

    def see_on_map(self, obj):
        ip_address = obj.ip_check.all()[0].ip_address
        geolocation_url = google_maps_geoloc_link(ip_address)
        return format_html('<a href="{}">{}</a>', geolocation_url, obj)
    see_on_map.short_description = _('See on map')


admin.site.register(RequestLog, RequestLogAdmin)
admin.site.register(IPInfoCheck, IPInfoCheckAdmin)
admin.site.register(IPInfo, IPInfoAdmin)
