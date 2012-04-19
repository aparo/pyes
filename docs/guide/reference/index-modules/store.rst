.. _es-guide-reference-index-modules-store:

=====
Store
=====

The store module allows to control the storage type each index shard stores the index content at. It's important to note that the storage is considered temporal only for the shared gateway (non **local**, which is the default).


The storage module allows to store the index either in memory or using file system. Typically, in non distributed systems, file system based storage is used to allow for large indices. In memory provides better performance at the cost of limited sizing of the index.


When using local gateway (the default), file system storage with *no* in memory storage is required to provide full persistency. This is required since the local gateway constructs its state from the local index state of each node. When using shared gateway (like shared fs, s3), the index can be safely stored in memory (with replicas).


Another important aspect of memory based storage is the fact that ElasticSearch supports storing the index in memory *outside of the JVM heap space* using the :ref:`Memory <es-guide-reference-index-modules>`  storage type. It translates to the fact that there is no need for extra large JVM heaps (with their own consequences) for storing the index in memory.


The following sections lists all the different storage types supported.


File System
===========

File system based storage, includes different internal types of how to work with the file system. This is the default storage used. Out of the different types, the best one suited will be automatically chosen (**mmapfs** on solaris/windows 64bit, **simplefs** on windows 32bit, and **niofs** for the rest).


The following are the different file system based storage types:


Simple FS
---------

The **simplefs** type is a plain forward implementation of file system storage (maps to Lucene **SimpleFsDirectory**) using random access file. This class has poor concurrent performance (multiple threads will bottleneck). Its usually better to use the **niofs** when file system is required.


NIO FS
------

The **niofs** type stores the shard index on the file system (maps to Lucene **NIOFSDirectory**) and allows for multiple threads to read from the same file concurrently. It is not recommended on Windows because of a bug in SUN Java implementation.


MMap FS
-------

The **mmapfs** type stores the shard index on the file system (maps to Lucene **MMapDirectory**) using mmap. Memory mapping uses up a portion of the virtual memory address space in your process equal to the size of the file being mapped.  Before using this class, be sure your have plenty of virtual address space.


Memory
======

The **memory** type stores the index in memory with the following configuration options:


There are also *node* level settings that control the caching of buffers (important when using direct buffers):


====================================  ===============================================================================
 Setting                               Description                                                                   
====================================  ===============================================================================
**cache.memory.direct**               Should the memory be allocated outside of the JVM heap. Defaults to **true**.  
**cache.memory.small_buffer_size**    The small buffer size, defaults to **1kb**.                                    
**cache.memory.large_buffer_size**    The large buffer size, defaults to **1mb**.                                    
**cache.memory.small_cache_size**     The small buffer cache size, defaults to **10mb**.                             
**cache.memory.large_cache_size**     The large buffer cache size, defaults to **500mb**.                            
====================================  ===============================================================================
