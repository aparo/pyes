# -*- coding: utf-8 -*-


from .utils import EqualityComparableUsingAttributeDictionary

__author__ = 'Alberto Paro'

__all__ = [
    'ESPendingDeprecationWarning',
    'ESDeprecationWarning',
    'NoServerAvailable',
    "QueryError",
    "NotFoundException",
    "AlreadyExistsException",
    "IndexAlreadyExistsException",
    "IndexMissingException",
    "SearchPhaseExecutionException",
    "InvalidIndexNameException",
    "InvalidSortOrder",
    "InvalidQuery",
    "InvalidParameterQuery",
    "InvalidParameter",
    "QueryParameterError",
    "ScriptFieldsError",
    "ReplicationShardOperationFailedException",
    "ClusterBlockException",
    "MapperParsingException",
    "ElasticSearchException",
    'ReduceSearchPhaseException',
    "VersionConflictEngineException",
    'DocumentAlreadyExistsEngineException',
    "DocumentAlreadyExistsException",
    "TypeMissingException",
    "BulkOperationException",
    "DocumentMissingException"
]

class ESPendingDeprecationWarning(PendingDeprecationWarning):
    pass


class ESDeprecationWarning(DeprecationWarning):
    pass


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


class ScriptFieldsError(Exception):
    pass


class InvalidParameter(Exception):
    pass


class InvalidSortOrder(Exception):
    pass


class ElasticSearchException(Exception):
    """Base class of exceptions raised as a result of parsing an error return
    from ElasticSearch.

    An exception of this class will be raised if no more specific subclass is
    appropriate.

    """

    def __init__(self, error, status=None, result=None, request=None):
        super(ElasticSearchException, self).__init__(error)
        self.status = status
        self.result = result
        self.request = request


class ElasticSearchIllegalArgumentException(ElasticSearchException):
    pass


class IndexMissingException(ElasticSearchException):
    pass


class NotFoundException(ElasticSearchException):
    pass


class AlreadyExistsException(ElasticSearchException):
    pass


class IndexAlreadyExistsException(AlreadyExistsException):
    pass


class InvalidIndexNameException(ElasticSearchException):
    pass


class SearchPhaseExecutionException(ElasticSearchException):
    pass


class ReplicationShardOperationFailedException(ElasticSearchException):
    pass


class ClusterBlockException(ElasticSearchException):
    pass


class MapperParsingException(ElasticSearchException):
    pass


class ReduceSearchPhaseException(ElasticSearchException):
    pass


class VersionConflictEngineException(ElasticSearchException):
    pass


class DocumentAlreadyExistsEngineException(ElasticSearchException):
    pass


class DocumentAlreadyExistsException(ElasticSearchException):
    pass


class TypeMissingException(ElasticSearchException):
    pass

class MappedFieldNotFoundException(ElasticSearchException):
    pass

class BulkOperationException(ElasticSearchException, EqualityComparableUsingAttributeDictionary):
    def __init__(self, errors, bulk_result):
        super(BulkOperationException, self).__init__(
            "At least one operation in the bulk request has failed: %s" % errors)
        self.errors = errors
        self.bulk_result = bulk_result

class DocumentMissingException(ElasticSearchException):
    pass
