#
# models
#
try:
    # For Python >= 2.6
    import json
except ImportError:
    # For Python < 2.6 or people using a newer version of simplejson
    import simplejson as json

class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)

    __setattr__ = dict.__setitem__

    __delattr__ = dict.__delitem__

class ElasticSearchModel(DotDict):
    def __init__(self, *args, **kwargs):
        self.meta = DotDict()
        self.__initialised = True
        from pyes.es import ES
        if len(args) == 2 and isinstance(args[0], ES):
            item = args[1]
            self.update(item.pop("_source", DotDict()))
            self.update(item.pop("fields", {}))
            self.meta = DotDict([(k.lstrip("_"), v) for k, v in item.items()])
            self.meta.connection = args[0]
        else:
            self.update(dict(*args, **kwargs))

    def __setattr__(self, key, value):
        if not self.__dict__.has_key('_ElasticSearchModel__initialised'):  # this test allows attributes to be set in the __init__ method
            return dict.__setattr__(self, key, value)
        elif self.__dict__.has_key(key):       # any normal attributes are handled normally
            dict.__setattr__(self, key, value)
        else:
            self.__setitem__(key, value)

    def __repr__(self):
        return repr(self)

    def save(self, bulk=False, id=None):
        """
        Save the object and returns id
        """
        meta = self.meta
        conn = meta['connection']
        id = id or meta.get("id", None)
        version = None
        if 'version' in meta:
            version = meta['version']
        res = conn.index(self,
                         meta.index, meta.type, id, bulk=bulk, version=version)
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

    def __hash__(self):
        # the hash of our string is our unique hash
        return hash(self.meta.id)

    def __cmp__(self, other):
        # similarly the strings are good for comparisons
        return cmp(self.meta.id, self.meta.id)

    def delete(self, bulk=False):
        """
        Delete the object
        """
        meta = self.meta
        self.meta['connection'].delete(meta.index, meta.type, meta.id, bulk=bulk)

    def get_full_id(self):
        """Return an id of type index:type:id"""
        return "%s:%s:%s" % (self.meta.index, self.meta.type, self.get_id())


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
        result.append(json.dumps(self, cls=self.meta.connection.encoder))
        result.append("\n")
        return ''.join(result)
