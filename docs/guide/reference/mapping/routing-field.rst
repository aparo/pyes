.. _es-guide-reference-mapping-routing-field:

=============
Routing Field
=============

The routing field allows to control the **_routing** aspect when indexing data and explicit routing control is required.


store / index
=============

The first thing the **_routing** mapping does is to store the routing value provided (**store** set to **yes**) and index it (**index** set to **not_analyzed**). The reason why the routing is stored by default is so reindexing data will be possible if the routing value is completely external and not part of the docs.


required
========

Another aspect of the **_routing** mapping is the ability to define it as required by setting **required** to **true**. This is very important to set when using routing features, as it allows different APIs to make use of it. For example, an index operation will be rejected if no routing value has been provided (or derived from the doc). A delete operation will be broadcasted to all shards if no routing value is provided and **_routing** is required.


path
====

The routing value can be provided as an external value when indexing (and still stored as part of the document, in much the same way **_source** is stored). But, it can also be automatically extracted from the index doc based on a **path**. For example, having the following mapping:


.. code-block:: js


    {
        "comment" : {
            "_routing" : {
                "required" : true,
                "path" : "blog.post_id"
            }
        }
    }


Will cause the following doc to be routed based on the **111222** value:


.. code-block:: js


    {
        "text" : "the comment text"
        "blog" : {
            "post_id" : "111222"
        }
    }


Note, using **path** without explicit routing value provided required an additional (though quite fast) parsing phase.

