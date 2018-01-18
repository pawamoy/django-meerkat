=========
Changelog
=========

0.2.6 (2018-01-18)
==================

- Update pinned requirements.

0.2.5 (2017-12-18)
==================

- Update to work with ``django-app-settings`` 0.3.0.

0.2.4 (2017-10-04)
==================

- Add ``archan`` submodule.
- Add Science/Reseach classifier.
- Allow failure for style and spell on travis.
- Drop support for Python 2.7 and PyPy (``dependenpy`` v3).
- Fix boolean setting in apps.
- Setup travis stages, rename tox env names.
- Update for ``dependenpy`` 3.1.0.
- Update for ``django-app-settings`` 0.2.5.
- Update for ``django-suit-dashboard`` 2.0.5.

0.2.3 (2017-05-18)
==================

- Remove use of ``DJANGO_SHELL`` environment variable (to be done by user).
- Implement auto-complete functions in ``RequestLog`` to populate some values.
- Improve admin displays.
- Fix most visited pages box (+ huge performance improvement).
- Move geolocation functions into ``utils.geolocation``.

0.2.2 (2017-05-11)
==================

- Block thread being started if ``DJANGO_SHELL`` environment variable is set.
- Fix log parser code.

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
