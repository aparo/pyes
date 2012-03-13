.. _es-guide-reference-api-search-scroll:

======
Scroll
======

A search request can be scrolled by specifying the **scroll** parameter. The **scroll** parameter is a time value parameter (for example: **scroll=5m**), indicating for how long the nodes that participate in the search will maintain relevant resources in order to continue and support it. This is very similar in its idea to opening a cursor against a database.


A **scroll_id** is returned from the first search request (and from continuous) scroll requests. The **scroll_id** should be used when scrolling (and that's it, no other parameter is required). The scroll id can also be passed as part of the search request body. Note that the **scroll_id** changes for each scroll request and only the most recent one should be used.


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter/tweet/_search?scroll=5m' -d '{
        :ref:`query <es-guide-reference-api-search>`  ry <es-guide-reference-api-search>`  {
            "query_string" : {
                "query" : "some query string here"
            }
        }
    }
    '


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_search/scroll?scroll_id=c2Nhbjs2OzM0NDg1ODpzRlBLc0FXNlNyNm5JWUc1'


Note
    Scrolling is not intended for real time user requests, it is intended for cases like scrolling over large portions of data that exists within elasticsearch to reindex it for example.


For more information on scrolling, see the *scan* search type.

