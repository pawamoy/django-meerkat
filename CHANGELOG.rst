=========
Changelog
=========

0.2.1 (2017-05-11)
==================

- Remove reverse column from migration.

0.2.0 (2017-05-11)
==================

Implements logs models and functions:

- thread to read Nginx logs continuously,
- functions and classes to get IP information from ipinfo and ip-api,
- function to append previous logs in DB,
- better match log lines (improved parser regular expression).

Various additions and fixes:

- Add ISP, ASN and Proxy fields in ``IPInfo`` model.
- Add Highcharts as asset.
- Monkey patch progress bar for Django 1.8.
- Change ``geolocation`` names to ``ip_info``.
- Add ``django-app-settings`` requirement.
- Add verbose names.
- Improve geolocation.
- Register models in admin.
- Keep reference to thread reading logs in ``RequestLog`` attributes.
- Link sub-models in main-models module.
- Fix deprecated ``IPAddressField``.
- Add initial migration.
- Use Codacy instead of Codecov.
- Change license from MPL 2.0 to ISC (no 'same license' condition).
- Remove Python 3.3 support.

0.1.0 (2016-06-08)
==================

* Alpha release on PyPi.
