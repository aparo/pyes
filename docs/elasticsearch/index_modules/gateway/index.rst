Index Gateway Module
====================

The index gateway module allows to have long term persistence of an index. Think of it as Time Machine for an index, or as Write Behind in Data Grid concepts. The gateway, in a reliable asynchronous manner, persist changes to the gateway and recover from it.


The index gateway works on a shard level. An index is broken down into shards, each shard id group (partition) can have one or more shard replicas. In each partition, a primary shard which adds extra responsibilities for that shard. One of those is working against the index gateway.


When a primary shard is first allocated on a node (not when its relocated), it recovers its state from the index gateway. It can then, persist the changes done on the shard to the gateway. The process of persisting the changes to the gateway is called snapshot. It can either be performed explicitly using an :doc:`API </elasticsearch/rest_api/admin/indices/gateway_snapshot/index>`, or periodically.


The index level gateway stores both the actual index files for a shard, as well as the transaction log of the specific shard.


Note, there are two levels of high availability when using ElasticSearch distributed model. The first, is the ability create an index with several replicas per shard. The second level, in case of a complete cluster shutdown / failure, is the gateway support. The fact that the gateway works in a periodic mode and not persisted on every change is very safe, since there is always the shard replicas that will be used in case of a node failure, even before the gateway comes into play.


Gateway Type
------------

The type of the index gateway to use when an index is created can be controlled using the **index.gateway.type** setting. The following types are supported:


=========================  ===================================
 Type                       Description                       
=========================  ===================================
none                       No state is stored.                
:doc:`fs <./fs/index>`     Shared file system based storage.  
=========================  ===================================

The default type used is decided based on the node level :doc:`gateway <.//../modules/gateway/index>`. For example, if its **none**, then by default, the index is created with **none** index gateway. If it is **fs**, then the index is created with **fs** index gateway. This makes things simpler to configure as usually when wanting persistent indices, the global gateway should be configured as well, and usually it will use the same type of gateway.


snapshot_interval
-----------------

The **index.gateway.snapshot_interval** is a time setting allowing to configure the interval at which snapshotting of the index shard to the gateway will take place. Note, only primary shards start this scheduled snapshotting process. It defaults to **10s**, and can be disabled by setting it to **-1**.


snapshot_on_close
-----------------

When a primary shard is shut down explicitly (not relocated), the **index.gateway.snapshot_on_close** flag can control if while shutting down, a gateway snapshot should be performed. It defaults to **true**.

