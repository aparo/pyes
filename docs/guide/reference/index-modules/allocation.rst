.. _es-guide-reference-index-modules-allocation:

==========
Allocation
==========

Shard Allocation Filtering
==========================

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


Total Shards Per Node
=====================

The **index.routing.allocation.total_shards_per_node** setting allows to control how many total shards for an index will be allocated per node. It can be dynamically set on a live index using the update index settings API.
