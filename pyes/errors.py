#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['NoServerAvailable', "QueryError"]

class NoServerAvailable(Exception):
    pass

class QueryError(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)