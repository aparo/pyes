.. _es-guide-reference-api-search-scroll:

======
Scroll
======

Note, scroll is currently an experimental feature.


A search request can be scrolled by specifying the **scroll** parameter. The **scroll** parameter is a time value parameter (for example: **scroll=5m**), indicating for how long the nodes that participate in the search will maintain relevant resources in order to continue and support it. This is very similar in its idea to opening a cursor against a database.


A **scroll_id** is returned from the first search request (and from continuos) scroll requests. The **scroll_id** should be used when scrolling (and thats it, no other parameter is required). The scroll id can also be passed as part of the search request body.


Note
    Scrolling is not intended for real time user requests, it is intended for cases like scrolling over large portions of data that exists within elasticsearch to reindex it for example.

