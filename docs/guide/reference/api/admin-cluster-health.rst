.. _es-guide-reference-api-admin-cluster-health:

====================
Admin Cluster Health
====================

The cluster health API allows to get a very simple status on the health of the cluster.


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_cluster/health?pretty=true'
    {                                                                                            
      "cluster_name" : "testcluster",                                                              
      "status" : "green",                                                                        
      "timed_out" : false,                                                                       
      "number_of_nodes" : 2,                                                                     
      "number_of_data_nodes" : 2,                                                                
      "active_primary_shards" : 5,                                                               
      "active_shards" : 10,                                                                      
      "relocating_shards" : 0,                                                                   
      "initializing_shards" : 0,                                                                 
      "unassigned_shards" : 0                                                                    
    }


The API can also be executed against one or more indices to get just the specified indices health:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_cluster/health/test1,test2'


The cluster health is status is: **green**, **yellow** or **red**. On the shard level, a **red** status indicates that the specific shard is not allocated in the cluster, **yellow** means that the primary shard is allocated but replicas are not, and **green** means that all shards are allocated. The index level status is controlled by the worst shard status. The cluster status is controlled by the worst index status.


One of the main benefits of the API is the ability to wait until the cluster reaches a certain health level. For example, the following Will wait till the cluster reaches the **green** level for 50 seconds (if it reaches the **green** status beforehand, it will return):


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_cluster/health?wait_for_status=green&timeout=50s'


Request Parameters
==================

The cluster health API accepts the following request parameters:


============================  =============================================================================================================================================================================================================================
 Name                          Description                                                                                                                                                                                                                 
============================  =============================================================================================================================================================================================================================
level                         Can be one of **cluster**, **indices** or **shards**. Controls the details level of the health information returned. Defaults to **cluster**.                                                                                
wait_for_status               One of **green**, **yellow** or **red**. Will wait (until the timeout provided) until the status of the cluster changes to the one provided. By default, will not wait for any status.                                       
wait_for_relocating_shards    A number controlling to how many relocating shards to wait for. Usually will be **0** to indicate to wait till all relocation have happened. Defaults to not to wait.                                                        
wait_for_nodes                The request waits until the specified number **N** of nodes is available. It also accepts **>=N**, **<=N**, **>N** and **<N**. Alternatively, it is possible to use **ge(N)**, **le(N)**, **gt(N)** and **lt(N)** notation.  
timeout                       A time based parameter controlling how long to wait if one of the wait_for_XXX are provided. Defaults to **30s**.                                                                                                            
============================  =============================================================================================================================================================================================================================

The following is example of getting cluster health at the **shards** level:


.. code-block:: js


    $ curl -XGET 'http://localhost:9200/_cluster/health/twitter?level=shards'

