.. _es-guide-reference-api-search-fields:

======
Fields
======

Allows to selectively load specific fields for each document represented by a search hit. Defaults to load the internal **_source** field.


.. code-block:: js


    {
        "fields" : ["user", "postDate"],
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }


The fields will automatically load stored fields (**store** mapping set to **yes**), or, if not stored, will load the **_source** and extract it from it (allowing to return nested document object).


***** can be used to load all stored fields from the document.


An empty array will cause only the **_id** and **_type** for each hit to be returned, for example:


.. code-block:: js


    {
        "fields" : [],
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }


Script fields can also be automatically detected and used as fields, so things like **_source.obj1.obj2** can be used, though not recommended, as **obj1.obj2** will work as well.


Partial
-------

When loading data from **_source**, partial fields can be used to use wildcards to control what part of the **_source** will be loaded based on **include** and **explude** patterns. For example:


.. code-block:: js


    {
        "query" : {
            "match_all" : {}
        },
        "partial_fields" : {
            "partial1" : {
                "include" : "obj1.obj2.*",
            }
        }
    }


And one that will also exclude **obj1.obj3**:


.. code-block:: js


    {
        "query" : {
            "match_all" : {}
        },
        "partial_fields" : {
            "partial1" : {
                "include" : "obj1.obj2.*",
                "exclude" : "obj1.obj3.*"
            }
        }
    }


Both **include** and **exclude** support multiple patterns:


.. code-block:: js


    {
        "query" : {
            "match_all" : {}
        },
        "partial_fields" : {
            "partial1" : {
                "include" : ["obj1.obj2.*", "obj1.obj4.*"],
                "exclude" : "obj1.obj3.*"
            }
        }
    }

