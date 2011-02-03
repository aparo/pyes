Index Robin Engine Module
=========================

The robin engine is a high performance engine implementation applying operations performed on the index immediately. It provides near realtime support (using Lucene NRT). Each operation performed (index, delete) is *atomic and persistent* (meaning that they will not get lost if successful). This is achieved by performing the operation using Lucene and maintaining a transaction log for all operations since the last flush.


Refresh
-------

The near real time search feature is done by executing a scheduled refresh operation (the same one the :doc:`Refresh API </elasticsearch/rest_api/admin/indices/refresh)/index>`. The **index.engine.robin.refreshInterval** setting is a time setting allowing to control the interval at which the refresh is executed. The default is **1s**. The setting can also be set to **-1** in order to completely disable the automatic scheduling and control the refresh just through the API, it can be done.


Flush
-----

The flush operation flushes all the changes done against the index (using Lucene) and clears the transaction log (since now they are within the index itself). The flush operation basically frees up memory occupied by both Lucene and the transaction log.


Settings
--------

=====================================  =================================================================================================================================================================================================
 Setting                                Description                                                                                                                                                                                     
=====================================  =================================================================================================================================================================================================
index.engine.robin.refresh_interval    A time setting controlling how often the refresh operation will be executed. Defaults to **1s**. Can be set to **-1** in order to disable it. Can also be set using **index.refresh_interval**.  
=====================================  =================================================================================================================================================================================================

