Index Engine Module
===================

The index engine module provides the ability to have different actual implementations of how basic operations are performed on the shard level index (index, and delete operations for example), think MySQL pluggable storage module.


Some characteristics the can be controlled by an engine implementation are its (near) real time nature, its handling of actual operations (perform them immediately, aync them, batch them), locking, and so on.


The default engine (and currently the only one implemented) is the :doc:`Robin Engine <./robin/index>`. 
