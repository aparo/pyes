# -*- coding: utf-8 -*-
from __future__ import absolute_import
import base64
from urllib import quote
import array
import uuid

__all__ = ['clean_string', "ESRange", "ESRangeOp", "string_b64encode", "string_b64decode", "make_path", "make_id"]

def make_id(value):
    """
    Build a string id from a value
    :param value: a text value
    :return: a string
    """
    if isinstance(value, unicode):
        value=value.encode("utf8", errors="ignore")
    from hashlib import md5
    val = uuid.UUID(bytes=md5(value).digest(), version=4)

    return base64.urlsafe_b64encode(val.get_bytes())[:-2]

def make_path(*path_components):
    """
    Smash together the path components. Empty components will be ignored.
    """
    path_components = [quote(str(component), "") for component in path_components if component]
    path = '/'.join(path_components)
    if not path.startswith('/'):
        path = '/' + path
    return path

def string_b64encode(s):
    """
    This function is useful to convert a string to a valid id to be used in ES.
    You can use it to generate an ID for urls or some texts
    """
    return base64.urlsafe_b64encode(s).strip('=')


def string_b64decode(s):
    return base64.urlsafe_b64decode(s + '=' * (len(s) % 4))

# Characters that are part of Lucene query syntax must be stripped
# from user input: + - && || ! ( ) { } [ ] ^ " ~ * ? : \
# See: http://lucene.apache.org/java/3_0_2/queryparsersyntax.html#Escaping
SPECIAL_CHARS = [33, 34, 38, 40, 41, 42, 45, 58, 63, 91, 92, 93, 94, 123, 124, 125, 126]
UNI_SPECIAL_CHARS = dict((c, None) for c in SPECIAL_CHARS)
STR_SPECIAL_CHARS = ''.join([chr(c) for c in SPECIAL_CHARS])

class EqualityComparableUsingAttributeDictionary(object):
    """
    Instances of classes inheriting from this class can be compared
    using their attribute dictionary (__dict__). See GitHub issue
    128 and http://stackoverflow.com/q/390640
    """

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self == other


class ESRange(EqualityComparableUsingAttributeDictionary):
    def __init__(self, field, from_value=None, to_value=None, include_lower=None,
                 include_upper=None, boost=None, **kwargs):
        self.field = field
        self.from_value = from_value
        self.to_value = to_value
        self.include_lower = include_lower
        self.include_upper = include_upper
        self.boost = boost

    def negate(self):
        """Reverse the range"""
        self.from_value, self.to_value = self.to_value, self.from_value
        self.include_lower, self.include_upper = self.include_upper, self.include_lower

    def serialize(self):
        filters = {}
        if self.from_value is not None:
            filters['from'] = self.from_value
        if self.to_value is not None:
            filters['to'] = self.to_value
        if self.include_lower is not None:
            filters['include_lower'] = self.include_lower
        if self.include_upper is not None:
            filters['include_upper'] = self.include_upper
        if self.boost is not None:
            filters['boost'] = self.boost
        return self.field, filters


class ESRangeOp(ESRange):
    def __init__(self, field, op, value, boost=None):
        from_value = to_value = include_lower = include_upper = None
        if op == "gt":
            from_value = value
            include_lower = False
        elif op == "gte":
            from_value = value
            include_lower = True
        if op == "lt":
            to_value = value
            include_upper = False
        elif op == "lte":
            to_value = value
            include_upper = True
        super(ESRangeOp, self).__init__(field, from_value, to_value,
            include_lower, include_upper, boost)


def clean_string(text):
    """
    Remove Lucene reserved characters from query string
    """
    if isinstance(text, unicode):
        return text.translate(UNI_SPECIAL_CHARS).strip()
    return text.translate(None, STR_SPECIAL_CHARS).strip()


def keys_to_string(data):
    """
    Function to convert all the unicode keys in string keys
    """
    if isinstance(data, dict):
        for key in list(data.keys()):
            if isinstance(key, unicode):
                value = data[key]
                val = keys_to_string(value)
                del data[key]
                data[key.encode("utf8", "ignore")] = val
    return data
