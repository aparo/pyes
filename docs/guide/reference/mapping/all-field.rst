.. _es-guide-reference-mapping-all-field:

=========
All Field
=========

The idea of the **_all** field is that it includes the text of one or more other fields within the document indexed. It can come very handy especially for search requests, where we want to execute a search query against the content of a document, without knowing which fields to search on. This comes at the expense of CPU cycles and index size.


The **_all** fields can be completely disabled. Explicit field mapping and object mapping can be excluded / included in the **_all** field. By default, it is enabled and all fields are included in it for ease of use.


One of the nice features of the **_all** field is that it takes into account specific fields boost levels. Meaning that if a title field is boosted more than content, the title (part) in the **_all** field will mean more than the content (part) in the **_all** field.


Here is a sample mapping:


.. code-block:: js


    {
        "person" : {
            "_all" : {"enabled" : true},
            "properties" : {
                "name" : {
                    "type" : "object",
                    "dynamic" : false,
                    "properties" : {
                        "first" : {"type" : "string", "store" : "yes", "include_in_all" : false},
                        "last" : {"type" : "string", "index" : "not_analyzed"}
                    }
                },
                "address" : {
                    "type" : "object",
                    "include_in_all" : false,
                    "properties" : {
                        "first" : {
                            "properties" : {
                                "location" : {"type" : "string", "store" : "yes", "index_name" : "firstLocation"}
                            }
                        },
                        "last" : {
                            "properties" : {
                                "location" : {"type" : "string"}
                            }
                        }
                    }
                },
                "simple1" : {"type" : "long", "include_in_all" : true},
                "simple2" : {"type" : "long", "include_in_all" : false}
            }
        }
    }


The **_all** fields allows for **store**, **term_vector** and **analyzer** (with specific **index_analyzer** and **search_analyzer**) to be set.


Highlighting
------------

For any field to allow :ref:`highlighting <es-guide-reference-api-search-highlighting>`  ch-highlighting`  it has to be either stored or part of the **_source** field. By default **_all** field does not qualify for either, so highlighting for it does not yield any data.

Although it is possible to **store** the **_all** field, it is basically an aggregation of all fields, which means more data will be stored, and highlighting it might produce strange results.

