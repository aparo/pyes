#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'

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
                self._total = self.results['hits'].get("total", 0)
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