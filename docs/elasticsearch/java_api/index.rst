Java API
========

This section describes the Java API elasticsearch provides. All of elasticsearch APIs are executed using a :doc:`Client <./client/index>`, and are completely asynchronous in nature (either accepts a listener, or return a future).


=================================  ==============================================================================
 API                                Description                                                                  
=================================  ==============================================================================
:doc:`index <./index/index>`       Index a typed JSON document into a specific index and make it searchable.     
:doc:`delete <./delete/index>`     Delete a typed JSON document from a specific index based on its id.           
:doc:`get <./get/index>`           Get a typed JSON document from an index based on its id.                      
:doc:`search <./search/index>`     Execute a search query against one or more indices and get back search hits.  
:doc:`count <./count/index>`       Execute a query against one or more indices and get hits count.               
=================================  ==============================================================================

There is also an evolving :doc:`Administration Java API <./admin/index>`. 


Maven Repository
----------------

ElasticSearch is hosted on `Sonatype <http://www.sonatype.org/>`, with both a `releases repo <http://oss.sonatype.org/content/repositories/releases/>` and a `snapshots repo <http://oss.sonatype.org/content/repositories/snapshots>`. 
