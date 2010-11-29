#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro, Robert Eanes, Matt Dennewitz'
__all__ = ['ES', 'file_to_attachment', 'decode_json']

try:
    # For Python < 2.6 or people using a newer version of simplejson
    import json
except ImportError:
    # For Python >= 2.6
    import simplejson as json

import logging
from datetime import date, datetime
import base64
import time
from StringIO import StringIO
from functools import wraps
from decimal import Decimal
import traceback

try:
    from connection import connect as thrift_connect
    from pyesthrift.ttypes import *
    thrift_enable = True
except ImportError:
    from fakettypes import *
    thrift_enable = False
from connection_http import connect as http_connect
log = logging.getLogger('pyes')
from mappings import Mapper

#---- Errors
from pyes.exceptions import IndexMissingException, NotFoundException, SearchPhaseExecutionException, ReplicationShardOperationFailedException, ClusterBlockException

def process_errors(func):
    @wraps(func)
    def _func(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, dict):
            if 'ok' in result:
                return result
            if 'error' in result:
                error = result['error']
                if error.startswith("IndexMissingException"):
                    raise IndexMissingException(error)      
                if error.endswith("] missing"):
                    raise IndexMissingException(error)      
                print "tocheck",error  
        return result
    return _func

def process_error(status, result):
    if isinstance(result, dict):
        if 'ok' in result:
            return result
        if 'error' in result:
            error = result['error']
            if error.startswith("IndexMissingException"):
                raise IndexMissingException(error)      
            if status==400:
                if error.endswith("] missing"):
                    raise NotFoundException(error.split(" ")[0].strip("[]"))
            if status==500:
                if error.startswith("SearchPhaseExecutionException["):
                    raise SearchPhaseExecutionException(error[len("SearchPhaseExecutionException"):].strip("[]"))
                elif error.startswith("ReplicationShardOperationFailedException["):
                    raise ReplicationShardOperationFailedException(error[len("ReplicationShardOperationFailedException"):].strip("[]"))
                elif error.startswith("ClusterBlockException["):
                    raise ClusterBlockException(error[len("ClusterBlockException"):].strip("[]"))
                 
            print "tocheck",error  
    return result

#def process_query_result(func):
#    @wraps(func)
#    def _func(*args, **kwargs):
#        result = func(*args, **kwargs)
#        if 'hits' in result:
##            setattr(result, "total", result['hits']['total'])
#            if 'hits' in result['hits']:
#                for hit in result['hits']['hits']:
#                    for key, item in hit.items():
#                        if key.startswith("_"):
#                            hit[key[1:]]=item
#                            del hit[key]
##        else:
##            setattr(result, "total", 0)
#        return result
#    return _func

def file_to_attachment(filename):
    """
    Convert a file to attachment
    """
#    return base64.b64encode(open(filename, 'rb').read())
    return {'_name':filename,
            'content':base64.b64encode(open(filename, 'rb').read())
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
        if isinstance(obj, basestring) and len(obj)==19:
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
            if isinstance(v, basestring) and len(v)==19:
                try:
                    d[k]=datetime(*time.strptime(v, "%Y-%m-%dT%H:%M:%S")[:6])
                except ValueError:
                    pass
            elif isinstance(v, list):
                d[k] = [self.string_to_datetime(elem) for elem in v]
        return d

class ES(object):
    """
    ES connection object.
    """
    
    def __init__(self, server, timeout=5.0, bulk_size = 400, 
                 encoder= None, decoder = None,
                 max_retries=3):
        """
        Init a es object
        
        server: the server name, it can be a list of servers
        timeout: timeout for a call
        bulk_size: size of bulk operation
        encoder: tojson encoder
        max_retries: number of max retries for server if a server is down
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.cluster = None
        self.debug_dump = False
        self.cluster_name = "undefined"
        self.connection = None
        
        #used in bulk
        self.bulk_size = bulk_size #size of the bulk
        self.bulk_data = StringIO()
        self.bulk_items = 0
        
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
        self.default_indexes = ['_all']
        self._init_connection()


    def __del__(self):
        """
        Destructor
        """
        if self.bulk_items>0:
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
            raise RuntimeError("If you want to use thrift, please install pythrift")
        self.connection = thrift_connect(self.servers, timeout=self.timeout, max_retries=self.max_retries)
        
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
        if body:
            if isinstance(body, dict):
                body = json.dumps(body, cls=self.encoder)
        else:
            body=""
        request = RestRequest(method=Method._NAMES_TO_VALUES[method.upper()], uri=path, parameters=params, headers={}, body=body)
        response = self.connection.execute(request)
        try:
            decoded = json.loads(response.body, cls=self.decoder)
        except:
            traceback.print_exc()
            try:
                decoded = json.loads(response.body, cls=ESJsonDecoder)
            except:
                decoded = response.body
        if response.status!=200:
            process_error(response.status, decoded)
        return  decoded
    
    def _make_path(self, path_components):
        """
        Smush together the path components. Empty components will be ignored.
        """
        path_components = [str(component) for component in path_components if component]
        path = '/'.join(path_components)
        if not path.startswith('/'):
            path = '/'+path
        return path
        
    def _query_call(self, query_type, query, indexes=None, doc_types=None, **query_params):
        """
        This can be used for search and count calls.
        These are identical api calls, except for the type of query.
        """
        querystring_args = query_params
        indexes = self._validate_indexes(indexes)
        if doc_types is None:
            doc_type = []
        body = query
        if hasattr(query, "to_json"):
            body = query.to_json()
        path = self._make_path([','.join(indexes), ','.join(doc_types),query_type])
        response = self._send_request('GET', path, body, querystring_args)
        return response

    def _validate_indexes(self, indexes=None):
        """
        Return a valid list of integers. Allow to use a string or a list of indexers. 
        """
        indexes = indexes or self.default_indexes
        if isinstance(indexes, basestring):
            indexes = [indexes]
        return indexes
            
    #---- Admin commands
    def status(self, indexes=None):
        """
        Retrieve the status of one or more indices
        """
        indexes = self._validate_indexes(indexes)
        path = self._make_path([','.join(indexes), '_status'])
        return self._send_request('GET', path)

    def create_index(self, index, settings=None):
        """
        Creates an index with optional settings.
        Settings must be a dictionary which will be converted to JSON.
        Elasticsearch also accepts yaml, but we are only passing JSON.
        """
        return self._send_request('PUT', index, settings)
        
    def delete_index(self, index):
        """
        Deletes an index.
        """
        return self._send_request('DELETE', index)

    def close_index(self, index):
        """
        Close an index.
        """
        return self._send_request('POST', "/%s/_close"%index)

    def open_index(self, index):
        """
        Open an index.
        """
        return self._send_request('POST', "/%s/_open"%index)
        
    def flush(self, indexes=None, refresh=None):
        """
        Flushes one or more indices (clear memory)
        """
        self.force_bulk()

        indexes = self._validate_indexes(indexes)

        path = self._make_path([','.join(indexes), '_flush'])
        args = {}
        if refresh is not None:
            args['refresh'] = refresh
        return self._send_request('POST', path, params=args)

    def refresh(self, indexes=None):
        """
        Refresh one or more indices
        """
        self.force_bulk()

        indexes = self._validate_indexes(indexes)

        path = self._make_path([','.join(indexes), '_refresh'])
        return self._send_request('POST', path)
        
    def optimize(self, indexes=None, **args):
        """
        Optimize one ore more indices
        """
        indexes = self._validate_indexes(indexes)
        path = self._make_path([','.join(indexes), '_optimize'])
        return self._send_request('POST', path, params=args)

    def gateway_snapshot(self, indexes=None):
        """
        Gateway snapshot one or more indices
        """
        indexes = self._validate_indexes(indexes)
        path = self._make_path([','.join(indexes), '_gateway', 'snapshot'])
        return self._send_request('POST', path)

    def put_mapping(self, doc_type, mapping, indexes):
        """
        Register specific mapping definition for a specific type against one or more indices.
        """
        indexes = self._validate_indexes(indexes)
        path = self._make_path([','.join(indexes), doc_type,"_mapping"])
        if hasattr(mapping, "to_json"):
            mapping = mapping.to_json()
        if doc_type not in mapping:
            mapping = {doc_type:mapping}
        return self._send_request('PUT', path, mapping)

    def get_mapping(self, doc_type=None, indexes=None):
        """
        Register specific mapping definition for a specific type against one or more indices.
        """
        indexes = self._validate_indexes(indexes)
        if doc_type:
            path = self._make_path([','.join(indexes), doc_type,"_mapping"])
        else:
            path = self._make_path([','.join(indexes),"_mapping"])
        result = self._send_request('GET', path)
        #processing indexes
        self.mappings = Mapper(result)
        return result


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
        return self._send_request('GET', "/_cluster/state")

    def cluster_nodes(self, nodes = None):
        """
        Retrieve the node infos
        """
        parts = ["_cluster", "nodes"]
        if nodes:
            parts.append(",".join(nodes))
        path = self._make_path(parts)
        return self._send_request('GET', path)

    def index(self, doc, index, doc_type, id=None, force_insert=False, bulk=False):
        """
        Index a typed JSON document into a specific index and make it searchable.
        """
        if bulk:
            optype = "index"
            if force_insert:
                optype = "create"
            cmd = { optype : { "_index" : index, "_type" : doc_type}}
            if id:
                cmd[optype]['_id'] = id
            self.bulk_data.write(json.dumps(cmd, cls=self.encoder))
            self.bulk_data.write("\n")
            if isinstance(doc, dict):
                doc = json.dumps(doc, cls=self.encoder)
            self.bulk_data.write(doc)
            self.bulk_data.write("\n")
            self.bulk_items += 1
            self.flush_bulk()
            return
            
            
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

    def flush_bulk(self, forced=False):
        """
        Wait to process all pending operations
        """
        if not forced and self.bulk_items < self.bulk_size: 
            return
        self.force_bulk()
        
    def force_bulk(self):
        """
        Force executing of all bulk data
        """
        if self.bulk_items==0:
            return
        self._send_request("POST", "/_bulk", self.bulk_data.getvalue())
        self.bulk_data = StringIO()
        self.bulk_items = 0

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
        
    def delete_mapping(self, index, doc_type):
        """
        Delete a typed JSON document type from a specific index.
        """
        path = self._make_path([index, doc_type])
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
        indexes = self._validate_indexes(indexes)
        if doc_types is None:
            doc_types = []
        if isinstance(doc_types, basestring):
            doc_types = [doc_types]
        if not isinstance(query, basestring):
            if isinstance(query, dict):
                query = json.dumps(query, cls=self.encoder)
            elif hasattr(query, "to_json"):
                query = query.to_json()
                
        return self._query_call("_search", query, indexes, doc_types, **query_params)
        
    def count(self, query, indexes=None, doc_types=None, **query_params):
        """
        Execute a query against one or more indices and get hits count.
        """
        from query import Query
        indexes = self._validate_indexes(indexes)
        if doc_types is None:
            doc_types = []
        if isinstance(query, Query):
            query = query.count()
        return self._query_call("_count", query, indexes, doc_types, **query_params)

    def create_river(self, river, river_name=None):
        """
        Create a river
        """
        if hasattr(river, "q"):
            river_name = river.name
            river = river.q
        return self._send_request('PUT', '/_river/%s/_meta'%river_name, river)

    def delete_river(self, river, river_name=None):
        """
        Delete a river
        """
        if hasattr(river, "q"):
            river_name = river.name
        return self._send_request('DELETE', '/_river/%s/'%river_name)
                    
#    def terms(self, fields, indexes=None, **query_params):
#        """
#        Extract terms and their document frequencies from one or more fields.
#        The fields argument must be a list or tuple of fields.
#        For valid query params see: 
#        http://www.elasticsearch.com/docs/elasticsearch/rest_api/terms/
#        """
#        indexes = self._validate_indexes(indexes)
#        path = self._make_path([','.join(indexes), "_terms"])
#        query_params['fields'] = ','.join(fields)
#        return self._send_request('GET', path, params=query_params)
#    
#    def morelikethis(self, index, doc_type, id, fields, **query_params):
#        """
#        Execute a "more like this" search query against one or more fields and get back search hits.
#        """
#        path = self._make_path([index, doc_type, id, '_mlt'])
#        query_params['fields'] = ','.join(fields)
#        return self._send_request('GET', path, params=query_params)        

def decode_json(data):
    """ Decode some json to dict"""
    return json.loads(data, cls=ESJsonDecoder)

def encode_json(data):
    """ Encode some json to dict"""
    return json.dumps(data, cls=ESJsonEncoder)
    
