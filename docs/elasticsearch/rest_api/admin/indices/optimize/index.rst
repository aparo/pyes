Optimize
========

The optimize API allows to optimize one or more indices through an API. The optimize process basically optimizes the index for faster search operations (and relates to the number of segments a lucene index within each shard). The optimize operation allows to optimize the number of segments to optimize to.


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/twitter/_optimize'


Request Parameters
------------------

The optimize API accepts the following request parameters:


============================  =================================================================================================================================================================================================================================================================================================================================
 Name                          Description                                                                                                                                                                                                                                                                                                                     
============================  =================================================================================================================================================================================================================================================================================================================================
 **max_num_segments**          The number of segments to optimize to. To fully optimize the index, set it to **1**. Defaults to half the number configured by the merge policy (which in turn defaults to **10**).                                                                                                                                             
 **only_expunge_deletes**      Should the optimize process only expunge segments with deletes in it. In Lucene, a document is not deleted from a segment, just marked as deleted. During a merge process of segments, a new segment is created that does have those deletes. This flag allow to only merge segments that have deletes. Defaults to **false**.  
 **refresh**                   Should a refresh be performed after the optimize. Defaults to **false**.                                                                                                                                                                                                                                                        
 **flush**                     Should a flush be performed after the optimize. Defaults to **false**.                                                                                                                                                                                                                                                          
============================  =================================================================================================================================================================================================================================================================================================================================

Multi Index
-----------

The optimize API can be applied to more than one index with a single call, or even on **_all** the indices.


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/kimchy,elasticsearch/_optimize'
    
    $ curl -XPOST 'http://localhost:9200/_optimize'

