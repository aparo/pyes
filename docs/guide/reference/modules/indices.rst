.. _es-guide-reference-modules-indices:

=======
Indices
=======

The indices module allow to control settings that are globally managed for all indices.


Indexing Buffer
===============

The indexing buffer setting allows to control how much memory will be allocated for the indexing process. It is a global setting that bubbles down to all the different shards allocated on a specific node.


The **indices.memory.index_buffer_size** accepts either a percentage or a byte size value. It defaults to **10%**, meaning that **10%** of the total memory allocated to a node will be used as the indexing buffer size. This amount is then divided between all the different shards. Also, if percentage is used, allow to set **min_index_buffer_size** (defaults to **48mb**) and **max_index_buffer_size** which by default is unbounded.


The **indices.memory.min_shard_index_buffer_size** allows to set a hard lower limit for the memory allocated per shard for its own indexing buffer. It defaults to **4mb**.


