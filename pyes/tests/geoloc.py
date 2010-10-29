#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""
import unittest
from pyes.tests import ESTestCase
from pyes import *

#--- Geo Queries Test case
class GeoQuerySearchTestCase(ESTestCase):
    def setUp(self):
        super(GeoQuerySearchTestCase, self).setUp()
        mapping ={
                "pin" : {
                    "properties" : {
                        "location" : {
                            "type" : "geo_point"
                        }
                    }
                }
            } 
        self.conn.create_index("test-index")
        self.conn.put_mapping("test-type", {'properties':mapping}, ["test-index"])
        self.conn.index({
                            "pin" : {
                                "location" : {
                                    "lat" : 40.12,
                                    "lon" : -71.34
                                }
                            }
                        }, "test-index", "test-type", 1)
        self.conn.index({
                            "pin" : {
                                "location" : {
                                    "lat" : 40.12,
                                    "lon" : 71.34
                                }
                            }
                        }, "test-index", "test-type", 2)

        self.conn.refresh(["test-index"])
        
        #Sleep to allow ElasticSearch to set up 
        #mapping and indices before running tests
        #sleep(0.5)

    def test_GeoDistanceQuery(self):
        gq = GeoDistanceQuery("pin.location", {"lat" : 40, "lon" : -70}, "200km")
        q = FilteredQuery(MatchAllQuery(), gq)
        result = self.conn.search(query = q, indexes=["test-index"])
        self.assertEquals(result['hits']['total'], 1)

        gq = GeoDistanceQuery("pin.location", [40, -70], "200km")
        q = FilteredQuery(MatchAllQuery(), gq)
        result = self.conn.search(query = q, indexes=["test-index"])
        self.assertEquals(result['hits']['total'], 1)

    def test_GeoBoundingBoxQuery(self):
        gq = GeoBoundingBoxQuery("pin.location", location_tl = {"lat" : 40.717, "lon" : 70.99}, location_br = {"lat" : 40.03, "lon" : 72.0})
        q = FilteredQuery(MatchAllQuery(), gq)
        result = self.conn.search(query = q, indexes=["test-index"])
        self.assertEquals(result['hits']['total'], 1)

        gq = GeoBoundingBoxQuery("pin.location",  [40.717, 70.99], [40.03, 74.1])
        q = FilteredQuery(MatchAllQuery(), gq)
        result = self.conn.search(query = q, indexes=["test-index"])
        self.assertEquals(result['hits']['total'], 1)

    def test_GeoPolygonQuery(self):
        gq = GeoPolygonQuery("pin.location", [{"lat" : 50, "lon" : -30},
                                                {"lat" : 30, "lon" : -80},
                                                {"lat" : 80, "lon" : -90}]
                                                )
        q = FilteredQuery(MatchAllQuery(), gq)
        result = self.conn.search(query = q, indexes=["test-index"])
        self.assertEquals(result['hits']['total'], 1)

        gq = GeoPolygonQuery("pin.location", [[ 50, -30],
                                              [ 30, -80],
                                              [ 80, -90]]
                                                )
        q = FilteredQuery(MatchAllQuery(), gq)
        result = self.conn.search(query = q, indexes=["test-index"])
        self.assertEquals(result['hits']['total'], 1)

if __name__ == "__main__":
    unittest.main()