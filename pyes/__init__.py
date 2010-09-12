#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

VERSION = (0, 10, 0)

__version__ = ".".join(map(str, VERSION[0:3])) + "".join(VERSION[3:])
__author__ = "Alberto Paro"
__contact__ = "alberto.paro@gmail.com"
__homepage__ = "http://github.com/aparo/pyes/"
__docformat__ = "restructuredtext"


def is_stable_release():
    if len(VERSION) > 3 and isinstance(VERSION[3], basestring):
        return False
    return not VERSION[1] % 2


def version_with_meta():
    return "%s (%s)" % (__version__,
                        is_stable_release() and "stable" or "unstable")

from pyes.connection import *
from elasticsearch import ElasticSearch
from query import *
from objectid import ObjectId

try:
    #useful for additional query extra features
    from query_extra import *
except ImportError:
    pass