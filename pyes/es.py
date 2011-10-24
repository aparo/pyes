#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
import threading

__author__ = 'Alberto Paro'
__all__ = ['ES', 'file_to_attachment', 'decode_json']

try:
    # For Python >= 2.6
    import json
except ImportError:
    # For Python < 2.6 or people using a newer version of simplejson
    import simplejson as json

import logging
from datetime import date, datetime
import base64
import time
from StringIO import StringIO
from decimal import Decimal
from urllib import quote
import copy

try:
    from connection import connect as thrift_connect
    from pyesthrift.ttypes import Method, RestRequest
    thrift_enable = True
except ImportError:
    from fakettypes import Method, RestRequest
    thrift_enable = False

from connection_http import connect as http_connect
log = logging.getLogger('pyes')
from mappings import Mapper

from convert_errors import raise_if_error
from pyes.exceptions import (InvalidParameter,
        ElasticSearchException, IndexAlreadyExistsException,
        IndexMissingException, NotFoundException, InvalidQuery,
        ReduceSearchPhaseException
        )
import collections

#
# models
#

class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)

    __setattr__ = dict.__setitem__

    __delattr__ = dict.__delitem__

    def __deepcopy__(self, memo):
      return DotDict([(copy.deepcopy(k, memo), copy.deepcopy(v, memo)) for k, v in self.items()])

class ElasticSearchModel(DotDict):
    def __init__(self, *args, **kwargs):
        self.meta = DotDict()
        if len(args) == 2 and isinstance(args[0], ES):
            item = args[1]
            self.update(item.pop("_source", DotDict()))
            self.update(item.pop("fields", {}))
            self.meta = DotDict([(k.lstrip("_"), v) for k, v in item.items()])
            self.meta.parent = self.pop("_parent", None) 
            self.meta.connection = args[0]
        else:
            self.update(dict(*args, **kwargs))

    def save(self, bulk=False, id=None, parent=None):
        """
        Save the object and returns id
        """
        meta = self.meta
        conn = meta['connection']
        id = id or meta.get("id")
        parent = parent or meta.get('parent')
        version = meta.get('version')
        res = conn.index(dict([(k, v) for k, v in self.items() if k != "meta"]),
                         meta.index, meta.type, id, parent=parent, bulk=bulk, version=version)
        if not bulk:
            self.meta.id = res._id
            self.meta.version = res._version
            return res._id
        return id

    def get_id(self):
        """ Force the object saveing to get an id"""
        _id = self.meta.get("id", None)
        if _id is None:
            _id = self.save()
        return _id

    def get_bulk(self, create=False):
        """Return bulk code"""
        result = []
        op_type = "index"
        if create:
            op_type = "create"
        meta = self.meta
        cmd = { op_type : { "_index" : meta.index, "_type" : meta.type}}
        if meta.parent:
            cmd[op_type]['_parent'] = meta.parent
        if meta.version:
            cmd[op_type]['_version'] = meta.version
        if meta.id:
            cmd[op_type]['_id'] = meta.id
        result.append(json.dumps(cmd, cls=self.meta.connection.encoder))
        result.append("\n")
        result.append(json.dumps(self.store, cls=self.meta.connection.encoder))
        result.append("\n")
        return ''.join(result)

def file_to_attachment(filename, filehandler=None):
    """
    Convert a file to attachment
    """
    if filehandler:
        return {'_name':filename,
                'content':base64.b64encode(filehandler.read())
                }
    with open(filename, 'rb') as _file:
        return {'_name':filename,
                'content':base64.b64encode(_file.read())
                }

class ESJsonEncoder(json.JSONEncoder):
    def default(self, value):
        """Convert rogue and mysterious data types.
        Conversion notes:
        
        - ``datetime.date`` and ``datetime.datetime`` objects are
        converted into datetime strings.
        """

        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%dT%H:%M:%S")
        elif isinstance(value, date):
            dt = datetime(value.year, value.month, value.day, 0, 0, 0)
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
        elif isinstance(value, Decimal):
            return float(str(value))
        else:
            # use no special encoding and hope for the best
            return value

class ESJsonDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        kwargs['object_hook'] = self.dict_to_object
        json.JSONDecoder.__init__(self, *args, **kwargs)

    def string_to_datetime(self, obj):
        """Decode a datetime string to a datetime object
        """
        if isinstance(obj, basestring) and len(obj) == 19:
            try:
                return datetime(*obj.strptime("%Y-%m-%dT%H:%M:%S")[:6])
            except:
                pass
        return obj

    def dict_to_object(self, d):
        """
        Decode datetime value from string to datetime
        """
        for k, v in d.items():
            if isinstance(v, basestring) and len(v) == 19:
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

    def __init__(self, server="localhost:9200", timeout=5.0, bulk_size=400,
                 encoder=None, decoder=None,
                 max_retries=3, autorefresh=False,
                 default_indices=['_all'],
                 default_types=None,
                 dump_curl=False,
                 model=ElasticSearchModel):
        """
        Init a es object
        
        server: the server name, it can be a list of servers
        timeout: timeout for a call
        bulk_size: size of bulk operation
        encoder: tojson encoder
        max_retries: number of max retries for server if a server is down
        autorefresh: check if need a refresh before a query
        model: used to objectify the dictinary. If None, the raw dict is returned.

        dump_curl: If truthy, this will dump every query to a curl file.  If
        this is set to a string value, it names the file that output is sent
        to.  Otherwise, it should be set to an object with a write() method,
        which output will be written to.

        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.cluster = None
        self.debug_dump = False
        self.cluster_name = "undefined"
        self.connection = None
        self.autorefresh = autorefresh
        self.refreshed = True

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
        self.bulk_size = bulk_size #size of the bulk
        self.bulk_data = []
        self.last_bulk_response = None #last response of a bulk insert
        self.bulk_lock = threading.Lock()

        self.info = {} #info about the current server
        self.mappings = None #track mapping
        self.encoder = encoder
        if self.encoder is None:
            self.encoder = ESJsonEncoder
        self.decoder = decoder
        if self.decoder is None:
            self.decoder = ESJsonDecoder
        if isinstance(server, (str, unicode)):
            self.servers = [server]
        else:
            self.servers = server
        self.default_indices = default_indices
        self.default_types = default_types or []
        self._init_connection()

    def __del__(self):
        """
        Destructor
        """
        if len(self.bulk_data) > 0:
            self.flush()

    def _init_connection(self):
        """
        Create initial connection pool
        """
        #detect connectiontype
        port = self.servers[0].split(":")[1]
        if port.startswith("92"):
            self.connection = http_connect(self.servers, timeout=self.timeout, max_retries=self.max_retries)
            return
        if not thrift_enable:
            raise RuntimeError("If you want to use thrift, please install thrift. \"pip install thrift\"")
        self.connection = thrift_connect(self.servers, timeout=self.timeout, max_retries=self.max_retries)

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

    def _send_request(self, method, path, body=None, params=None, headers=None):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        # prepare the request
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
            if response.status != 200:
                return False
            return True

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
        if isinstance(decoded, dict):
            decoded = DotDict(decoded)
        return  decoded

    def _make_path(self, path_components):
        """
        Smush together the path components. Empty components will be ignored.
        """
        path_components = [quote(str(component), "") for component in path_components if component]
        path = '/'.join(path_components)
        if not path.startswith('/'):
            path = '/' + path
        return path

    def _query_call(self, query_type, query, indices=None, doc_types=None, **query_params):
        """
        This can be used for search and count calls.
        These are identical api calls, except for the type of query.
        """
        if self.autorefresh and self.refreshed == False:
            self.refresh(indices)
        querystring_args = query_params
        indices = self._validate_indices(indices)
        if doc_types is None:
            doc_types = self.default_types
        if isinstance(doc_types, basestring):
            doc_types = [doc_types]
        body = query
        path = self._make_path([','.join(indices), ','.join(doc_types), query_type])
        return self._send_request('GET', path, body, params=querystring_args)

    def _validate_indices(self, indices=None):
        """Return a valid list of indices.

        `indices` may be a string or a list of strings.
        If `indices` is not supplied, returns the default_indices.

        """
        indices = indices or self.default_indices
        if isinstance(indices, basestring):
            indices = [indices]
        return indices

    def _dump_curl_request(self, request):
        self.dump_curl.write("# [%s]\n" % datetime.now().isoformat())
        self.dump_curl.write("curl -X" + Method._VALUES_TO_NAMES[request.method])
        self.dump_curl.write(" http://" + self.servers[0] + request.uri)
        if request.body:
            self.dump_curl.write(" -d \"%s\"" % request.body.replace('"', '\\"'))
        self.dump_curl.write("\n")

    #---- Admin commands
    def status(self, indices=None):
        """
        Retrieve the status of one or more indices
        """
        if not indices:
            indices = ["_all"]
#        indices = self._validate_indices(indices)
        path = self._make_path([','.join(indices), '_status'])
        return self._send_request('GET', path)

    def create_index(self, index, settings=None):
        """
        Creates an index with optional settings.
        Settings must be a dictionary which will be converted to JSON.
        Elasticsearch also accepts yaml, but we are only passing JSON.
        """
        return self._send_request('PUT', index, settings)

    def create_index_if_missing(self, index, settings=None):
        """Creates an index if it doesn't already exist.

        If supplied, settings must be a dictionary.

        """
        try:
            return self.create_index(index, settings)
        except IndexAlreadyExistsException, e:
            return e.result

    def delete_index(self, index):
        """Deletes an index.
        """
        return self._send_request('DELETE', index)

    def exists_index(self, index):
        """
        Check if an index exists.
        """
        return self._send_request('HEAD', index)

    def delete_index_if_exists(self, index):
        """Deletes an index if it exists.

        """
        try:
            return self.delete_index(index)
        except IndexMissingException:
            pass
        except NotFoundException, e:
            return e.result

    def get_indices(self, include_aliases=False):
        """Get a dict holding an entry for each index which exists.

        If include_alises is True, the dict will also contain entries for
        aliases.

        The key for each entry in the dict is the index or alias name.  The
        value is a dict holding the following properties:

         - num_docs: Number of documents in the index or alias.
         - alias_for: Only present for an alias: holds a list of indices which
           this is an alias for.

        """
        state = self.cluster_state()
        status = self.status()
        result = {}
        indices_status = status['indices']
        indices_metadata = state['metadata']['indices']
        for index in sorted(indices_status.keys()):
            info = indices_status[index]
            metadata = indices_metadata[index]
            num_docs = info['docs']['num_docs']
            result[index] = dict(num_docs=num_docs)
            if not include_aliases:
                continue
            for alias in metadata.get('aliases', []):
                try:
                    alias_obj = result[alias]
                except KeyError:
                    alias_obj = {}
                    result[alias] = alias_obj
                alias_obj['num_docs'] = alias_obj.get('num_docs', 0) + num_docs
                try:
                    alias_obj['alias_for'].append(index)
                except KeyError:
                    alias_obj['alias_for'] = [index]
        return result

    def get_closed_indices(self):
        """
        Get all closed indices.
        """
        state = self.cluster_state()
        status = self.status()

        indices_metadata = set(state['metadata']['indices'].keys())
        indices_status = set(status['indices'].keys())

        return indices_metadata.difference(indices_status)

    def get_alias(self, alias):
        """Get the index or indices pointed to by a given alias.

        Raises IndexMissingException if the alias does not exist.

        Otherwise, returns a list of index names.

        """
        status = self.status(alias)
        return status['indices'].keys()

    def change_aliases(self, commands):
        """Change the aliases stored.

        `commands` is a list of 3-tuples; (command, index, alias), where
        `command` is one of "add" or "remove", and `index` and `alias` are the
        index and alias to add or remove.

        """
        body = {
            'actions': [
                 {command: dict(index=index, alias=alias) }
                 for (command, index, alias) in commands
            ]
        }
        return self._send_request('POST', "_aliases", body)

    def add_alias(self, alias, indices):
        """Add an alias to point to a set of indices.

        """
        indices = self._validate_indices(indices)
        return self.change_aliases(['add', index, alias]
                                   for index in indices)

    def delete_alias(self, alias, indices):
        """Delete an alias.

        The specified index or indices are deleted from the alias, if they are
        in it to start with.  This won't report an error even if the indices
        aren't present in the alias.

        """
        indices = self._validate_indices(indices)
        return self.change_aliases(['remove', index, alias]
                                   for index in indices)

    def set_alias(self, alias, indices):
        """Set an alias.

        This handles removing the old list of indices pointed to by the alias.

        Warning: there is a race condition in the implementation of this
        function - if another client modifies the indices which this alias
        points to during this call, the old value of the alias may not be
        correctly set.

        """
        indices = self._validate_indices(indices)
        try:
            old_indices = self.get_alias(alias)
        except IndexMissingException:
            old_indices = []
        commands = [['remove', index, alias] for index in old_indices]
        commands.extend([['add', index, alias] for index in indices])
        if len(commands) > 0:
            return self.change_aliases(commands)

    def close_index(self, index):
        """
        Close an index.
        """
        return self._send_request('POST', "/%s/_close" % index)

    def open_index(self, index):
        """
        Open an index.
        """
        return self._send_request('POST', "/%s/_open" % index)

    def flush(self, indices=None, refresh=None):
        """
        Flushes one or more indices (clear memory)
        """
        self.force_bulk()

        indices = self._validate_indices(indices)

        path = self._make_path([','.join(indices), '_flush'])
        args = {}
        if refresh is not None:
            args['refresh'] = refresh
        return self._send_request('POST', path, params=args)

    def refresh(self, indices=None, timesleep=1):
        """
        Refresh one or more indices
        
        timesleep: seconds to wait
        """
        self.force_bulk()
        indices = self._validate_indices(indices)

        path = self._make_path([','.join(indices), '_refresh'])
        result = self._send_request('POST', path)
        time.sleep(timesleep)
        self.cluster_health(wait_for_status='green')
        self.refreshed = True
        return result


    def optimize(self, indices=None,
                 wait_for_merge=False,
                 max_num_segments=None,
                 only_expunge_deletes=False,
                 refresh=True,
                 flush=True):
        """Optimize one or more indices.

        `indices` is the list of indices to optimise.  If not supplied, or
        "_all", all indices are optimised.

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
        indices = self._validate_indices(indices)
        path = self._make_path([','.join(indices), '_optimize'])
        params = dict(
            wait_for_merge=wait_for_merge,
            only_expunge_deletes=only_expunge_deletes,
            refresh=refresh,
            flush=flush,
        )
        if max_num_segments is not None:
            params['max_num_segments'] = max_num_segments
        result = self._send_request('POST', path, params=params)
        self.refreshed = True
        return result

    def analyze(self, text, index=None):
        """
        Performs the analysis process on a text and return the tokens breakdown of the text
        """
        path = self._make_path([index, '_analyze'])
        return self._send_request('POST', path, text)

    def gateway_snapshot(self, indices=None):
        """
        Gateway snapshot one or more indices
        """
        indices = self._validate_indices(indices)
        path = self._make_path([','.join(indices), '_gateway', 'snapshot'])
        return self._send_request('POST', path)

    def put_mapping(self, doc_type=None, mapping=None, indices=None):
        """
        Register specific mapping definition for a specific type against one or more indices.
        """
        indices = self._validate_indices(indices)
        if mapping is None:
            mapping = {}
        if hasattr(mapping, "to_json"):
            mapping = mapping.to_json()

        if doc_type:
            path = self._make_path([','.join(indices), doc_type, "_mapping"])
            if doc_type not in mapping:
                mapping = {doc_type:mapping}
        else:
            path = self._make_path([','.join(indices), "_mapping"])

        self.refreshed = False
        return self._send_request('PUT', path, mapping)

    def get_mapping(self, doc_type=None, indices=None):
        """
        Register specific mapping definition for a specific type against one or more indices.
        """
        indices = self._validate_indices(indices)
        if doc_type:
            path = self._make_path([','.join(indices), doc_type, "_mapping"])
        else:
            path = self._make_path([','.join(indices), "_mapping"])
        return self._send_request('GET', path)

    def collect_info(self):
        """
        Collect info about the connection and fill the info dictionary
        """
        self.info = {}
        res = self._send_request('GET', "/")
        self.info['server'] = {}
        self.info['server']['name'] = res['name']
        self.info['server']['version'] = res['version']
        self.info['allinfo'] = res
        self.info['status'] = self.status(["_all"])
        return self.info

    #--- cluster
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
        path = self._make_path(["_cluster", "health"])
        mapping = {}
        if level != "cluster":
            if level not in ["cluster", "indices", "shards"]:
                raise ValueError("Invalid level: %s" % level)
            mapping['level'] = level
        if wait_for_status:
            if wait_for_status not in ["green", "yellow", "red"]:
                raise ValueError("Invalid wait_for_status: %s" % wait_for_status)
            mapping['wait_for_status'] = wait_for_status

            mapping['timeout'] = "%ds" % timeout
        return self._send_request('GET', path, mapping)

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
        path = self._make_path(["_cluster", "state"])
        parameters = {}

        if filter_nodes is not None:
            parameters['filter_nodes'] = filter_nodes

        if filter_routing_table is not None:
            parameters['filter_routing_table'] = filter_routing_table

        if filter_metadata is not None:
            parameters['filter_metadata'] = filter_metadata

        if filter_blocks is not None:
            parameters['filter_blocks'] = filter_blocks

        if filter_blocks is not None:
            if isinstance(filter_indices, basestring):
                parameters['filter_indices'] = filter_indices
            else:
                parameters['filter_indices'] = ",".join(filter_indices)

        return self._send_request('GET', path, params=parameters)

    def cluster_nodes(self, nodes=None):
        """
        The cluster :ref:`nodes info <es-guide-reference-api-admin-cluster-state>` API allows to retrieve one or more (or all) of 
        the cluster nodes information.
        """
        parts = ["_cluster", "nodes"]
        if nodes:
            parts.append(",".join(nodes))
        path = self._make_path(parts)
        return self._send_request('GET', path)

    def cluster_stats(self, nodes=None):
        """
        The cluster :ref:`nodes info <es-guide-reference-api-admin-cluster-nodes-stats>` API allows to retrieve one or more (or all) of 
        the cluster nodes information.
        """
        parts = ["_cluster", "nodes", "stats"]
        if nodes:
            parts = ["_cluster", "nodes", ",".join(nodes), "stats"]

        path = self._make_path(parts)
        return self._send_request('GET', path)

    def index_raw_bulk(self, header, document):
        """
        Function helper for fast inserting

        header and document must be string "\n" ended
        """
        self.bulk_data.append("%s%s" % (header, document))
        return self.flush_bulk()

    def index(self, doc, index, doc_type, id=None, parent=None,
              force_insert=False,
              op_type=None,
              bulk=False, version=None, querystring_args=None):
        """
        Index a typed JSON document into a specific index and make it searchable.
        """
        if querystring_args is None:
            querystring_args = {}

        self.refreshed = False

        if bulk:
            if op_type is None:
                op_type = "index"
            op_type = "index"
            if force_insert:
                op_type = "create"
            cmd = { op_type : { "_index" : index, "_type" : doc_type}}
            if parent:
                cmd[op_type]['_parent'] = parent
            if version:
                cmd[op_type]['_version'] = version
            if 'routing' in querystring_args:
                cmd[op_type]['_routing'] = querystring_args['routing']
            if 'percolate' in querystring_args:
                cmd[op_type]['percolate'] = querystring_args['percolate']
            if id:
                cmd[op_type]['_id'] = id

            if isinstance(doc, dict):
                doc = json.dumps(doc, cls=self.encoder)
            command = "%s\n%s" % (json.dumps(cmd, cls=self.encoder), doc)
            self.bulk_data.append(command)
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

        path = self._make_path([index, doc_type, id])
        return self._send_request(request_method, path, doc, querystring_args)

    def flush_bulk(self, forced=False):
        """
        Wait to process all pending operations
        """
        if not forced and len(self.bulk_data) < self.bulk_size:
            return None
        return self.force_bulk()

    def force_bulk(self):
        """
        Force executing of all bulk data.
        
        Return the bulk response
        
        If not item self.last_bulk_response to None and returns None
        """
        locked = self.bulk_lock.acquire(False)
        if locked:
            try:
                if len(self.bulk_data):
                    batch = self.bulk_data
                    self.bulk_data = []
                    self.last_bulk_response = self._send_request("POST", "/_bulk", "\n".join(batch) + "\n")
                else:
                    self.last_bulk_response = None
            finally:
              self.bulk_lock.release()
        return self.last_bulk_response

    def put_file(self, filename, index, doc_type, id=None):
        """
        Store a file in a index
        """
        querystring_args = {}

        if id is None:
            request_method = 'POST'
        else:
            request_method = 'PUT'
        path = self._make_path([index, doc_type, id])
        doc = file_to_attachment(filename)
        return self._send_request(request_method, path, doc, querystring_args)

    def get_file(self, index, doc_type, id=None):
        """
        Return the filename and memory data stream
        """
        data = self.get(index, doc_type, id)
        return data["_source"]['_name'], base64.standard_b64decode(data["_source"]['content'])

    def delete(self, index, doc_type, id, bulk=False, querystring_args=None):
        """
        Delete a typed JSON document from a specific index based on its id.
        If bulk is True, the delete operation is put in bulk mode.
        """
        querystring_args = querystring_args or {}
        if bulk:
            cmd = { "delete" : { "_index" : index, "_type" : doc_type,
                                "_id": id}}
            self.bulk_data.append(json.dumps(cmd, cls=self.encoder))
            self.flush_bulk()
            return

        path = self._make_path([index, doc_type, id])
        return self._send_request('DELETE', path, params=querystring_args)

    def deleteByQuery(self, indices, doc_types, query, **request_params):
        """
        Delete documents from one or more indices and one or more types based on a query.
        """
        querystring_args = request_params
        indices = self._validate_indices(indices)
        if doc_types is None:
            doc_types = []
        if isinstance(doc_types, basestring):
            doc_types = [doc_types]

        if hasattr(query, 'to_query_json'):
            # Then is a Query object.
            body = query.to_query_json()
        elif isinstance(query, dict):
            # A direct set of search parameters.
            body = json.dumps(query, cls=self.encoder)
        else:
            raise InvalidQuery("deleteByQuery() must be supplied with a Query object, or a dict")

        path = self._make_path([','.join(indices), ','.join(doc_types), '_query'])
        return self._send_request('DELETE', path, body, querystring_args)

    def delete_mapping(self, index, doc_type):
        """
        Delete a typed JSON document type from a specific index.
        """
        path = self._make_path([index, doc_type])
        return self._send_request('DELETE', path)

    def get(self, index, doc_type, id, fields=None, routing=None, **get_params):
        """
        Get a typed JSON document from an index based on its id.
        """
        path = self._make_path([index, doc_type, id])
        if fields is not None:
            get_params["fields"] = ",".join(fields)
        if routing:
            get_params["routing"] = routing
        return self.model(self, self._send_request('GET', path, params=get_params))


    def factory_object(self, index, doc_type, data=None, id=None, vertex=False):
        """
        Create a stub object to be manipulated
        """
        data = data or {}
        obj = ElasticSearchModel()
        obj.meta.index = index
        obj.meta.type = doc_type
        obj.meta.connection = self
        if id:
            obj.meta.id = id
        if data:
            obj.update(data)
        if vertex:
            obj.force_vertex()
        return obj

    def mget(self, ids, index=None, doc_type=None, routing=None, **get_params):
        """
        Get multi JSON documents.
        
        ids can be:
            list of tuple: (index, type, id)
            list of ids: index and doc_type are required
        
        """
        if len(ids) == 0:
            return []

        body = []
        for value in ids:
            if isinstance(value, tuple):
                a, b, c = value
                body.append({"_index":a,
                             "_type":b,
                             "_id":c})
            else:
                if index is None:
                    raise InvalidQuery("index value is required for id")
                if doc_type is None:
                    raise InvalidQuery("doc_type value is required for id")
                body.append({"_index":index,
                             "_type":doc_type,
                             "_id":value})

        if routing:
            get_params["routing"] = routing
        results = self._send_request('GET', "/_mget",
                                  body={'docs':body},
                                  params=get_params)
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
        indices = self._validate_indices(indices)
        if doc_types is None:
            doc_types = []
        elif isinstance(doc_types, basestring):
            doc_types = [doc_types]

        if hasattr(query, 'to_search_json'):
            # Common case - a Search or Query object.
            body = query.to_search_json()
        elif isinstance(query, dict):
            # A direct set of search parameters.
            body = json.dumps(query, cls=self.encoder)
        else:
            raise InvalidQuery("search() must be supplied with a Search or Query object, or a dict")

        return self._query_call("_search", body, indices, doc_types, **query_params)

    def search(self, query, indices=None, doc_types=None, **query_params):
        """Execute a search against one or more indices to get the resultset.

        `query` must be a Search object, a Query object, or a custom
        dictionary of search parameters using the query DSL to be passed
        directly.

        """
        indices = self._validate_indices(indices)
        if doc_types is None:
            doc_types = []
        elif isinstance(doc_types, basestring):
            doc_types = [doc_types]
        if hasattr(query, 'search'):
            query = query.search()

        if hasattr(query, 'to_search_json') or isinstance(query, dict):
            pass
        else:
            raise InvalidQuery("search() must be supplied with a Search or Query object, or a dict")
        return ResultSet(connection=self, query=query, indices=indices, doc_types=doc_types, query_params=query_params)

#    scan method is no longer working due to change in ES.search behavior.  May no longer warrant its own method.
#    def scan(self, query, indices=None, doc_types=None, scroll_timeout="10m", **query_params):
#        """Return a generator which will scan against one or more indices and iterate over the search hits. (currently support only by ES Master)
#
#        `query` must be a Search object, a Query object, or a custom
#        dictionary of search parameters using the query DSL to be passed
#        directly.
#
#        """
#        results = self.search(query=query, indices=indices, doc_types=doc_types, search_type="scan", scroll=scroll_timeout, **query_params)
#        while True:
#            scroll_id = results["_scroll_id"]
#            results = self._send_request('GET', "_search/scroll", scroll_id, {"scroll":scroll_timeout})
#            total = len(results["hits"]["hits"])
#            if not total:
#                break
#            yield results

    def search_scroll(self, scroll_id, scroll_timeout="10m"):
        """
        Executes a scrolling given an scroll_id
        """
        return self._send_request('GET', "_search/scroll", scroll_id, {"scroll":scroll_timeout})

    def reindex(self, query, indices=None, doc_types=None, **query_params):
        """
        Execute a search query against one or more indices and and reindex the hits.
        query must be a dictionary or a Query object that will convert to Query DSL.
        Note: reindex is only available in my ElasticSearch branch on github.
        """
        indices = self._validate_indices(indices)
        if doc_types is None:
            doc_types = []
        if isinstance(doc_types, basestring):
            doc_types = [doc_types]
        if not isinstance(query, basestring):
            if isinstance(query, dict):
                if 'query' in query:
                    query = query['query']
                query = json.dumps(query, cls=self.encoder)
            elif hasattr(query, "to_query_json"):
                query = query.to_query_json(inner=True)
        querystring_args = query_params
        indices = self._validate_indices(indices)
        body = query
        path = self._make_path([','.join(indices), ','.join(doc_types), "_reindexbyquery"])
        return self._send_request('POST', path, body, querystring_args)

    def count(self, query, indices=None, doc_types=None, **query_params):
        """
        Execute a query against one or more indices and get hits count.
        """
        indices = self._validate_indices(indices)
        if doc_types is None:
            doc_types = []
        if hasattr(query, 'to_query_json'):
            query = query.to_query_json()
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
    def update_settings(self, index, newvalues):
        """
        Update Settings of an index.
        
        """
        path = self._make_path([index, "_settings"])
        return self._send_request('PUT', path, newvalues)

#    def terms(self, fields, indices=None, **query_params):
#        """
#        Extract terms and their document frequencies from one or more fields.
#        The fields argument must be a list or tuple of fields.
#        For valid query params see: 
#        http://www.elasticsearch.com/docs/elasticsearch/rest_api/terms/
#        """
#        indices = self._validate_indices(indices)
#        path = self._make_path([','.join(indices), "_terms"])
#        query_params['fields'] = ','.join(fields)
#        return self._send_request('GET', path, params=query_params)
#    
    def morelikethis(self, index, doc_type, id, fields, **query_params):
        """
        Execute a "more like this" search query against one or more fields and get back search hits.
        """
        path = self._make_path([index, doc_type, id, '_mlt'])
        query_params['fields'] = ','.join(fields)
        body = query_params["body"] if query_params.has_key("body") else None
        return self._send_request('GET', path, body=body, params=query_params)

    def create_percolator(self, index, name, query, **kwargs):
        """
        Create a percolator document

        Any kwargs will be added to the document as extra properties.

        """
        path = self._make_path(['_percolator', index, name])

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
        elif not isinstance(doc_types, list):
            doc_types = [doc_types]

        path = self._make_path([index, ','.join(doc_types), '_percolate'])
        body = None

        if hasattr(query, 'to_query_json'):
            # Then is a Query object.
            body = query.to_query_json()
        elif isinstance(query, dict):
            # A direct set of search parameters.
            body = json.dumps(query, cls=self.encoder)
        else:
            raise InvalidQuery("percolate() must be supplied with a Query object, or a dict")

        return self._send_request('GET', path, body=body)

def decode_json(data):
    """ Decode some json to dict"""
    return json.loads(data, cls=ESJsonDecoder)

def encode_json(data):
    """ Encode some json to dict"""
    return json.dumps(data, cls=ESJsonEncoder)

class ResultSet(object):
    def __init__(self, connection, query, indices=None, doc_types=None, query_params=None,
                 auto_fix_keys=False, auto_clean_highlight=False):
        """
        results: an es query results dict
        fix_keys: remove the "_" from every key, useful for django views
        clean_highlight: removed empty highlight
        query can be a dict or a Search object.
        """
        self.connection = connection
        self.indices = indices
        self.doc_types = doc_types
        self.query_params = query_params or {}
        self.scroller_parameters = {}
        self.scroller_id = None
        self._results = None
        self._total = None
        self.valid = False
        self._facets = {}
        self.auto_fix_keys = auto_fix_keys
        self.auto_clean_highlight = auto_clean_highlight

        from pyes.query import Search, Query

        if not isinstance(query, (Query, Search, dict)):
            raise InvalidQuery("search() must be supplied with a Search or Query object, or a dict")

        if not isinstance(query, Search):
            self.query = Search(query)
        else:
            self.query = query

        self.iterpos = 0 #keep track of iterator position
        self.start = self.query.start or 0
        self.chuck_size = self.query.size or 10

    def _do_search(self, auto_increment=False):
        self.iterpos = 0
        process_post_query = True #used to skip results in first scan
        if self.scroller_id is None:
            if auto_increment:
                self.start += self.chuck_size

            self.query.start = self.start
            self.query.size = self.chuck_size

            self._results = self.connection.search_raw(self.query, indices=self.indices,
                                                       doc_types=self.doc_types, **self.query_params)
            if 'search_type' in self.query_params and self.query_params['search_type'] == "scan":
                self.scroller_parameters['search_type'] = self.query_params['search_type']
                del self.query_params['search_type']
                if 'scroll' in self.query_params:
                    self.scroller_parameters['scroll'] = self.query_params['scroll']
                    del self.query_params['scroll']
                if 'size' in self.query_params:
                    self.scroller_parameters['size'] = self.query_params['size']
                    del self.query_params['size']
                    self.chuck_size = self.scroller_parameters['size']
            if '_scroll_id' in self._results:
                #scan query, let's load the first bulk of data
                self.scroller_id = self._results['_scroll_id']
                self._do_search()
                process_post_query = False
        else:
            try:
                self._results = self.connection.search_scroll(self.scroller_id, self.scroller_parameters.get("scroll", "10m"))
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

    def __len__(self):
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
                else:
                    start -= 1
                end = val.stop or self.total
                if end < 0:
                    end = self.total + end
                return start, end
            return val, val + 1

        start, end = get_start_end(val)
        model = self.connection.model

        if self._results:
            if start >= self.start and end < self.start + self.chuck_size:
                if not isinstance(val, slice):
                    return model(self.connection, self._results['hits']['hits'][val - self.start])
                else:
                    return [model(self.connection, hit) for hit in self._results['hits']['hits'][start:end]]


        query = self.query.serialize()
        query['from'] = start
        query['size'] = end - start

        results = self.connection.search_raw(query, indices=self.indices,
                        doc_types=self.doc_types, **self.query_params)

        hits = results['hits']['hits']
        if not isinstance(val, slice):
            if len(hits) == 1:
                return model(self.connection, hits[0])
            raise IndexError
        return [model(self.connection, hit) for hit in hits]

    def next(self):
        if self._results is None:
            self._do_search()
        if len(self.hits) == 0:
            raise StopIteration
        if self.iterpos < len(self.hits):
            res = self.hits[self.iterpos]
            self.iterpos += 1
            return self.connection.model(self.connection, res)

        if self.iterpos == self.total:
            raise StopIteration
        self._do_search(auto_increment=True)
        self.iterpos = 0
        if len(self.hits) == 0:
            raise StopIteration
        res = self.hits[self.iterpos]
        self.iterpos += 1
        return self.connection.model(self.connection, res)

    def __iter__(self):
        self.iterpos = 0
        self.start = 0
        self._results = None
        return self
