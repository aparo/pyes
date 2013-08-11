# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging

logger = logging.getLogger(__name__)

VERSION = (0, 20, 1)

__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
__author__ = "Alberto Paro"
__contact__ = "alberto.paro@gmail.com"
__homepage__ = "http://github.com/aparo/pyes/"
__docformat__ = "restructuredtext"


def is_stable_release():
    if len(VERSION) > 3:
        return False
    return True


def version_with_meta():
    return "%s (%s)" % (__version__,
                        is_stable_release() and "stable" or "unstable")

from .es import ES, file_to_attachment
from .query import *
from .rivers import *
from .filters import *
#from highlight import HighLighter
from .utils import *

try:
    #useful for additional query extra features
    from .query_extra import *
except ImportError:
    pass
