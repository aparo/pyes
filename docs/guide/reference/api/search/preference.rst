.. _es-guide-reference-api-search-preference:

==========
Preference
==========

Controls a **preference** of which shard replicas to execute the search request on. By default, the operation is randomized between the each shard replicas.


The **preference** can be set to:

* **_primary**: The operation will go and be executed only on the primary shards.
* **_primary_first**: The operation will go and be executed on the primary shard, and if not available (failover), will execute on other shards.
* **_local**: The operation will prefer to be executed on a local allocated shard is possible.
* **_only_node:xyz**: Restricts the search to execute only on a node with the provided node id (**xyz** in this case).
* Custom (string) value: A custom value will be used to guarantee that the same shards will be used for the same custom value. This can help with "jumping values" when hitting different shards in different refresh states. A sample value can be something like the web session id, or the user name.