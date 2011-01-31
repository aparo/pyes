#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'

__all__ = ['NoServerAvailable',
           "QueryError",
           "NotFoundException", 
           "AlreadyExistsException", 
           "IndexMissingException",
           "SearchPhaseExecutionException",
           "InvalidQuery",
           "InvalidParameterQuery",
           "QueryParameterError",
           "ReplicationShardOperationFailedException",
           "ClusterBlockException"]

class NoServerAvailable(Exception):
    pass

class InvalidQuery(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)

class InvalidParameterQuery(InvalidQuery):
    pass

class QueryError(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)
    
class IndexMissingException(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)

class QueryParameterError(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message

    message = property(_get_message, _set_message)

class NotFoundException(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)

class AlreadyExistsException(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)
    
class SearchPhaseExecutionException(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)

class ReplicationShardOperationFailedException(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)

class ClusterBlockException(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)
