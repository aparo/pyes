.. _es-guide-reference-modules-gateway-hadoop:

======
Hadoop
======

The hadoop (HDFS) based gateway stores the cluster meta and indices data in hadoop. Hadoop support is provided as a plugin and installing is explained `here <https://github.com/elasticsearch/elasticsearch-hadoop>`_  or downloading the hadoop plugin and placing it under the **plugins** directory. Here is an example config to enable it:


.. code-block:: js

    gateway:
        type: hdfs
        hdfs:
            uri: hdfs://myhost:8022


Settings
========

The hadoop gateway requires two simple settings. The **gateway.hdfs.uri** controls the URI to connect to the hadoop cluster, for example: **hdfs://myhost:8022**. The **gateway.hdfs.path** controls the path under which the gateway will store the data.


concurrent_streams
==================

The **gateway.hdfs.concurrent_streams** allow to throttle the number of streams (per node) opened against the shared gateway performing the snapshot operation. It defaults to **5**.
