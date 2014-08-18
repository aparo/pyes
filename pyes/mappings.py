# -*- coding: utf-8 -*-


import threading
try:
    from collections import OrderedDict
except ImportError:
    # python 2.6 or earlier, use backport
    from ordereddict import OrderedDict
from .models import SortedDict, DotDict
from datetime import datetime, date
import six
from .exceptions import MappedFieldNotFoundException

_thread_locals = threading.local()
#store threadsafe data
from .utils import keys_to_string

def to_bool(value):
    """
    Convert a value to boolean
    :param value: the value to convert
    :type value: any type
    :return: a boolean value
    :rtype: a boolean
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        if value=="no":
            return False
        elif value=="yes":
            return True

check_values = {
    'index': ['no', 'analyzed', 'not_analyzed'],
    'term_vector': ['no', 'yes', 'with_offsets', 'with_positions', 'with_positions_offsets'],
    'type': ['float', 'double', 'byte', 'short', 'integer', 'long'],
    'store': ['yes', 'no'],
    'index_analyzer': [],
    'search_analyzer': [],
    }


class AbstractField(object):
    def __init__(self, index=True, store=False, boost=1.0,
                 term_vector=False,
                 term_vector_positions=False,
                 term_vector_offsets=False,
                 omit_norms=True, tokenize=True,
                 omit_term_freq_and_positions=True,
                 type=None, index_name=None,
                 index_options=None,
                 path=None,
                 norms=None,
                 analyzer=None,
                 index_analyzer=None,
                 search_analyzer=None,
                 name=None,
                 locale=None,
                 fields=None):
        self.tokenize = tokenize
        self.store = to_bool(store)
        self.boost = boost
        self.term_vector = term_vector
        self.term_vector_positions = term_vector_positions
        self.term_vector_offsets = term_vector_offsets
        self.index = index
        self.index_options = index_options
        self.omit_norms = omit_norms
        self.omit_term_freq_and_positions = omit_term_freq_and_positions
        self.index_name = index_name
        self.type = type
        self.analyzer = analyzer
        self.index_analyzer = index_analyzer
        self.search_analyzer = search_analyzer
        self.name = name
        self.path = path
        self.locale = locale
        #back compatibility
        if isinstance(store, six.string_types):
            self.store = to_bool(store)
        if isinstance(index, six.string_types):
            if index == "no":
                self.index = False
                self.tokenize = False
            elif index == "not_analyzed":
                self.index = True
                self.tokenize = False
            elif index == "analyzed":
                self.index = True
                self.tokenize = True
        self.fields=[]
        if fields and isinstance(fields, dict):
            _fs=[]
            for n,v in fields.items():
                _fs.append(get_field(n,v))
            self.fields=_fs
        self.norms=norms

    def as_dict(self):
        result = {"type": self.type,
                  'index': self.index}
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
        if self.term_vector:
            result['term_vector'] = self.term_vector
        if self.term_vector_positions:
            result['term_vector_positions'] = self.term_vector_positions
        if self.term_vector_offsets:
            result['term_vector_offsets'] = self.term_vector_offsets
        if self.index_options:
            result['index_options'] = self.index_options

        if self.omit_norms != True:
            result['omit_norms'] = self.omit_norms
        if self.omit_term_freq_and_positions != True:
            result['omit_term_freq_and_positions'] = self.omit_term_freq_and_positions
        if self.index_name:
            result['index_name'] = self.index_name
        if self.norms:
            result['norms'] = self.norms
        if self.analyzer:
            result['analyzer'] = self.analyzer
        if self.index_analyzer:
            result['index_analyzer'] = self.index_analyzer
        if self.search_analyzer:
            result['search_analyzer'] = self.search_analyzer
        if self.path is not None:
            result['path'] = self.path
        if self.locale:
            result['locale'] = self.locale
        if self.fields:
            result['fields'] = dict([(f.name, f.as_dict()) for f in self.fields])

        return result

    def get_code(self, num=0):
        data = SortedDict(self.as_dict())
        if "store" in data:
            data["store"]=to_bool(data["store"])
        var_name = "prop_"+self.name
        return var_name, var_name+" = "+self.__class__.__name__+"(name=%r, "%self.name+", ".join(["%s=%r"%(k,v) for k,v in list(data.items())])+")"

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
        if self.term_vector_positions:
            result['term_vector_positions'] = self.term_vector_positions
        if self.term_vector_offsets:
            result['term_vector_offsets'] = self.term_vector_offsets
        return result


class GeoPointField(AbstractField):
    def __init__(self, null_value=None, include_in_all=None,
                 lat_lon=None, geohash=None, geohash_precision=None,
                 normalize_lon=None, normalize_lat=None,
                 validate_lon=None, validate_lat=None,
                 *args, **kwargs):
        super(GeoPointField, self).__init__(*args, **kwargs)
        self.null_value = null_value
        self.include_in_all = include_in_all
        self.lat_lon = lat_lon
        self.geohash = geohash
        self.geohash_precision = geohash_precision
        self.normalize_lon = normalize_lon
        self.normalize_lat = normalize_lat
        self.validate_lat = validate_lat
        self.validate_lon = validate_lon
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
        if self.normalize_lon is not None:
            result['normalize_lon'] = self.normalize_lon
        if self.normalize_lat is not None:
            result['normalize_lat'] = self.normalize_lat

        if self.validate_lon is not None:
            result['validate_lon'] = self.validate_lon

        if self.validate_lat is not None:
            result['validate_lat'] = self.validate_lat

        if self.geohash_precision is not None:
            try:
                int(self.geohash_precision)
            except ValueError:
                raise ValueError("geohash_precision must be an integer")
            result['geohash_precision'] = self.geohash_precision
        return result


class NumericFieldAbstract(AbstractField):
    def __init__(self, null_value=None, include_in_all=None, precision_step=4,
                 numeric_resolution=None, ignore_malformed=None, **kwargs):
        super(NumericFieldAbstract, self).__init__(**kwargs)
        self.null_value = null_value
        self.include_in_all = include_in_all
        self.precision_step = precision_step
        self.numeric_resolution = numeric_resolution
        self.ignore_malformed=ignore_malformed

    def as_dict(self):
        result = super(NumericFieldAbstract, self).as_dict()
        if self.null_value is not None:
            result['null_value'] = self.null_value
        if self.include_in_all is not None:
            result['include_in_all'] = self.include_in_all
        if self.precision_step != 4:
            result['precision_step'] = self.precision_step
        if self.numeric_resolution:
            result['numeric_resolution'] = self.numeric_resolution
        if self.ignore_malformed is not None:
            result['ignore_malformed'] = self.ignore_malformed
        return result


class IpField(NumericFieldAbstract):
    def __init__(self, *args, **kwargs):
        super(IpField, self).__init__(*args, **kwargs)
        self.type = "ip"

class ByteField(NumericFieldAbstract):
    def __init__(self, *args, **kwargs):
        super(ByteField, self).__init__(*args, **kwargs)
        self.type = "byte"

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

    def to_es(self, value):
        if isinstance(value, datetime):
            if value.microsecond:
                value = value.replace(microsecond=0)
            return value.isoformat()
        elif isinstance(value, date):
            return date.isoformat()

    def to_python(self, value):
        if isinstance(value, six.string_types) and len(value) == 19:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        elif isinstance(value, six.string_types) and len(value) == 10:
            return date.strptime(value, "%Y-%m-%d")

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

class BinaryField(AbstractField):
    def __init__(self, *args, **kwargs):
        kwargs["tokenize"] = False
        super(BinaryField, self).__init__(*args, **kwargs)
        self.type = "binary"


    def as_dict(self):
        result = super(BinaryField, self).as_dict()
        return result

class MultiField(object):
    def __init__(self, name, type=None, path=None, fields=None):
        self.name = name
        self.type = "multi_field"
        self.path = path
        self.fields = {}
        if fields:
            if isinstance(fields, dict):
                self.fields = dict([(name, get_field(name, data)) for name, data in list(fields.items())])
            elif isinstance(fields, list):
                for field in fields:
                    self.fields[field.name] = field.as_dict()

    def add_fields(self, fields):
        if isinstance(fields, list):
            for field in fields:
                if isinstance(field, AbstractField):
                    self.fields[field.name] = field.as_dict()
                elif isinstance(field, tuple):
                    name, data = field
                    self.fields[name] = data


    def as_dict(self):
        result = {"type": self.type,
                  "fields": {}}
        if self.fields:
            for name, value in list(self.fields.items()):
                if isinstance(value, dict):
                    result['fields'][name] = value
                else:
                    result['fields'][name] = value.as_dict()
        if self.path:
            result['path'] = self.path
        return result
    def get_diff(self, other_mapping):
        """
        Returns a Multifield with diff fields. If not changes, returns None
        :param other_mapping:
        :return: a Multifield or None
        """
        result = MultiField(name=self.name)
        new_fields = set(self.fields.keys())
        if not isinstance(other_mapping, MultiField):
            n_mapping = MultiField(name=self.name)
            n_mapping.add_fields([other_mapping])
            other_mapping = n_mapping

        old_fields = set(other_mapping.fields.keys())
        #we propagate new fields
        added = new_fields - old_fields
        if added:
            result.add_fields([(add, self.fields[add]) for add in added])
            #TODO: raise in field changed
        if len(result.fields) > 0:
            return result
        return None


class AttachmentField(object):
    """An attachment field.

    Requires the mapper-attachments plugin to be installed to be used.

    """

    def __init__(self, name, type=None, path=None, fields=None):
        self.name = name
        self.type = "attachment"
        self.path = path
        #        self.fields = dict([(name, get_field(name, data)) for name, data in fields.items()])
        self.fields = fields

    def as_dict(self):
    #        result_fields = dict((name, value.as_dict())
    #                             for (name, value) in self.fields.items())
        result_fields = self.fields
        result = dict(type=self.type, fields=result_fields)
        if self.path:
            result['path'] = self.path
        return result


class ObjectField(object):
    def __init__(self, name=None, type=None, path=None, properties=None,
                 dynamic=None, enabled=None, include_in_all=None, dynamic_templates=None,
                 include_in_parent=None, include_in_root=None,
                 connection=None, index_name=None, *args, **kwargs):
        self.name = name
        self.type = "object"
        self.path = path
        self.properties = properties
        self.include_in_all = include_in_all
        self.dynamic = dynamic
        self.dynamic_templates = dynamic_templates or []
        self.enabled = enabled
        self.include_in_all = include_in_all
        self.include_in_parent = include_in_parent
        self.include_in_root = include_in_root
        self.connection = connection
        self.index_name = index_name
        if properties:
            self.properties = OrderedDict(sorted([(name, get_field(name, data)) for name, data in properties.items()]))
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
        if self.dynamic is not None:
            result['dynamic'] = self.dynamic
        if self.enabled is not None:
            result['enabled'] = self.enabled
        if self.include_in_all is not None:
            result['include_in_all'] = self.include_in_all
        if self.include_in_parent is not None:
            result['include_in_parent'] = self.include_in_parent
        if self.include_in_root is not None:
            result['include_in_root'] = self.include_in_root

        if self.path is not None:
            result['path'] = self.path

        if self.properties:
            for name, value in list(self.properties.items()):
                result['properties'][name] = value.as_dict()
        return result

    def __str__(self):
        return str(self.as_dict())

    def clear_properties(self):
        """
        Helper function to reset properties
        """
        self.properties = OrderedDict()

    def save(self):
        if self.connection is None:
            raise RuntimeError("No connection available")

        self.connection.put_mapping(doc_type=self.name, mapping=self.as_dict(), indices=self.index_name)

    def get_properties_by_type(self, type, recursive=True, parent_path=""):
        """
        Returns a sorted list of fields that match the type.

        :param type the type of the field "string","integer" or a list of types
        :param recursive recurse to sub object
        :returns a sorted list of fields the match the type

        """
        if parent_path:
            parent_path += "."

        if isinstance(type, str):
            if type == "*":
                type = set(MAPPING_NAME_TYPE.keys()) - set(["nested", "multi_field", "multifield"])
            else:
                type = [type]
        properties = []
        for prop in list(self.properties.values()):
            if prop.type in type:
                properties.append((parent_path + prop.name, prop))
                continue
            elif prop.type == "multi_field" and prop.name in prop.fields and prop.fields[prop.name].type in type:
                properties.append((parent_path + prop.name, prop))
                continue

            if not recursive:
                continue
            if prop.type in ["nested", "object"]:
                properties.extend(
                    prop.get_properties_by_type(type, recursive=recursive, parent_path=parent_path + prop.name))
        return sorted(properties)

    def get_property_by_name(self, name):
        """
        Returns a mapped object.

        :param name the name of the property
        :returns the mapped object or exception NotFoundMapping

        """
        if "." not in name and name in self.properties:
            return self.properties[name]

        tokens = name.split(".")
        object = self
        for token in tokens:
            if isinstance(object, (DocumentObjectField, ObjectField, NestedObject)):
                if token in object.properties:
                    object = object.properties[token]
                    continue
            elif isinstance(object, MultiField):
                if token in object.fields:
                    object = object.fields[token]
                    continue
            raise MappedFieldNotFoundException(token)
        if isinstance(object, (AbstractField, MultiField)):
            return object
        raise MappedFieldNotFoundException(object)


    def get_available_facets(self):
        """
        Returns Available facets for the document
        """
        result = []
        for k, v in list(self.properties.items()):
            if isinstance(v, DateField):
                if not v.tokenize:
                    result.append((k, "date"))
            elif isinstance(v, NumericFieldAbstract):
                result.append((k, "numeric"))
            elif isinstance(v, StringField):
                if not v.tokenize:
                    result.append((k, "term"))
            elif isinstance(v, GeoPointField):
                if not v.tokenize:
                    result.append((k, "geo"))
            elif isinstance(v, ObjectField):
                for n, t in self.get_available_facets():
                    result.append((self.name + "." + k, t))
        return result

    def get_datetime_properties(self, recursive=True):
        """
        Returns a dict of property.path and property.

        :param recursive the name of the property
        :returns a dict

        """
        res = {}
        for name, field in self.properties.items():
            if isinstance(field, DateField):
                res[name] = field
            elif recursive and isinstance(field, ObjectField):
                for n, f in field.get_datetime_properties(recursive=recursive):
                    res[name + "." + n] = f
        return res

    def get_code(self, num=1):
        data = SortedDict(self.as_dict())
        data.pop("properties", [])
        var_name ="obj_%s"%self.name
        code= [var_name+" = "+self.__class__.__name__+"(name=%r, "%self.name+", ".join(["%s=%r"%(k,v) for k,v in list(data.items())])+")"]
        for name, field in list(self.properties.items()):
            num+=1
            vname, vcode = field.get_code(num)
            code.append(vcode)
            code.append("%s.add_property(%s)"%(var_name, vname))

        return var_name, '\n'.join(code)

    def get_diff(self, new_mapping):
        """
        Given two mapping it extracts a schema evolution mapping. Returns None if no evolutions are required
        :param new_mapping: the new mapping
        :return: a new evolution mapping or None
        """
        import copy
        result = copy.deepcopy(new_mapping)
        result.clear_properties()

        no_check_types = (BooleanField, IntegerField, FloatField, DateField, LongField, BinaryField,
                          GeoPointField, IpField)

        old_fields = set(self.properties.keys())
        new_fields = set(new_mapping.properties.keys())
        #we propagate new fields
        added = new_fields - old_fields
        if added:
            for add in added:
                result.add_property(new_mapping.properties[add])

        #we check common fields
        common_fields = new_fields & old_fields

        #removing standard data
        common_fields = [c for c in common_fields if not isinstance(new_mapping.properties[c], no_check_types)]

        for field in common_fields:
            prop = new_mapping.properties[field]
            if isinstance(prop, StringField):
                continue
            if isinstance(prop, MultiField):
                diff = prop.get_diff(self.properties[field])
                if diff:
                    result.add_property(diff)
            elif isinstance(prop, ObjectField):
                diff = self.properties[field].get_diff(prop)
                if diff:
                    result.add_property(diff)

        if len(result.properties) > 0:
            return result
        return None

class NestedObject(ObjectField):
    def __init__(self, *args, **kwargs):
        super(NestedObject, self).__init__(*args, **kwargs)
        self.type = "nested"


class DocumentObjectField(ObjectField):
    def __init__(self, _all=None, _boost=None, _id=None,
                 _index=None, _source=None, _type=None, date_formats=None, _routing=None, _ttl=None,
                 _parent=None, _timestamp=None, _analyzer=None, _size=None, date_detection=None,
                 numeric_detection=None, dynamic_date_formats=None, _meta=None, *args, **kwargs):
        super(DocumentObjectField, self).__init__(*args, **kwargs)
        self._timestamp = _timestamp
        self._all = _all
        self._boost = _boost
        self._id = _id
        self._index = _index
        self._source = _source
        self._routing = _routing
        self._ttl = _ttl
        self._analyzer = _analyzer
        self._size = _size

        self._type = _type
        if self._type is None:
            self._type = {"store": "yes"}

        self._parent = _parent
        self.date_detection = date_detection
        self.numeric_detection = numeric_detection
        self.dynamic_date_formats = dynamic_date_formats
        self._meta = DotDict(_meta or {})


    def get_meta(self, subtype=None):
        """
        Return the meta data.
        """
        if subtype:
            return DotDict(self._meta.get(subtype, {}))
        return  self._meta

    def enable_compression(self, threshold="5kb"):
        self._source.update({"compress": True, "compression_threshold": threshold})

    def as_dict(self):
        result = super(DocumentObjectField, self).as_dict()
        result['_type'] = self._type
        if self._all is not None:
            result['_all'] = self._all
        if self._source is not None:
            result['_source'] = self._source
        if self._boost is not None:
            result['_boost'] = self._boost
        if self._routing is not None:
            result['_routing'] = self._routing
        if self._ttl is not None:
            result['_ttl'] = self._ttl
        if self._id is not None:
            result['_id'] = self._id
        if self._timestamp is not None:
            result['_timestamp'] = self._timestamp
        if self._index is not None:
            result['_index'] = self._index
        if self._parent is not None:
            result['_parent'] = self._parent
        if self._analyzer is not None:
            result['_analyzer'] = self._analyzer
        if self._size is not None:
            result['_size'] = self._size

        if self.date_detection is not None:
            result['date_detection'] = self.date_detection
        if self.numeric_detection is not None:
            result['numeric_detection'] = self.numeric_detection
        if self.dynamic_date_formats is not None:
            result['dynamic_date_formats'] = self.dynamic_date_formats

        return result

    def add_property(self, prop):
        """
        Add a property to the object
        """
        self.properties[prop.name] = prop

    def __repr__(self):
        return "<DocumentObjectField:%s>" % self.name


    def save(self):
        if self.connection is None:
            raise RuntimeError("No connection available")
        self.connection.put_mapping(doc_type=self.name, mapping=self.as_dict(), indices=self.index_name)

    def get_code(self, num=1):
        data = SortedDict(self.as_dict())
        data.pop("properties", [])
        var_name ="doc_%s"%self.name
        code= [var_name+" = "+self.__class__.__name__+"(name=%r, "%self.name+", ".join(["%s=%r"%(k,v) for k,v in list(data.items())])+")"]
        for name, field in list(self.properties.items()):
            num+=1
            vname, vcode = field.get_code(num)
            code.append(vcode)
            code.append("%s.add_property(%s)"%(var_name, vname))

        return '\n'.join(code)

def get_field(name, data, default="object", document_object_field=None, is_document=False):
    """
    Return a valid Field by given data
    """
    if isinstance(data, AbstractField):
        return data
    data = keys_to_string(data)
    _type = data.get('type', default)
    if _type == "string":
        return StringField(name=name, **data)
    elif _type == "binary":
        return BinaryField(name=name, **data)
    elif _type == "boolean":
        return BooleanField(name=name, **data)
    elif _type == "byte":
        return ByteField(name=name, **data)
    elif _type == "short":
        return ShortField(name=name, **data)
    elif _type == "integer":
        return IntegerField(name=name, **data)
    elif _type == "long":
        return LongField(name=name, **data)
    elif _type == "float":
        return FloatField(name=name, **data)
    elif _type == "double":
        return DoubleField(name=name, **data)
    elif _type == "ip":
        return IpField(name=name, **data)
    elif _type == "date":
        return DateField(name=name, **data)
    elif _type == "multi_field":
        return MultiField(name=name, **data)
    elif _type == "geo_point":
        return GeoPointField(name=name, **data)
    elif _type == "attachment":
        return AttachmentField(name=name, **data)
    elif is_document or _type == "document":
        if document_object_field:
            return document_object_field(name=name, **data)
        else:
            data.pop("name",None)
            return DocumentObjectField(name=name, **data)

    elif _type == "object":
        if '_timestamp' in data or "_all" in data:
            if document_object_field:
                return document_object_field(name=name, **data)
            else:
                return DocumentObjectField(name=name, **data)

        return ObjectField(name=name, **data)
    elif _type == "nested":
        return NestedObject(name=name, **data)
    raise RuntimeError("Invalid type: %s" % _type)


class Mapper(object):
    def __init__(self, data, connection=None, is_mapping=False, document_object_field=None):
        """
        Create a mapper object

        :param data: a dict containing the mappings
        :param connection: a connection object
        :param is_mapping: if it's a mapping or index/mapping
        :param document_object_field: the kind of object to be used for document object Field
        :return:
        """
        self.indices = OrderedDict()
        self.mappings = OrderedDict()
        self.is_mapping = is_mapping
        self.connection = connection
        self.full_mappings = False
        self.document_object_field = document_object_field
        self._process(data)

    def _process(self, data):
        """
        Process indexer data
        """
        indices = []
        for indexname, indexdata in list(data.items()):
            idata = []
            for docname, docdata in list(indexdata.get("mappings", {}).items()):
                o = get_field(docname, docdata, document_object_field=self.document_object_field, is_document=True)
                o.connection = self.connection
                o.index_name = indexname
                idata.append((docname, o))
            idata.sort()
            indices.append((indexname, idata))
        indices.sort()
        self.indices = OrderedDict(indices)


    def get_doctypes(self, index, edges=True):
        """
        Returns a list of doctypes given an index
        """
        if index not in self.indices:
            self.get_all_indices()
        return self.indices.get(index, {})

    def get_doctype(self, index, name):
        """
        Returns a doctype given an index and a name
        """
        if index not in self.indices:
            self.get_all_indices()
        return self.indices.get(index, {}).get(name, None)

    def get_property(self, index, doctype, name):
        """
        Returns a property of a given type

        :return a mapped property
        """

        return self.indices[index][doctype].properties[name]

    def get_all_indices(self):
        if not self.full_mappings:
            mappings = self.connection.indices.get_mapping(raw=True)
            self._process(mappings)
            self.full_mappings = True
        return self.indices.keys()

    def migrate(self, mapping, index, doc_type):
        """
        Migrate a ES mapping


        :param mapping: new mapping
        :param index: index of old mapping
        :param doc_type: type of old mapping
        :return: The diff mapping
        """
        old_mapping = self.get_doctype(index, doc_type)
        #case missing
        if not old_mapping:
            self.connection.indices.put_mapping(doc_type=doc_type, mapping=mapping, indices=index)
            return mapping
            # we need to calculate the diff
        mapping_diff = old_mapping.get_diff(mapping)
        if not mapping_diff:
            return None
        from pprint import pprint

        pprint(mapping_diff.as_dict())
        mapping_diff.connection = old_mapping.connection
        mapping_diff.save()


MAPPING_NAME_TYPE = {
    "attachment": AttachmentField,
    "boolean": BooleanField,
    "date": DateField,
    "double": DoubleField,
    "float": FloatField,
    "geopoint": GeoPointField,
    "integer": IntegerField,
    "int": IntegerField,
    "ip": IpField,
    "long": LongField,
    "multifield": MultiField,
    "nested": NestedObject,
    "short": ShortField,
    "string": StringField,
    "binary":BinaryField
}

