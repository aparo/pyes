.. _es-guide-reference-query-dsl-geo-bounding-box-filter:

=======================
Geo Bounding Box Filter
=======================

A filter allowing to filter hits based on a point location using a bounding box. Assuming the following indexed document:


.. code-block:: js


    {
        "pin" : {
            "location" : {
                "lat" : 40.12,
                "lon" : -71.34
            }
        }
    }


Then the following simple query can be executed with a **geo_bounding_box** filter:


.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_bounding_box" : {
                    "pin.location" : {
                        "top_left" : {
                            "lat" : 40.73,
                            "lon" : -74.1
                        },
                        "bottom_right" : {
                            "lat" : 40.717,
                            "lon" : -73.99
                        }
                    }
                }
            }
        }
    }


Accepted Formats
================

In much the same way the geo_point type can accept different representation of the geo point, the filter can accept it as well:


Lat Lon As Properties
---------------------

.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_bounding_box" : {
                    "pin.location" : {
                        "top_left" : {
                            "lat" : 40.73,
                            "lon" : -74.1
                        },
                        "bottom_right" : {
                            "lat" : 40.717,
                            "lon" : -73.99
                        }
                    }
                }
            }
        }
    }


Lat Lon As Array
----------------

Format in **[lon, lat]**, note, the order of lon/lat here in order to conform with `GeoJSON <http://geojson.org/>`_.  

.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_bounding_box" : {
                    "pin.location" : {
                        "top_left" : [40.73, -74.1],
                        "bottom_right" : [40.717, -73.99]
                    }
                }
            }
        }
    }


Lat Lon As String
-----------------

Format in **lat,lon**.


.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_bounding_box" : {
                    "pin.location" : {
                        "top_left" : "40.73, -74.1",
                        "bottom_right" : "40.717, -73.99"
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
                "geo_bounding_box" : {
                    "pin.location" : {
                        "top_left" : "drm3btev3e86",
                        "bottom_right" : "drm3btev3e86"
                    }
                }
            }
        }
    }


geo_point Type
==============

The filter *requires* the **geo_point** type to be set on the relevant field.


Multi Location Per Document
===========================

The filter can work with multiple locations / points per document. Once a single location / point matches the filter, the document will be included in the filter


Type
====

The type of the bounding box execution by default is set to **memory**, which means in memory checks if the doc falls within the bounding box range. In some cases, an **indexed** option will perform faster (but note that the **geo_point** type must have lat and lon indexed in this case). Note, when using the indexed option, multi locations per document field are not supported. Here is an example:


.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_bounding_box" : {
                    "pin.location" : {
                        "top_left" : {
                            "lat" : 40.73,
                            "lon" : -74.1
                        },
                        "bottom_right" : {
                            "lat" : 40.717,
                            "lon" : -73.99
                        }
                    },
                    "type" : "indexed"
                }
            }
        }
    }



Caching
=======

The result of the filter is not cached by default. The **_cache** can be set to **true** to cache the *result* of the filter. This is handy when the same bounding box parameters are used on several (many) other queries. Note, the process of caching the first execution is higher when caching (since it needs to satisfy different queries).

