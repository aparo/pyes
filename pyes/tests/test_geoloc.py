# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from .estestcase import ESTestCase
from ..filters import GeoBoundingBoxFilter, GeoDistanceFilter, GeoPolygonFilter
from ..query import FilteredQuery, MatchAllQuery

#--- Geo Queries Test case
class GeoQuerySearchTestCase(ESTestCase):

    def setUp(self):
        super(GeoQuerySearchTestCase, self).setUp()
        mapping = {
            "pin" : {
                "properties" : {
                    "location" : {
                        "type" : "geo_point"
                    }
                }
            }
        }
        self.conn.delete_index_if_exists("test-mindex")
        self.conn.create_index("test-mindex")
        self.conn.put_mapping(self.document_type, {'properties':mapping}, ["test-mindex"])
        self.conn.index({
            "pin" : {
                "location" : {
                    "lat" : 40.12,
                    "lon" :-71.34
                }
            }
        }, "test-mindex", self.document_type, 1)
        self.conn.index({
            "pin" : {
                "location" : {
                    "lat" : 40.12,
                    "lon" : 71.34
                }
            }
        }, "test-mindex", self.document_type, 2)

        self.conn.refresh(["test-mindex"])

    def tearDown(self):
        self.conn.delete_index_if_exists("test-mindex")

    def test_GeoDistanceFilter(self):
        gq = GeoDistanceFilter("pin.location", {"lat" : 40, "lon" :70}, "200km")
        q = FilteredQuery(MatchAllQuery(), gq)
        resultset = self.conn.search(query=q, indices=["test-mindex"])
        self.assertEquals(resultset.total, 1)

        gq = GeoDistanceFilter("pin.location", [70, 40], "200km")
        q = FilteredQuery(MatchAllQuery(), gq)
        resultset = self.conn.search(query=q, indices=["test-mindex"])
        self.assertEquals(resultset.total, 1)

    def test_GeoBoundingBoxFilter(self):
        gq = GeoBoundingBoxFilter("pin.location", location_tl={"lat" : 40.717, "lon" : 70.99}, location_br={"lat" : 40.03, "lon" : 72.0})
        q = FilteredQuery(MatchAllQuery(), gq)
        resultset = self.conn.search(query=q, indices=["test-mindex"])
        self.assertEquals(resultset.total, 1)

        gq = GeoBoundingBoxFilter("pin.location", [70.99, 40.717], [74.1, 40.03])
        q = FilteredQuery(MatchAllQuery(), gq)
        result2 = self.conn.search(query=q, indices=["test-mindex"])
        self.assertEquals(result2.total, 1)
#        del result['took']
#        del result2['took']
#        self.assertEquals(result, result2)

    def test_GeoPolygonFilter(self):
        gq = GeoPolygonFilter("pin.location", [{"lat" : 50, "lon" :-30},
                                                {"lat" : 30, "lon" :-80},
                                                {"lat" : 80, "lon" :-90}]
                                                )
        q = FilteredQuery(MatchAllQuery(), gq)
        resultset = self.conn.search(query=q, indices=["test-mindex"])
        self.assertEquals(resultset.total, 1)

        gq = GeoPolygonFilter("pin.location", [[ -30, 50],
                                              [ -80, 30],
                                              [ -90, 80]]
                                                )
        q = FilteredQuery(MatchAllQuery(), gq)
        resultset = self.conn.search(query=q, indices=["test-mindex"])
        self.assertEquals(resultset.total, 1)

if __name__ == "__main__":
    unittest.main()
