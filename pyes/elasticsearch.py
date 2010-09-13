#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro, Robert Eanes, Matt Dennewitz'
__all__ = ['ElasticSearch']
__version__ = (0, 0, 10)

import logging
try:
    # For Python < 2.6 or people using a newer version of simplejson
    import simplejson as json
except ImportError:
    # For Python >= 2.6
    import json

from urlparse import urlsplit
from urllib import urlencode
import logging
from random import randint
import copy
from datetime import date, datetime
from pprint import pprint 
import base64
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.transport import THttpClient
from thrift.protocol import TBinaryProtocol
from pyesthrift import Rest
from pyesthrift.ttypes import *
from connection import *

log = logging.getLogger('pyes')

#---- Errors
class QueryError(Exception):
    def _get_message(self): 
        return self._message
    def _set_message(self, message): 
        self._message = message
    message = property(_get_message, _set_message)
    
def file_to_attachment(filename):
    return {'_name':filename,
            'content':base64.standard_b64encode(open(filename, 'rb').read())
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
        else:
            # use no special encoding and hope for the best
            return value
        
class ElasticSearch(object):
    """
    ElasticSearch connection object.
    """
    
    def __init__(self, server, timeout=5.0):
        """
        Init a elasticsearch object
        
        server: the server name, it can be a list of servers
        debug: if the calls must be debugged
        tracefile: name of the log file
        timeout: timeout for a call

        """
        self.timeout = timeout
        self.cluster = None
        self.debug_dump = False
        self.cluster_name = "undefined"
        self.connection = None
        if isinstance(server, (str, unicode)):
            self.servers = [server]
        else:
            self.servers = server
        self._init_connection()
        
    def _init_connection(self):
        """
        Create initial connection pool
        """
        self.connection = connect(self.servers, timeout=self.timeout)
        
    def _discovery(self):
        """
        Find other servers asking nodes to given server
        """
        data = self.cluster_nodes()
        self.cluster_name = data["cluster_name"]
        for nodename, nodedata in data["nodes"].items():
            server = nodedata['http_address'].replace("]", "").replace("inet[", "http:/")
            if server not in self.servers:
                self.servers.append(server)
        self._init_connection()
        return self.servers

    def _send_request(self, method, path, body=None, params={}):
        if not path.startswith("/"):
            path = "/"+path
        if not self.connection:
            self._init_connection()
        if isinstance(body, dict):
            body = json.dumps(body, cls=ESJsonEncoder)
        if body is None:
            body=""
        request = RestRequest(method=Method._NAMES_TO_VALUES[method.upper()], uri=path, params=params, headers={}, body=body)
        response = self.connection.execute(request)
        return json.loads(response.body)
    
    def _make_path(self, path_components):
        """
        Smush together the path components. Empty components will be ignored.
        """
        path_components = [str(component) for component in path_components if component]
        path = '/'.join(path_components)
        if not path.startswith('/'):
            path = '/'+path
        return path
    
#    def _prep_request(self, body):
#        """
#        Encodes body as json.
#        """
#        return json.dumps(body, cls=ESJsonEncoder)
#        
#    def _prep_response(self, response):
#        """
#        Parses json to a native python object.
#        """
#        response = json.loads(response)
#        if self.debug_dump:
#            print "response.data"
#            pprint(response)
#        return response
        
    def _query_call(self, query_type, query, indexes=['_all'], doc_types=[], **query_params):
        """
        This can be used for search and count calls.
        These are identical api calls, except for the type of query.
        """
        querystring_args = query_params
        body = query
        if hasattr(query, "to_json"):
            body = query.to_json()
        path = self._make_path([','.join(indexes), ','.join(doc_types),query_type])
        response = self._send_request('GET', path, body, querystring_args)
        return response

    #---- Admin commands
    def status(self, indexes=None):
        """
        Retrieve the status of one or more indices
        """
        if indexes is None:
            indexes = ['_all']
        if isinstance(indexes, (str, unicode)):
            path = self._make_path([indexes, '_status'])
        else: 
            path = self._make_path([','.join(indexes), '_status'])
        return self._send_request('GET', path)

    def create_index(self, index, settings=None):
        """
        Creates an index with optional settings.
        Settings must be a dictionary which will be converted to JSON.
        Elasticsearch also accepts yaml, but we are only passing JSON.
        """
        return self._send_request('PUT', index, settings)
        
    def delete_index(self, index, safe_call=True):
        """
        Deletes an index.
        safe_call: if true does not raise an error on missing index
        """
        try:
            res = self._send_request('DELETE', index)
        except QueryError, e:
            if not safe_call:
                raise e
            res = {}
        return res
        
    def flush(self, indexes=None, refresh=None):
        """
        Flushes one or more indices (clear memory)
        """
        if indexes is None:
            indexes = ['_all']
        if isinstance(indexes, (str, unicode)):
            path = self._make_path([indexes, '_flush'])
        else: 
            path = self._make_path([','.join(indexes), '_flush'])
        args = {}
        if refresh is not None:
            args['refresh'] = refresh
        return self._send_request('POST', path, params=args)

    def refresh(self, indexes=None):
        """
        Refresh one or more indices
        """
        if indexes is None:
            indexes = ['_all']
        path = self._make_path([','.join(indexes), '_refresh'])
        return self._send_request('POST', path)
        
    def optimize(self, indexes=None, **args):
        """
        Optimize one ore more indices
        """
        if indexes is None:
            indexes = ['_all']
        path = self._make_path([','.join(indexes), '_optimize'])
        return self._send_request('POST', path, params=args)

    def gateway_snapshot(self, indexes=None):
        """
        Gateway snapshot one or more indices
        """
        if indexes is None:
            indexes = ['_all']
        path = self._make_path([','.join(indexes), '_gateway', 'snapshot'])
        return self._send_request('POST', path)

    def put_mapping(self, doc_type, mapping, indexes=None):
        """
        Register specific mapping definition for a specific type against one or more indices.
        """
        if indexes is None:
            indexes = ['_all']
        path = self._make_path([','.join(indexes), doc_type,"_mapping"])
        if doc_type not in mapping:
            mapping = {doc_type:mapping}
        return self._send_request('PUT', path, mapping)

    def get_mapping(self, doc_type, indexes=None):
        """
        Register specific mapping definition for a specific type against one or more indices.
        """
        if indexes is None:
            indexes = ['_all']
        path = self._make_path([','.join(indexes), doc_type,"_mapping"])
        return self._send_request('GET', path)

    #--- cluster
    def cluster_health(self, indexes=None, level="cluster", wait_for_status=None, 
               wait_for_relocating_shards=None, timeout=30):
        """
        Request Parameters

        The cluster health API accepts the following request parameters:
        - level:                Can be one of cluster, indices or shards. Controls the details 
                                level of the health information returned. Defaults to cluster.
        - wait_for_status       One of green, yellow or red. Will wait (until the timeout provided) 
                                until the status of the cluster changes to the one provided. 
                                By default, will not wait for any status.
        - wait_for_relocating_shards     A number controlling to how many relocating shards to 
                                         wait for. Usually will be 0 to indicate to wait till 
                                         all relocation have happened. Defaults to not to wait.
        - timeout       A time based parameter controlling how long to wait if one of the 
                        wait_for_XXX are provided. Defaults to 30s.
        """
        path = self._make_path(["_cluster", "health"])
        mapping = {}
        if level!="cluster":
            if level not in ["cluster", "indices", "shards"]:
                raise ValueError("Invalid level: %s"%level)
            mapping['level'] = level
        if wait_for_status:
            if wait_for_status not in ["cluster", "indices", "shards"]:
                raise ValueError("Invalid wait_for_status: %s"%wait_for_status)
            mapping['wait_for_status'] = wait_for_status
            
            mapping['timeout'] = "%ds"%timeout
        return self._send_request('GET', path, mapping)

    def cluster_state(self):
        """
        Retrieve the cluster state
        """
        path = self._make_path(["_cluster", "state"])
        return self._send_request('GET', path)

    def cluster_nodes(self, nodes = None):
        """
        Retrieve the node infos
        """
        parts = ["_cluster", "nodes"]
        if nodes:
            parts.append(",".join(nodes))
        path = self._make_path(parts)
        return self._send_request('GET', path)

    def index(self, doc, index, doc_type, id=None, force_insert=False):
        """
        Index a typed JSON document into a specific index and make it searchable.
        """
        if force_insert:
            querystring_args = {'opType':'create'}
        else:
            querystring_args = {}
            
        if id is None:
            request_method = 'POST'
        else:
            request_method = 'PUT'
        path = self._make_path([index, doc_type, id])
        return self._send_request(request_method, path, doc, querystring_args)

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
        
    def delete(self, index, doc_type, id):
        """
        Delete a typed JSON document from a specific index based on its id.
        """
        path = self._make_path([index, doc_type, id])
        return self._send_request('DELETE', path)
        
    def get(self, index, doc_type, id):
        """
        Get a typed JSON document from an index based on its id.
        """
        path = self._make_path([index, doc_type, id])
        return self._send_request('GET', path)
        
    def search(self, query, indexes=None, doc_types=None, **query_params):
        """
        Execute a search query against one or more indices and get back search hits.
        query must be a dictionary or a Query object that will convert to Query DSL
        """
        if indexes is None:
            indexes = ['_all']
        if doc_types is None:
            doc_types = []
        if not isinstance(query, basestring):
            if isinstance(query, dict):
                query = json.dumps(body, cls=ESJsonEncoder)
            elif hasattr(query, "to_json"):
                query = query.to_json()
                
#        if body:
#            body.update(query_params)
#            query_params = {}
        return self._query_call("_search", query, indexes, doc_types, **query_params)
        
    def count(self, query, indexes=None, doc_types=None, **query_params):
        """
        Execute a query against one or more indices and get hits count.
        """
        if indexes is None:
            indexes = ['_all']
        if doc_types is None:
            doc_types = []
        if isinstance(query, Query):
            query = query.count()
        return self._query_call("_count", query, indexes, doc_types, **query_params)
                    
    def terms(self, fields, indexes=None, **query_params):
        """
        Extract terms and their document frequencies from one or more fields.
        The fields argument must be a list or tuple of fields.
        For valid query params see: 
        http://www.elasticsearch.com/docs/elasticsearch/rest_api/terms/
        """
        if indexes is None:
            indexes = ['_all']
        path = self._make_path([','.join(indexes), "_terms"])
        query_params['fields'] = ','.join(fields)
        return self._send_request('GET', path, params=query_params)
    
    def morelikethis(self, index, doc_type, id, fields, **query_params):
        """
        Execute a "more like this" search query against one or more fields and get back search hits.
        """
        path = self._make_path([index, doc_type, id, '_mlt'])
        query_params['fields'] = ','.join(fields)
        return self._send_request('GET', path, params=query_params)        
