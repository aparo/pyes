.. _es-guide-reference-mapping-id-field:

========
Id Field
========

Each document indexed is associated with an id and a type. The **_id** field can be used to index just the id, and possible also store it. By default it is not indexed and not stored (thus, not created).


Note, even though the **_id** is not indexed, all the APIs still work (since they work with the **_uid** field), as well as fetching by ids using **term**, **term** or **prefix** queries / filters (including the specific **ids** query/filter).


The **_id** field can be enabled to be indexed, and possibly stored, using:


.. code-block:: js


    {
        "tweet" : {
            :ref:`_id" : {"index <es-guide-reference-mapping>`  ex <es-guide-reference-mapping>`  "not_analyzed", "store" : "yes"}
        }
    }


In order to maintain backward compatibility, a node level setting **index.mapping._id.indexed** can be set to **true** to make sure that the id is indexed when upgrading to **0.16**, though its recommended to not index the id.


The **_id** mapping can also be associated with a **path** that will be used to extract the id from a different location in the source document. For example, having the following mapping:


.. code-block:: js


    {
        "tweet" : {
            "_id" : {
                "path" : "post_id"
            }
        }
    }


Will cause **1** to be used as the id for:


.. code-block:: js


    {
        "message" : "You know, for Search",
        "post_id" : "1"
    }


This does require an additional lightweight parsing step while indexing, in order to extract the id in order to decide which shard the index operation will be executed on.