.. _es-guide-reference-java-api-index_:

======
Index_
======

The index API allows one to index a typed JSON document into a specific index and make it searchable. The following example indexes a JSON document into an index called twitter, under a type called tweet, with id valued 1:


.. code-block:: java


    import static org.elasticsearch.common.xcontent.XContentFactory.*;
    
    IndexResponse response = client.prepareIndex("twitter", "tweet", "1")
            .setSource(jsonBuilder()
                        .startObject()
                            .field("user", "kimchy")
                            .field("postDate", new Date())
                            .field("message", "trying out Elastic Search")
                        .endObject()
                      )
            .execute()
            .actionGet();


The source to be indexed a json object that can be built easily using the elasticsearch **XContent** JSON Builder.


For more information on the index operation, check out the REST :ref:`index <es-guide-reference-java-api-index_>`  docs.


Source Parameter
================

The source parameter represents a JSON object. It can be provided in different ways: as a native **byte[]**, as a **String**, as a byte array built using the **jsonBuilder**, or as a **Map** (that will be automatically converted to its JSON equivalent). Internally, each type is converted to **byte[]** (so a String is converted to a **byte[]**). Therefore, if the object is in this form already, then use it. The **jsonBuilder** is highly optimized JSON generator that directly constructs a **byte[]**.


Operation Threading
===================

The index API allows to set the threading model the operation will be performed when the actual execution of the API is performed on the same node (the API is executed on a shard that is allocated on the same server).


The options are to execute the operation on a different thread, or to execute it on the calling thread (note that the API is still async). By default, **operationThreaded** is set to **true** which means the operation is executed on a different thread.

