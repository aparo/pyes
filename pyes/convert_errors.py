# -*- coding: utf-8 -*-


"""
Routines for converting error responses to appropriate exceptions.
"""
from . import exceptions

__all__ = ['raise_if_error']

# Patterns used to map exception strings to classes.

# First, exceptions for which the messages start with the error name,
# and then contain the error description wrapped in [].
exceptions_by_name = dict((name, getattr(exceptions, name))
for name in (
    "DocumentAlreadyExistsEngineException",
    "DocumentAlreadyExistsException",
    "TypeMissingException",
    "VersionConflictEngineException",
    'ClusterBlockException',
    'ElasticSearchIllegalArgumentException',
    'IndexAlreadyExistsException',
    'IndexMissingException',
    'InvalidIndexNameException',
    'MapperParsingException',
    'ReduceSearchPhaseException',
    'ReplicationShardOperationFailedException',
    'SearchPhaseExecutionException',
    'DocumentMissingException',
    )
)

# Second, patterns for exceptions where the message is just the error
# description, and doesn't contain an error name.  These patterns are matched
# at the end of the exception.
exception_patterns_trailing = {
    '] missing': exceptions.NotFoundException,
    '] Already exists': exceptions.AlreadyExistsException,
    }

def raise_if_error(status, result, request=None):
    """Raise an appropriate exception if the result is an error.

    Any result with a status code of 400 or higher is considered an error.

    The exception raised will either be an ElasticSearchException, or a more
    specific subclass of ElasticSearchException if the type is recognised.

    The status code and result can be retrieved from the exception by accessing its
    status and result properties.

    Optionally, this can take the original RestRequest instance which generated
    this error, which will then get included in the exception.

    """
    assert isinstance(status, int)

    if status < 400:
        return

    if status == 404 and isinstance(result, dict) and 'error' not in result:
        raise exceptions.NotFoundException("Item not found", status, result, request)

    if not isinstance(result, dict) or 'error' not in result:
        raise exceptions.ElasticSearchException("Unknown exception type: %d, %s" % (status, result), status,
            result, request)

    error = result['error']
    if '; nested: ' in error:
        error_list = error.split('; nested: ')
        error = error_list[len(error_list) - 1]

    bits = error.split('[', 1)
    if len(bits) == 2:
        excClass = exceptions_by_name.get(bits[0], None)
        if excClass is not None:
            msg = bits[1]
            if msg.endswith(']'):
                msg = msg[:-1]
            '''
            if request:
                msg += ' (' + str(request) + ')'
            '''
            raise excClass(msg, status, result, request)

    for pattern, excClass in list(exception_patterns_trailing.items()):
        if not error.endswith(pattern):
            continue
            # For these exceptions, the returned value is the whole descriptive
        # message.
        raise excClass(error, status, result, request)

    raise exceptions.ElasticSearchException(error, status, result, request)
