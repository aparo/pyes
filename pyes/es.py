#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import with_statement
import urllib
from .helpers import SettingsBuilder
from .models import ElasticSearchModel, DotDict, ListBulker

try:
    # For Python < 2.6 or people using a newer version of simplejson
    import simplejson as json
    from simplejson import JSONDecoder, JSONEncoder
except ImportError:
    # For Python >= 2.6
    import json
    from json import JSONDecoder, JSONEncoder

import random
from datetime import date, datetime
from urllib import urlencode
from urlparse import urlunsplit, urlparse
import base64
import time
import weakref
from decimal import Decimal
from .managers import Indices, Cluster
try:
    from .connection import connect as thrift_connect
    from .pyesthrift.ttypes import Method, RestRequest

except ImportError:
    from .fakettypes import Method, RestRequest

    thrift_connect = None

from .connection_http import connect as http_connect
from . import logger
from .mappings import Mapper

from .convert_errors import raise_if_error
from .exceptions import (ElasticSearchException, InvalidQuery,
                         ReduceSearchPhaseException, VersionConflictEngineException)
from .decorators import deprecated
from .utils import make_path

__all__ = ['ES', 'file_to_attachment', 'decode_json']

#
# models
#


def file_to_attachment(filename, filehandler=None):
    """
    Convert a file to attachment
    """
    if filehandler:
        return {'_name': filename,
                'content': base64.b64encode(filehandler.read())
        }
    with open(filename, 'rb') as _file:
        return {'_name': filename,
                'content': base64.b64encode(_file.read())
        }


class ESJsonEncoder(JSONEncoder):
    def default(self, value):
        """Convert rogue and mysterious data types.
        Conversion notes:

        - ``datetime.date`` and ``datetime.datetime`` objects are
        converted into datetime strings.
        """

        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, date):
            dt = datetime(value.year, value.month, value.day, 0, 0, 0)
            return dt.isoformat()
        elif isinstance(value, Decimal):
            return float(str(value))
        elif isinstance(value, set):
            return list(value)
        # raise TypeError
        return super(ESJsonEncoder, self).default(value)


class ESJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        kwargs['object_hook'] = self.dict_to_object
        json.JSONDecoder.__init__(self, *args, **kwargs)

    def string_to_datetime(self, obj):
        """
        Decode a datetime string to a datetime object
        """
        if isinstance(obj, basestring) and len(obj) == 19:
            try:
                return datetime(*time.strptime(obj, "%Y-%m-%dT%H:%M:%S")[:6])
            except ValueError:
                pass
        return obj


    def dict_to_object(self, d):
        """
        Decode datetime value from string to datetime
        """
        for k, v in d.items():
            if isinstance(v, basestring) and len(v) == 19:
                # Decode a datetime string to a datetime object
                try:
                    d[k] = datetime(*time.strptime(v, "%Y-%m-%dT%H:%M:%S")[:6])
                except ValueError:
                    pass
            elif isinstance(v, list):
                d[k] = [self.string_to_datetime(elem) for elem in v]
        return DotDict(d)


class ES(object):
    """
    ES connection object.
    """
    #static to easy overwrite
    encoder = ESJsonEncoder
    decoder = ESJsonDecoder

    def __init__(self, server="localhost:9200", timeout=30.0, bulk_size=400,
                 encoder=None, decoder=None,
                 max_retries=3,
                 default_indices=None,
                 default_types=None,
                 dump_curl=False,
                 model=ElasticSearchModel,
                 basic_auth=None,
                 raise_on_bulk_item_failure=False,
                 document_object_field=None,
                 bulker_class=ListBulker):
        """
        Init a es object.
        Servers can be defined in different forms:

        - host:port with protocol guess (i.e. 127.0.0.1:9200 protocol -> http
                                            127.0.0.1:9500  protocol -> thrift )
        - type://host:port (i.e. http://127.0.0.1:9200  https://127.0.0.1:9200 thrift://127.0.0.1:9500)

        - (type, host, port) (i.e. tuple ("http", "127.0.0.1", "9200") ("https", "127.0.0.1", "9200")
                                         ("thrift", "127.0.0.1", "9500")). This is the prefered form.

        :param server: the server name, it can be a list of servers.
        :param timeout: timeout for a call
        :param bulk_size: size of bulk operation
        :param encoder: tojson encoder
        :param max_retries: number of max retries for server if a server is down
        :param basic_auth: Dictionary with 'username' and 'password' keys for HTTP Basic Auth.
        :param model: used to objectify the dictinary. If None, the raw dict is returned.


        :param dump_curl: If truthy, this will dump every query to a curl file.  If
        this is set to a string value, it names the file that output is sent
        to.  Otherwise, it should be set to an object with a write() method,
        which output will be written to.

        :param raise_on_bulk_item_failure: raises an exception if an item in a
        bulk operation fails

        :param document_object_field: a class to use as base document field in mapper
        """
        if default_indices is None:
            default_indices = ["_all"]
        self.timeout = timeout
        self.default_indices = default_indices
        self.max_retries = max_retries
        self.cluster = None
        self.debug_dump = False
        self.cluster_name = "undefined"
        self.basic_auth = basic_auth
        self.connection = None
        self._mappings = None
        self.document_object_field = document_object_field

        if model is None:
            model = lambda connection, model: model
        self.model = model
        if dump_curl:
            if isinstance(dump_curl, basestring):
                self.dump_curl = open(dump_curl, "wb")
            elif hasattr(dump_curl, 'write'):
                self.dump_curl = dump_curl
            else:
                raise TypeError("dump_curl parameter must be supplied with a "
                                "string or an object with a write() method")
        else:
            self.dump_curl = None

        #used in bulk
        self._bulk_size = bulk_size #size of the bulk
        self.bulker = bulker_class(weakref.proxy(self), bulk_size=bulk_size,
                                   raise_on_bulk_item_failure=raise_on_bulk_item_failure)
        self.bulker_class = bulker_class
        self._raise_on_bulk_item_failure = raise_on_bulk_item_failure

        self.info = {} #info about the current server
        if encoder:
            self.encoder = encoder
        if decoder:
            self.decoder = decoder
        if isinstance(server, (str, unicode)):
            self.servers = [server]
        elif isinstance(server, tuple):
            self.servers = [server]
        else:
            self.servers = server

        #init managers
        self.indices = Indices(weakref.proxy(self))
        self.cluster = Cluster(weakref.proxy(self))

        self.default_types = default_types or []
        #check the servers variable
        self._check_servers()
        #init connections
        self._init_connection()


    def __del__(self):
        """
        Destructor
        """
        # Don't bother getting the lock
        if self.bulker:
            # It's not safe to rely on the destructor to flush the queue:
            # the Python documentation explicitly states "It is not guaranteed
            # that __del__() methods are called for objects that still exist "
            # when the interpreter exits."
            logger.error("pyes object %s is being destroyed, but bulk "
                         "operations have not been flushed. Call force_bulk()!",
                         self)
            # Do our best to save the client anyway...
            self.bulker.flush_bulk(True)

    def _check_servers(self):
        """Check the servers variable and convert in a valid tuple form"""
        new_servers = []

        def check_format(server):
            if server.scheme not in ["thrift", "http", "https"]:
                raise RuntimeError("Unable to recognize protocol: \"%s\"" % _type)

            if server.scheme == "thrift":
                if not thrift_connect:
                    raise RuntimeError("If you want to use thrift, please install thrift. \"pip install thrift\"")
                if server.port is None:
                    raise RuntimeError("If you want to use thrift, please provide a port number")

            new_servers.append(server)

        for server in self.servers:
            if isinstance(server, (tuple, list)):
                if len(list(server)) != 3:
                    raise RuntimeError("Invalid server definition: \"%s\"" % repr(server))
                _type, host, port = server
                server = urlparse('%s://%s:%s' % (_type, host, port))
                check_format(server)
            elif isinstance(server, basestring):
                if server.startswith(("thrift:", "http:", "https:")):
                    server = urlparse(server)
                    check_format(server)
                    continue
                else:
                    tokens = [t for t in server.split(":") if t.strip()]
                    if len(tokens) == 2:
                        host = tokens[0]
                        try:
                            port = int(tokens[1])
                        except ValueError:
                            raise RuntimeError("Invalid port: \"%s\"" % port)

                        if 9200 <= port <= 9299:
                            _type = "http"
                        elif 9500 <= port <= 9599:
                            _type = "thrift"
                        else:
                            raise RuntimeError("Unable to recognize port-type: \"%s\"" % port)

                        server = urlparse('%s://%s:%s' % (_type, host, port))
                        check_format(server)

        self.servers = new_servers

    def _init_connection(self):
        """
        Create initial connection pool
        """
        #detect connectiontype
        if not self.servers:
            raise RuntimeError("No server defined")

        server = random.choice(self.servers)
        if server.scheme in ["http", "https"]:
            self.connection = http_connect(
                filter(lambda server: server.scheme in ["http", "https"], self.servers),
                timeout=self.timeout, basic_auth=self.basic_auth, max_retries=self.max_retries)
            return
        elif server.scheme == "thrift":
            self.connection = thrift_connect(
                filter(lambda server: server.scheme == "thrift", self.servers),
                timeout=self.timeout, max_retries=self.max_retries)

    def _discovery(self):
        """
        Find other servers asking nodes to given server
        """
        data = self.cluster_nodes()
        self.cluster_name = data["cluster_name"]
        for _, nodedata in data["nodes"].items():
            server = nodedata['http_address'].replace("]", "").replace("inet[", "http:/")
            if server not in self.servers:
                self.servers.append(server)
        self._init_connection()
        return self.servers

    def _get_bulk_size(self):
        """
        Get the current bulk_size

        :return a int: the size of the bulk holder
        """
        return self._bulk_size

    def _set_bulk_size(self, bulk_size):
        """
        Set the bulk size

        :param bulk_size the bulker size
        """
        self._bulk_size = bulk_size
        self.bulker.bulk_size = bulk_size

    bulk_size = property(_get_bulk_size, _set_bulk_size)

    def _get_raise_on_bulk_item_failure(self):
        """
        Get the raise_on_bulk_item_failure status

        :return a bool: the status of raise_on_bulk_item_failure
        """
        return self._bulk_size

    def _set_raise_on_bulk_item_failure(self, raise_on_bulk_item_failure):
        """
        Set the raise_on_bulk_item_failure parameter

        :param raise_on_bulk_item_failure a bool the status of the raise_on_bulk_item_failure
        """
        self._raise_on_bulk_item_failure = raise_on_bulk_item_failure
        self.bulker.raise_on_bulk_item_failure = raise_on_bulk_item_failure

    raise_on_bulk_item_failure = property(_get_raise_on_bulk_item_failure, _set_raise_on_bulk_item_failure)

    def _send_request(self, method, path, body=None, params=None, headers=None, raw=False):
        if params is None:
            params = {}
        elif "routing" in params and params["routing"] is None:
            del params["routing"]

        if headers is None:
            headers = {}
        if not path.startswith("/"):
            path = "/" + path
        if not self.connection:
            self._init_connection()
        if body:
            if not isinstance(body, dict) and hasattr(body, "as_dict"):
                body = body.as_dict()
            if isinstance(body, dict):
               body = json.dumps(body, cls=self.encoder)
        else:
            body = ""

        request = RestRequest(method=Method._NAMES_TO_VALUES[method.upper()],
                              uri=path, parameters=params, headers=headers, body=body)
        if self.dump_curl is not None:
            self._dump_curl_request(request)

        # execute the request
        response = self.connection.execute(request)

        if method == "HEAD":
            return response.status == 200

        # handle the response
        try:
            decoded = json.loads(response.body, cls=self.decoder)
        except ValueError:
            try:
                decoded = json.loads(response.body, cls=ESJsonDecoder)
            except ValueError:
                # The only known place where we get back a body which can't be
                # parsed as JSON is when no handler is found for a request URI.
                # In this case, the body is actually a good message to return
                # in the exception.
                raise ElasticSearchException(response.body, response.status, response.body)
        if response.status != 200:
            raise_if_error(response.status, decoded)
        if not raw and isinstance(decoded, dict):
            decoded = DotDict(decoded)
        return decoded

    def _query_call(self, query_type, query, indices=None, doc_types=None, **query_params):
        """
        This can be used for search and count calls.
        These are identical api calls, except for the type of query.
        """
        path = self._make_path(indices, doc_types, query_type)
        return self._send_request('GET', path, query, params=query_params)

    def _make_path(self, indices, doc_types, *components, **kwargs):
        indices = self._validate_indices(indices)
        if 'allow_all_indices' in kwargs:
            allow_all_indices = kwargs.pop('allow_all_indices')
            if not allow_all_indices and indices == ['_all']:
                indices = []
        if doc_types is None:
            doc_types = self.default_types
        if isinstance(doc_types, basestring):
            doc_types = [doc_types]
        return make_path(','.join(indices), ','.join(doc_types), *components)

    def _validate_indices(self, indices=None):
        """Return a valid list of indices.

        `indices` may be a string or a list of strings.
        If `indices` is not supplied, returns the default_indices.
        """
        if indices is None:
            indices = self.default_indices
        if isinstance(indices, basestring):
            indices = [indices]
        return indices

    def _dump_curl_request(self, request):
        print >> self.dump_curl, "# [%s]" % datetime.now().isoformat()
        params = {'pretty': 'true'}
        params.update(request.parameters)
        method = Method._VALUES_TO_NAMES[request.method]
        server = self.servers[0]
        url = urlunsplit((server.scheme, server.netloc, request.uri, urlencode(params), ''))
        curl_cmd = "curl -X%s '%s'" % (method, url)
        if request.body:
            curl_cmd += " -d '%s'" % request.body
        print >> self.dump_curl, curl_cmd

    def _get_default_indices(self):
        return self._default_indices

    def _set_default_indices(self, indices):
        if indices is None:
            raise ValueError("default_indices cannot be set to None")
        self._default_indices = self._validate_indices(indices)

    default_indices = property(_get_default_indices, _set_default_indices)
    del _get_default_indices, _set_default_indices

    @property
    def mappings(self):
        if self._mappings is None:
            self._mappings = Mapper(self.get_mapping(indices=self.default_indices),
                                    connection=self,
                                    document_object_field=self.document_object_field)
        return self._mappings

    def create_bulker(self):
        """
        Create a bulker object and return it to allow to manage custom bulk policies
        """
        return  self.bulker_class(self, bulk_size=self.bulk_size,
                                  raise_on_bulk_item_failure=self.raise_on_bulk_item_failure)

    #---- Indices commands
    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.aliases")
    def aliases(self, indices=None):
        """
        Deprecated:
            use: indices.aliases(indices=indices)

        Retrieve the aliases of one or more indices
        """
        return self.indices.aliases(indices=indices)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.status")
    def status(self, indices=None):
        """
        Deprecated:
            use: indices.aliases(indices=indices)

        Retrieve the status of one or more indices
        """
        return self.indices.status(indices=indices)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.create_index")
    def create_index(self, index, settings=None):
        """
        Deprecated:
            use: indices.create_index(self, index, settings=None)

        Creates an index with optional settings.
        """
        return self.indices.create_index(index=index, settings=settings)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.create_index_if_missing")
    def create_index_if_missing(self, index, settings=None):
        """
        Deprecated

        Creates an index if it doesn't already exist.

        If supplied, settings must be a dictionary.
        """
        return  self.indices.create_index_if_missing(index=index, settings=settings)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.delete_index")
    def delete_index(self, index):
        """
        Deprecated

        Deletes an index.
        """
        return self.indices.delete_index(index=index)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.exists_index")
    def exists_index(self, index):
        """
        Deprecated

        Check if an index exists.
        """
        return self.indices.exists_index(index=index)

    def ensure_index(self, index, mappings=None, settings=None, clear=False):
        """
        Ensure if an index with mapping exists
        """
        mappings = mappings or []
        if isinstance(mappings, dict):
            mappings = [mappings]
        exists = self.exists_index(index)
        if exists and not mappings and not clear:
            return
        if exists and clear:
            self.indices.delete_index(index)
            exists = False

        if exists:
            if not mappings:
                self.delete_index(index)
                self.refresh()
                self.create_index(index, settings)
                return

            if clear:
                for maps in mappings:
                    for key in maps.keys():
                        self.delete_mapping(index, doc_type=key)
                self.refresh()
            if isinstance(mappings, SettingsBuilder):
                for name, data in mappings.mappings.items():
                    self.put_mapping(doc_type=name, mapping=data, indices=index)

            else:
                for maps in mappings:
                    if isinstance(maps, tuple):
                        name, mapping = maps
                        self.put_mapping(doc_type=name, mapping=mapping, indices=index)
                    elif isinstance(maps, dict):
                        for name, data in maps.items():
                            self.put_mapping(doc_type=name, mapping=maps, indices=index)

                return

        if settings:
            if isinstance(settings, dict):
                settings = SettingsBuilder(settings, mappings)
        else:
            if isinstance(mappings, SettingsBuilder):
                settings = mappings
            else:
                settings = SettingsBuilder(mappings=mappings)
        if not exists:
            self.create_index(index, settings)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.delete_index_if_exists")
    def delete_index_if_exists(self, index):
        """
        Deprecated

        Deletes an index if it exists.
        """
        return self.indices.delete_index_if_exists(index=index)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.get_indices")
    def get_indices(self, include_aliases=False):
        """
        Deprecated

        Get a dict holding an entry for each index which exists.

        If include_alises is True, the dict will also contain entries for
        aliases.

        The key for each entry in the dict is the index or alias name.  The
        value is a dict holding the following properties:

         - num_docs: Number of documents in the index or alias.
         - alias_for: Only present for an alias: holds a list of indices which
           this is an alias for.
        """
        return self.indices.get_indices(include_aliases=include_aliases)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.get_closed_indices")
    def get_closed_indices(self):
        """
        Deprecated

        Get all closed indices.
        """
        return self.indices.get_closed_indices()

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.get_alias")
    def get_alias(self, alias):
        """
        Deprecated

        Get the index or indices pointed to by a given alias.

        Raises IndexMissingException if the alias does not exist.

        Otherwise, returns a list of index names.
        """
        return self.indices.get_alias(alias)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.change_aliases")
    def change_aliases(self, commands):
        """
        Deprecated

        Change the aliases stored.

        `commands` is a list of 3-tuples; (command, index, alias), where
        `command` is one of "add" or "remove", and `index` and `alias` are the
        index and alias to add or remove.
        """
        return self.indices.change_aliases(commands)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.add_alias")
    def add_alias(self, alias, indices=None):
        """
        Deprecated

        Add an alias to point to a set of indices.
        """
        return self.indices.add_alias(alias, indices)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.delete_alias")
    def delete_alias(self, alias, indices=None):
        """
        Deprecated

        Delete an alias.

        The specified index or indices are deleted from the alias, if they are
        in it to start with.  This won't report an error even if the indices
        aren't present in the alias.
        """
        return self.indices.delete_alias(alias, indices)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.set_alias")
    def set_alias(self, alias, indices=None):
        """
        Deprecated

        Set an alias.

        This handles removing the old list of indices pointed to by the alias.

        Warning: there is a race condition in the implementation of this
        function - if another client modifies the indices which this alias
        points to during this call, the old value of the alias may not be
        correctly set.
        """
        return self.indices.set_alias(alias, indices)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.close_index")
    def close_index(self, index):
        """
        Deprecated

        Close an index.
        """
        return self.indices.close_index(index)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.open_index")
    def open_index(self, index):
        """
        Deprecated

        Open an index.
        """
        return self.indices.open_index(index)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.flush")
    def flush(self, indices=None, refresh=None):
        """
        Deprecated

        Flushes one or more indices (clear memory)
        If a bulk is full, it sends it.

        :keyword indices: an index or a list of indices
        :keyword refresh: set the refresh parameter
        """
        return self.indices.flush(indices=indices, refresh=refresh)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.refresh")
    def refresh(self, indices=None, timesleep=None):
        """
        Deprecated

        Refresh one or more indices

        timesleep: seconds to wait
        """
        return self.indices.refresh(indices=indices, timesleep=timesleep)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.optimize")
    def optimize(self, indices=None,
                 wait_for_merge=False,
                 max_num_segments=None,
                 only_expunge_deletes=False,
                 refresh=True,
                 flush=True):
        """Optimize one or more indices.

        `indices` is the list of indices to optimise.  If not supplied, all
        default_indices are optimised.

        `wait_for_merge` (boolean): If True, the operation will not return
        until the merge has been completed.  Defaults to False.

        `max_num_segments` (integer): The number of segments to optimize to. To
        fully optimize the index, set it to 1. Defaults to half the number
        configured by the merge policy (which in turn defaults to 10).

        `only_expunge_deletes` (boolean): Should the optimize process only
        expunge segments with deletes in it. In Lucene, a document is not
        deleted from a segment, just marked as deleted. During a merge process
        of segments, a new segment is created that does have those deletes.
        This flag allow to only merge segments that have deletes. Defaults to
        false.

        `refresh` (boolean): Should a refresh be performed after the optimize.
        Defaults to true.

        `flush` (boolean): Should a flush be performed after the optimize.
        Defaults to true.
        """
        return self.indices.optimize(indices=indices,
                 wait_for_merge=wait_for_merge,
                 max_num_segments=max_num_segments,
                 only_expunge_deletes=only_expunge_deletes,
                 refresh=refresh,
                 flush=flush)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.analyze")
    def analyze(self, text, index=None, analyzer=None, tokenizer=None, filters=None, field=None):
        """
        Performs the analysis process on a text and return the tokens breakdown of the text
        """
        if filters is None:
            filters = []
        argsets = 0
        args = {}

        if analyzer:
            args['analyzer'] = analyzer
            argsets += 1
        if tokenizer or filters:
            if tokenizer:
                args['tokenizer'] = tokenizer
            if filters:
                args['filters'] = ','.join(filters)
            argsets += 1
        if field:
            args['field'] = field
            argsets += 1

        if argsets > 1:
            raise ValueError('Argument conflict: Speficy either analyzer, tokenizer/filters or field')

        if field and index is None:
            raise ValueError('field can only be specified with an index')

        path = make_path(index, '_analyze')
        return self._send_request('POST', path, text, args)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.gateway_snapshot")
    def gateway_snapshot(self, indices=None):
        """
        Gateway snapshot one or more indices

        :param indices: a list of indices or None for default configured.
        """
        return self.indices.gateway_snapshot(indices=indices)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.put_mapping")
    def put_mapping(self, doc_type=None, mapping=None, indices=None):
        """
        Register specific mapping definition for a specific type against one or more indices.
        """
        return self.indices.put_mapping(doc_type=doc_type, mapping=mapping, indices=indices)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.get_mapping")
    def get_mapping(self, doc_type=None, indices=None):
        """
        Register specific mapping definition for a specific type against one or more indices.
        """
        return self.indices.get_mapping(doc_type=doc_type, indices=indices)

    def collect_info(self):
        """
        Collect info about the connection and fill the info dictionary.
        """
        try:
            info = {}
            res = self._send_request('GET', "/")
            info['server'] = {}
            info['server']['name'] = res['name']
            info['server']['version'] = res['version']
            info['allinfo'] = res
            info['status'] = self.status()
            info['aliases'] = self.aliases()
            self.info = info
            return True
        except:
            self.info = {}
            return False

    #--- cluster
    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].cluster.cluster_health")
    def cluster_health(self, indices=None, level="cluster", wait_for_status=None,
                       wait_for_relocating_shards=None, timeout=30):
        """
        Check the current :ref:`cluster health <es-guide-reference-api-admin-cluster-health>`.
        Request Parameters

        The cluster health API accepts the following request parameters:

        :param level: Can be one of cluster, indices or shards. Controls the
                        details level of the health information returned.
                        Defaults to *cluster*.
        :param wait_for_status: One of green, yellow or red. Will wait (until
                                the timeout provided) until the status of the
                                cluster changes to the one provided.
                                By default, will not wait for any status.
        :param wait_for_relocating_shards: A number controlling to how many
                                           relocating shards to wait for.
                                           Usually will be 0 to indicate to
                                           wait till all relocation have
                                           happened. Defaults to not to wait.
        :param timeout: A time based parameter controlling how long to wait
                        if one of the wait_for_XXX are provided.
                        Defaults to 30s.
        """
        return self.cluster.health(indices=indices, level=level, wait_for_status=wait_for_status,
                                   wait_for_relocating_shards=wait_for_relocating_shards,
                                   timeout=timeout)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].cluster.state")
    def cluster_state(self, filter_nodes=None, filter_routing_table=None,
                      filter_metadata=None, filter_blocks=None,
                      filter_indices=None):
        """
        Retrieve the :ref:`cluster state <es-guide-reference-api-admin-cluster-state>`.

        :param filter_nodes: set to **true** to filter out the **nodes** part
                             of the response.
        :param filter_routing_table: set to **true** to filter out the
                                     **routing_table** part of the response.
        :param filter_metadata: set to **true** to filter out the **metadata**
                                part of the response.
        :param filter_blocks: set to **true** to filter out the **blocks**
                              part of the response.
        :param filter_indices: when not filtering metadata, a comma separated
                               list of indices to include in the response.
        """
        return self.cluster.state(filter_nodes=filter_nodes, filter_routing_table=filter_routing_table,
                      filter_metadata=filter_metadata, filter_blocks=filter_blocks,
                      filter_indices=filter_indices)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].cluster.nodes_info")
    def cluster_nodes(self, nodes=None):
        """
        The cluster :ref:`nodes info <es-guide-reference-api-admin-cluster-state>` API allows to retrieve one or more (or all) of
        the cluster nodes information.
        """
        return self.cluster.nodes_info(nodes=nodes)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].cluster.node_stats")
    def cluster_stats(self, nodes=None):
        """
        The cluster :ref:`nodes info <es-guide-reference-api-admin-cluster-nodes-stats>` API allows to retrieve one or more (or all) of
        the cluster nodes information.
        """
        return self.cluster.node_stats(nodes=nodes)

    def index_raw_bulk(self, header, document):
        """
        Function helper for fast inserting

        :param header: a string with the bulk header must be ended with a newline
        :param header: a json document string must be ended with a newline
        """
        self.bulker.add(u"%s%s" % (header, document))
        return self.flush_bulk()

    def index(self, doc, index, doc_type, id=None, parent=None, force_insert=False,
              op_type=None, bulk=False, version=None, querystring_args=None):
        """
        Index a typed JSON document into a specific index and make it searchable.
        """
        if querystring_args is None:
            querystring_args = {}

        if bulk:
            if op_type is None:
                op_type = "index"
            if force_insert:
                op_type = "create"
            cmd = {op_type: {"_index": index, "_type": doc_type}}
            if parent:
                cmd[op_type]['_parent'] = parent
            if version:
                cmd[op_type]['_version'] = version
            if 'routing' in querystring_args:
                cmd[op_type]['_routing'] = querystring_args['routing']
            if 'percolate' in querystring_args:
                cmd[op_type]['percolate'] = querystring_args['percolate']
            if id is not None:#None to support 0 as id
                cmd[op_type]['_id'] = id

            if isinstance(doc, dict):
                doc = json.dumps(doc, cls=self.encoder)
            command = "%s\n%s" % (json.dumps(cmd, cls=self.encoder), doc)
            self.bulker.add(command)
            return self.flush_bulk()

        if force_insert:
            querystring_args['op_type'] = 'create'
        if op_type:
            querystring_args['op_type'] = op_type

        if parent:
            if not isinstance(parent, basestring):
                parent = str(parent)
            querystring_args['parent'] = parent

        if version:
            if not isinstance(version, basestring):
                version = str(version)
            querystring_args['version'] = version

        if id is None:
            request_method = 'POST'
        else:
            request_method = 'PUT'

        path = make_path(index, doc_type, id)
        return self._send_request(request_method, path, doc, querystring_args)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.stats")
    def index_stats(self, indices=None):
        """
        http://www.elasticsearch.org/guide/reference/api/admin-indices-stats.html
        """
        return self.indices.stats(indices=indices)

    def flush_bulk(self, forced=False):
        """
        Send pending operations if forced or if the bulk threshold is exceeded.
        """
        return self.bulker.flush_bulk(forced)

    def force_bulk(self):
        """
        Force executing of all bulk data.

        Return the bulk response
        """
        return self.flush_bulk(True)

    def put_file(self, filename, index, doc_type, id=None, name=None):
        """
        Store a file in a index
        """
        if id is None:
            request_method = 'POST'
        else:
            request_method = 'PUT'
        path = make_path(index, doc_type, id)
        doc = file_to_attachment(filename)
        if name:
            doc["_name"] = name
        return self._send_request(request_method, path, doc)

    def get_file(self, index, doc_type, id=None):
        """
        Return the filename and memory data stream
        """
        data = self.get(index, doc_type, id)
        return data['_name'], base64.standard_b64decode(data['content'])
        #return data["_source"]['_name'], base64.standard_b64decode(data["_source"]['content'])

    def update(self, extra_doc, index, doc_type, id, querystring_args=None,
               update_func=None, attempts=2):
        """
        Update an already indexed typed JSON document.

        The update happens client-side, i.e. the current document is retrieved,
        updated locally and finally pushed to the server. This may repeat up to
        ``attempts`` times in case of version conflicts.

        :param update_func: A callable ``update_func(current_doc, extra_doc)``
            that computes and returns the updated doc. Alternatively it may
            update ``current_doc`` in place and return None. The default
            ``update_func`` is ``dict.update``.

        :param attempts: How many times to retry in case of version conflict.
        """
        if querystring_args is None:
            querystring_args = {}

        if update_func is None:
            update_func = dict.update

        for attempt in xrange(attempts - 1, -1, -1):
            current_doc = self.get(index, doc_type, id, **querystring_args)
            new_doc = update_func(current_doc, extra_doc)
            if new_doc is None:
                new_doc = current_doc
            try:
                return self.index(new_doc, index, doc_type, id,
                                  version=current_doc._meta.version, querystring_args=querystring_args)
            except VersionConflictEngineException:
                if attempt <= 0:
                    raise
                self.refresh(index)

    def delete(self, index, doc_type, id, bulk=False, **query_params):
        """
        Delete a typed JSON document from a specific index based on its id.
        If bulk is True, the delete operation is put in bulk mode.
        """
        if bulk:
            cmd = {"delete": {"_index": index, "_type": doc_type,
                              "_id": id}}
            self.bulker.add(json.dumps(cmd, cls=self.encoder))
            return self.flush_bulk()

        path = make_path(index, doc_type, id)
        return self._send_request('DELETE', path, params=query_params)

    def delete_by_query(self, indices, doc_types, query, **query_params):
        """
        Delete documents from one or more indices and one or more types based on a query.
        """
        if hasattr(query, 'to_query_json'):
            # Then is a Query object.
            body = query.to_query_json()
        elif isinstance(query, dict):
            # A direct set of search parameters.
            body = json.dumps(query, cls=ES.encoder)
        else:
            raise InvalidQuery("delete_by_query() must be supplied with a Query object, or a dict")

        path = self._make_path(indices, doc_types, '_query')
        return self._send_request('DELETE', path, body, query_params)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.delete_mapping")
    def delete_mapping(self, index, doc_type):
        """
        Delete a typed JSON document type from a specific index.
        """
        return self.indices.delete_mapping(index=index, doc_type=doc_type)

    def exists(self, index, doc_type, id, **query_params):
        """
        Return if a document exists
        """
        if isinstance(id, (int, long, float)):
            id = str(id)
        path = make_path(index, doc_type, urllib.quote_plus(id))
        return self._send_request('HEAD', path, params=query_params)

    def get(self, index, doc_type, id, fields=None, model=None, **query_params):
        """
        Get a typed JSON document from an index based on its id.
        """
        path = make_path(index, doc_type, id)
        if fields is not None:
            query_params["fields"] = ",".join(fields)
        model = model or self.model
        return model(self, self._send_request('GET', path, params=query_params))

    def factory_object(self, index, doc_type, data=None, id=None, vertex=False):
        """
        Create a stub object to be manipulated
        """
        data = data or {}
        obj = ElasticSearchModel()
        obj._meta.index = index
        obj._meta.type = doc_type
        obj._meta.connection = self
        if id:
            obj._meta.id = id
        if data:
            obj.update(data)
        if vertex:
            obj.force_vertex()
        return obj

    def mget(self, ids, index=None, doc_type=None, **query_params):
        """
        Get multi JSON documents.

        ids can be:
            list of tuple: (index, type, id)
            list of ids: index and doc_type are required
        """
        if not ids:
            return []

        body = []
        for value in ids:
            if isinstance(value, tuple):
                if len(value) == 3:
                    a, b, c = value
                    body.append({"_index": a,
                                 "_type": b,
                                 "_id": c})
                elif len(value) == 4:
                    a, b, c, d = value
                    body.append({"_index": a,
                                 "_type": b,
                                 "_id": c,
                                 "fields": d})

            else:
                if index is None:
                    raise InvalidQuery("index value is required for id")
                if doc_type is None:
                    raise InvalidQuery("doc_type value is required for id")
                body.append({"_index": index,
                             "_type": doc_type,
                             "_id": value})

        results = self._send_request('GET', "/_mget", body={'docs': body},
                                     params=query_params)
        if 'docs' in results:
            model = self.model
            return [model(self, item) for item in results['docs']]
        return []

    def search_raw(self, query, indices=None, doc_types=None, **query_params):
        """Execute a search against one or more indices to get the search hits.

        `query` must be a Search object, a Query object, or a custom
        dictionary of search parameters using the query DSL to be passed
        directly.
        """
        if hasattr(query, 'to_search_json'):
            # Common case - a Search or Query object.
            query.encoder = self.encoder
            body = query.to_search_json()
        elif isinstance(query, dict):
            # A direct set of search parameters.
            body = json.dumps(query, cls=self.encoder)
        else:
            raise InvalidQuery("search() must be supplied with a Search or Query object, or a dict")

        return self._query_call("_search", body, indices, doc_types, **query_params)

    def search(self, query, indices=None, doc_types=None, model=None, scan=False, **query_params):
        """Execute a search against one or more indices to get the resultset.

        `query` must be a Search object, a Query object, or a custom
        dictionary of search parameters using the query DSL to be passed
        directly.
        """
        from .query import Search, Query
        if isinstance(query, Search):
            search = query
        elif isinstance(query, (Query, dict)):
            search = Search(query)
        else:
            raise InvalidQuery("search() must be supplied with a Search or Query object, or a dict")

        if scan:
            query_params.setdefault("search_type", "scan")
            query_params.setdefault("scroll", "10m")

        return ResultSet(self, search, indices=indices, doc_types=doc_types,
                         model=model, query_params=query_params)

    #    scan method is no longer working due to change in ES.search behavior.  May no longer warrant its own method.
    #    def scan(self, query, indices=None, doc_types=None, scroll="10m", **query_params):
    #        """Return a generator which will scan against one or more indices and iterate over the search hits. (currently support only by ES Master)
    #
    #        `query` must be a Search object, a Query object, or a custom
    #        dictionary of search parameters using the query DSL to be passed
    #        directly.
    #
    #        """
    #        results = self.search(query=query, indices=indices, doc_types=doc_types, search_type="scan", scroll=scroll, **query_params)
    #        while True:
    #            scroll_id = results["_scroll_id"]
    #            results = self._send_request('GET', "_search/scroll", scroll_id, {"scroll":scroll})
    #            total = len(results["hits"]["hits"])
    #            if not total:
    #                break
    #            yield results

    def search_scroll(self, scroll_id, scroll="10m"):
        """
        Executes a scrolling given an scroll_id
        """
        return self._send_request('GET', "_search/scroll", scroll_id, {"scroll": scroll})

    def reindex(self, query, indices=None, doc_types=None, **query_params):
        """
        Execute a search query against one or more indices and and reindex the hits.
        query must be a dictionary or a Query object that will convert to Query DSL.
        Note: reindex is only available in my ElasticSearch branch on github.
        """
        if not isinstance(query, basestring):
            if isinstance(query, dict):
                if 'query' in query:
                    query = query['query']
                query = json.dumps(query, cls=self.encoder)
            elif hasattr(query, "to_query_json"):
                query = query.to_query_json(inner=True)
        path = self._make_path(indices, doc_types, "_reindexbyquery")
        return self._send_request('POST', path, query, query_params)

    def count(self, query=None, indices=None, doc_types=None, **query_params):
        """
        Execute a query against one or more indices and get hits count.
        """
        if query is None:
            from .query import MatchAllQuery
            query = MatchAllQuery()
        if hasattr(query, 'to_query_json'):
            query = query.to_query_json()
        if hasattr(query, 'to_json'):
            query = query.to_json()
        return self._query_call("_count", query, indices, doc_types, **query_params)

    #--- river management
    def create_river(self, river, river_name=None):
        """
        Create a river
        """
        if hasattr(river, "q"):
            river_name = river.name
            river = river.q
        return self._send_request('PUT', '/_river/%s/_meta' % river_name, river)

    def delete_river(self, river, river_name=None):
        """
        Delete a river
        """
        if hasattr(river, "q"):
            river_name = river.name
        return self._send_request('DELETE', '/_river/%s/' % river_name)

    #--- settings management

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.get_settings")
    def get_settings(self, index=None):
        """
        Returns the current settings for an index.
        """
        return self.indices.get_settings(index=index)

    @deprecated(deprecation="0.19.1", removal="0.20", alternative="[self].indices.update_settings")
    def update_settings(self, index, newvalues):
        """
        Update Settings of an index.
        """
        return self.indices.update_settings(index=index, newvalues=newvalues)

    def update_mapping_meta(self, doc_type, values, indices=None):
        """
        Update mapping meta
        :param doc_type: a doc type or a list of doctypes
        :param values: the dict of meta
        :param indices: a list of indices
        :return:
        """
        indices = self._validate_indices(indices)
        for index in indices:
            mapping = self.mappings.get_doctype(index, doc_type)
            if mapping is None:
                continue
            meta = mapping.get_meta()
            meta.update(values)
            mapping = {doc_type:{"_meta":meta}}
            self.indices.put_mapping(doc_type=doc_type, mapping=mapping, indices=indices)

    def morelikethis(self, index, doc_type, id, fields, **query_params):
        """
        Execute a "more like this" search query against one or more fields and get back search hits.
        """
        path = make_path(index, doc_type, id, '_mlt')
        query_params['fields'] = ','.join(fields)
        body = query_params["body"] if query_params.has_key("body") else None
        return self._send_request('GET', path, body=body, params=query_params)

    def create_percolator(self, index, name, query, **kwargs):
        """
        Create a percolator document

        Any kwargs will be added to the document as extra properties.
        """
        path = make_path('_percolator', index, name)

        if hasattr(query, 'serialize'):
            query = {'query': query.serialize()}

        if not isinstance(query, dict):
            raise InvalidQuery("create_percolator() must be supplied with a Query object or dict")
            # A direct set of search parameters.
        query.update(kwargs)
        body = json.dumps(query, cls=self.encoder)

        return self._send_request('PUT', path, body=body)

    def delete_percolator(self, index, name):
        """
        Delete a percolator document
        """
        return self.delete('_percolator', index, name)

    def percolate(self, index, doc_types, query):
        """
        Match a query with a document
        """
        if doc_types is None:
            raise RuntimeError('percolate() must be supplied with at least one doc_type')

        if hasattr(query, 'to_query_json'):
            # Then is a Query object.
            body = query.to_query_json()
        elif isinstance(query, dict):
            # A direct set of search parameters.
            body = json.dumps(query, cls=self.encoder)
        else:
            raise InvalidQuery("percolate() must be supplied with a Query object, or a dict")

        path = self._make_path(index, doc_types, '_percolate')
        return self._send_request('GET', path, body=body)


def decode_json(data):
    """ Decode some json to dict"""
    return json.loads(data, cls=ES.decoder)


def encode_json(data):
    """ Encode some json to dict"""
    return json.dumps(data, cls=ES.encoder)


class ResultSet(object):

    def __init__(self, connection, search, indices=None, doc_types=None, query_params=None,
                 auto_fix_keys=False, auto_clean_highlight=False, model=None):
        """
        results: an es query results dict
        fix_keys: remove the "_" from every key, useful for django views
        clean_highlight: removed empty highlight
        search: a Search object.
        """
        from .query import Search
        if not isinstance(search, Search):
            raise InvalidQuery("ResultSet must be supplied with a Search object")

        self.search = search
        self.connection = connection
        self.indices = indices
        self.doc_types = doc_types
        self.query_params = query_params or {}
        self.scroller_parameters = {}
        self.scroller_id = None
        self._results = None
        self.model = model or self.connection.model
        self._total = None
        self.valid = False
        self._facets = {}
        self.auto_fix_keys = auto_fix_keys
        self.auto_clean_highlight = auto_clean_highlight

        self.iterpos = 0 #keep track of iterator position
        self.start = query_params.get("start", search.start) or 0
        self._max_item = query_params.get("size", search.size)
        self._current_item = 0
        self.chuck_size = search.bulk_read or search.size or 10

    def _do_search(self, auto_increment=False):
        self.iterpos = 0
        process_post_query = True #used to skip results in first scan
        if self.scroller_id is None:
            if auto_increment:
                self.start += self.chuck_size

            self._results = self._search_raw(self.start, self.chuck_size)

            do_scan = self.query_params.pop("search_type", None) == "scan"
            if do_scan:
                self.scroller_parameters['search_type'] = "scan"
                if 'scroll' in self.query_params:
                    self.scroller_parameters['scroll'] = self.query_params.pop('scroll')
                if 'size' in self.query_params:
                    self.chuck_size = self.scroller_parameters['size'] = self.query_params.pop('size')

            if '_scroll_id' in self._results:
                #scan query, let's load the first bulk of data
                self.scroller_id = self._results['_scroll_id']
                self._do_search()
                process_post_query = False
        else:
            try:
                self._results = self.connection.search_scroll(self.scroller_id,
                                                              self.scroller_parameters.get("scroll", "10m"))
                self.scroller_id = self._results['_scroll_id']
            except ReduceSearchPhaseException:
                #bad hack, should be not hits on the last iteration
                self._results['hits']['hits'] = []

        if process_post_query:
            self._facets = self._results.get('facets', {})
            if 'hits' in self._results:
                self.valid = True
                self.hits = self._results['hits']['hits']
            else:
                self.hits = []
            if self.auto_fix_keys:
                self._fix_keys()
            if self.auto_clean_highlight:
                self.clean_highlight()

    @property
    def total(self):
        if self._results is None:
            self._do_search()
        if self._total is None:
            self._total = 0
            if self.valid:
                self._total = self._results.get("hits", {}).get('total', 0)
        return self._total

    @property
    def facets(self):
        if self._results is None:
            self._do_search()
        return self._facets

    def fix_facets(self):
        """
        This function convert date_histogram facets to datetime
        """
        facets = self.facets
        for key in facets.keys():
            _type = facets[key].get("_type", "unknown")
            if _type == "date_histogram":
                for entry in facets[key].get("entries", []):
                    for k, v in entry.items():
                        if k in ["count", "max", "min", "total_count", "mean", "total"]:
                            continue
                        entry[k] = datetime.utcfromtimestamp(v / 1e3)

    def __len__(self):
        return self.total

    def count(self):
        return self.total

    def fix_keys(self):
        """
        Remove the _ from the keys of the results
        """
        if not self.valid:
            return

        for hit in self._results['hits']['hits']:
            for key, item in hit.items():
                if key.startswith("_"):
                    hit[key[1:]] = item
                    del hit[key]

    def clean_highlight(self):
        """
        Remove the empty highlight
        """
        if not self.valid:
            return

        for hit in self._results['hits']['hits']:
            if 'highlight' in hit:
                hl = hit['highlight']
                for key, item in hl.items():
                    if not item:
                        del hl[key]

    def __getattr__(self, name):
        if self._results is None:
            self._do_search()
        if name == "facets":
            return self._facets

        elif name in self._results:
            #we manage took, timed_out, _shards
            return self._results[name]

        elif name == "shards" and "_shards" in self._results:
            #trick shards -> _shards
            return self._results["_shards"]
        return self._results['hits'][name]

    def __getitem__(self, val):
        if not isinstance(val, (int, long, slice)):
            raise TypeError('%s indices must be integers, not %s' % (
                self.__class__.__name__, val.__class__.__name__))

        def get_start_end(val):
            if isinstance(val, slice):
                start = val.start
                if not start:
                    start = 0
                end = val.stop or self.total
                if end < 0:
                    end = self.total + end
                if self._max_item is not None and end > self._max_item:
                    end = self._max_item
                return start, end
            return val, val + 1

        start, end = get_start_end(val)
        model = self.model

        if self._results:
            if start >= 0 and end < self.start + self.chuck_size and len(self._results['hits']['hits']) > 0 and \
                ("_source" in self._results['hits']['hits'][0] or "_fields" in self._results['hits']['hits'][0]):
                if not isinstance(val, slice):
                    return model(self.connection, self._results['hits']['hits'][val - self.start])
                else:
                    return [model(self.connection, hit) for hit in self._results['hits']['hits'][start:end]]

        results = self._search_raw(start + self.start, end - start)
        hits = results['hits']['hits']
        if not isinstance(val, slice):
            if len(hits) == 1:
                return model(self.connection, hits[0])
            raise IndexError
        return [model(self.connection, hit) for hit in hits]

    def next(self):
        if self._max_item is not None and self._current_item == self._max_item:
            raise StopIteration
        if self._results is None:
            self._do_search()
        if "_scroll_id" in self._results and self._total != 0 and self._current_item == 0 and len(
            self._results["hits"].get("hits", [])) == 0:
            self._do_search()
        if len(self.hits) == 0:
            raise StopIteration
        if self.iterpos < len(self.hits):
            res = self.hits[self.iterpos]
            self.iterpos += 1
            self._current_item += 1
            return self.model(self.connection, res)

        if self.start + self.iterpos == self.total:
            raise StopIteration
        self._do_search(auto_increment=True)
        self.iterpos = 0
        if len(self.hits) == 0:
            raise StopIteration
        res = self.hits[self.iterpos]
        self.iterpos += 1
        self._current_item += 1
        return self.model(self.connection, res)

    def __iter__(self):
        self.iterpos = 0
        if self._current_item != 0:
            self._results = None
        self._current_item = 0

        return self

    def _search_raw(self, start=None, size=None):
        if start is None and size is None:
            query_params = self.query_params
        else:
            query_params = dict(self.query_params)
            if start is not None:
                query_params["from"] = start
            if size is not None:
                query_params["size"] = size

        return self.connection.search_raw(self.search, indices=self.indices,
                                          doc_types=self.doc_types, **query_params)
