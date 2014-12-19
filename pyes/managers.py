#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from .exceptions import IndexAlreadyExistsException, IndexMissingException
from .utils import make_path
from .filters import Filter
from .mappings import Mapper
import six

class Indices(object):
    alias_params = ['filter', 'routing', 'search_routing', 'index_routing']

    def __init__(self, conn):
        self.conn = conn

    #TODO: clearcache segments templates

    #Alias Management - START
    def aliases(self, indices=None):
        """
        Retrieve the aliases of one or more indices.
        ( See :ref:`es-guide-reference-api-admin-indices-aliases`)

        :keyword indices: an index or a list of indices

        """
        path = self.conn._make_path(indices, (), '_aliases')
        return self.conn._send_request('GET', path)

    def get_alias(self, alias):
        """
        Get the index or indices pointed to by a given alias.
        (See :ref:`es-guide-reference-api-admin-indices-aliases`)

        :param alias: the name of an alias

        :return returns a list of index names.
        :raise IndexMissingException if the alias does not exist.

        """
        status = self.status([alias])
        return status['indices'].keys()

    def change_aliases(self, commands):
        """
        Change the aliases stored.
        (See :ref:`es-guide-reference-api-admin-indices-aliases`)

        :param commands: is a list of 3-tuples; (command, index, alias), where
                         `command` is one of "add" or "remove", and `index` and
                         `alias` are the index and alias to add or remove.

        """
        body = {'actions': [{command: dict(index=index, alias=alias, **params)}
                            for (command, index, alias, params) in commands]}
        return self.conn._send_request('POST', "_aliases", body)

    def _get_alias_params(self, **kwargs):
        ret = {}
        for name, value in kwargs.items():
            if name in self.alias_params and value:
                if isinstance(value, Filter):
                    ret[name] = value.serialize()
                else:
                    ret[name] = value

        return ret

    def add_alias(self, alias, indices, **kwargs):
        """
        Add an alias to point to a set of indices.
        (See :ref:`es-guide-reference-api-admin-indices-aliases`)

        :param alias: the name of an alias
        :param indices: a list of indices

        """
        indices = self.conn._validate_indices(indices)

        return self.change_aliases(['add', index, alias,
                                    self._get_alias_params(**kwargs)]
                                    for index in indices)

    def delete_alias(self, alias, indices):
        """
        Delete an alias.
        (See :ref:`es-guide-reference-api-admin-indices-aliases`)

        The specified index or indices are deleted from the alias, if they are
        in it to start with.  This won't report an error even if the indices
        aren't present in the alias.

        :param alias: the name of an alias
        :param indices: a list of indices
        """
        indices = self.conn._validate_indices(indices)

        return self.change_aliases(['remove', index, alias, {}] for index in indices)

    def set_alias(self, alias, indices, **kwargs):
        """
        Set an alias.
        (See :ref:`es-guide-reference-api-admin-indices-aliases`)

        This handles removing the old list of indices pointed to by the alias.

        Warning: there is a race condition in the implementation of this
        function - if another client modifies the indices which this alias
        points to during this call, the old value of the alias may not be
        correctly set.

        :param alias: the name of an alias
        :param indices: a list of indices
        """
        indices = self.conn._validate_indices(indices)
        try:
            old_indices = self.get_alias(alias)
        except IndexMissingException:
            old_indices = []
        commands = [['remove', index, alias, {}] for index in old_indices]
        commands.extend([['add', index, alias,
                          self._get_alias_params(**kwargs)] for index in indices])
        if len(commands) > 0:
            return self.change_aliases(commands)

    def stats(self, indices=None):
        """
        Retrieve the statistic of one or more indices
        (See :ref:`es-guide-reference-api-admin-indices-stats`)

        :keyword indices: an index or a list of indices
        """
        path = self.conn._make_path(indices, (), "_stats")
        return self.conn._send_request('GET', path)

    def status(self, indices=None):
        """
        Retrieve the status of one or more indices
        (See :ref:`es-guide-reference-api-admin-indices-status`)

        :keyword indices: an index or a list of indices
        """
        path = self.conn._make_path(indices, (), '_status', allow_all_indices=False)
        return self.conn._send_request('GET', path)
    # Following signature differs because field data isn't available at _all endpoint.   
    def field_stats(self, indices=''):
        """
        Retrieve the field data stats for one or more indices
        (See :ref:'es-guide-reference-api-admin-cluster-nodes-stats')

        :keyword indices: an index or a list of indices
        """
        path = self.conn._make_path(indices, (), '_stats','fielddata')
        return self.conn._send_request('GET', path)

    def create_index(self, index, settings=None):
        """
        Creates an index with optional settings.
        :ref:`es-guide-reference-api-admin-indices-create-index`

        :param index: the name of the index
        :keyword settings: a settings object or a dict containing settings

        """
        return self.conn._send_request('PUT', index, settings)

    def create_index_if_missing(self, index, settings=None):
        """Creates an index if it doesn't already exist.

        If supplied, settings must be a dictionary.

        :param index: the name of the index
        :keyword settings: a settings object or a dict containing settings
        """
        try:
            return self.create_index(index, settings)
        except IndexAlreadyExistsException as e:
            return e.result

    def delete_index(self, index):
        """
        Deletes an index.
        :ref:`es-guide-reference-api-admin-indices-delete-index`

        :param index: the name of the index

        """
        return self.conn._send_request('DELETE', index)

    def exists_index(self, index):
        """
        Check if an index exists.
        (See :ref:`es-guide-reference-api-admin-indices-indices-exists`)

        :param index: the name of the index
        """
        return self.conn._send_request('HEAD', index)

    def delete_index_if_exists(self, index):
        """
        Deletes an index if it exists.

        :param index: the name of the index

        """
        if self.exists_index(index):
            return self.delete_index(index)

    def get_indices(self, include_aliases=False):
        """
        Get a dict holding an entry for each index which exists.

        If include_alises is True, the dict will also contain entries for
        aliases.

        The key for each entry in the dict is the index or alias name.  The
        value is a dict holding the following properties:

         - num_docs: Number of documents in the index or alias.
         - alias_for: Only present for an alias: holds a list of indices which
           this is an alias for.

        """
        state = self.conn.cluster.state()
        status = self.status()
        result = {}
        indices_status = status['indices']
        indices_metadata = state['metadata']['indices']
        for index in sorted(indices_status.keys()):
            info = indices_status[index]
            try:
                num_docs = info['docs']['num_docs']
            except KeyError:
                num_docs = 0
            result[index] = dict(num_docs=num_docs)

            if not include_aliases:
                continue
            try:
                metadata = indices_metadata[index]
            except KeyError:
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
        state = self.conn.cluster.state()
        status = self.status()

        indices_metadata = set(state['metadata']['indices'].keys())
        indices_status = set(status['indices'].keys())

        return indices_metadata.difference(indices_status)

    def close_index(self, index):
        """
        Close an index.
        (See :ref:`es-guide-reference-api-admin-indices-open-close`)


        :param index: the name of the index

        """
        return self.conn._send_request('POST', "/%s/_close" % index)

    def open_index(self, index):
        """
        Open an index.
        (See :ref:`es-guide-reference-api-admin-indices-open-close`)

        :param index: the name of the index
        """
        return self.conn._send_request('POST', "/%s/_open" % index)

    def flush(self, indices=None, refresh=None):
        """
        Flushes one or more indices (clear memory)
        If a bulk is full, it sends it.

        (See :ref:`es-guide-reference-api-admin-indices-flush`)


        :keyword indices: an index or a list of indices
        :keyword refresh: set the refresh parameter

        """
        self.conn.force_bulk()
        path = self.conn._make_path(indices, '_flush')
        args = {}
        if refresh is not None:
            args['refresh'] = refresh
        return self.conn._send_request('POST', path, params=args)

    def refresh(self, indices=None, timesleep=None, timeout=0):
        """
        Refresh one or more indices
        If a bulk is full, it sends it.
        (See :ref:`es-guide-reference-api-admin-indices-refresh`)

        :keyword indices: an index or a list of indices
        :keyword timesleep: seconds to wait
        :keyword timeout: seconds to wait before timing out when waiting for
            the cluster's health.
        """
        self.conn.force_bulk()
        path = self.conn._make_path(indices, (), '_refresh', allow_all_indices=False)
        result = self.conn._send_request('POST', path)
        if timesleep:
            time.sleep(timesleep)
        self.conn.cluster.health(wait_for_status='green', timeout=timeout)
        return result

    def optimize(self, indices=None,
                 wait_for_merge=False,
                 max_num_segments=None,
                 only_expunge_deletes=False,
                 refresh=True,
                 flush=True):
        """
        Optimize one or more indices.
        (See :ref:`es-guide-reference-api-admin-indices-optimize`)


        :keyword indices: the list of indices to optimise.  If not supplied, all
                          default_indices are optimised.

        :keyword wait_for_merge: If True, the operation will not return until the merge has been completed.
                                 Defaults to False.

        :keyword max_num_segments: The number of segments to optimize to. To fully optimize the index, set it to 1.
                                   Defaults to half the number configured by the merge policy (which in turn defaults
                                   to 10).


        :keyword only_expunge_deletes: Should the optimize process only expunge segments with deletes in it.
                                       In Lucene, a document is not deleted from a segment, just marked as deleted.
                                       During a merge process of segments, a new segment is created that does have
                                       those deletes.
                                       This flag allow to only merge segments that have deletes. Defaults to false.

        :keyword refresh: Should a refresh be performed after the optimize. Defaults to true.

        :keyword flush: Should a flush be performed after the optimize. Defaults to true.

        """
        path = self.conn._make_path(indices, (), '_optimize')
        params = dict(
            wait_for_merge=wait_for_merge,
            only_expunge_deletes=only_expunge_deletes,
            refresh=refresh,
            flush=flush,
            )
        for k, v in params.items():
            params[k] = v and "true" or "false"
        if max_num_segments is not None:
            params['max_num_segments'] = max_num_segments
        return self.conn._send_request('POST', path, params=params)

    def analyze(self, text, index=None, analyzer=None, tokenizer=None, filters=None, field=None):
        """
        Performs the analysis process on a text and return the tokens breakdown of the text

        (See :ref:`es-guide-reference-api-admin-indices-optimize`)

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
            raise ValueError('Argument conflict: Specify either analyzer, tokenizer/filters or field')

        if field and index is None:
            raise ValueError('field can only be specified with an index')

        path = make_path(index, '_analyze')
        return self.conn._send_request('POST', path, text, args)

    def gateway_snapshot(self, indices=None):
        """
        Gateway snapshot one or more indices
        (See :ref:`es-guide-reference-api-admin-indices-gateway-snapshot`)

        :keyword indices: a list of indices or None for default configured.
        """
        path = self.conn._make_path(indices, (), '_gateway', 'snapshot')
        return self.conn._send_request('POST', path)

    def put_mapping(self, doc_type=None, mapping=None, indices=None, ignore_conflicts=None):
        """
        Register specific mapping definition for a specific type against one or more indices.
        (See :ref:`es-guide-reference-api-admin-indices-put-mapping`)

        """
        if not isinstance(mapping, dict):
            if mapping is None:
                mapping = {}
            if hasattr(mapping, "as_dict"):
                mapping = mapping.as_dict()

        if doc_type:
            path = self.conn._make_path(indices, doc_type, "_mapping")
            if doc_type not in mapping:
                mapping = {doc_type: mapping}
        else:
            path = self.conn._make_path(indices, (), "_mapping")

        parameters = {}

        if ignore_conflicts is not None:
            parameters['ignore_conflicts'] = ignore_conflicts

        return self.conn._send_request('PUT', path, mapping, params=parameters)

    def get_mapping(self, doc_type=None, indices=None, raw=False):
        """
        Register specific mapping definition for a specific type against one or more indices.
        (See :ref:`es-guide-reference-api-admin-indices-get-mapping`)

        """
        if doc_type is None and indices is None:
            path = make_path("_mapping")
            is_mapping = False
        else:
            indices = self.conn._validate_indices(indices)
            if doc_type:
                path = make_path(','.join(indices), doc_type, "_mapping")
                is_mapping = True
            else:
                path = make_path(','.join(indices), "_mapping")
                is_mapping = False
        result = self.conn._send_request('GET', path)
        if raw:
            return result
        from pyes.mappings import Mapper
        mapper = Mapper(result, is_mapping=False,
                        connection=self.conn,
                        document_object_field=self.conn.document_object_field)
        if doc_type:
            return mapper.mappings[doc_type]
        return mapper

    def delete_mapping(self, index, doc_type):
        """
        Delete a typed JSON document type from a specific index.
        (See :ref:`es-guide-reference-api-admin-indices-delete-mapping`)

        """
        path = make_path(index, doc_type)
        return self.conn._send_request('DELETE', path)

    def get_settings(self, index=None):
        """
        Returns the current settings for an index.
        (See :ref:`es-guide-reference-api-admin-indices-get-settings`)

        """
        path = make_path(index, "_settings")
        return self.conn._send_request('GET', path)

    def update_settings(self, index, newvalues):
        """
        Update Settings of an index.
        (See  :ref:`es-guide-reference-api-admin-indices-update-settings`)

        """
        path = make_path(index, "_settings")
        return self.conn._send_request('PUT', path, newvalues)

class Cluster(object):
    def __init__(self, conn):
        self.conn = conn

    #TODO: node shutdown, update settings

    def shutdown(self, all_nodes=False, master=False, local=False, nodes=[],
                 delay=None):
        if all_nodes:
            path = make_path('_shutdown')
        elif master:
            path = make_path("_cluster", "nodes", "_master", "_shutdown")
        elif nodes:
            path = make_path("_cluster", "nodes", ",".join(nodes), "_shutdown")
        elif local:
            path = make_path("_cluster", "nodes", "_local", "_shutdown")
        if delay:
            try:
                int(delay)
                path += "?%s"%delay
            except ValueError:
                raise ValueError("%s is not a valid delay time"%delay)
            except TypeError:
                raise TypeError("%s is not of type int or string"%delay)
        if not path:
            # default action
            path = make_path('_shutdown')
        return self.conn._send_request('GET', path)



    def health(self, indices=None, level="cluster", wait_for_status=None,
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
        if indices:
            path = make_path("_cluster", "health", ",".join(indices))
        else:
            path = make_path("_cluster", "health")
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
        return self.conn._send_request('GET', path, params=mapping)

    def state(self, filter_nodes=None, filter_routing_table=None,
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
        path = make_path("_cluster", "state")
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
            if isinstance(filter_indices, six.string_types):
                parameters['filter_indices'] = filter_indices
            else:
                parameters['filter_indices'] = ",".join(filter_indices)

        return self.conn._send_request('GET', path, params=parameters)

    def nodes_info(self, nodes=None):
        """
        The cluster :ref:`nodes info <es-guide-reference-api-admin-cluster-state>` API allows to retrieve one or more (or all) of
        the cluster nodes information.
        """
        parts = ["_cluster", "nodes"]
        if nodes:
            parts.append(",".join(nodes))
        path = make_path(*parts)
        return self.conn._send_request('GET', path)


    def info(self):
        """
        The cluster :ref:`nodes info <es-guide-reference-api-admin-cluster-state>` API allows to retrieve one or more (or all) of
        the cluster nodes information.
        """
        return self.conn._send_request('GET', "/")


    def node_stats(self, nodes=None):
        """
        The cluster :ref:`nodes info <es-guide-reference-api-admin-cluster-nodes-stats>` API allows to retrieve one or more (or all) of
        the cluster nodes information.
        """
        parts = ["_cluster", "nodes", "stats"]
        if nodes:
            parts = ["_cluster", "nodes", ",".join(nodes), "stats"]

        path = make_path(*parts)
        return self.conn._send_request('GET', path)

    def node_field_stats(self, nodes=None):
        """
        Retrieve field stats per node(s) or cluster wide
        :ref:`nodes info <es-guide-reference-api-admin-cluster-nodes-stats>` API allows to retrieve one or more (or all) 
        the cluster nodes info about field data memory usage
        """
        parts = ['_nodes', 'stats', 'indices']
        if nodes:
            paths = ['_nodes', ",".join(nodes), 'stats', 'indices']

        path = make_path(*parts)
        return self.conn._send_request('GET', path)
