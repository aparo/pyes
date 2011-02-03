Groovy API
==========

This section describes the `Groovy <http://groovy.codehaus.org/>` API elasticsearch provides. All of elasticsearch APIs are executed using a :doc:`GClient <./client/index>`, and are completely asynchronous in nature (either accepts a listener, or return a future).


The Groovy API is a wrapper on top of the :doc:`Java API </elasticsearch/java_api/index>` exposing it in a groovier manner. The execution options for each API follow a similar manner and covered in :doc:`the anatomy of a Groovy API <./anatomy/index>`. The following section lists more detailed explanation of the more common APIs:


=================================  ==============================================================================
 API                                Description                                                                  
=================================  ==============================================================================
:doc:`index <./index/index>`       Index a typed JSON document into a specific index and make it searchable.     
:doc:`delete <./delete/index>`     Delete a typed JSON document from a specific index based on its id.           
:doc:`get <./get/index>`           Get a typed JSON document from an index based on its id.                      
:doc:`search <./search/index>`     Execute a search query against one or more indices and get back search hits.  
:doc:`count <./count/index>`       Execute a query against one or more indices and get hits count.               
=================================  ==============================================================================

Maven Repository
----------------

ElasticSearch is hosted on `Sonatype <http://www.sonatype.org/>`, with both a `releases repo <http://oss.sonatype.org/content/repositories/releases/>` and a `snapshots repo <http://oss.sonatype.org/content/repositories/snapshots>`. 
