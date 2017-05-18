# -*- coding: utf-8 -*-

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from ..utils.geolocation import google_maps_geoloc_link
from .models import IPInfo, IPInfoCheck, RequestLog


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

    date_hierarchy = 'datetime'

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
    date_hierarchy = 'date'


class CheckInline(admin.TabularInline):
    model = IPInfoCheck
    extra = 0
    fields = ('date', 'ip_address', 'ip_info')
    readonly_fields = fields

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class LogInline(admin.TabularInline):
    model = RequestLog
    extra = 0
    fields = ('datetime', 'request', 'status_code', 'user_agent', 'referrer')
    readonly_fields = fields

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class IPInfoAdmin(admin.ModelAdmin):
    inlines = [CheckInline, LogInline]

    list_display = (
        'ip_address', 'org', 'asn', 'isp', 'proxy', 'hostname', 'see_on_map',
        'continent', 'continent_code', 'country', 'country_code',
        'region', 'region_code',
        'city', 'city_code', 'latitude', 'longitude'
    )

    readonly_fields = ('see_on_map', )

    list_filter = ('proxy', 'continent', 'continent_code',
                   'country', 'country_code')

    fieldsets = (
        (None, {
            'fields': ('ip_address', 'org', 'asn', 'isp', 'proxy', 'hostname')
        }),
        (_('Geolocation'), {
            'fields': (
                'see_on_map', 'latitude', 'longitude',
                'continent', 'continent_code', 'country', 'country_code',
                'region', 'region_code', 'city', 'city_code'),
        }),
    )

    def see_on_map(self, obj):
        geo_url = google_maps_geoloc_link((obj.latitude, obj.longitude))
        return format_html('<a href="{}">{}</a>', geo_url, obj)
    see_on_map.short_description = _('See on map')


admin.site.register(RequestLog, RequestLogAdmin)
admin.site.register(IPInfoCheck, IPInfoCheckAdmin)
admin.site.register(IPInfo, IPInfoAdmin)
