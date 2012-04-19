# -*- coding: utf-8 -*-
from __future__ import absolute_import
from .estestcase import ESTestCase
from .. import decode_json
from ..mappings import Mapper

class MapperTestCase(ESTestCase):
    def test_parser(self):
        self.datamap = decode_json(self.get_datafile("map.json"))
        _ = Mapper(self.datamap)

        #mapping = self.conn.get_mapping()
        #self.dump(mapping)
