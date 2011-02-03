Cached ThreadPool Module
========================

A cached thread pool is an unbounded thread pool that reuses previously constructed threads.


Settings
--------

Settings for the cached Thread Pool module should be set for within **threadpool.cached**. For example, the **keep_alive** setting should be set using **threadpool.cached.keepAlive**.


====================  ===========================================================================================================
 Setting               Description                                                                                               
====================  ===========================================================================================================
**keep_alive**        A time based settings controlling how long an unused thread can be kept in the pool. Defaults to **60s**.  
**scheduled_size**    The number of threads that will be used to execute scheduled tasks. Defaults to **20**.                    
====================  ===========================================================================================================
