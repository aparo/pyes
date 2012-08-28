#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import with_statement

import copy
import threading
import json

from .exceptions import BulkOperationException

__author__ = 'alberto'

class DotDict(dict):
    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        return self.get(attr, None)

    __setattr__ = dict.__setitem__

    __delattr__ = dict.__delitem__

    def __deepcopy__(self, memo):
        return DotDict([(copy.deepcopy(k, memo), copy.deepcopy(v, memo)) for k, v in self.items()])


class ElasticSearchModel(DotDict):
    def __init__(self, *args, **kwargs):
        from pyes import ES
        self._meta = DotDict()
        self.__initialised = True
        if len(args) == 2 and isinstance(args[0], ES):
            item = args[1]
            self.update(item.pop("_source", DotDict()))
            self.update(item.pop("fields", {}))
            self._meta = DotDict([(k.lstrip("_"), v) for k, v in item.items()])
            self._meta.parent = self.pop("_parent", None)
            self._meta.connection = args[0]
        else:
            self.update(dict(*args, **kwargs))

    def __setattr__(self, key, value):
        if not self.__dict__.has_key(
            '_ElasticSearchModel__initialised'):  # this test allows attributes to be set in the __init__ method
            return dict.__setattr__(self, key, value)
        elif self.__dict__.has_key(key):       # any normal attributes are handled normally
            dict.__setattr__(self, key, value)
        else:
            self.__setitem__(key, value)

    def get_meta(self):
        return self._meta

    def delete(self, bulk=False):
        """
        Delete the object
        """
        meta = self._meta
        conn = meta['connection']
        conn.delete(meta.index, meta.type, meta.id, bulk=bulk)

    def save(self, bulk=False, id=None, parent=None, force=False):
        """
        Save the object and returns id
        """
        meta = self._meta
        conn = meta['connection']
        id = id or meta.get("id", None)
        parent = parent or meta.get('parent', None)
        version = meta.get('version', None)
        if force:
            version = None
        res = conn.index(self,
                         meta.index, meta.type, id, parent=parent, bulk=bulk, version=version, force_insert=force)
        if not bulk:
            self._meta.id = res._id
            self._meta.version = res._version
            return res._id
        return id

    def reload(self):
        meta = self._meta
        conn = meta['connection']
        res = conn.get(meta.index, meta.type, meta["id"])
        self.update(res)


    def get_id(self):
        """ Force the object saveing to get an id"""
        _id = self._meta.get("id", None)
        if _id is None:
            _id = self.save()
        return _id

    def get_bulk(self, create=False):
        """Return bulk code"""
        result = []
        op_type = "index"
        if create:
            op_type = "create"
        meta = self._meta
        cmd = {op_type: {"_index": meta.index, "_type": meta.type}}
        if meta.parent:
            cmd[op_type]['_parent'] = meta.parent
        if meta.version:
            cmd[op_type]['_version'] = meta.version
        if meta.id:
            cmd[op_type]['_id'] = meta.id
        result.append(json.dumps(cmd, cls=self._meta.connection.encoder))
        result.append("\n")
        result.append(json.dumps(self, cls=self._meta.connection.encoder))
        result.append("\n")
        return ''.join(result)




#--------
# Bulkers
#--------

class BaseBulker(object):
    """
    Base class to implement a bulker strategy

    """

    def __init__(self, conn, bulk_size=400, raise_on_bulk_item_failure=False):
        self.conn = conn
        self._bulk_size = bulk_size
        # protects bulk_data
        self.bulk_lock = threading.RLock()
        with self.bulk_lock:
            self.bulk_data = []
        self.raise_on_bulk_item_failure = raise_on_bulk_item_failure

    def get_bulk_size(self):
        """
        Get the current bulk_size

        :return a int: the size of the bulk holder
        """
        return self._bulk_size

    def set_bulk_size(self, bulk_size):
        """
        Set the bulk size

        :param bulk_size the bulker size
        """
        self._bulk_size = bulk_size
        self.flush_bulk()

    bulk_size = property(get_bulk_size, set_bulk_size)

    def add(self, content):
        raise NotImplementedError

    def flush_bulk(self, forced=False):
        raise NotImplementedError


class ListBulker(BaseBulker):
    """
    A bulker that store data in a list
    """

    def __init__(self, conn, bulk_size=400, raise_on_bulk_item_failure=False):
        super(ListBulker, self).__init__(conn=conn, bulk_size=bulk_size,
                                         raise_on_bulk_item_failure=raise_on_bulk_item_failure)
        with self.bulk_lock:
            self.bulk_data = []

    def add(self, content):
        with self.bulk_lock:
            self.bulk_data.append(content)

    def flush_bulk(self, forced=False):
        with self.bulk_lock:
            if forced or len(self.bulk_data) >= self.bulk_size:
                batch = self.bulk_data
                self.bulk_data = []
            else:
                return None

        if len(batch) > 0:
            bulk_result = self.conn._send_request("POST",
                                                  "/_bulk",
                                                  "\n".join(batch) + "\n")

            if self.raise_on_bulk_item_failure:
                _raise_exception_if_bulk_item_failed(bulk_result)

            return bulk_result


def _is_bulk_item_ok(item):
    if "index" in item:
        return "ok" in item["index"]
    elif "delete" in item:
        return "ok" in item["delete"]
    else:
        # unknown response type; be conservative
        return False


def _raise_exception_if_bulk_item_failed(bulk_result):
    errors = [item for item in bulk_result["items"] if not _is_bulk_item_ok(item)]
    if len(errors) > 0:
        raise BulkOperationException(errors, bulk_result)
    return None
