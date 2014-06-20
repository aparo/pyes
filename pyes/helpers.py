# -*- coding: utf-8 -*-

class SettingsBuilder(object):
    def __init__(self, settings=None, mappings=None):
        self.settings = settings or {'index.number_of_replicas': 1,
                                     "index.number_of_shards": 5}
        self.mappings = {}
        if mappings:
            self.add_mapping(mappings)

    def add_mapping(self, data, name=None):
        """
        Add a new mapping
        """
        from .mappings import DocumentObjectField
        from .mappings import NestedObject
        from .mappings import ObjectField

        if isinstance(data, (DocumentObjectField, ObjectField, NestedObject)):
            self.mappings[data.name] = data.as_dict()
            return

        if name:
            self.mappings[name] = data
            return
            if isinstance(data, dict):
                self.mappings.update(data)
            elif isinstance(data, list):
                for d in data:
                    if isinstance(d, dict):
                        self.mappings.update(d)
                    elif isinstance(d, DocumentObjectField):
                        self.mappings[d.name] = d.as_dict()
                    else:
                        name, data = d
                        self.add_mapping(data, name)

    def as_dict(self):
        """Returns a dict"""
        return {"settings": self.settings,
                "mappings": self.mappings}


class StatusProcessor(object):
    def __init__(self, connection):
        self.connection = connection
        self.cstate = connection.cluster_state()
        self.cstatus = connection.status()
        self.cnodes = connection.cluster_nodes()
        nodes = [({"code":k, "name":v["name"]}, v["transport_address"]) for k, v in self.cstate.nodes.items()]
        nodes = sorted(nodes, key=lambda v: v[0]["name"])
        self.node_names = [k for k, v in nodes]

    def get_indices_data(self):
        indices_names = sorted(self.cstatus.indices.keys())
        data = {}
        for indexname in indices_names:
            data['name'] = indexname
            data['data'] = self.cstatus.indices[indexname]
            nodes = []
            for nodename in self.node_names:
                shards = []
                for shardid, shards_replica in sorted(data['data']['shards'].items()):
                    for shard in shards_replica:
                        if shard["routing"]['node'] == nodename["code"]:
                            shards.append((shardid, shard))
                nodes.append((nodename["name"], shards))
            data['nodes'] = nodes
            yield data
            data = {}
