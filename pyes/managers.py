#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from pyes.exceptions import IndexAlreadyExistsException, IndexMissingException

class Indices(object):
    def __init__(self, conn):
        self.conn=conn

    #Alias Management - START
    def aliases(self, indices=None):
        """
        Retrieve the aliases of one or more indices.
        :ref:`Admin Indices Alias <es-guide-reference-api-admin-indices-aliases>`

        :keyword indices: an index or a list of indices


        """
        indices = self.conn._validate_indices(indices)
        path = self.conn._make_path([','.join(indices), '_aliases'])
        return self.conn._send_request('GET', path)

    def get_alias(self, alias):
        """
        Get the index or indices pointed to by a given alias.
        :ref:`Admin Indices Alias <es-guide-reference-api-admin-indices-aliases>`

        :param alias: the name of an alias
        :return returns a list of index names.
        :raise IndexMissingException if the alias does not exist.
        """
        status = self.status([alias])
        return status['indices'].keys()

    def change_aliases(self, commands):
        """
        Change the aliases stored.
        :ref:`Admin Indices Alias <es-guide-reference-api-admin-indices-aliases>`

        :param commands: is a list of 3-tuples; (command, index, alias), where
        `command` is one of "add" or "remove", and `index` and `alias` are the
        index and alias to add or remove.

        """
        body = {
            'actions': [
                {command: dict(index=index, alias=alias)}
            for (command, index, alias) in commands
            ]
        }
        return self.conn._send_request('POST', "_aliases", body)

    def add_alias(self, alias, indices):
        """
        Add an alias to point to a set of indices.
        :ref:`Admin Indices Alias <es-guide-reference-api-admin-indices-aliases>`

        :param alias: the name of an alias
        :param indices: a list of indices

        """
        indices = self.conn._validate_indices(indices)
        return self.change_aliases(['add', index, alias] for index in indices)

    def delete_alias(self, alias, indices):
        """
        Delete an alias.
        :ref:`Admin Indices Alias <es-guide-reference-api-admin-indices-aliases>`

        The specified index or indices are deleted from the alias, if they are
        in it to start with.  This won't report an error even if the indices
        aren't present in the alias.

        :param alias: the name of an alias
        :param indices: a list of indices
        """
        indices = self.conn._validate_indices(indices)
        return self.change_aliases(['remove', index, alias]
        for index in indices)

    def set_alias(self, alias, indices):
        """
        Set an alias.
        :ref:`Admin Indices Alias <es-guide-reference-api-admin-indices-aliases>`

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
        commands = [['remove', index, alias] for index in old_indices]
        commands.extend([['add', index, alias] for index in indices])
        if len(commands) > 0:
            return self.change_aliases(commands)


    def status(self, indices=None):
        """
        Retrieve the status of one or more indices
        :ref:`Admin Indices Status <es-guide-reference-api-admin-indices-status>`

        :keyword indices: an index or a list of indices
        """
        indices = self.conn._validate_indices(indices)
        path = self.conn._make_path([','.join(indices), '_status'])
        return self.conn._send_request('GET', path)

    def create_index(self, index, settings=None):
        """
        Creates an index with optional settings.
        :ref:`Admin Create Index <es-guide-reference-api-admin-create-index>`

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
        except IndexAlreadyExistsException, e:
            return e.result

    def delete_index(self, index):
        """
        Deletes an index.
        :ref:`Admin Delete Index <es-guide-reference-api-admin-delete-index>`

        :param index: the name of the index

        """
        return self.conn._send_request('DELETE', index)

    def exists_index(self, index):
        """
        Check if an index exists.
        :ref:`Admin Index Exists <es-guide-reference-api-admin-indices-indices-exists>`

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
        state = self.conn.cluster.state()
        status = self.status()

        indices_metadata = set(state['metadata']['indices'].keys())
        indices_status = set(status['indices'].keys())

        return indices_metadata.difference(indices_status)

    def close_index(self, index):
        """
        Close an index.
        :ref:`Admin Indices Open Close <es-guide-reference-api-admin-indices-open-close>`


        :param index: the name of the index

        """
        return self.conn._send_request('POST', "/%s/_close" % index)

    def open_index(self, index):
        """
        Open an index.
        :ref:`Admin Indices Open Close <es-guide-reference-api-admin-indices-open-close>`

        :param index: the name of the index
        """
        return self.conn._send_request('POST', "/%s/_open" % index)

    def flush(self, indices=None, refresh=None):
        """
        Flushes one or more indices (clear memory)
        If a bulk is full, it sends it.

        :ref:`Admin Indices Flush <es-guide-reference-api-admin-indices-flush>`


        :keyword indices: an index or a list of indices
        :keyword refresh: set the refresh parameter

        """
        self.conn.force_bulk()

        indices = self.conn._validate_indices(indices)

        path = self.conn._make_path([','.join(indices), '_flush'])
        args = {}
        if refresh is not None:
            args['refresh'] = refresh
        return self.conn._send_request('POST', path, params=args)

    def refresh(self, indices=None, timesleep=None):
        """
        Refresh one or more indices
        If a bulk is full, it sends it.
        :ref:`Admin Indices Refresh <es-guide-reference-api-admin-indices-refresh>`

        :keyword indices: an index or a list of indices
        :keyword timesleep: seconds to wait

        """
        self.conn.force_bulk()
        indices = self.conn._validate_indices(indices)

        path = self.conn._make_path([','.join(indices), '_refresh'])
        result = self.conn._send_request('POST', path)
        if timesleep:
            time.sleep(timesleep)
        self.conn.cluster.health(wait_for_status='green')
        return result


class Cluster(object):
    def __init__(self, conn):
        self.conn=conn
