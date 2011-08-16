#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'

import threading

_thread_locals = threading.local()
#store threadsafe data
from pyes.utils import keys_to_string

check_values = {
                'index': ['no', 'analyzed', 'not_analyzed'],
                'term_vector': ['no', 'yes', 'with_offsets', 'with_positions', 'with_positions_offsets'],
                'type': ['float', 'double', 'short', 'integer', 'long'],
                'store': ['yes', 'no'],
                'index_analyzer' : [],
                'search_analyzer' : [],
                }


class AbstractField(object):
    def __init__(self, index="not_analyzed", store="no", boost=1.0,
                 term_vector="no", omit_norms=True,
                 omit_term_freq_and_positions=True,
                 type=None, index_name=None,
                 analyzer=None,
                 index_analyzer=None,
                 search_analyzer=None,
                 name=None):
        self.store = store
        self.boost = boost
        self.term_vector = term_vector
        self.index = index
        self.omit_norms = omit_norms
        self.omit_term_freq_and_positions = omit_term_freq_and_positions
        self.index_name = index_name
        self.type = type
        self.analyzer = analyzer
        self.index_analyzer = index_analyzer
        self.search_analyzer = search_analyzer
        self.name = name

    def as_dict(self):
        result = {"type":self.type,
                  'index':self.index}
        if self.store != "no":
            if isinstance(self.store, bool):
                if self.store:
                    result['store'] = "yes"
                else:
                    result['store'] = "no"
            else:
                result['store'] = self.store
        if self.boost != 1.0:
            result['boost'] = self.boost
        if self.term_vector != "no":
            result['term_vector'] = self.term_vector
        if self.omit_norms != True:
            result['omit_norms'] = self.omit_norms
        if self.omit_term_freq_and_positions != True:
            result['omit_term_freq_and_positions'] = self.omit_term_freq_and_positions
        if self.index_name:
            result['index_name'] = self.index_name
        if self.analyzer:
            result['analyzer'] = self.analyzer
        if self.index_analyzer:
            result['index_analyzer'] = self.index_analyzer
        if self.search_analyzer:
            result['search_analyzer'] = self.search_analyzer

        return result

class StringField(AbstractField):
    def __init__(self, null_value=None, include_in_all=None, *args, **kwargs):
        super(StringField, self).__init__(*args, **kwargs)
        self.null_value = null_value
        self.include_in_all = include_in_all
        self.type = "string"

    def as_dict(self):
        result = super(StringField, self).as_dict()
        if self.null_value is not None:
            result['null_value'] = self.null_value
        if self.include_in_all is not None:
            result['include_in_all'] = self.include_in_all
        return result

class GeoPointField(AbstractField):
    def __init__(self, null_value=None, include_in_all=None,
                 lat_lon=None, geohash=None, geohash_precision=None,
                 *args, **kwargs):
        super(GeoPointField, self).__init__(**kwargs)
        self.null_value = null_value
        self.include_in_all = include_in_all
        self.lat_lon = lat_lon
        self.geohash = geohash
        self.geohash_precision = geohash_precision
        self.type = "geo_point"

    def as_dict(self):
        result = super(GeoPointField, self).as_dict()
        if self.null_value is not None:
            result['null_value'] = self.null_value
        if self.include_in_all is not None:
            result['include_in_all'] = self.include_in_all
        if self.lat_lon is not None:
            result['lat_lon'] = self.lat_lon
        if self.geohash is not None:
            result['geohash'] = self.geohash
        if self.geohash_precision is not None:
            try:
                int(self.geohash_precision)
            except ValueError:
                raise ValueError("geohash_precision must be an integer")
            result['geohash_precision'] = self.geohash_precision
        return result

class NumericFieldAbstract(AbstractField):
    def __init__(self, null_value=None, include_in_all=None, precision_step=4,
                 **kwargs):
        super(NumericFieldAbstract, self).__init__(**kwargs)
        self.null_value = null_value
        self.include_in_all = include_in_all
        self.precision_step = precision_step

    def as_dict(self):
        result = super(NumericFieldAbstract, self).as_dict()
        if self.null_value is not None:
            result['null_value'] = self.null_value
        if self.include_in_all is not None:
            result['include_in_all'] = self.include_in_all
        if self.precision_step != 4:
            result['precision_step'] = self.precision_step
        return result

class IpField(NumericFieldAbstract):
    def __init__(self, *args, **kwargs):
        super(IpField, self).__init__(*args, **kwargs)
        self.type = "ip"

class ShortField(NumericFieldAbstract):
    def __init__(self, *args, **kwargs):
        super(ShortField, self).__init__(*args, **kwargs)
        self.type = "short"

class IntegerField(NumericFieldAbstract):
    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)
        self.type = "integer"

class LongField(NumericFieldAbstract):
    def __init__(self, *args, **kwargs):
        super(LongField, self).__init__(*args, **kwargs)
        self.type = "long"

class FloatField(NumericFieldAbstract):
    def __init__(self, *args, **kwargs):
        super(FloatField, self).__init__(*args, **kwargs)
        self.type = "float"

class DoubleField(NumericFieldAbstract):
    def __init__(self, *args, **kwargs):
        super(DoubleField, self).__init__(*args, **kwargs)
        self.type = "double"

class DateField(NumericFieldAbstract):
    def __init__(self, format=None, **kwargs):
        super(DateField, self).__init__(**kwargs)
        self.format = format
        self.type = "date"

    def as_dict(self):
        result = super(DateField, self).as_dict()
        if self.format:
            result['format'] = self.format
        return result

class BooleanField(AbstractField):
    def __init__(self, null_value=None, include_in_all=None, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)
        self.null_value = null_value
        self.include_in_all = include_in_all
        self.type = "boolean"

    def as_dict(self):
        result = super(BooleanField, self).as_dict()
        if self.null_value is not None:
            result['null_value'] = self.null_value
        if self.include_in_all is not None:
            result['include_in_all'] = self.include_in_all
        return result

class MultiField(object):
    def __init__(self, name, type=None, path=None, fields=None):
        self.name = name
        self.type = "multi_field"
        self.path = path
        self.fields = {}
        if fields and isinstance(fields, dict):
            self.fields = dict([(name, get_field(name, data)) for name, data in fields.items()])

    def as_dict(self):
        result = {"type": self.type,
                  "fields": {}}
        if self.fields:
            for name, value in self.fields.items():
                result['fields'][name] = value.as_dict()
        if self.path:
            result['path'] = self.path
        return result

class AttachmentField(object):
    """An attachment field.

    Requires the mapper-attachments plugin to be installed to be used.

    """
    def __init__(self, name, type=None, path=None, fields=None):
        self.name = name
        self.type = "attachment"
        self.path = path
        self.fields = dict([(name, get_field(name, data)) for name, data in fields.items()])

    def as_dict(self):
        result_fields = dict((name, value.as_dict())
                             for (name, value) in self.fields.items())
        result = dict(type=self.type, fields=result_fields)
        if self.path:
            result['path'] = self.path
        return result

class ObjectField(object):
    def __init__(self, name=None, type=None, path=None, properties=None,
                 dynamic=None, enabled=None, include_in_all=None, dynamic_templates=None,
                 _id=False, _type=False, _source=None, _all=None,
                 _analyzer=None, _boost=None,
                 _parent=None, _index=None, _routing=None):
        self.name = name
        self.type = "object"
        self.path = path
        self.properties = properties
        self.include_in_all = include_in_all
        self.dynamic = dynamic
        self.dynamic_templates = dynamic_templates or []
        self.enabled = enabled
        self._id = _id
        self._type = _type
        self._source = _source
        self._all = _all
        self._analyzer = _analyzer
        self._boost = _boost
        self._parent = _parent
        self._index = _index
        self._routing = _routing
        if properties:
            self.properties = dict([(name, get_field(name, data)) for name, data in properties.items()])
        else:
            self.properties = {}

    def add_property(self, prop):
        """
        Add a property to the object
        """
        self.properties[prop.name] = prop

    def as_dict(self):
        result = {"type": self.type,
                  "properties": {}}
        if self._id:
            result['_id'] = {"store":True}
        if self._type:
            result['_type'] = {"store":True}
        if self._source is not None:
            result['_source'] = self._source
        if self._all is not None:
            result['_all'] = self._all
        if self._analyzer is not None:
            result['_analyzer'] = self._analyzer
        if self._boost is not None:
            result['_boost'] = self._boost
        if self._parent is not None:
            result['_parent'] = self._parent
        if self._index:
            result['_index'] = {"store":True}
        if self._routing is not None:
            result['_routing'] = self._routing
        if self.dynamic is not None:
            result['dynamic'] = self.dynamic
        if self.enabled is not None:
            result['enabled'] = self.enabled
        if self.include_in_all is not None:
            result['include_in_all'] = self.include_in_all
        if self.path is not None:
            result['path'] = self.path

        if self.properties:
            for name, value in self.properties.items():
                result['properties'][name] = value.as_dict()
        return result

    def __str__(self):
        return str(self.as_dict())

class DocumentObjectField(object):
    def __init__(self, name=None, type=None, path=None, properties=None,
                 dynamic=None, enabled=None, _all=None, _boost=None, _id=None,
                 _index=None, _source=None, _type=None, date_formats=None,
                 _parent=None):
        self.name = name
        self.type = "object"
        self.path = path
        self.properties = properties or {}
        self.dynamic = dynamic
        self.enabled = enabled
        self._all = _all
        self._boost = _boost
        self._id = _id
        self._index = _index
        self._source = _source
        self._type = _type
        self._parent = _parent
        self.date_formats = date_formats
        if properties:
            self.properties = dict([(name, get_field(name, data)) for name, data in properties.items()])

    def as_dict(self):
        result = {"type": self.type,
                  "properties": {}}
        if self.dynamic is not None:
            result['dynamic'] = self.dynamic
        if self.enabled is not None:
            result['enabled'] = self.enabled
        if self.path is not None:
            result['path'] = self.path
        if self._all is not None:
            result['_all'] = self._all
        if self._boost is not None:
            result['_boost'] = self._boost
        if self._id is not None:
            result['_id'] = self._id
        if self._index is not None:
            result['_index'] = self._index
        if self._source is not None:
            result['_source'] = self._source
        if self._type is not None:
            result['_type'] = self._type
        if self._parent is not None:
            result['_parent'] = self._parent

        if self.properties:
            for name, value in self.properties.items():
                result['properties'][name] = value.as_dict()
        return result

    def __unicode__(self):
        return "<DocumentObjectField:%s>" % self.as_dict()

def get_field(name, data):
    """
    Return a valid Field by given data
    """
    if isinstance(data, AbstractField):
        return data
    data = keys_to_string(data)
    type = data.get('type', 'object')
    if type == "string":
        return StringField(name=name, **data)
    elif type == "boolean":
        return BooleanField(name=name, **data)
    elif type == "short":
        return ShortField(name=name, **data)
    elif type == "integer":
        return IntegerField(name=name, **data)
    elif type == "long":
        return LongField(name=name, **data)
    elif type == "float":
        return FloatField(name=name, **data)
    elif type == "double":
        return DoubleField(name=name, **data)
    elif type == "ip":
        return IpField(name=name, **data)
    elif type == "date":
        return DateField(name=name, **data)
    elif type == "multi_field":
        return MultiField(name=name, **data)
    elif type == "geo_point":
        return GeoPointField(name=name, **data)
    elif type == "attachment":
        return AttachmentField(name=name, **data)
    elif type == "object":
        if '_all' in data:
            return DocumentObjectField(name=name, **data)

        return ObjectField(name=name, **data)
    raise RuntimeError("Invalid type: %s" % type)

class Mapper(object):
    def __init__(self, data, is_mapping=False):
        self.indices = {}
        self.mappings = {}
        self.is_mapping = is_mapping
        self._process(data)

    def _process(self, data):
        """
        Process indexer data
        """
        if self.is_mapping:
            for docname, docdata in data.items():
                self.mappings[docname] = get_field(docname, docdata)
        else:
            for indexname, indexdata in data.items():
                self.indices[indexname] = {}
                for docname, docdata in indexdata.items():
                    self.indices[indexname][docname] = get_field(docname, docdata)

    def get_doctype(self, index, name):
        """
        Returns a doctype given an index and a name
        """
        return self.indices[index][name]
