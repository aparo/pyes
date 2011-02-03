Index Translog Module
=====================

A shard is flushed to local disk based on number of operations accumulated in translog. It can be controled using the **index.translog.flush_threshold** setting (defaults to **5000**).

