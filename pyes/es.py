# -*- coding: utf-8 -*-

import six

from datetime import date, datetime
from decimal import Decimal

if six.PY2:
    from six.moves.urllib.parse import urlencode, urlunsplit, urlparse
else:
    from urllib.parse import urlencode, urlunsplit, urlparse
# import urllib.request, urllib.parse, urllib.error


import base64
import codecs
import random
import weakref

try:
    import simplejson as json
except ImportError:
    import json

from . import logger
from . import connection_http
from .connection_http import connect as http_connect
from .convert_errors import raise_if_error
#from .decorators import deprecated
from .exceptions import ElasticSearchException, ReduceSearchPhaseException, \
    InvalidQuery, VersionConflictEngineException
from .helpers import SettingsBuilder
from .managers import Indices, Cluster
from .mappings import Mapper
from .models import ElasticSearchModel, DotDict, ListBulker
from .query import Search, Query
from .rivers import River
from .utils import make_path, get_unicode_string

try:
    from .connection import connect as thrift_connect
    from .pyesthrift.ttypes import Method, RestRequest
except ImportError:
    thrift_connect = None
    from .fakettypes import Method, RestRequest

import six


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


def expand_suggest_text(suggest):
    from itertools import product

    suggested = set()
    all_segments = {}
    for field, tokens in suggest.items():
        if field.startswith(u"_"):
            #we skip _shards
            continue
        if len(tokens) == 1 and not tokens[0]["options"]:
            continue
        texts = []
        for token in tokens:
            if not token["options"]:
                texts.append([(1.0, 1, token["text"])])
                continue
            values = []
            for option in token["options"]:
                values.append((option["score"], option.get("freq", option["score"]), option["text"]))
            texts.append(values)
        for terms in product(*texts):
            score = sum([v for v, _, _ in terms])
            freq = sum([v for _, v, _ in terms])
            text = u' '.join([t for _, _, t in terms])
            if text in all_segments:
                olds, oldf = all_segments[text]
                all_segments[text] = (score + olds, freq + oldf)
            else:
                all_segments[text] = (score, freq)
                #removing dupped
    for t, (s, f) in all_segments.items():
        suggested.add((s, f, t))

    return sorted(suggested, reverse=True)


class ESJsonEncoder(json.JSONEncoder):
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


class ESJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        kwargs['object_hook'] = self.dict_to_object
        super(ESJsonDecoder, self).__init__(*args, **kwargs)

    def string_to_datetime(self, obj):
        """
        Decode a datetime string to a datetime object
        """
        if isinstance(obj, six.string_types) and len(obj) == 19:
            try:
                return datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                pass
        if isinstance(obj, six.string_types) and len(obj) > 19:
            try:
                return datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                pass
        if isinstance(obj, six.string_types) and len(obj) == 10:
            try:
                return datetime.strptime(obj, "%Y-%m-%d")
            except ValueError:
                pass
        return obj


    def dict_to_object(self, d):
        """
        Decode datetime value from string to datetime
        """
        for k, v in list(d.items()):
            if isinstance(v, six.string_types) and len(v) == 19:
                # Decode a datetime string to a datetime object
                try:
                    d[k] = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    pass
            elif isinstance(v, six.string_types) and len(v) > 20:
                try:
                    d[k] = datetime.strptime(v, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    pass
            elif isinstance(v, list):
                d[k] = [self.string_to_datetime(elem) for elem in v]
        return DotDict(d)


def get_id(text):
    return str(uuid.uuid3(DotDict(bytes=""), text))


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
                 retry_time=60,
                 default_indices=None,
                 default_types=None,
                 log_curl=False,
                 dump_curl=False,
                 model=ElasticSearchModel,
                 basic_auth=None,
                 raise_on_bulk_item_failure=False,
                 document_object_field=None,
                 bulker_class=ListBulker,
                 cert_reqs='CERT_OPTIONAL'):
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
        :param retry_time: number of seconds between retries
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
        self.retry_time = retry_time
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
        self.log_curl = log_curl
        if dump_curl:
            if isinstance(dump_curl, six.string_types):
                self.dump_curl = codecs.open(dump_curl, "wb", "utf8")
            elif hasattr(dump_curl, 'write'):
                self.dump_curl = dump_curl
            else:
                raise TypeError("dump_curl parameter must be supplied with a "
                                "string or an object with a write() method")
        else:
            self.dump_curl = None

        #used in bulk
        self._bulk_size = bulk_size  #size of the bulk
        self.bulker = bulker_class(weakref.proxy(self), bulk_size=bulk_size,
                                   raise_on_bulk_item_failure=raise_on_bulk_item_failure)
        self.bulker_class = bulker_class
        self._raise_on_bulk_item_failure = raise_on_bulk_item_failure

        connection_http.CERT_REQS = cert_reqs

        self.info = {}  #info about the current server
        if encoder:
            self.encoder = encoder
        if decoder:
            self.decoder = decoder
        if isinstance(server, six.string_types):
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
        if self.bulker and self.bulker.bulk_data:
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
            elif isinstance(server, six.string_types):
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
                            raise RuntimeError("Invalid port: \"%s\"" % tokens[1])

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
                [server for server in self.servers if server.scheme in ["http", "https"]],
                timeout=self.timeout, basic_auth=self.basic_auth, max_retries=self.max_retries, retry_time=self.retry_time)
            return
        elif server.scheme == "thrift":
            self.connection = thrift_connect(
                [server for server in self.servers if server.scheme == "thrift"],
                timeout=self.timeout, max_retries=self.max_retries, retry_time=self.retry_time)

    def _discovery(self):
        """
        Find other servers asking nodes to given server
        """
        data = self.cluster_nodes()
        self.cluster_name = data["cluster_name"]
        for _, nodedata in list(data["nodes"].items()):
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

    def _send_request(self, method, path, body=None, params=None, headers=None, raw=False, return_response=False):
        if params is None:
            params = {}
        elif "routing" in params and params["routing"] is None:
            del params["routing"]

        path = path.replace("%2C", ",")
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

        if params:
            for k in params:
                params[k] = str(params[k])
        request = RestRequest(method=Method._NAMES_TO_VALUES[method.upper()],
                              uri=path, parameters=params, headers=headers, body=body)
        if self.dump_curl is not None:
            self.dump_curl.write(("# [%s]" % datetime.now().isoformat()).encode('utf-8'))
            self.dump_curl.write(self._get_curl_request(request).encode('utf-8'))

        if self.log_curl:
            logger.debug(self._get_curl_request(request))

        # execute the request
        response = self.connection.execute(request)

        if self.dump_curl is not None:
            self.dump_curl.write(("# response status: %s" % response.status).encode('utf-8'))
            self.dump_curl.write(("# response body: %s" % response.body).encode('utf-8'))

        if return_response:
            return response

        if method == "HEAD":
            return response.status == 200

        # handle the response
        response_body = response.body
        if six.PY3:
            response_body = response_body.decode(encoding='UTF-8')

        try:
            decoded = json.loads(response_body, cls=self.decoder)
        except ValueError:
            try:
                decoded = json.loads(response_body, cls=ESJsonDecoder)
            except ValueError:
                # The only known place where we get back a body which can't be
                # parsed as JSON is when no handler is found for a request URI.
                # In this case, the body is actually a good message to return
                # in the exception.
                raise ElasticSearchException(response_body, response.status, response_body)
        if response.status not in [200, 201]:
            raise_if_error(response.status, decoded)
        if not raw and isinstance(decoded, dict):
            decoded = DotDict(decoded)
        return decoded

    def _make_path(self, indices, doc_types, *components, **kwargs):
        indices = self._validate_indices(indices)
        if 'allow_all_indices' in kwargs:
            allow_all_indices = kwargs.pop('allow_all_indices')
            if not allow_all_indices and indices == ['_all']:
                indices = []
        if doc_types is None:
            doc_types = self.default_types
        if isinstance(doc_types, six.string_types):
            doc_types = [doc_types]
        return make_path(','.join(indices), ','.join(doc_types), *components)

    def _validate_indices(self, indices=None):
        """Return a valid list of indices.

        `indices` may be a string or a list of strings.
        If `indices` is not supplied, returns the default_indices.
        """
        if indices is None:
            indices = self.default_indices
        if isinstance(indices, six.string_types):
            indices = [indices]
        return indices

    def validate_types(self, types=None):
        """Return a valid list of types.

        `types` may be a string or a list of strings.
        If `types` is not supplied, returns the default_types.

        """
        types = types or self.default_types
        if types is None:
            types = []
        if isinstance(types, six.string_types):
            types = [types]
        return types

    def _get_curl_request(self, request):
        params = {'pretty': 'true'}
        params.update(request.parameters)
        method = Method._VALUES_TO_NAMES[request.method]
        server = self.servers[0]
        url = urlunsplit((server.scheme, server.netloc, request.uri, urlencode(params), ''))
        curl_cmd = "curl -X%s '%s'" % (method, url)
        body = request.body
        if body:
            if not isinstance(body, str):
                body = get_unicode_string(body)
            curl_cmd += " -d '%s'" % body
        return curl_cmd

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
            self._mappings = Mapper(self.indices.get_mapping(indices=self.default_indices, raw=True),
                                    connection=self,
                                    document_object_field=self.document_object_field)
        return self._mappings

    def create_bulker(self):
        """
        Create a bulker object and return it to allow to manage custom bulk policies
        """
        return self.bulker_class(self, bulk_size=self.bulk_size,
                                 raise_on_bulk_item_failure=self.raise_on_bulk_item_failure)

    def ensure_index(self, index, mappings=None, settings=None, clear=False):
        """
        Ensure if an index with mapping exists
        """
        mappings = mappings or []
        if isinstance(mappings, dict):
            mappings = [mappings]
        exists = self.indices.exists_index(index)
        if exists and not mappings and not clear:
            return
        if exists and clear:
            self.indices.delete_index(index)
            exists = False

        if exists:
            if not mappings:
                self.indices.delete_index(index)
                self.indices.refresh()
                self.indices.create_index(index, settings)
                return

            if clear:
                for maps in mappings:
                    for key in list(maps.keys()):
                        self.indices.delete_mapping(index, doc_type=key)
                self.indices.refresh()
            if isinstance(mappings, SettingsBuilder):
                for name, data in list(mappings.mappings.items()):
                    self.indices.put_mapping(doc_type=name, mapping=data, indices=index)

            else:
                from pyes.mappings import DocumentObjectField, ObjectField

                for maps in mappings:
                    if isinstance(maps, tuple):
                        name, mapping = maps
                        self.indices.put_mapping(doc_type=name, mapping=mapping, indices=index)
                    elif isinstance(maps, dict):
                        for name, data in list(maps.items()):
                            self.indices.put_mapping(doc_type=name, mapping=maps, indices=index)
                    elif isinstance(maps, (DocumentObjectField, ObjectField)):
                        self.put_mapping(doc_type=maps.name, mapping=maps.as_dict(), indices=index)

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
            self.indices.create_index(index, settings)
            self.indices.refresh(index, timesleep=1)

    def put_warmer(self, doc_types=None, indices=None, name=None, warmer=None, querystring_args=None):
        """
        Put new warmer into index (or type)

        :param doc_types: list of document types
        :param warmer: anything with ``serialize`` method or a dictionary
        :param name: warmer name
        :param querystring_args: additional arguments passed as GET params to ES
        """
        if not querystring_args:
            querystring_args = {}
        doc_types_str = ''
        if doc_types:
            doc_types_str = '/' + ','.join(doc_types)
        path = '/{0}{1}/_warmer/{2}'.format(','.join(indices), doc_types_str, name)
        if hasattr(warmer, 'serialize'):
            body = warmer.serialize()
        else:
            body = warmer
        return self._send_request(method='PUT', path=path, body=body, params=querystring_args)

    def get_warmer(self, doc_types=None, indices=None, name=None, querystring_args=None):
        """
        Retrieve warmer

        :param doc_types: list of document types
        :param warmer: anything with ``serialize`` method or a dictionary
        :param name: warmer name. If not provided, all warmers will be returned
        :param querystring_args: additional arguments passed as GET params to ES
        """
        name = name or ''
        if not querystring_args:
            querystring_args = {}
        doc_types_str = ''
        if doc_types:
            doc_types_str = '/' + ','.join(doc_types)
        path = '/{0}{1}/_warmer/{2}'.format(','.join(indices), doc_types_str, name)

        return self._send_request(method='GET', path=path, params=querystring_args)

    def delete_warmer(self, doc_types=None, indices=None, name=None, querystring_args=None):
        """
        Retrieve warmer

        :param doc_types: list of document types
        :param warmer: anything with ``serialize`` method or a dictionary
        :param name: warmer name. If not provided, all warmers for given indices will be deleted
        :param querystring_args: additional arguments passed as GET params to ES
        """
        name = name or ''
        if not querystring_args:
            querystring_args = {}
        doc_types_str = ''
        if doc_types:
            doc_types_str = '/' + ','.join(doc_types)
        path = '/{0}{1}/_warmer/{2}'.format(','.join(indices), doc_types_str, name)

        return self._send_request(method='DELETE', path=path, params=querystring_args)

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
            info['status'] = self.cluster.status()
            info['aliases'] = self.indices.aliases()
            self.info = info
            return True
        except:
            self.info = {}
            return False

    def index_raw_bulk(self, header, document):
        """
        Function helper for fast inserting

        :param header: a string with the bulk header must be ended with a newline
        :param document: a json document string must be ended with a newline
        """
        self.bulker.add("%s%s" % (header, document))
        return self.flush_bulk()

    def index(self, doc, index, doc_type, id=None, parent=None, force_insert=False,
              op_type=None, bulk=False, version=None, querystring_args=None, ttl=None):
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
            if id is not None:  #None to support 0 as id
                cmd[op_type]['_id'] = id
            if ttl is not None:
                cmd[op_type]['_ttl'] = ttl

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
            if not isinstance(parent, str):
                parent = str(parent)
            querystring_args['parent'] = parent

        if version:
            if not isinstance(version, str):
                version = str(version)
            querystring_args['version'] = version

        if ttl is not None:
            if not isinstance(ttl, str):
                ttl = str(ttl)
            querystring_args['ttl'] = ttl

        if id is None:
            request_method = 'POST'
        else:
            request_method = 'PUT'

        path = make_path(index, doc_type, id)
        return self._send_request(request_method, path, doc, querystring_args)

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

    def update(self, index, doc_type, id, script=None, lang="mvel", params=None, document=None, upsert=None,
               model=None, bulk=False, querystring_args=None, retry_on_conflict=None, routing=None, doc_as_upsert=None):
        if querystring_args is None:
            querystring_args = {}

        body = {}
        if script:
            body.update({"script": script, "lang": lang})
        if params:
            body["params"] = params

        if upsert:
            body["upsert"] = upsert
        if document:
            body["doc"] = document
        if doc_as_upsert is not None:
            body["doc_as_upsert"] = doc_as_upsert

        if bulk:
            cmd = {"update": {"_index": index, "_type": doc_type, "_id": id}}
            if retry_on_conflict:
                cmd["update"]['_retry_on_conflict'] = retry_on_conflict
            if routing:
                cmd["update"]['routing'] = routing
            for arg in ("routing", "percolate", "retry_on_conflict"):
                if arg in querystring_args:
                    cmd["update"]['_%s' % arg] = querystring_args[arg]

            command = "%s\n%s" % (json.dumps(cmd, cls=self.encoder), json.dumps(body, cls=self.encoder))
            self.bulker.add(command)
            return self.flush_bulk()
        else:
            if routing is not None:
                querystring_args['routing'] = routing
            if retry_on_conflict is not None:
                body["retry_on_conflict"] = retry_on_conflict

        path = make_path(index, doc_type, id, "_update")
        model = model or self.model
        return model(self, self._send_request('POST', path, body, querystring_args))

    def update_by_function(self, extra_doc, index, doc_type, id, querystring_args=None,
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

        for attempt in range(attempts - 1, -1, -1):
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

    def partial_update(self, index, doc_type, id, doc=None, script=None, params=None,
                       upsert=None, querystring_args=None):
        """
        Partially update a document with a script
        """
        if querystring_args is None:
            querystring_args = {}

        if doc is None and script is None:
            raise InvalidQuery("script or doc can not both be None")

        if doc is None:
            cmd = {"script": script}
            if params:
                cmd["params"] = params
            if upsert:
                cmd["upsert"] = upsert
        else:
            cmd = {"doc": doc }
        path = make_path(index, doc_type, id, "_update")

        return self._send_request('POST', path, cmd, querystring_args)

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
        path = self._make_path(indices, doc_types, '_query')
        body = {"query": query.serialize()}
        return self._send_request('DELETE', path, body, query_params)

    def exists(self, index, doc_type, id, **query_params):
        """
        Return if a document exists
        """
        path = make_path(index, doc_type, id)
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

    def factory_object(self, index, doc_type, data=None, id=None):
        """
        Create a stub object to be manipulated
        """
        data = data or {}
        obj = self.model()
        obj._meta.index = index
        obj._meta.type = doc_type
        obj._meta.connection = self
        if id:
            obj._meta.id = id
        if data:
            obj.update(data)
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

    def search_raw(self, query, indices=None, doc_types=None, headers=None, **query_params):
        """Execute a search against one or more indices to get the search hits.

        `query` must be a Search object, a Query object, or a custom
        dictionary of search parameters using the query DSL to be passed
        directly.
        """
        from .query import Search, Query

        if isinstance(query, Query):
            query = query.search()
        if isinstance(query, Search):
            query = query.serialize()
        body = self._encode_query(query)
        path = self._make_path(indices, doc_types, "_search")
        return self._send_request('GET', path, body, params=query_params, headers=headers)

    def search_raw_multi(self, queries, indices_list=None, doc_types_list=None,
                         routing_list=None, search_type_list=None):
        if indices_list is None:
            indices_list = [None] * len(queries)

        if doc_types_list is None:
            doc_types_list = [None] * len(queries)

        if routing_list is None:
            routing_list = [None] * len(queries)

        if search_type_list is None:
            search_type_list = [None] * len(queries)

        queries = [query.search() if isinstance(query, Query)
                   else query.serialize() for query in queries]
        queries = list(map(self._encode_query, queries))
        headers = []
        for index_name, doc_type, routing, search_type in zip(indices_list,
                                                              doc_types_list,
                                                              routing_list,
                                                              search_type_list):
            d = {}
            if index_name is not None:
                d['index'] = index_name
            if doc_type is not None:
                d['type'] = doc_type
            if routing is not None:
                d['routing'] = routing
            if search_type is not None:
                d['search_type'] = search_type

            if d:
                headers.append(d)
            else:
                headers.append('')

        headers = [json.dumps(header) for header in headers]

        body = '\n'.join(['%s\n%s' % (h_q[0], h_q[1]) for h_q in zip(headers, queries)])
        body = '%s\n' % body
        path = self._make_path(None, None, '_msearch')

        return body, self._send_request('GET', path, body)

    def search(self, query, indices=None, doc_types=None, model=None, scan=False, headers=None, **query_params):
        """Execute a search against one or more indices to get the resultset.

        `query` must be a Search object, a Query object, or a custom
        dictionary of search parameters using the query DSL to be passed
        directly.
        """
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
                         model=model, query_params=query_params, headers=headers)

    def search_multi(self, queries, indices_list=None, doc_types_list=None,
                     routing_list=None, search_type_list=None, models=None, scans=None):
        searches = [query if isinstance(query, Search) else Search(query) for query in queries]

        return ResultSetMulti(self, searches, indices_list=indices_list,
                              doc_types_list=doc_types_list,
                              routing_list=routing_list, search_type_list=None, models=models)


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

    def suggest_from_object(self, suggest, indices=None, preference=None,
                            routing=None, raw=False, **kwargs):
        indices = self._validate_indices(indices)

        path = make_path(','.join(indices), "_suggest")
        querystring_args = {}
        if routing:
            querystring_args["routing"] = routing
        if preference:
            querystring_args["preference"] = preference

        result = self._send_request('POST', path, suggest.serialize(), querystring_args)
        if raw:
            return result
        return expand_suggest_text(result)


    def suggest(self, name, text, field, type='term', size=None, params=None,
                **kwargs):
        """
        Execute suggester of given type.

        :param name: name for the suggester
        :param text: text to search for
        :param field: field to search
        :param type: One of: completion, phrase, term
        :param size: number of results
        :param params: additional suggester params
        :param kwargs:
        :return:
        """

        from .query import Suggest

        suggest = Suggest()

        suggest.add(text, name, field, type=type, size=size, params=params)

        return self.suggest_from_object(suggest, **kwargs)


    def count(self, query=None, indices=None, doc_types=None, **query_params):
        """
        Execute a query against one or more indices and get hits count.
        """
        from .query import MatchAllQuery

        if query is None:
            query = MatchAllQuery()
        body = {"query": query.serialize()}
        path = self._make_path(indices, doc_types, "_count")
        return self._send_request('GET', path, body, params=query_params)

    #--- river management
    def create_river(self, river, river_name=None):
        """
        Create a river
        """
        if isinstance(river, River):
            body = river.serialize()
            river_name = river.name
        else:
            body = river
        return self._send_request('PUT', '/_river/%s/_meta' % river_name, body)

    def delete_river(self, river, river_name=None):
        """
        Delete a river
        """
        if isinstance(river, River):
            river_name = river.name
        return self._send_request('DELETE', '/_river/%s/' % river_name)

    #--- settings management

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
            mapping = {doc_type: {"_meta": meta}}
            self.indices.put_mapping(doc_type=doc_type, mapping=mapping, indices=indices)

    def morelikethis(self, index, doc_type, id, fields, **query_params):
        """
        Execute a "more like this" search query against one or more fields and get back search hits.
        """
        path = make_path(index, doc_type, id, '_mlt')
        query_params['mlt_fields'] = ','.join(fields)
        body = query_params["body"] if "body" in query_params else None
        return self._send_request('GET', path, body=body, params=query_params)

    def create_percolator(self, index, name, query, **kwargs):
        """
        Create a percolator document

        Any kwargs will be added to the document as extra properties.
        """
        if isinstance(query, Query):
            query = {"query": query.serialize()}
        if not isinstance(query, dict):
            raise InvalidQuery("create_percolator() must be supplied with a Query object or dict")
        if kwargs:
            query.update(kwargs)

        path = make_path(index, '.percolator', name)
        body = json.dumps(query, cls=self.encoder)
        return self._send_request('PUT', path, body)

    def delete_percolator(self, index, name):
        """
        Delete a percolator document
        """
        return self.delete(index, '.percolator', name)

    def percolate(self, index, doc_types, query):
        """
        Match a query with a document
        """
        if doc_types is None:
            raise RuntimeError('percolate() must be supplied with at least one doc_type')

        path = self._make_path(index, doc_types, '_percolate')
        body = self._encode_query(query)
        return self._send_request('GET', path, body)

    def encode_json(self, serializable):
        """
        Serialize to json a serializable object (Search, Query, Filter, etc).
        """
        return json.dumps(serializable.serialize(), cls=self.encoder)

    def _encode_query(self, query):
        from .query import Query

        if isinstance(query, Query):
            query = query.serialize()
        if isinstance(query, dict):
            return json.dumps(query, cls=self.encoder)

        raise InvalidQuery("`query` must be Query or dict instance, not %s"
                           % query.__class__)


class ResultSetList(object):
    def __init__(self, items, model=None):
        """
        results: an es query results dict
        fix_keys: remove the "_" from every key, useful for django views
        clean_highlight: removed empty highlight
        search: a Search object.
        """

        self.items = items
        self.model = model or self.connection.model
        self.iterpos = 0  #keep track of iterator position
        self._current_item = 0

    @property
    def total(self):
        return len(self.items)

    @property
    def facets(self):
        return {}

    def __len__(self):
        return len(self.items)

    def count(self):
        return len(self.items)

    def __getattr__(self, name):
        if name == "facets":
            return {}
        elif name == "hits":
            return self.items

        # elif name in self._results:
        #     #we manage took, timed_out, _shards
        #     return self._results[name]
        #
        # elif name == "shards" and "_shards" in self._results:
        #     #trick shards -> _shards
        #     return self._results["_shards"]
        # return self._results['hits'][name]
        return None

    def __getitem__(self, val):
        if not isinstance(val, (int, long, slice)):
            raise TypeError('%s indices must be integers, not %s' % (
                self.__class__.__name__, val.__class__.__name__))

        def get_start_end(val):
            if isinstance(val, slice):
                start = val.start
                if not start:
                    start = 0
                end = val.stop or len(self.items)
                if end < 0:
                    end = len(self.items) + end
                if end > len(self.items):
                    end = len(self.items)
                return start, end
            return val, val + 1


        start, end = get_start_end(val)

        if not isinstance(val, slice):
            if len(self.items) == 1:
                return self.items[0]
            raise IndexError
        return [hit for hit in self.items[start:end]]


    def __next__(self):

        if len(self.items) == self.iterpos:
            raise StopIteration
        res = self.items[self.iterpos]
        self.iterpos += 1
        return res

    def __iter__(self):
        self.iterpos = 0
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

    if six.PY2:
        next = __next__


class ResultSet(object):
    def __init__(self, connection, search, indices=None, doc_types=None, query_params=None,
                 headers=None, auto_fix_keys=False, auto_clean_highlight=False, model=None):
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
        self.headers = headers
        self.scroller_parameters = {}
        self.scroller_id = None
        self._results = None
        self.model = model or self.connection.model
        self._total = None
        self._max_score = None
        self.valid = False
        self._facets = {}
        self._aggs = {}
        self._hits = []
        self.auto_fix_keys = auto_fix_keys
        self.auto_clean_highlight = auto_clean_highlight

        self.iterpos = 0  #keep track of iterator position
        self.start = query_params.get("start", search.start) or 0
        self._max_item = query_params.get("size", search.size)
        self._current_item = 0
        if search.bulk_read is not None:
            self.chuck_size = search.bulk_read
        elif search.size is not None:
            self.chuck_size = search.size
        else:
            self.chuck_size = 10

    def _do_search(self, auto_increment=False):
        self.iterpos = 0
        process_post_query = True  #used to skip results in first scan
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
            self._post_process_query()

    def _post_process_query(self):
        self._facets = self._results.get('facets', {})
        self._aggs = self._results.get('aggregations', {})
        if 'hits' in self._results:
            self.valid = True
            self._hits = self._results['hits']['hits']
        else:
            self._hits = []
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
    def max_score(self):
        if self._results is None:
            self._do_search()
        if self._max_score is None:
            self._max_score = 1.0
            if self.valid:
                self._max_score = self._results.get("hits", {}).get('max_score', 1.0)
        return self._max_score

    @property
    def facets(self):
        if self._results is None:
            self._do_search()
        return self._facets

    @property
    def aggs(self):
        if self._results is None:
            self._do_search()
        return self._aggs

    def fix_facets(self):
        """
        This function convert date_histogram facets to datetime
        """
        facets = self.facets
        for key in list(facets.keys()):
            _type = facets[key].get("_type", "unknown")
            if _type == "date_histogram":
                for entry in facets[key].get("entries", []):
                    for k, v in list(entry.items()):
                        if k in ["count", "max", "min", "total_count", "mean", "total"]:
                            continue
                        if not isinstance(entry[k], datetime):
                            entry[k] = datetime.utcfromtimestamp(v / 1e3)

    def fix_aggs(self):
        """
        This function convert date_histogram aggs to datetime
        """
        aggs = self.aggs
        for key in list(aggs.keys()):
            _type = aggs[key].get("_type", "unknown")
            if _type == "date_histogram":
                for entry in aggs[key].get("entries", []):
                    for k, v in list(entry.items()):
                        if k in ["count", "max", "min", "total_count", "mean", "total"]:
                            continue
                        if not isinstance(entry[k], datetime):
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
            for key, item in list(hit.items()):
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
                for key, item in list(hl.items()):
                    if not item:
                        del hl[key]

    def __getattr__(self, name):
        if self._results is None:
            self._do_search()
        if name == "facets":
            return self._facets

        elif name == "aggs":
            return self._aggs

        elif name == "hits":
            return self._hits

        elif name in self._results:
            #we manage took, timed_out, _shards
            return self._results[name]

        elif name == "shards" and "_shards" in self._results:
            #trick shards -> _shards
            return self._results["_shards"]
        return self._results['hits'][name]

    def __getitem__(self, val):
        if not isinstance(val, (int, slice)):
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
            if start >= 0 and end <= self.start + self.chuck_size and len(self._results['hits']['hits']) > 0 and \
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

    def __next__(self):
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

    if six.PY2:
        next = __next__


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
                                          doc_types=self.doc_types, headers=self.headers, **query_params)

    def get_suggested_texts(self):
        return expand_suggest_text(self.suggest)


class EmptyResultSet(object):
    def __init__(self, *args, **kwargs):
        """
        An empty resultset
        """


    @property
    def total(self):
        return 0

    @property
    def facets(self):
        return {}

    @property
    def aggs(self):
        return {}

    def __len__(self):
        return self.total

    def count(self):
        return self.total

    def __getitem__(self, val):
        raise IndexError

    def __next__(self):
        raise StopIteration

    def __iter__(self):
        return self


class ResultSetMulti(object):
    def __init__(self, connection, searches, indices_list=None,
                 doc_types_list=None, routing_list=None, search_type_list=None, models=None):
        """
        results: an es query results dict
        fix_keys: remove the "_" from every key, useful for django views
        clean_highlight: removed empty highlight
        search: a Search object.
        """
        for search in searches:
            if not isinstance(search, Search):
                raise InvalidQuery("ResultSet must be supplied with a Search object")

        self.searches = searches
        num_searches = len(self.searches)
        self.connection = connection

        if indices_list is None:
            self.indices_list = [None] * num_searches
        else:
            self.indices_list = indices_list

        if doc_types_list is None:
            self.doc_types_list = [None] * num_searches
        else:
            self.doc_types_list = doc_types_list
        if routing_list is None:
            self.routing_list = [None] * num_searches
        else:
            self.routing_list = routing_list
        if search_type_list is None:
            self.search_type_list = [None] * num_searches
        else:
            self.search_type_list = search_type_list
        self._results_list = None
        self.models = models or self.connection.model
        self._total = None
        self.valid = False
        self.error = None

        self.multi_search_query = None

        self.iterpos = 0
        self._max_item = None

    def _do_search(self):
        self.iterpos = 0

        response = self._search_raw_multi()

        if 'responses' in response:
            responses = response['responses']
            self._results_list = [ResultSet(self.connection, search,
                                            indices=indices, query_params={},
                                            doc_types=doc_types)
                                  for search, indices, doc_types in
                                  zip(self.searches, self.indices_list,
                                      self.doc_types_list)]

            for rs, rsp in zip(self._results_list, responses):
                if 'error' in rsp:
                    rs.error = rsp['error']
                else:
                    rs._results = rsp
                    rs._post_process_query()

            self.valid = True

            self._max_item = len(self._results_list or [])
        else:
            self.error = response

    def _search_raw_multi(self):
        self.multi_search_query, result = self.connection.search_raw_multi(
            self.searches, indices_list=self.indices_list,
            doc_types_list=self.doc_types_list, routing_list=self.routing_list,
            search_type_list=self.search_type_list)

        return result

    def __len__(self):
        if self._results_list is None:
            self._do_search()

        return len(self._results_list or [])

    def __getitem__(self, val):
        if not isinstance(val, (int, slice)):
            raise TypeError('%s indices must be integers, not %s' % (
                self.__class__.__name__, val.__class__.__name__))

        if self._results_list is None:
            self._do_search()

        if isinstance(val, slice):
            return self._results_list[val.start:val.stop]

        return self._results_list[val]

    def __iter__(self):
        self.iterpos = 0

        return self

    def __next__(self):
        if self._results_list is None:
            self._do_search()

        if self._max_item is not None and self.iterpos == self._max_item:
            raise StopIteration

        if self._max_item == 0:
            raise StopIteration

        if self.iterpos < self._max_item:
            res = self._results_list[self.iterpos]
            self.iterpos += 1
            return res

        raise StopIteration

    if six.PY2:
        next = __next__
