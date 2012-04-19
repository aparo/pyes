# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from .estestcase import ESTestCase
from ..query import TermQuery
from ..es import file_to_attachment
import os

class TestFileSaveTestCase(ESTestCase):
    def test_filesave(self):
        mapping = {
            "my_attachment": {"type": "attachment",
                              'fields': {
                                  "file": {'store': "yes"},
                                  "date": {'store': "yes"},
                                  "author": {'store': "yes"},
                                  "title": {'store': "yes"}, }
            }
        }
        self.conn.create_index(self.index_name)
        self.conn.put_mapping(self.document_type, {self.document_type: {'properties': mapping}}, self.index_name)
        self.conn.refresh(self.index_name)
        self.conn.get_mapping(self.document_type, self.index_name)
        name = "map.json"
        content = self.get_datafile(name)
        self.conn.put_file(self.get_datafile_path(name), self.index_name, self.document_type, 1, name=name)
        self.conn.refresh(self.index_name)
        _ = self.conn.get_mapping(self.document_type, self.index_name)
        nname, ncontent = self.conn.get_file(self.index_name, self.document_type, 1)
        self.assertEquals(name, nname)
        self.assertEquals(content, ncontent)


class QueryAttachmentTestCase(ESTestCase):
    def setUp(self):
        super(QueryAttachmentTestCase, self).setUp()
        mapping = {
            "attachment": {"type": "attachment",
                           'fields': {
                               "file": {'store': "yes"},
                               "date": {'store': "yes"},
                               "author": {'store': "yes"},
                               "title": {'store': "yes", "term_vector": "with_positions_offsets"},
                               "attachment": {'store': "yes"},
                               }
            },
            'uuid': {'boost': 1.0,
                     'index': 'not_analyzed',
                     'store': 'yes',
                     'type': u'string'}
        }
        #        mapping = {
        #            self.document_type: {
        #                "_index": {"enabled": "yes"},
        #                "_id": {"store": "yes"},
        #                "properties": {
        #                    "attachment": {
        #                        "type": "attachment",
        #                        "fields": {
        #                            "title": {"store": "yes", "term_vector" : "with_positions_offsets"},
        #                            "attachment": {"store":"yes", "term_vector" : "with_positions_offsets"}
        #                        },
        #                        "store":"yes"
        #
        #                    },
        #                    "uuid": {"type": "string", "store": "yes", "index": "not_analyzed"}
        #                },
        #                "_all": {"store": "yes", "term_vector": "with_positions_offsets"}
        #            }
        #        }
        self.conn.debug_dump = True
        self.conn.create_index(self.index_name)
        self.conn.put_mapping(self.document_type, {self.document_type: {'properties': mapping}}, self.index_name)
        self.conn.refresh(self.index_name)
        self.conn.get_mapping(self.document_type, self.index_name)
        self.conn.index({"attachment": file_to_attachment(self.get_datafile_path("testXHTML.html")), "uuid": "1"}
            , self.index_name, self.document_type, 1)
        self.conn.refresh(self.index_name)

    def test_TermQuery(self):
        q = TermQuery("uuid", "1").search(
            fields=['attachment', 'attachment.author', 'attachment.title', 'attachment.date'])
        #        q = TermQuery("uuid", "1", fields=['*'])
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(resultset.hits[0]['fields']['attachment.author'], u'Tika Developers')

if __name__ == "__main__":
    unittest.main()
