.. _es-guide-reference-modules-cluster:

=======
Cluster
=======

Shards Allocation
=================

Shards allocation is the process of allocating shards to nodes. This can happen during initial recovery, replica allocation, rebalancing, or handling nodes being added or removed.


The following settings allow to control it. Note **c.r.a** is an abbreviation for **cluster.routing.allocation**, so make sure to use the full form in the configuration.


=============================================  ====================================================================================================================================================================================================================================================================================
 Setting                                        Description                                                                                                                                                                                                                                                                        
=============================================  ====================================================================================================================================================================================================================================================================================
**c.r.a.allow_rebalance**                      Allow to control when rebalancing will happen based on the total state of all the indices shards in the cluster. **always**, **indices_primaries_active**, and **indices_all_active** are allowed, defaulting to **indices_all_active** to reduce chatter during initial recovery.  
**c.r.a.cluster_concurrent_rebalance**         Allow to control how many concurrent rebalancing of shards are allowed cluster wide, and default it to **2**.                                                                                                                                                                       
**c.r.a.node_initial_primaries_recoveries**    Allow to control specifically the number of initial recoveries of primaries that are allowed per node. Since most times local gateway is used, those should be fast and we can handle more of those per node without creating load.                                                 
**c.r.a.node_concurrent_recoveries**           How many concurrent recoveries are allowed to happen on a node. Defaults to **2**.                                                                                                                                                                                                  
**c.r.a.disable_allocation**                   Allows to disable either primary or replica allocation. Note, a replica will still be promoted to primary if one does not exists. This setting really make sense when dynamically updating it using the cluster update settings API.                                                
**c.r.a.disable_replica_allocation**           Allows to disable only replica allocation. Similar to the previous setting, mainly make sense when using it dynamically using the cluster update settings API.                                                                                                                      
**indices.recovery.concurrent_streams**        The number of streams to open (on a *node* level) to recover a shard from a peer shard. Defaults to **5**.                                                                                                                                                                          
=============================================  ====================================================================================================================================================================================================================================================================================

Shard Allocation Awareness
--------------------------

Cluster allocation awareness allows to configure shard and replicas allocation across generic attributes associated the nodes. Lets explain it through an example:


Assume we have several racks. When we start a node, we can configure an attribute called **rack_id** (any attribute name works), for example, here is a sample config:


<pre>
node.rack_id: rack_one

    
The above sets an attribute called **rack_id** for the relevant node with a value of **rack_one**. Now, we need to configure the **rack_id** attribute as one of the awareness allocation attributes (set it on *all* (master eligible) nodes config):


<pre>
cluster.routing.allocation.awareness.attributes: rack_id

    
The above will mean that the **rack_id** attribute will be used to do awareness based allocation of shard and its replicas. For example, lets say we start 2 nodes with **node.rack_id** set to **rack_one**, and deploy a single index with 5 shards and 1 replica. The index will be fully deployed on the current nodes (5 shards and 1 replica each, total of 10 shards).


Now, if we start two more nodes, with **node.rack_id** set to **rack_two**, shards will relocate to even the number of shards across the nodes, but, a shard and its replica will not be allocated in the same **rack_id** value.


The awareness attributes can hold several values, for example:

<pre>
cluster.routing.allocation.awareness.attributes: rack_id,zone

    
*NOTE*: When using awareness attributes, shards will not be allocated to nodes that don't have values set for those attributes.

    
Forced Awareness
""""""""""""""""

Sometimes, we know in advance the number of values an awareness attribute can have, and more over, we would like never to have more replicas then needed allocated on a specific group of nodes with the same awareness attribute value. For that, we can force awareness on specific attributes.


For example, lets say we have an awareness attribute called **zone**, and we know we are going to have two zones, **zone1** and **zone2**. Here is how we can force awareness one a node:


<pre>
cluster.routing.allocation.awareness.force.zone.values: zone1,zone2
cluster.routing.allocation.awareness.attributes: zone


Now, lets say we start 2 nodes with **node.zone** set to **zone1** and create an index with 5 shards and 1 replica. The index will be created, but only 5 shards will be allocated (with no replicas). Only when we start more shards with **node.zone** set to **zone2** will the replicas be allocated.


Automatic Preference When Searching / GETing
""""""""""""""""""""""""""""""""""""""""""""

When executing a search, or doing a get, the node receiving the request will prefer to execute the request on shards that exists on nodes that have the same attribute values as the executing node.

Realtime Settings Update
""""""""""""""""""""""""

The settings can be updated using the cluster update settings API on a live cluster.


Shard Allocation Filtering
--------------------------

Allow to control allocation if indices on nodes based on include/exclude filters. The filters can be set both on the index level and on the cluster level. Lets start with an example of setting it on the cluster level:


Lets say we have 4 nodes, each has specific attribute called **tag** associated with it (the name of the attribute can be any name). Each node has a specific value associated with **tag**. Node 1 has a setting **node.tag: value1**, Node 2 a setting of **node.tag: value2**, and so on.


We can create an index that will only deploy on nodes that have **tag** set to **value1** and **value2** by setting **index.routing.allocation.include.tag** to **value1,value2**. For example:


.. code-block:: js

    curl -XPUT localhost:9200/test -d '{
        "index.routing.allocation.include.tag" : "value1,value2"
    }'



On the other hand, we can create an index that will be deployed on all nodes except for nodes with a **tag** of value **value3** by setting **index.routing.allocation.exclude.tag** to **value3**. For example:


.. code-block:: js

    curl -XPUT localhost:9200/test -d '{
        "index.routing.allocation.exclude.tag" : "value3"
    }'


The **include** and **exclude** values can have generic simple matching wildcards, for example, **value1***. A special attribute name called **_ip** can be used to match on node ip values.


Obviously a node can have several attributes associated with it, and both the attribute name and value are controlled in the setting. For example, here is a sample of several node configurations:


.. code-block:: js

    node.group1: group1_value1
    node.group2: group2_value4


In the same manner, **include** and **exclude** can work against several attributes, for example:

.. code-block:: js

    curl -XPUT localhost:9200/test -d '{
        "index.routing.allocation.include.group1" : "xxx"
        "index.routing.allocation.include.group2" : "yyy",
        "index.routing.allocation.exclude.group3" : "zzz",
    }'


The provided settings can also be updated in real time using the update settings API, allowing to "move" indices (shards) around in realtime.


Cluster wide filtering can also be defined, and be updated in real time using the cluster update settings API. This setting can come in handy for things like decommissioning nodes (even if the replica count is set to 0). Here is a sample of how to decommission a node based on **_ip** address:


.. code-block:: js

    curl -XPUT localhost:9200/_cluster/settings -d '{
        "transient" : {
            "cluster.routing.allocation.exclude._ip" : "10.0.0.1"
        }
    }'

