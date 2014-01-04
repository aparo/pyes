#!/usr/bin/env python
# -*- coding: utf-8 -*-


import warnings

from functools import wraps

from .exceptions import ESPendingDeprecationWarning, ESDeprecationWarning

PENDING_DEPRECATION_FMT = """
    %(description)s is scheduled for deprecation in \
    version %(deprecation)s and removal in version v%(removal)s. \
    %(alternative)s
"""

DEPRECATION_FMT = """
    %(description)s is deprecated and scheduled for removal in
    version %(removal)s. %(alternative)s
"""

def warn_deprecated(description=None, deprecation=None, removal=None,
        alternative=None):
    ctx = {"description": description,
           "deprecation": deprecation, "removal": removal,
           "alternative": alternative}
    if deprecation is not None:
        w = ESPendingDeprecationWarning(PENDING_DEPRECATION_FMT % ctx)
    else:
        w = ESDeprecationWarning(DEPRECATION_FMT % ctx)
    warnings.warn(w)


def deprecated(description=None, deprecation=None, removal=None,
        alternative=None):

    def _inner(fun):

        @wraps(fun)
        def __inner(*args, **kwargs):
            from .utils.imports import qualname
            warn_deprecated(description=description or qualname(fun),
                            deprecation=deprecation,
                            removal=removal,
                            alternative=alternative)
            return fun(*args, **kwargs)
        return __inner
    return _inner
