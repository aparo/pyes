.. _es-guide-reference-modules-cluster:

=======
Cluster
=======

Shards Allocation
=================

Shards allocation is the process of allocating shards to nodes. This can happen during initial recovery, replica allocation, rebalancing, or handling nodes being added or removed.


==================================================================  ====================================================================================================================================================================================================================================================================================
 Setting                                                             Description                                                                                                                                                                                                                                                                        
==================================================================  ====================================================================================================================================================================================================================================================================================
**cluster.routing.allocation.allow_rebalance**                      Allow to control when rebalancing will happen based on the total state of all the indices shards in the cluster. **always**, **indices_primaries_active**, and **indices_all_active** are allowed, defaulting to **indices_all_active** to reduce chatter during initial recovery.  
**cluster.routing.allocation.cluster_concurrent_rebalance**         Allow to control how many concurrent rebalancing of shards are allowed cluster wide, and default it to **3**.                                                                                                                                                                       
**cluster.routing.allocation.node_initial_primaries_recoveries**    Allow to control specifically the number of initial recoveries of primaries that are allowed per node. Since most times local gateway is used, those should be fast and we can handle more of those per node without creating load.                                                 
**cluster.routing.allocation.node_concurrent_recoveries**           How many concurrent recoveries are allowed to happen on a node. Defaults to **2**.                                                                                                                                                                                                  
**index.shard.recovery.concurrent_streams**                         The number of streams to open (on a *node* level) to recover a shard from a peer shard. Defaults to **5**.                                                                                                                                                                          
==================================================================  ====================================================================================================================================================================================================================================================================================
