#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""
import unittest
from pyes.tests import ESTestCase
from pyes import TermQuery, decode_json
from time import sleep
from pyes.mappings import *
from pyes.utils import keys_to_string
import os

class MapperTestCase(ESTestCase):
    def setUp(self):
        super(MapperTestCase, self).setUp()
        self.datamap = decode_json(open(os.path.join("data", "map.json"), "rb").read())        

    def test_parser(self):
        mapper = Mapper(self.datamap)
        mapping=self.conn.get_mapping()
        self.dump(mapping)
#        for key, value in self.datatomap['properties'].items():
#            r=mapper.get_field(key, value)
#            print r.to_json()


if __name__ == "__main__":
    unittest.main()