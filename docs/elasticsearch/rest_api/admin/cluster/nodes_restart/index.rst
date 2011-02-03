Nodes Restart
=============

The nodes restart API allows to restart one or more (or all) nodes in the cluster. Here is an example of shutting the **_local** node the request is directed to:


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/_cluster/nodes/_local/_restart'


Specific node(s) can be restarted as well using their respective node ids:


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/_cluster/nodes/nodeId1,nodeId2/_restart'


The master (of the cluster) can also be restarted using:


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/_cluster/nodes/_master/_restart'


Finally, all nodes can be restarted using either options below:


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/_cluster/nodes/_restart'
    
    $ curl -XPOST 'http://localhost:9200/_cluster/nodes/_all/_restart'


Delay
-----

By default, the restart will be executed after a 1 seconds delay (**1s**). The delay can be customized by setting the **delay** parameter in a time value format. For example:


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/_cluster/nodes/_local/_restart?delay=10s'


Restart Execution
-----------------

When the node is started using the service wrapper, a restart will cause a full JVM exit and a new JVM will be created. This is the preferable manner to perform the restart. When not started using the service wrapper, the node will perform an internal restart within the same JVM.
