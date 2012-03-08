.. _es-guide-reference-index-modules-store:

=====
Store
=====

The store module allow you to control how index data is stored. It's important to note that the storage is considered temporal only for the shared gateway (non **local**, which is the default).


The index can either be stored in-memory (no persistence) or on-disk (the default). In-memory indices provide better performance at the cost of limiting the index size to the amount of available physical memory.


When using a local gateway (the default), file system storage with *no* in memory storage is required to maintain index consistency. This is required since the local gateway constructs its state from the local index state of each node. When using a shared gateway (like NFS or S3), the index can be safely stored in memory (with replicas).


Another important aspect of memory based storage is the fact that ElasticSearch supports storing the index in memory *outside of the JVM heap space* using the "Memory" (see below) storage type. It translates to the fact that there is no need for extra large JVM heaps (with their own consequences) for storing the index in memory.


The following sections lists all the different storage types supported.


File System
===========

File system based storage is the default storage used. There are different implementations or storage types. The best one for the operating environment will be automatically chosen: **mmapfs** on Solaris/Windows 64bit, **simplefs** on Windows 32bit, and **niofs** for the rest.


The following are the different file system based storage types:


Simple FS
---------

The **simplefs** type is a straightforward implementation of file system storage (maps to Lucene **SimpleFsDirectory**) using a random access file. This implementation has poor concurrent performance (multiple threads will bottleneck). Its usually better to use the **niofs** when you need index persistence.


NIO FS
------

The **niofs** type stores the shard index on the file system (maps to Lucene **NIOFSDirectory**) using NIO. It allows multiple threads to read from the same file concurrently. It is not recommended on Windows because of a bug in the SUN Java implementation.


MMap FS
-------

The **mmapfs** type stores the shard index on the file system (maps to Lucene **MMapDirectory**) by mapping a file into memory (mmap). Memory mapping uses up a portion of the virtual memory address space in your process equal to the size of the file being mapped.  Before using this class, be sure your have plenty of virtual address space.


Memory
======

The **memory** type stores the index in main memory with the following configuration options:


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
