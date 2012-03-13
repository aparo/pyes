.. _es-guide-reference-java-api-percolate:

=========
Percolate
=========

The percolator allows to register queries against an index, and then send **percolate** requests which include a doc, and getting back the queries that match on that doc out of the set of registered queries.


Read the main :ref:`percolate <es-guide-reference-java-api-percolate>`  colate>`  documentation before reading this guide.

.. code-block:: java


    //This is the query we're registering in the percolator
    QueryBuilder qb = termQuery("content", "amazing");
    
    //Index the query = register it in the percolator
    client.prepareIndex("_percolator", "myIndexName", "myDesignatedQueryName")
        .setSource(qb)
        .setRefresh(true) //Needed when the query shall be available immediately
        .execute().actionGet();


This indexes the above term query under the name *myDesignatedQueryName*.

In order to check a document against the registered queries, use this code:


.. code-block:: java


    //Build a document to check against the percolator
    XContentBuilder docBuilder = XContentFactory.jsonBuilder().startObject();
    docBuilder.field("doc").startObject(); //This is needed to designate the document
    docBuilder.field("content", "This is amazing!");
    docBuilder.endObject(); //End of the doc field
    docBuilder.endObject(); //End of the JSON root object
    //Percolate
    PercolateResponse response = 
    	client.preparePercolate("myIndexName", "myDocumentType").setSource(docBuilder).execute().actionGet();
    //Iterate over the results
    for(String result : response) {
        //Handle the result which is the name of
        //the query in the percolator
    }


