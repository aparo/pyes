.. _es-guide-reference-api-admin-indices-stats:

===================
Admin Indices Stats
===================

Indices level stats provide statistics on different operations happening on an index. The API provides statistics on the index level scope (though most stats can also be retrieved using node level scope).


The following returns high level aggregation and index level stats for all indices:

.. code-block:: js

    curl localhost:9200/_stats

    
Specific index stats can be retrieved using:

.. code-block:: js

    curl localhost:9200/index1,index2/_stats


By default, **docs**, **store**, and **indexing**, **get**, and **search** stats are returned, other stats can be enabled as well:

* **docs**: The number of docs / deleted docs (docs not yet merged out). Note, affected by refreshing the index.
* **store**: The size of the index.
* **indexing**: Indexing statistics, can be combined with a comma separated list of **types** to provide document type level stats.
* **get**: Get statistics, including missing stats.
* **search**: Search statistics, including custom grouping using the **groups** parameter (search operations can be associated with one or more groups).
* **merge**: merge stats.
* **flush**: flush stats.
* **refresh**: refresh stats.
* **clear**: Clears all the flags (first).

Here are some samples:


.. code-block:: js

    # Get back stats for merge and refresh on top of the defaults
    curl 'localhost:9200/_stats?merge=true&refresh=true'
    # Get back stats just for flush
    curl 'localhost:9200/_stats?clear=true&flush=true'
    # Get back stats for type1 and type2 documents for the my_index index
    curl 'localhost:9200/my_index/_stats?clear=true&indexing=true&types=type1,type2

    
The stats returned are aggregated on the index level, with **primaries** and **total** aggregations. In order to get back shard level stats, set the **level** parameter to **shards**. 


Note, as shards move around the cluster, their stats will be cleared as they are created on other nodes. On the other hand, even though a shard "left" a node, that node will still retain the stats that shard contributed to.


Specific stats endpoints
------------------------

Instead of using flags to indicate which stats to return, specific REST endpoints can be used, for example:

.. code-block:: js

    # Merge stats across all indices
    curl localhost:9200/_stats/merge
    # Merge stats for the my_index index
    curl localhost:9200/my_index/_stats/merge
    # Indexing stats for my_index
    curl localhost:9200/my_index/_stats/indexing
    # Indexing stats for my_index for my_type1 and my_type2
    curl localhost:9200/my_index/_stats/indexing/my_type1,my_type2

