#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'

from pyes.utils import keys_to_string
from pyes.models import DotDict
from pyes.exceptions import InvalidParameter
check_values = {
                'index': ['no', 'analyzed', 'not_analyzed'],
                'term_vector': ['no', 'yes', 'with_offsets', 'with_positions', 'with_positions_offsets'],
                'type': ['float', 'double', 'short', 'integer', 'long'],
                'store': ['yes', 'no'],
                'index_analyzer' : [],
                'search_analyzer' : [],
                }


class AbstractField(DotDict):
    def __init__(self, **kwargs):
        self._valid_fields = {"index":["yes", "no"],
                            "store":["yes", "no"],
                            "boost":[],
                            "type":[],
                            "index_name":[],
                            "name":[],
                            }
        self.__initialised = True

    def __setattr__(self, key, value):
        if not self.__dict__.has_key('_AbstractField__initialised'):
            return dict.__setattr__(self, key, value)
        elif self.__dict__.has_key(key):
            dict.__setattr__(self, key, value)
        else:
            if key not in self._valid_fields:
                raise InvalidParameter("Invalid parameter:%s" % key)
            if self._valid_fields[key] and value not in self._valid_fields[key]:
                raise InvalidParameter('Invalid value "%s" for parameter %s' % (value, key))

            self.__setitem__(key, value)


class StringField(AbstractField):
    """The text based string type is the most basic type, and contains one or more characters.

    The following table lists all the attributes that can be used with the **string** type:
    
    ==================================  ============================================================================================================================================================================================================================================================================================================================
     Attribute                           Description                                                                                                                                                                                                                                                                                                                
    ==================================  ============================================================================================================================================================================================================================================================================================================================
    **index_name**                      The name of the field that will be stored in the index. Defaults to the property/field name.                                                                                                                                                                                                                                
    **store**                           Set to **yes** the store actual field in the index, **no** to not store it. Defaults to **no** (note, the JSON document itself is stored, and it can be retrieved from it).                                                                                                                                                 
    **index**                           Set to **analyzed** for the field to be indexed and searchable after being broken down into token using an analyzer. **not_analyzed** means that its still searchable, but does not go through any analysis process or broken down into tokens. **no** means that it won't be searchable at all. Defaults to **analyzed**.  
    **term_vector**                     Possible values are **no**, **yes**, **with_offsets**, **with_positions**, **with_positions_offsets**. Defaults to **no**.                                                                                                                                                                                                  
    **boost**                           The boost value. Defaults to **1.0**.                                                                                                                                                                                                                                                                                       
    **null_value**                      When there is a (JSON) null value for the field, use the **null_value** as the field value. Defaults to not adding the field at all.                                                                                                                                                                                        
    **omit_norms**                      Boolean value if norms should be omitted or not. Defaults to **false**.                                                                                                                                                                                                                                                     
    **omit_term_freq_and_positions**    Boolean value if term freq and positions should be omitted. Defaults to **false**.                                                                                                                                                                                                                                          
    **analyzer**                        The analyzer used to analyze the text contents when **analyzed** during indexing and when searching using a query string. Defaults to the globally configured analyzer.                                                                                                                                                     
    **index_analyzer**                  The analyzer used to analyze the text contents when **analyzed** during indexing.                                                                                                                                                                                                                                           
    **search_analyzer**                 The analyzer used to analyze the field when part of a query string.                                                                                                                                                                                                                                                         
    **include_in_all**                  Should the field be included in the **_all** field (if enabled). Defaults to **true** or to the parent **object** type setting.                                                                                                                                                                                             
    ==================================  ============================================================================================================================================================================================================================================================================================================================
    """
    def __init__(self, **kwargs):
        super(StringField, self).__init__()
        self._valid_fields.update({"index":['no', 'analyzed', 'not_analyzed'],
                                    "null_value":[],
                                    "include_in_all":[],
                                    "omit_norms":[False, True],
                                    "omit_term_freq_and_positions":[False, True],
                                    "index_analyzer":[],
                                    "search_analyzer":[],
                                    "term_vector":['no', 'yes', 'with_offsets', 'with_positions', 'with_positions_offsets'],
                                    "analyzer":[],
                                    })
        self.update(kwargs)
        self.type = "string"


class GeoPointField(AbstractField):
    def __init__(self, **kwargs):
        super(GeoPointField, self).__init__()
        self._valid_fields.update({ "null_value":[],
                                    "include_in_all":[],
                                    "lat_lon":[],
                                    "geohash":[], #must be an integer
                                    "geohash_precision":[],
                                    })
        self.update(kwargs)
        self.type = "geo_point"

class NumericFieldAbstract(AbstractField):
    def __init__(self, null_value=None, include_in_all=None, precision_step=4,
                 **kwargs):
        super(NumericFieldAbstract, self).__init__(**kwargs)
        self._valid_fields.update({ "null_value":[],
                                    "include_in_all":[],
                                    "precision_step":[],
                                    })

class IpField(NumericFieldAbstract):
    def __init__(self, **kwargs):
        super(IpField, self).__init__(**kwargs)
        self.update(kwargs)
        self.type = "ip"

class ShortField(NumericFieldAbstract):
    def __init__(self, **kwargs):
        super(ShortField, self).__init__(**kwargs)
        self.update(kwargs)
        self.type = "short"

class IntegerField(NumericFieldAbstract):
    def __init__(self, **kwargs):
        super(IntegerField, self).__init__(**kwargs)
        self.update(kwargs)
        self.type = "integer"

class LongField(NumericFieldAbstract):
    def __init__(self, **kwargs):
        super(LongField, self).__init__(**kwargs)
        self.update(kwargs)
        self.type = "long"

class FloatField(NumericFieldAbstract):
    def __init__(self, **kwargs):
        super(FloatField, self).__init__(**kwargs)
        self.update(kwargs)
        self.type = "float"

class DoubleField(NumericFieldAbstract):
    def __init__(self, **kwargs):
        super(DoubleField, self).__init__(**kwargs)
        self.update(kwargs)
        self.type = "double"

class DateField(NumericFieldAbstract):
    def __init__(self, **kwargs):
        super(DateField, self).__init__(**kwargs)
        self._valid_fields.update({ "format":[],
                                    })
        self.update(kwargs)
        self.type = "date"

class BooleanField(AbstractField):
    def __init__(self, **kwargs):
        super(BooleanField, self).__init__(**kwargs)
        self._valid_fields.update({ "null_value":[],
                                    "include_in_all":[],
                                    })
        self.update(kwargs)
        self.type = "date"


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

class ObjectField(DotDict):
    def __init__(self, **kwargs):
#        name=None, type=None, path=None, properties=None,
#                 dynamic=None, enabled=None, include_in_all=None, dynamic_templates=None,
#                 _id=False, _type=False, _source=None, _all=None,
#                 _analyzer=None, _boost=None,
#                 _parent=None, _index=None, _routing=None):
        self._valid_fields = {
                              "name":[],
                              "type":[],
                              "path":[],
                              "properties":[],
                              "include_in_all":[],
                              "include_in_all":[],
                              "dynamic":[],
                              "dynamic_templates":[],
                              "enabled":[],
                              "_id":[],
                              "_type":[],
                              "_source":[],
                              "_all":[],
                              "_analyzer":[],
                              "_boost":[],
                              "_parent":[],
                              "_index":[],
                              "_routing":[],
                            }
        self.__initialised = True
        properties = kwargs.pop("properties", None)

        self.update(kwargs)
        self.type = "object"
        if properties:
            self.properties = dict([(name, get_field(name, data)) for name, data in properties.items()])


    def __setattr__(self, key, value):
        if not self.__dict__.has_key('_ObjectField__initialised'):
            return dict.__setattr__(self, key, value)
        elif self.__dict__.has_key(key):
            dict.__setattr__(self, key, value)
        else:
            if key not in self._valid_fields:
                raise InvalidParameter("Invalid parameter:%s" % key)
            if self._valid_fields[key] and value not in self._valid_fields[key]:
                raise InvalidParameter('Invalid value "%s" for parameter %s' % (value, key))

            self.__setitem__(key, value)

    def add_property(self, prop):
        """
        Add a property to the object
        """
        self.properties[prop.name] = prop


class DocumentObjectField(ObjectField):
    pass

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
    def __init__(self, data, has_indices=False):
        self.indices = {}
        self.mappings = {}
        self.has_indices = has_indices
        self._process(data)

    def _process(self, data):
        """
        Process indexer data
        """
        if self.has_indices:
            for indexname, indexdata in data.items():
                self.indices[indexname] = {}
                for docname, docdata in indexdata.items():
                    self.indices[indexname][docname] = get_field(docname, docdata)
        else:
            for docname, docdata in data.items():
                self.mappings[docname] = get_field(docname, docdata)

    def get_doctype(self, index, name):
        """
        Returns a doctype given an index and a name
        """
        return self.indices[index][name]
