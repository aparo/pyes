# -*- coding: utf-8 -*-

class SettingsBuilder(object):
    def __init__(self, settings=None, mappings=None):
        self.settings = settings or {'index.number_of_replicas': 1,
                                     "index.number_of_shards": 5}
        self.mappings = mappings or {}

    def add_mapping(self, data, name=None):
        """
        Add a new mapping
        """
        if name:
            self.mappings[name] = data
        else:
            if isinstance(data, dict):
                self.mappings.update(data)
            elif isinstance(data, list):
                for d in data:
                    self.mappings.update(d)

    def as_dict(self):
        """Returns a dict"""
        return {"settings": self.settings,
                "mappings": self.mappings}
