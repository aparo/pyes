.. _es-guide-reference-java-api-bulk:

====
Bulk
====

The bulk API allows one to index and delete several documents in a single request. Here is a sample usage:


.. code-block:: java


    import static org.elasticsearch.common.xcontent.XContentFactory.*;
    
    BulkRequestBuilder bulkRequest = client.prepareBulk();
    
    // either use client#prepare, or use Requests# to directly build index/delete requests
    bulkRequest.add(client.prepareIndex("twitter", "tweet", "1")
            .setSource(jsonBuilder()
                        .startObject()
                            .field("user", "kimchy")
                            .field("postDate", new Date())
                            .field("message", "trying out Elastic Search")
                        .endObject()
                      )
            );
    
    bulkRequest.add(client.prepareIndex("twitter", "tweet", "2")
            .setSource(jsonBuilder()
                        .startObject()
                            .field("user", "kimchy")
                            .field("postDate", new Date())
                            .field("message", "another post")
                        .endObject()
                      )
            );
            
    BulkResponse bulkResponse = bulkRequest.execute().actionGet();
    if (bulkResponse.hasFailures()) {
        // process failures by iterating through each bulk response item
    }

