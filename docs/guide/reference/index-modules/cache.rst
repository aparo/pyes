.. _es-guide-reference-index-modules-cache:

=====
Cache
=====

There are different caching inner modules that correspond to an index. They include **filter**, **field** and others.


Filter Cache
============

The filter cache is responsible to cache the results of filters (used in the query). The default implementation of a filter cache (and the one recommended to use in almost all cases) is the **node** filter cache type.


Node Filter Cache
-----------------

The **node** filter cache allows to configure either a percentage (of the total memory allocated to the process) or an exact value of the cache used for filter cache. All shards allocated on that node will use this cache (thats why its called **node**), and evicted based on LRU logic.


The setting that allows to control the memory size for the filter cache is **indices.cache.filter.size** and it defaults to **20%**. *Note*, this is *not* an index level setting but a node level setting (can be configured in the node configuration).


**indices.cache.filter.size** can accept either a percentage value, like **30%**, or an exact value, like **512mb**.


Index Filter Cache
------------------

A filter cache that exists on the index level (on each node). Generally, not recommended for use since its memory usage depends on which shards are allocated on each node and its hard to predict it. The types are: **resident**, **soft** and **weak**.


All types support the following settings:


=================================  =========================================================================================================================================================================================
 Setting                            Description                                                                                                                                                                             
=================================  =========================================================================================================================================================================================
**index.cache.filter.max_size**    The max size (count, not byte size) of the cache (per search segment in a shard). Defaults to not set (**-1**), which is usually fine with **soft** cache and proper cacheable filters.  
**index.cache.filter.expire**      A time based setting that expires filters after a certain time of inactivity. Defaults to **-1**. For example, can be set to **5m** for a 5 minute expiry.                               
=================================  =========================================================================================================================================================================================

Field Data Cache
----------------

The field data cache is used mainly when sorting on or faceting on a field. It loads all the field values to memory in order to provide fast document based access to those values. The field data cache can be expensive to build for a field, so its recommended to have enough memory to allocate it, and keep it loaded.


The default type for the field data cache is **resident** (because of the cost of rebuilding it). Other types include **soft**.


================================  ============================================================================================================================================================
 Setting                           Description                                                                                                                                                
================================  ============================================================================================================================================================
**index.cache.field.max_size**    The max size (count, not byte size) of the cache (per search segment in a shard). Defaults to not set (**-1**).                                             
**index.cache.field.expire**      A time based setting that expires filters after a certain time of inactivity. Defaults to **-1**. For example, can be set to **5m** for a 5 minute expiry.  
================================  ============================================================================================================================================================
