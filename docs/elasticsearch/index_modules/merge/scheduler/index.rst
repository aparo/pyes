Index Merge Scheduler Module
============================

Merge schedulers controls the execution of merge operations once they are needed (according to the :doc:`merge policy <.//policy)/index>`. The following types are support with the default set to **ConcurrentMergeScheduler**.


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



