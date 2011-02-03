Hadoop HDFS Gateway
===================

The hadoop (HDFS) based gateway stores the cluster meta data in hadoop. Hadoop support is provided as a plugin and installing is as simply as executing **plugin -install hadoop** or downloading the hadoop plugin and placing it under the **plugins** directory.


Settings
--------

The hadoop gateway requires two simple settings. The **gateway.hdfs.uri** controls the URI to connect to the hadoop cluster, for example: **hdfs://myhost:8022**. The **gateway.hdfs.path** controls the path under which the gateway will store the data.


The hadoop HDFS gateway automatically sets for each index created to use an :doc:`Hadoop index gateway <.//../../index_modules/gateway/hadoop/index>`. oop/index>`. 
