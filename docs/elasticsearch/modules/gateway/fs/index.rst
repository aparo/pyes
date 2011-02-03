Fie System Gateway
==================

The file system based gateway stores the cluster meta data in a file system. Note, since its a distributed system, the file system should be shared between all different nodes.


location
--------

The location where the gateway stores the cluster state can be set using the **gateway.fs.location** setting. By default, it will be stored under the **work** directory. Note, the **work** directory is considered a temporal directory with ElasticSearch (meaning it is safe to **rm -rf** it), the default location of the persistent gateway in work intentional, *it should be changed*.


When explicitly specifying the **gateway.fs.location**, each node will append its **cluster.name** to the provided location. It means that the location provided can safely support several clusters.


The file system gateway automatically sets for each index created to use an :doc:`fs index gateway <.//../../index_modules/gateway/fs/index>`. /fs. The location specified using **gateway.fs.location** will automatically be used in this case to store index level data (appended by the index name)/index>`. 
