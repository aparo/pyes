.. _es-guide-reference-modules-gateway-index:
.. _es-guide-reference-modules-gatewa:
=======
Gateway
=======

The gateway module allows one to store the state of the cluster meta data across full cluster restarts. The cluster meta data mainly holds all the indices created with their respective (index level) settings and explicit type mappings.


Each time the cluster meta data changes (for example, when an index is added or deleted), those changes will be persisted using the gateway. When the cluster first starts up, the state will be read from the gateway and applied.


The gateway set on the node level will automatically control the index gateway that will be used. For example, if the **fs** gateway is used, then automatically, each index created on the node will also use its own respective index level **fs** gateway. In this case, if an index should not persist its state, it should be explicitly set to **none** (which is the only other value it can be set to).


The default gateway used is the :ref:`local <es-guide-reference-modules-gateway-local>`  gateway.


Recovery After Nodes / Time
---------------------------

In many cases, the actual cluster meta data should only be recovered after specific nodes have started in the cluster, or a timeout has passed. This is handy when restarting the cluster, and each node local index storage still exists to be reused and not recovered from the gateway (which reduces the time it takes to recover from the gateway).


The **gateway.recover_after_nodes** setting (which accepts a number) controls after how many nodes within the cluster recovery will start. The **gateway.recover_after_time** setting (which accepts a time value) sets the time to wait till recovery happens once the nodes are met.


The **gateway.expected_nodes** allows to set how many nodes are expected to be in the cluster, and once met, the `recover_after_time` is ignored and recovery starts. For example setting:


.. code-block:: js

    gateway:
        recover_after_nodes: 1
        recover_after_time: 5m
        expected_nodes: 2


In an expected 2 nodes cluster will cause recovery to start 5 minutes after the first node is up, but once there are 2 nodes in the cluster, recovery will begin immediately (without waiting).


Note, once the meta data has been recovered from the gateway (which indices to create, mappings and so on), then this setting is no longer effective until the next full restart of the cluster.


Operations are blocked while the cluster meta data has not been recovered in order not to mix with the actual cluster meta data that will be recovered once the settings has been reached.


.. toctree::
    :maxdepth: 1

    fs
    hadoop
    local
    s3

