# -*- coding: utf-8 -*-
from __future__ import absolute_import
from pyes.tests import ESTestCase
from pyes import json, ES
from pyes.mappings import Mapper

class MapperTestCase(ESTestCase):
    def test_parser(self):
        self.datamap = json.loads(self.get_datafile("map.json"), cls=ES.decoder)
        _ = Mapper(self.datamap)

        #mapping = self.conn.indices.get_mapping()
        #self.dump(mapping)
