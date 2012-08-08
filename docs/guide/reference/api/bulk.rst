.. _es-guide-reference-api-bulk:

====
Bulk
====

The bulk API makes it possible to perform many index/delete operations in a single API call. This can greatly increase the indexing speed. The REST API endpoint is **/_bulk**, and it expects the following JSON structure:


.. code-block:: js

    action_and_meta_data\n
    optional_source\n
    action_and_meta_data\n
    optional_source\n
    ....
    action_and_meta_data\n
    optional_source\n


*NOTE*: the final line of data must end with a newline character **\n**.


If you're providing text file input to **curl**, you *must* **--data-binary** instead of plain **-d**.  The latter doesn't preserve newlines.  Example:


.. code-block:: js

    $ cat requests
    { "index" : { "_index" : "test", "_type" : "type1", "_id" : "1" } }
    { "field1" : "value1" }
    $ curl -s -XPOST localhost:9200/_bulk --data-binary **requests; echo
    {"took":7,"items":[{"create":{"_index":"test","_type":"type1","_id":"1","_version":1,"ok":true}}]}


Because this format uses literal **\n**'s as delimiters, please be sure that the JSON actions and sources are not pretty printed. Here is an example of a correct sequence of bulk commands:


.. code-block:: js

    { "index" : { "_index" : "test", "_type" : "type1", "_id" : "1" } }
    { "field1" : "value1" }
    { "delete" : { "_index" : "test", "_type" : "type1", "_id" : "2" } }
    { "create" : { "_index" : "test", "_type" : "type1", "_id" : "3" } }
    { "field1" : "value3" }


The endpoints are **/_bulk**, **/{index}/_bulk**, and **{index}/type/_bulk**. When the index or the index/type are provided, they will be used by default on bulk items that don't provide them explicitly.


A note on the format. The idea here is to make processing of this as fast as possible. As some of the actions will be redirected to other shards on other nodes, only **action_meta_data** is parsed on the receiving node side.


Client libraries using this protocol should try and strive to do something similar on the client side, and reduce buffering as much as possible.


The response to a bulk action is a large JSON structure with the individual results of each action that was performed. The failure of a single action does not affect the remaining actions.


There is no "correct" number of actions to perform in a single bulk call. You should experiment with different settings to find the optimum size for your particular workload.


If using the HTTP API, make sure that the client does not send HTTP chunks, as this will slow things down.


Versioning
==========

Each bulk item can include the version value using the **_version**/**version** field. It automatically follows the behavior of the index / delete operation based on the **_version** mapping. It also support the **version_type**/**_version_type** when using **external** versioning.


Routing
=======

Each bulk item can include the routing value using the **_routing**/**routing** field. It automatically follows the behavior of the index / delete operation based on the **_routing** mapping.


Percolator
==========

Each bulk index action can include a percolate value using the **_percolate**/**percolate** field.


Parent
======

Each bulk item can include the parent value using the **_parent**/**parent** field. It automatically follows the behavior of the index / delete operation based on the **_parent** / **_routing** mapping.


Timestamp
=========

Each bulk item can include the timestamp value using the **_timestamp**/**timestamp** field. It automatically follows the behavior of the index operation based on the **_timestamp** mapping.


TTL
===

Each bulk item can include the ttl value using the **_ttl**/**ttl** field. It automatically follows the behavior of the index operation based on the **_ttl** mapping.


Write Consistency
=================

When making bulk calls, you can require a minimum number of active shards in the partition through the **consistency** parameter. The values allowed are **one**, **quorum**, and **all**. It defaults to the node level setting of **action.write_consistency**, which in turn defaults to **quorum**.


For example, in a N shards with 2 replicas index, there will have to be at least 2 active shards within the relevant partition (**quorum**) for the operation to succeed. In a N shards with 1 replica scenario, there will need to be a single shard active (in this case, **one** and **quorum** is the same).


Refresh
=======

The **refresh** parameter can be set to **true** in order to refresh the relevant shards immediately after the bulk operation has occurred and make it searchable, instead of waiting for the normal refresh interval to expire. Setting it to **true** can trigger additional load, and may slow down indexing.

