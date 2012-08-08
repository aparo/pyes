.. _es-guide-reference-index-modules-index:
.. _es-guide-reference-index-module:

=============
Index Modules
=============

Index Modules are modules created per index and control all aspects related to an index. Since those modules lifecycle are tied to an index, all the relevant modules settings can be provided when creating an index (and it is actually the recommended way to configure an index).


Index Settings
==============

There are specific index level settings that are not associated with any specific module. These include:


===========================  ================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
 Setting                      Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
===========================  ================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
index.compound_format        Should the compound file format be used (boolean setting). If not set, controlled by the actually store used, this is because the compound format was created to reduce the number of open file handles when using file based storage. By default, it is set to **false** for better performance (really applicable for file system based index storage), but, requires adapting the max open file handles.                                                                                                                     
index.term_index_interval    Set the interval between indexed terms.  Large values cause less memory to be used by a reader / searcher, but slow random-access to terms. Small values cause more memory to be used by a reader / searcher, and speed random-access to terms. Defaults to **128**.                                                                                                                                                                                                                                                            
index.term_index_divisor     Subsamples which indexed terms are loaded into RAM. This has the same effect as **index.term_index_interval** except that setting must be done at indexing time while this setting can be set per reader / searcher.  When set to N, then one in every N*termIndexInterval terms in the index is loaded into memory.  By setting this to a value > 1 you can reduce memory usage, at the expense of higher latency when loading a TermInfo.  The default value is 1.  Set this to -1 to skip loading the terms index entirely.  
index.refresh_interval       A time setting controlling how often the refresh operation will be executed. Defaults to **1s**. Can be set to **-1** in order to disable it.                                                                                                                                                                                                                                                                                                                                                                                   
===========================  ================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================

.. toctree::
    :maxdepth: 1

    allocation
    analysis/index
    cache
    mapper
    merge
    slowlog
    store
    translog
	