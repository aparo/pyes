#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'

class HighLighter:
    """
    This object manage the highlighting
    """
    def __init__(self, pre_tags = None, post_tags = None, fields = None):
        self.pre_tags = pre_tags
        self.post_tags = post_tags
        self.fields = fields or {}
    
    def add_field(self, name, fragment_size=150, number_of_fragments=3):
        """
        Add a field to Highlinghter
        """
        data = {}
        if fragment_size:
            data['fragment_size'] = fragment_size
        if number_of_fragments is not None:
            data['number_of_fragments'] = number_of_fragments
            
        self.fields[name] = data

    def serialize(self):
        res = {}
        if self.pre_tags:
            res["pre_tags"] = self.pre_tags
        if self.post_tags:
            res["post_tags"] = self.post_tags
        if self.fields:
            res["fields"] = self.fields
        else:
            res["fields"] = {"_all" : {}}
        return res
