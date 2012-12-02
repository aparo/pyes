.. _es-guide-reference-api-admin-indices-update-settings:

=============================
Admin Indices Update Settings
=============================

Change specific index level settings in real time.


The REST endpoint is **/_settings** (to update all indices) or **{index}/_settings** to update one (or more) indices settings. The body of the request includes the updated settings, for example:


.. code-block:: js

    {
        "index" : {
            "number_of_replicas" : 4
        }
    }


The above will change the number of replicas to 4 from the current number of replicas. Here is a curl example:


.. code-block:: js

    curl -XPUT 'localhost:9200/my_index/_settings' -d '
    {
        "index" : {
            "number_of_replicas" : 4
        }
    }
    '


Below is the list of settings that can be changed using the update settings API:


==========================================================  =================================================================================================================================================================================================================================================================
 Setting                                                     Description                                                                                                                                                                                                                                                     
==========================================================  =================================================================================================================================================================================================================================================================
**index.number_of_replicas**                                The number of replicas each shard has.                                                                                                                                                                                                                           
**index.auto_expand_replicas**                              Set to an actual value (like **0-all**) or **false** to disable it.                                                                                                                                                                                              
**index.blocks.read_only**                                  Set to **true** to have the index read only. **false** to allow writes and metadata changes.                                                                                                                                                                     
**index.blocks.read**                                       Set to **true** to disable read operations against the index.                                                                                                                                                                                                    
**index.blocks.write**                                      Set to **true** to disable write operations against the index.                                                                                                                                                                                                   
**index.blocks.metadata**                                   Set to **true** to disable metadata operations against the index.                                                                                                                                                                                                
**index.refresh_interval**                                  The async refresh interval of a shard.                                                                                                                                                                                                                           
**index.term_index_interval**                               The Lucene index term interval. Only applies to newly created docs.                                                                                                                                                                                              
**index.term_index_divisor**                                The Lucene reader term index divisor.                                                                                                                                                                                                                            
**index.translog.flush_threshold_ops**                      When to flush based on operations.                                                                                                                                                                                                                               
**index.translog.flush_threshold_size**                     When to flush based on translog (bytes) size.                                                                                                                                                                                                                    
**index.translog.flush_threshold_period**                   When to flush based on a period of not flushing.                                                                                                                                                                                                                 
**index.translog.disable_flush**                            Disables flushing. Note, should be set for a short interval and then enabled.                                                                                                                                                                                    
**index.cache.filter.max_size**                             The maximum size of filter cache (per segment in shard). Set to **-1** to disable.                                                                                                                                                                               
**index.cache.filter.expire**                               The expire after access time for filter cache. Set to **-1** to disable.                                                                                                                                                                                         
**index.gateway.snapshot_interval**                         The gateway snapshot interval (only applies to shared gateways).                                                                                                                                                                                                 
"merge policy":/guide/reference/index-modules/merge.html    All the settings for the merge policy currently configured. A different merge policy can't be set.                                                                                                                                                               
**index.routing.allocation.include.***                      Controls which nodes the index will be allowed to be allocated on.                                                                                                                                                                                               
**index.routing.allocation.exclude.***                      Controls which nodes the index will not be allowed ot be allocated on.                                                                                                                                                                                           
**index.routing.allocation.total_shards_per_node**          Controls the total number of shards allowed to be allocated on a single node. Defaults to unbounded.                                                                                                                                                             
**index.recovery.initial_shards**                           When using local gateway a particular shard is recovered only if there can be allocated quorum shards in the cluster. It can be set to **quorum** (default), **quorum-1** (or **half**), **full** and **full-1**. Number values are also supported, e.g. **1**.  
**index.gc_deletes**                                                                                                                                                                                                                                                                                                         
**index.ttl.disable_purge**                                 Disables temporarily the purge of expired docs.                                                                                                                                                                                                                  
==========================================================  =================================================================================================================================================================================================================================================================

Bulk Indexing Usage
===================

For example, the update settings API can be used to dynamically change the index from being more performant for bulk indexing, and then move it to more real time indexing state. Before the bulk indexing is started, use:


.. code-block:: js

    curl -XPUT localhost:9200/test/_settings -d '{
        "index" : {
            "refresh_interval" : "-1"
        }
    }'


(Another optimization option is to start the index without any replicas, and only later adding them, but that really depends on the use case).


Then, once bulk indexing is done, the settings can be updated (back to the defaults for example):


.. code-block:: js

    curl -XPUT localhost:9200/test/_settings -d '{
        "index" : {
            "refresh_interval" : "1s"
        }
    }'


And, an optimize should be called:


.. code-block:: js

    curl -XPOST 'http://localhost:9200/test/_optimize?max_num_segments=5'


