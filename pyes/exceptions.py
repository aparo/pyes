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
           "ClusterBlockException",
           "ElasticSearchException",
          ]

class NoServerAvailable(Exception):
    pass


class InvalidQuery(Exception):
    pass

class InvalidParameterQuery(InvalidQuery):
    pass

class QueryError(Exception):
    pass

class QueryParameterError(Exception):
    pass


class ElasticSearchException(Exception):
    """Base class of exceptions raised as a result of parsing an error return
    from ElasticSearch.

    An exception of this class will be raised if no more specific subclass is
    appropriate.

    """
    def __init__(self, error, status=None, result=None):
        super(ElasticSearchException, self).__init__(error)
        self.status = status
        self.result = result

class IndexMissingException(ElasticSearchException):
    pass

class NotFoundException(ElasticSearchException):
    pass

class AlreadyExistsException(ElasticSearchException):
    pass

class SearchPhaseExecutionException(ElasticSearchException):
    pass

class ReplicationShardOperationFailedException(ElasticSearchException):
    pass

class ClusterBlockException(ElasticSearchException):
    pass
