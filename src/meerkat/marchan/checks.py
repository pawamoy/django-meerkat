# -*- coding: utf-8 -*-

from django.core.checks import Tags, Warning, register

from archan.checker import Archan
from archan.criterion import Criterion

from ..apps import AppSettings


@register(Tags.security, deploy=True)
def check_dsm(app_configs, **kwargs):
    errors = []
    dsm = AppSettings.archan_dsm.get_dsm()
    ar = Archan()
    results = ar.check(dsm)
    for criterion in ar.criteria:
        r, msg = results[criterion.codename]
        if r == Criterion.FAILED:
            errors.append(
                Warning(
                    '%s check has failed.\n%s' % (criterion.title, msg),
                    hint=criterion.hint,
                    obj=None,
                    id='security.%s' % criterion.codename))
    return errors
