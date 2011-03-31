=====
Local
=====

The local gateway allows for recovery of the full cluster state and indices from the local storage of each node, and does not require a common node level shared storage.


In order to use the local gateway, the indices must be file system based with no memory caching.


Note, different from shared gateway types, the persistency to the local gateway is *not* done in an async manner. Once an operation is performed, the data is there for the local gateway to recover it in case of full cluster failure.


It is important to configure the **gateway.recover_after_nodes** setting to include most of the expected nodes to be started after a full cluster restart. This will insure that the latest cluster state is recovered. For example:


.. code-block:: js

    gateway:
        recover_after_nodes: 1
        recover_after_time: 5m
        expected_nodes: 2


