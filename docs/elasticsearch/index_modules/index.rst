Index Modules
=============

The index modules section describes index level modules that can be configured. Index level modules are modules that are configured on a per index basis, allowing for complete control over the how an index is created.


The following lists the available index level modules:


=====================================  =============================================================================================================================================================================================================================================================
 Module                                 Description                                                                                                                                                                                                                                                 
=====================================  =============================================================================================================================================================================================================================================================
:doc:`analysis <./analysis/index>`     Allows to configure and register different types of analyzers for both the indexing and search process.                                                                                                                                                      
:doc:`engine <./engine/index>`         An engine provides the ability to have different actual implementations of how basic operations are performed on the shard level index (index and delete operations for example), think MySQL pluggable storage module.                                      
:doc:`gateway <./gateway/index>`       The index gateway allows to have long term persistence of an index. Think of it as Time Machine for an index, or as Write Behind in Data Grid concepts. The gateway, in a reliable asynchronous manner, persist changes to the gateway and recover from it.  
:doc:`mapper <./mapper/index>`         The mapper module acts as a registry for the type mapping definitions added to an index using the :doc:`put mapping </elasticsearch/rest_api/admin/indices/put_mapping/index>`.                                                                              
:doc:`merge <./merge/index>`           The merge module allows to configure both the :doc:`merge policy <./merge/policy/index>` poli:doc:`merge scheduler <./merge/scheduler/index>` eduler of a specific shard index/index>`.                                                                      
:doc:`store <./store/index>`           The store module allows to control the storage type each index shard stores the index content at.                                                                                                                                                            
:doc:`translog <./translog/index>`     Allows to control flushing of shard based on number of translog operations.                                                                                                                                                                                  
=====================================  =============================================================================================================================================================================================================================================================

Index Settings
--------------

There specific index level settings that are not associated with any specific module. These include:


===========================  =============================================================================================================================================================================================================================================================================================================================================================================================================
 Setting                      Description                                                                                                                                                                                                                                                                                                                                                                                                 
===========================  =============================================================================================================================================================================================================================================================================================================================================================================================================
index.compound_format        Should the compound file format be used (boolean setting). If not set, controlled by the actually store used, this is because the compound format was created to reduce the number of open file handles when using file based storage. By default, it is set to **false** for better performance (really applicable for file system based index storage), but, requires adapting the max open file handles.  
index.term_index_interval    Set the interval between indexed terms.  Large values cause less memory to be used by a reader / searcher, but slow random-access to terms. Small values cause more memory to be used by a reader / searcher, and speed random-access to terms. Defaults to **128**.                                                                                                                                         
index.refresh_interval       A time setting controlling how often the refresh operation will be executed. Defaults to **1s**. Can be set to **-1** in order to disable it.                                                                                                                                                                                                                                                                
===========================  =============================================================================================================================================================================================================================================================================================================================================================================================================
