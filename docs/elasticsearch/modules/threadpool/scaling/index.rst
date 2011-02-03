Scaling ThreadPool Module
=========================

A bounded thread pool that reuses previously created free threads.


Settings
--------

Settings for the scaling thread pool should be set for within **threadpool.scaling**. For example, the **keep_alive** setting should be set using **threadpool.scaling.keep_alive**.


====================  ===========================================================================================================
 Setting               Description                                                                                               
====================  ===========================================================================================================
**min**               The minimum number of threads. Defaults to **1**.                                                          
**max**               The maximum number of threads. Defaults to **100**.                                                        
**keep_alive**        A time based settings controlling how long an unused thread can be kept in the pool. Defaults to **60s**.  
**scheduled_size**    The number of threads that will be used to execute scheduled tasks. Defaults to **20**.                    
====================  ===========================================================================================================
