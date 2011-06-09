.. _es-guide-reference-river-index:
.. _es-guide-reference-river:

=====
River
=====

A river is a pluggable service running within elasticsearch cluster pulling data (or being pushed with data) that is then indexed into the cluster.


A river is composed of a unique name and a type. The type is the type of the river (out of the box, there is the **dummy** river that simply logs that its running). The name uniquely identifies the river within the cluster. For example, one can run a river called **my_river** with type **dummy**, and another river called **my_other_river** with type **dummy**.

.. toctree::
    :maxdepth: 2
	
    couchdb
    rabbitmq
    twitter
    wikipedia


How it Works
============

A river instance (and its name) is a type within the **_river** index. All different rivers implementations accept a document called **_meta** that at the very least has the type of the river (twitter / couchdb / ...) associated with it. Creating a river is a simple curl request to index that **_meta** document (there is actually a **dummy** river used for testing):


.. code-block:: js

    curl -XPUT 'localhost:9200/_river/my_river/_meta' -d '{
        "type" : "dummy"
    }'


A river can also have more data associated with it in the form of more documents indexed under the given index type (the river name). For example, storing the last indexed state can be stored in a document that holds it.


Deleting a river is a call to delete the type (and all documents associated with it):


.. code-block:: js

    curl -XDELETE 'localhost:9200/_river/my_river/'


Cluster Allocation
==================

Rivers are singletons within the cluster. They get allocated automatically to one of the nodes and run. If that node fails, an river will be automatically allocated to another node.


River allocation on nodes can be controlled on each node. The **node.river** can be set to **_none_** disabling any river allocation to it. The **node.river** can also include a comma separated list of either river names or types controlling the rivers allowed to run on it. For example: **my_river1,my_river2**, or **dummy,twitter**.


Status
======

Each river (regardless of the implementation) exposes a high level **_status** doc which includes the node the river is running on. Getting the status is a simple curl GET request to **/_river/{river name}/_status**.


