.. _es-guide-reference-mapping-ttl-field:

=========
Ttl Field
=========

A lot of documents naturally come with an expiration date. Documents can therefore have a **_ttl** (time to live), which will cause the expired documents to be deleted automatically.


enabled
=======

By default it is disabled, in order to enable it, the following mapping should be defined:


.. code-block:: js


    {
        "tweet" : {
            "_ttl" : { "enabled" : true }
        }
    }


store / index
=============

By default the **_ttl** field has **store** set to **yes** and **index** set to **not_analyzed**. Note that **index** property has to be set to **not_analyzed** in order for the purge process to work.


default
=======

You can provide a per index/type default **_ttl** value as follows:


.. code-block:: js


    {
        "tweet" : {
            "_ttl" : { "enabled" : true, "default" : "1d" }
        }
    }


In this case, if you don't provide a **_ttl** value in your query or in the **_source** all tweets will have a **_ttl** of one day.


If no **default** is set and no **_ttl** value is given then the document has an infinite **_ttl** and will not expire.


You can dynamically update the **default** value using the put mapping API. It won't change the **_ttl** of already indexed documents but will be used for future documents.


Note on documents expiration
============================

Expired documents will be automatically deleted regularly. You can dynamically set the **indices.ttl.interval** to fit your needs. The default value is **60s**.


The deletion orders are processed by bulk. You can set **indices.ttl.bulk_size** to fit your needs. The default value is **10000**.


Note that the expiration procedure handle versioning properly so if a document is updated between the collection of documents to expire and the delete order, the document won't be deleted.
