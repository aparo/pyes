Local Gateway
=============

The local gateway allows for recovery of the full cluster state and indices from the local storage of each node, and does not require a common node level shared storage.


In order to use the local gateway, the indices must be file system based with no memory caching.


It is important to configure the **gateway.recover_after_nodes** setting to include most of the expected nodes to be started after a full cluster restart. This will insure that the latest cluster state is recovered.

