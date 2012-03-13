.. _es-guide-reference-index-modules-merge:

=====
Merge
=====

A shard in elasticsearch is a Lucene index, and a lucene index is broken down into segments. Segments are internal storage elements in the index where the index data is stored, and are immutable up to delete markers. Segments are, periodically, merged into larger segments to keep the index size at bay and expunge deletes.


The more segments one has in the Lucene index mean slower searches and more memory used, but, low number of segments means more merging that has to go on.


Policy
======

The index merge policy module allows one to control which segments of a shard index are to be merged. There are several types of policies with the default set to **tiered**.


tiered
------

Merges segments of approximately equal size, subject to an allowed number of segments per tier. This is similar to **log_bytes_size** merge policy, except this merge policy is able to merge non-adjacent segment, and separates how many segments are merged at once from how many segments are allowed per tier. This merge policy also does not over-merge (ie, cascade merges).


This policy has the following settings:


===================================================  =====================================================================================================================================================================================================================================================================
 Setting                                              Description                                                                                                                                                                                                                                                         
===================================================  =====================================================================================================================================================================================================================================================================
**index.merge.policy.expunge_deletes_allowed**       When expungeDeletes is called, we only merge away a segment if its delete percentage is over this threshold. Default is **10**.                                                                                                                                      
**index.merge.policy.floor_segment**                 Segments smaller than this are "rounded up" to this size, ie treated as equal (floor) size for merge selection. This is to prevent frequent flushing of tiny segments from allowing a long tail in the index. Default is **2mb**.                                    
**index.merge.policy.max_merge_at_once**             Maximum number of segments to be merged at a time during "normal" merging. Default is **10**.                                                                                                                                                                        
**index.merge.policy.max_merge_at_once_explicit**    Maximum number of segments to be merged at a time, during optimize or expungeDeletes. Default is **30**.                                                                                                                                                             
**index.merge.policy.max_merged_segment**            Maximum sized segment to produce during normal merging (not explicit optimize). This setting is approximate: the estimate of the merged segment size is made by summing sizes of to-be-merged segments (compensating for percent deleted docs). Default is **5gb**.  
**index.merge.policy.segments_per_tier**             Sets the allowed number of segments per tier. Smaller values mean more merging but fewer segments. Default is **10**. Note, this value needs to be >= then the **max_merge_at_once_** otherwise you'll force too many merges to occur.                               
**index.reclaim_deletes_weight**                     Controls how aggressively merges that reclaim more deletions are favored. Higher values favor selecting merges that reclaim deletions. A value of **0.0** means deletions don't impact merge selection. Defaults to **2.0**.                                         
**index.compound_format**                            Should the index be stored in compound format or not. Defaults to **false**.                                                                                                                                                                                         
===================================================  =====================================================================================================================================================================================================================================================================

For normal merging, this policy first computes a "budget" of how many segments are allowed by be in the index.  If the index is over-budget, then the policy sorts segments by decreasing size (pro-rating by percent deletes), and then finds the least-cost merge.  Merge cost is measured by a combination of the "skew" of the merge (size of largest seg divided by smallest seg), total merge size and pct deletes reclaimed, so that merges with lower skew, smaller size and those reclaiming more deletes, are favored.


If a merge will produce a segment that's larger than **max_merged_segment** then the policy will merge fewer segments (down to 1 at once, if that one has deletions) to keep the segment size under budget.


Note, this can mean that for large shards that holds many gigabytes of data, the default of **max_merged_segment** (**5gb**) can cause for many segments to be in an index, and causing searches to be slower. Use the indices segments API to see the segments that an index have, and possibly either increase the **max_merged_segment** or issue an optimize call for the index (try and aim to issue it on a low traffic time).


log_byte_size
-------------

A merge policy that merges segments into levels of exponentially increasing *byte size*, where each level has fewer segments than the value of the merge factor. Whenever extra segments (beyond the merge factor upper bound) are encountered, all segments within the level are merged.


This policy has the following settings:


===================================  ===========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
 Setting                              Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
===================================  ===========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
index.merge.policy.merge_factor      Determines how often segment indices are merged by index operation.  With smaller values, less RAM is used while indexing, and searches on unoptimized indices are faster, but indexing speed is slower.  With larger values, more RAM is used during indexing, and while searches on unoptimized indices are slower, indexing is faster.  Thus larger values (greater than 10) are best for batch index creation, and smaller values (lower than 10) for indices that are interactively maintained. Defaults to **10**.   
index.merge.policy.min_merge_size    A size setting type which sets the minimum size for the lowest level segments. Any segments below this size are considered to be on the same level (even if they vary drastically in size) and will be merged whenever there are mergeFactor of them.  This effectively truncates the "long tail" of small segments that would otherwise be created into a single level.  If you set this too large, it could greatly increase the merging cost during indexing (if you flush many small segments). Defaults to **1.6mb**  
index.merge.policy.max_merge_size    A size setting type which sets the largest segment (measured by total byte size of the segment's files) that may be merged with other segments. Defaults to unbounded.                                                                                                                                                                                                                                                                                                                                                     
index.merge.policy.maxMergeDocs      Determines the largest segment (measured by document count) that may be merged with other segments. Defaults to unbounded.                                                                                                                                                                                                                                                                                                                                                                                                 
===================================  ===========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================

log_doc
-------

A merge policy that tries to merge segments into levels of exponentially increasing *document count*, where each level has fewer segments than the value of the merge factor. Whenever extra segments (beyond the merge factor upper bound) are encountered, all segments within the level are merged.


===================================  ==========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
 Setting                              Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
===================================  ==========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
index.merge.policy.merge_factor      Determines how often segment indices are merged by index operation.  With smaller values, less RAM is used while indexing, and searches on unoptimized indices are faster, but indexing speed is slower.  With larger values, more RAM is used during indexing, and while searches on unoptimized indices are slower, indexing is faster.  Thus larger values (greater than 10) are best for batch index creation, and smaller values (lower than 10) for indices that are interactively maintained. Defaults to **10**.  
index.merge.policy.min_merge_docs    Sets the minimum size for the lowest level segments. Any segments below this size are considered to be on the same level (even if they vary drastically in size) and will be merged whenever there are mergeFactor of them.  This effectively truncates the "long tail" of small segments that would otherwise be created into a single level.  If you set this too large, it could greatly increase the merging cost during indexing (if you flush many small segments). Defaults to **1000**.                           
index.merge.policy.max_merge_docs    Determines the largest segment (measured by document count) that may be merged with other segments. Defaults to unbounded.                                                                                                                                                                                                                                                                                                                                                                                                
===================================  ==========================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================

Scheduling 
===========

The merge schedule controls the execution of merge operations once they are needed (according to the merge policy). The following types are supported, with the default being the **ConcurrentMergeScheduler**.


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

