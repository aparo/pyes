.. _es-guide-reference-index-modules-translog:

========
Translog
========

Each shard has a transaction log or write ahead log associated with it. It allows to guarantee that when an index/delete operation occurs, it is applied atomically, while not "committing" the internal lucene index for each request. A flush ("commit") still happens based on several parameters:


=======================================  ===============================================================================
 Setting                                  Description                                                                   
=======================================  ===============================================================================
index.translog.flush_threshold_ops       After how many operations to flush. Defaults to **5000**.                      
index.translog.flush_threshold_size      Once the translog hits this size, a flush will happen. Defaults to **500mb**.  
index.translog.flush_threshold_period    The period with no flush happening to force a flush. Defaults to **60m**.      
=======================================  ===============================================================================

