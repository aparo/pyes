.. _es-guide-reference-java-api-index_:

======
Index_
======

The index API allows to index a typed JSON document into a specific index and make it searchable. The following example index the JSON document into an index called twitter, under a type called tweet, with id valued 1:


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


The source to be indexed is a binary array representing the json to be indexed. It can be easily built using elasticsearch special **XContent** JSON Builder.


For more information on the index operation, check out the REST :ref:`index <es-guide-reference-java-api-index_>`  docs.


Source Parameter
================

The source parameter is a JSON. It can be provided in different means, as a native **byte[]**, as a **String**, be built using the **jsonBuilder** and as a **Map** (that will be automatically converted to its JSON equivalent). All different types are converted to **byte[]** (so a String is converted to a **byte[]**), so its preferable, if the JSON is in this form already, to use it. The **jsonBuilder** is highly optimized JSON generator that is built right into a **byte[]**.


Operation Threading
===================

The index API allows to set the threading model the operation will be performed when the actual execution of the API is performed on the same node (the API is executed on a shard that is allocated on the same server).


The options are to execute the operation on a different thread, or to execute it on the calling thread (note that the API is still async). By default, **operationThreaded** is set to **true** which means the operation is executed on a different thread.

