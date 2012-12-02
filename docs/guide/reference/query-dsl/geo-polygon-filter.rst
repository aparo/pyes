.. _es-guide-reference-query-dsl-geo-polygon-filter:

==================
Geo Polygon Filter
==================

A filter allowing to include hits that only fall within a polygon of points. Here is an example:


.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_polygon" : {
                    "person.location" : {
                        "points" : [
                            {"lat" : 40, "lon" : -70},
                            {"lat" : 30, "lon" : -80},
                            {"lat" : 20, "lon" : -90}
                        ]
                    }
                }
            }
        }
    }


Allowed Formats
===============

Lat Long as Array
-----------------

Format in **[lon, lat]**, note, the order of lon/lat here in order to conform with `GeoJSON <http://geojson.org/>`_.  

.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_polygon" : {
                    "person.location" : {
                        "points" : [
                            [-70, 40],
                            [-80, 30],
                            [-90, 20]
                        ]
                    }
                }
            }
        }
    }


Lat Lon as String
-----------------

Format in **lat,lon**.


.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_polygon" : {
                    "person.location" : {
                        "points" : [
                            "40, -70",
                            "30, -80",
                            "20, -90"
                        ]
                    }
                }
            }
        }
    }


Geohash
-------

.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_polygon" : {
                    "person.location" : {
                        "points" : [
                            "drn5x1g8cu2y",
                            "30, -80",
                            "20, -90"
                        ]
                    }
                }
            }
        }
    }


geo_point Type
==============

The filter *requires* the **geo_point** type to be set on the relevant field.


Caching
=======

The result of the filter is not cached by default. The **_cache** can be set to **true** to cache the *result* of the filter. This is handy when the same points parameters are used on several (many) other queries. Note, the process of caching the first execution is higher when caching (since it needs to satisfy different queries).

