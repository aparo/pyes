.. _es-guide-reference-query-dsl-geo-distance-range-filter:

=========================
Geo Distance Range Filter
=========================

Filters documents that exists within a range from a specific point:


.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "match_all" : {}
            },
            "filter" : {
                "geo_distance_range" : {
                    "from" : "200km",
                    "to" : "400km"
                    "pin.location" : {
                        "lat" : 40,
                        "lon" : -70
                    }
                }
            }
        }
    }


Supports the same point location parameter as the **geo_distance** filter. And also support the common parameters for range (lt, lte, gt, gte, from, to, include_upper and include_lower).
