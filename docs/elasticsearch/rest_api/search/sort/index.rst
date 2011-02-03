Sort
====

Allows to add one or more sort on specific fields. Each sort can be reversed as well. The sort is defined on a per field level, with special field name for **_score** to sort by score.


.. code-block:: js


    {
        "sort" : [
            { "postDate" : {"reverse" : true} },
            "user",
            { "name" : "desc" },
            { "age" : "desc" },
            "_score"
        ],
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }


If the JSON parser support ordering without an array, the sort request can also be structured as follows:


.. code-block:: js


    {
        "sort" : {
            "postDate" : {"reverse" : true},
            "user" : { },
            "_score" : { }
        },
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }


Sort Values
-----------

The sort values for each document returned are also returned as part of the response.


Geo Distance Sorting
--------------------

Allow to sort by **_geo_distance**. Here is an example:


.. code-block:: js


    {
        "sort" : [
            {
                "_geo_distance" : {
                    "pin.location" : [40, -70],
                    "order" : "asc",
                    "unit" : "km"
                }
            }
        ],
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }


Script Based Sorting
--------------------

Allow to sort based on custom scripts, here is an example:


.. code-block:: js


    {
        "query" : {
            ....
        },
        "sort" : {
            "_script" : { 
                "script" : "doc['field_name'].value * factor",
                "type" : "number",
                "params" : {
                    "factor" : 1.1
                },
                "order" : "asc"
            }
        }
    }


Note, it is recommended, for single custom based script based sorting, to use **custom_score** query instead as sorting based on score is faster.


Memory Considerations
---------------------

When sorting, the relevant sorted field values are loaded into memory. This means that per shard, there should be enough memory to contain them. For string based types, the field sorted on should not be analyzed / tokenized. For numeric types, if possible, it is recommended to explicitly set the type to narrower types (like **short**, **integer** and **float**).


