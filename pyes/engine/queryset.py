#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'alberto'
# Delete rules
DO_NOTHING = 0
NULLIFY = 1
CASCADE = 2
DENY = 3


class DoesNotExist(Exception):
    pass


class MultipleObjectsReturned(Exception):
    pass


class InvalidQueryError(Exception):
    pass


class OperationError(Exception):
    pass

class QuerySet(object):
    pass

class QuerySetManager(object):
    pass

