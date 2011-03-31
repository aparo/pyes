=====
Merge
=====

Lucene indices (which each shard has a complete standalone one) gets segmented over time while performing indexing (and delete) operations on them. The merge process keeps those segments at bay. The more segments you have, the slower the search will be, though merging can potentially be a heavy operation so forcing small number of segments will mean more heavy merge operations.


Policy
======

The index merge policy module allows to control which segments of a shard index are to be merged. There are several types of policies with the default set to **LogByteSizeMergePolicy**.


LogByteSizeMergePolicy
----------------------

A merge policy that tries to merge segments into levels of exponentially increasing *byte size*, where each level has fewer segments than the value of the merge factor. Whenever extra segments (beyond the merge factor upper bound) are encountered, all segments within the level are merged.


This policy has the following settings:


===================================  ===========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
 Setting                              Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
===================================  ===========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
index.merge.policy.merge_factor      Determines how often segment indices are merged by index operation.  With smaller values, less RAM is used while indexing, and searches on unoptimized indices are faster, but indexing speed is slower.  With larger values, more RAM is used during indexing, and while searches on unoptimized indices are slower, indexing is faster.  Thus larger values (greater than 10) are best for batch index creation, and smaller values (lower than 10) for indices that are interactively maintained. Defaults to **10**.   
index.merge.policy.min_merge_size    A size setting type which sets the minimum size for the lowest level segments. Any segments below this size are considered to be on the same level (even if they vary drastically in size) and will be merged whenever there are mergeFactor of them.  This effectively truncates the "long tail" of small segments that would otherwise be created into a single level.  If you set this too large, it could greatly increase the merging cost during indexing (if you flush many small segments). Defaults to **1.6mb**  
index.merge.policy.max_merge_size    A size setting type which sets the largest segment (measured by total byte size of the segment's files) that may be merged with other segments. Defaults to unbounded.                                                                                                                                                                                                                                                                                                                                                     
index.merge.policy.maxMergeDocs      Determines the largest segment (measured by document count) that may be merged with other segments. Defaults to unbounded.                                                                                                                                                                                                                                                                                                                                                                                                 
===================================  ===========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================

LogDocMergePolicyProvider
-------------------------

A merge policy that tries to merge segments into levels of exponentially increasing *document count*, where each level has fewer segments than the value of the merge factor. Whenever extra segments (beyond the merge factor upper bound) are encountered, all segments within the level are merged.


===================================  ==========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
 Setting                              Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
===================================  ==========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
index.merge.policy.merge_factor      Determines how often segment indices are merged by index operation.  With smaller values, less RAM is used while indexing, and searches on unoptimized indices are faster, but indexing speed is slower.  With larger values, more RAM is used during indexing, and while searches on unoptimized indices are slower, indexing is faster.  Thus larger values (greater than 10) are best for batch index creation, and smaller values (lower than 10) for indices that are interactively maintained. Defaults to **10**.  
index.merge.policy.min_merge_docs    Sets the minimum size for the lowest level segments. Any segments below this size are considered to be on the same level (even if they vary drastically in size) and will be merged whenever there are mergeFactor of them.  This effectively truncates the "long tail" of small segments that would otherwise be created into a single level.  If you set this too large, it could greatly increase the merging cost during indexing (if you flush many small segments). Defaults to **1000**.                           
index.merge.policy.max_merge_docs    Determines the largest segment (measured by document count) that may be merged with other segments. Defaults to unbounded.                                                                                                                                                                                                                                                                                                                                                                                                
===================================  ==========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================

Scheduler
---------

Merge schedulers controls the execution of merge operations once they are needed (according to the merge policy). The following types are support with the default set to **ConcurrentMergeScheduler**.


ConcurrentMergeScheduler
------------------------

A merge scheduler that runs merges using a separated thread, until the maximum number of threads at which when a merge is needed, the thread(s) that are updating the index will pause until one or more merges completes.


The scheduler supports the following settings:


========================================  =========================================================================================================================================================
 Setting                                   Description                                                                                                                                             
========================================  =========================================================================================================================================================
index.merge.scheduler.max_thread_count    The maximum number of threads to perform the merge operation. Defaults to **Math.max(1, Math.min(3, Runtime.getRuntime().availableProcessors() / 2))**.  
========================================  =========================================================================================================================================================

SerialMergeScheduler
--------------------

A merge scheduler that simply does each merge sequentially using the calling thread (blocking the operations that triggered the merge, the index operation).

