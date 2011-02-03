Index Merge Module
==================

The merge module allow to configure both the :doc:`merge policy <./policy/index>` and :doc:`merge scheduler <./scheduler/index>` of a specific shard index.


Lucene indices (which each shard has a complete standalone one) gets segmented over time while performing indexing (and delete) operations on them. The merge process keeps those segments at bay. The more segments you have, the slower the search will be, though merging can potentially be a heavy operation so forcing small number of segments will mean more heavy merge operations.
