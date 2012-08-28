#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'alberto'

class ObjectDoesNotExist(Exception):
    "The requested object does not exist"
    silent_variable_failure = True

class MultipleObjectsReturned(Exception):
    "The query returned multiple objects when only one was expected."
    pass

class FieldError(Exception):
    """Some kind of problem with a model field."""
    pass
