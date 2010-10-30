#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'
__all__ = ['clean_string', 'ResultSet', "ESRange"]


# Characters that are part of Lucene query syntax must be stripped
# from user input: + - && || ! ( ) { } [ ] ^ " ~ * ? : \
# See: http://lucene.apache.org/java/3_0_2/queryparsersyntax.html#Escaping
SPECIAL_CHARS = [33, 34, 38, 40, 41, 42, 58, 63, 91, 92, 93, 94, 123, 124, 125, 126]
UNI_SPECIAL_CHARS = dict((c, None) for c in SPECIAL_CHARS)
STR_SPECIAL_CHARS = ''.join([chr(c) for c in SPECIAL_CHARS])

class ESRange:
    def __init__(self, field, _from=None, _to=None, include_lower=None, 
                 include_upper=None, from_inclusive=None, 
                 
                 boost=None, type=None, **kwargs):
        """
        type can be "gt", "gte", "lt", "lte"
        
        """
        self.field = field
        self.fromV = _from
        self.to = _to
        self.include_lower = include_lower
        self.include_upper = include_upper
        self.boost = boost
        self.type = type
    
    def _validate(self):
        """
        Validate the ranges
        """
        if self.type is not None:
            if self.type == "gt":
                self._from = False
                self.from_inclusive = False
            elif self.type == "gte":
                self._from = True
                self.from_inclusive = True
            if self.type == "lt":
                self._to = False
                self.to_inclusive = False
            elif self.type == "lte":
                self._to = True
                self.to_inclusive = True
        
    def serialize(self):
        
        self._validate()

        filters = {}
        if self.fromV:
            filters['from'] = self.fromV
        if self.to:
            filters['to'] = self.to
        if self.from_inclusive is not None:
            filters['from_inclusive'] = self.from_inclusive
        if self.to_inclusive is not None:
            filters['to_inclusive'] = self.to_inclusive
        if self.include_lower is not None:
            filters['include_lower'] = self.include_lower
        if self.include_upper is not None:
            filters['include_upper'] = self.include_upper
        if self.boost is not None:
            filters['boost'] = self.boost
        return self.field, filters
    
def clean_string(text):
    """
    Remove Lucene reserved characters from query string
    """
    if isinstance(text, unicode):
        return text.translate(UNI_SPECIAL_CHARS)
    return text.translate(None, STR_SPECIAL_CHARS)
    
class ResultSet(object):
    def __init__(self, results, fix_keys = True, clean_highlight=True):
        """
        results: an es query results dict
        fix_keys: remove the "_" from every key, useful for django views
        clean_highlight: removed empty highlight
        """
        self.results = results
        self._total = None
        self.valid = False
        self.facets = self.results.get('facets', {})
        if 'hits' in self.results:
            self.valid = True
            self.results = self.results['hits']
        if fix_keys:
            self.fix_keys()
        if clean_highlight:
            self.clean_highlight()
        
    @property
    def total(self):
        if self._total is None:
            self._total = 0
            if self.valid:
                self._total = self.results.get("total", 0)
        return self._total
    
    def fix_keys(self):
        """
        Remove the _ from the keys of the results
        """
        if not self.valid:
            return
        
        for hit in self.results['hits']:
            for key, item in hit.items():
                if key.startswith("_"):
                    hit[key[1:]]=item
                    del hit[key]
    
    def clean_highlight(self):
        """
        Remove the empty highlight
        """
        if not self.valid:
            return
        
        for hit in self.results['hits']:
            if 'highlight' in hit:
                hl = hit['highlight']
                for key, item in hl.items():
                    if not item:
                        del hl[key]
    
    def __getattr__(self, name):
        if name in self.results:
            return self.results[name]

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
                data[str(key)] = val
    return data

#def process_query_result(func):
#    @wraps(func)
#    def _func(*args, **kwargs):
#        result = func(*args, **kwargs)
#        if 'hits' in result:
#            setattr(result, "total", result['hits']['total'])
#            if 'hits' in result['hits']:
#                for hit in result['hits']['hits']:
#                    for key, item in hit.items():
#                        if key.startswith("_"):
#                            hit[key[1:]]=item
#                            del hit[key]
#        else:
#            setattr(result, "total", 0)
#        return result
#    return _func
#
#def file_to_attachme